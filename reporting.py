"""Persisting client reports to SQLite, charting emissions, and building the PDF report."""
import io
import re
import sqlite3
import tempfile

import pandas as pd
import plotly.express as px
import plotly.io as pio
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image


class ReportGenerator:
    def __init__(self, db_path="carbon_reports.db"):
        self.db_path = db_path
        self._ensure_table_exists()

    def _connect(self):
        # sqlite3.connect() creates the file on disk if it doesn't exist yet
        return sqlite3.connect(self.db_path)

    def _ensure_table_exists(self):
        with self._connect() as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS reports (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    client_id TEXT NOT NULL,
                    energy_emission REAL,
                    waste_emission REAL,
                    travel_emission REAL,
                    total_emission REAL,
                    report_date TEXT
                )
            """)

    def save_report(self, client_data):
        if client_data.get("total_emission") is None:
            print("Incomplete data, cannot generate report.")
            return
        with self._connect() as conn:
            pd.DataFrame([client_data]).to_sql("reports", conn, if_exists="append", index=False)

    def load_all_reports(self):
        with self._connect() as conn:
            return pd.read_sql("SELECT * FROM reports", conn)


def plot_colored_bar_chart(data, active_client_id, emission_type, title):
    """Bar chart highlighting the active client's bar in orange among all clients."""
    data = data.copy()
    data["color"] = data["client_id"].apply(lambda x: "orange" if x == active_client_id else "steelblue")

    return px.bar(
        data,
        x="short_client_id",
        y=emission_type,
        color="color",
        color_discrete_map={"orange": "orange", "steelblue": "steelblue"},
        title=title,
        labels={"short_client_id": "Client ID", emission_type: f"{title} Emission"},
    )


def save_figures_as_images(figures):
    """Render Plotly figures to temporary PNG files for embedding in the PDF."""
    image_files = []
    for fig in figures:
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".png")
        pio.write_image(fig, temp_file.name, engine="kaleido")
        image_files.append(temp_file.name)
    return image_files


def _format_recommendation_html(recommendation):
    formatted = recommendation.replace("<br>", "<br/>")
    formatted = re.sub(r"\*\*(.*?)\*\*", r"<b>\1</b>", formatted)
    formatted = re.sub(r'<a href="[^"]+">([^<]+)</a>', r"\1", formatted)
    return formatted


def generate_pdf(client_data, image_files, recommendations):
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter)
    styles = getSampleStyleSheet()
    elements = []

    elements.append(Paragraph(f"Client ID: {client_data['client_id']}", styles["Normal"]))
    elements.append(Paragraph(f"Energy Emission: {client_data['energy_emission']} kgCO2/year", styles["Normal"]))
    elements.append(Paragraph(f"Waste Emission: {client_data['waste_emission']} kgCO2/year", styles["Normal"]))
    elements.append(Paragraph(f"Travel Emission: {client_data['travel_emission']} kgCO2/year", styles["Normal"]))
    elements.append(Paragraph(f"Total Emission: {client_data['total_emission']} kgCO2/year", styles["Normal"]))
    elements.append(Paragraph(f"Report Date: {client_data['report_date']}", styles["Normal"]))
    elements.append(Spacer(1, 0.2 * inch))

    elements.append(Paragraph("Recommendations:", styles["Heading2"]))
    for key, recommendation in recommendations.items():
        formatted_recommendation = _format_recommendation_html(recommendation)
        elements.append(Paragraph(f"<b>{key.capitalize()}:</b> {formatted_recommendation}", styles["Normal"]))
        elements.append(Spacer(1, 0.2 * inch))

    for image_file in image_files:
        elements.append(Spacer(1, 0.2 * inch))
        elements.append(Image(image_file, width=400, height=200))

    doc.build(elements)
    buffer.seek(0)
    return buffer
