import uuid
from datetime import datetime

import streamlit as st

from emissions import CarbonFootprint
from reporting import ReportGenerator, generate_pdf, plot_colored_bar_chart, save_figures_as_images

ENERGY_BENCHMARK = 352500
WASTE_BENCHMARK = 152750
TRAVEL_BENCHMARK = 76100
TOTAL_BENCHMARK = 581350


def handle_emission_calculation(carbon_footprint, emission_type, raw_inputs, calculate_fn, benchmark):
    """Validate inputs, run the calculation, store it in session state, and show benchmark feedback."""
    if not all(value.strip() for value in raw_inputs):
        st.warning("Please fill in all fields.")
        return

    try:
        parsed_inputs = [float(value) for value in raw_inputs]
    except ValueError:
        st.error("Please enter valid numbers for all inputs.")
        return

    emission = calculate_fn(*parsed_inputs)
    st.session_state[f"{emission_type}_emission"] = emission
    st.success(f"{emission_type.capitalize()} carbon emission: {emission:.2f} kgCO2/year.")

    message, recommendations, exceeds_benchmark = carbon_footprint.compare_to_benchmark(emission_type, emission, benchmark)
    st.warning(message)
    if exceeds_benchmark:
        with st.expander("See recommendations for Improvements"):
            st.write(recommendations, unsafe_allow_html=True)


def render_total_emission_section(carbon_footprint, report_generator):
    st.subheader("Total Carbon Footprint")
    st.write("Click the button below to calculate the total carbon footprint and see the overview and comparisons. You can also save your results as a report.")

    total_emission = carbon_footprint.calculate_total_emission()
    st.session_state["total_emission"] = total_emission

    if not st.button("Calculate Total Emission & Generate Report"):
        return

    if not all([st.session_state.get("energy_emission"), st.session_state.get("waste_emission"), st.session_state.get("travel_emission")]):
        st.error("Please fill in all fields.")
        return

    st.success(f"Total carbon emission: {total_emission:.2f} kgCO2/year.")

    message, _, _ = carbon_footprint.compare_to_benchmark("total", total_emission, TOTAL_BENCHMARK)
    st.warning(message)

    if total_emission is None:
        return

    active_client_id = st.session_state["active_client_id"]
    st.session_state["client_data"] = {
        "client_id": active_client_id,
        "energy_emission": carbon_footprint.energy_emission,
        "waste_emission": carbon_footprint.waste_emission,
        "travel_emission": carbon_footprint.travel_emission,
        "total_emission": total_emission,
        "report_date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    }

    # Values alone, not report_date: re-clicking with unchanged inputs shouldn't add a duplicate row.
    emission_signature = (active_client_id, carbon_footprint.energy_emission, carbon_footprint.waste_emission, carbon_footprint.travel_emission, total_emission)
    if st.session_state.get("last_saved_signature") != emission_signature:
        report_generator.save_report(st.session_state["client_data"])
        st.session_state["last_saved_signature"] = emission_signature

    all_reports = report_generator.load_all_reports()
    all_reports = all_reports.dropna(subset=["energy_emission", "waste_emission", "travel_emission"])
    all_reports["short_client_id"] = all_reports["client_id"].apply(lambda x: x[:8])

    charts = []
    if not all_reports.empty:
        for emission_type, title in [
            ("energy_emission", "Energy Emissions Comparison"),
            ("waste_emission", "Waste Emissions Comparison"),
            ("travel_emission", "Travel Emissions Comparison"),
            ("total_emission", "Total Emissions Comparison"),
        ]:
            chart = plot_colored_bar_chart(all_reports, active_client_id, emission_type, title)
            st.plotly_chart(chart)
            charts.append(chart)
    st.session_state["charts"] = charts

    recommendations = {
        "energy": carbon_footprint.get_energy_recommendations(),
        "waste": carbon_footprint.get_waste_recommendations(),
        "travel": carbon_footprint.get_travel_recommendations(),
    }
    image_files = save_figures_as_images(charts)
    pdf_buffer = generate_pdf(st.session_state["client_data"], image_files, recommendations)

    st.download_button(
        label="Download Report as PDF",
        data=pdf_buffer,
        file_name=f"report_{st.session_state['client_data']['client_id']}.pdf",
        mime="application/pdf",
    )


def main():
    if "client_id" not in st.session_state:
        st.session_state["client_id"] = str(uuid.uuid4())
    if "active_client_id" not in st.session_state:
        st.session_state["active_client_id"] = st.session_state["client_id"]
    if "charts" not in st.session_state:
        st.session_state["charts"] = []
    if "carbon_footprint" not in st.session_state:
        st.session_state["carbon_footprint"] = CarbonFootprint(st.session_state["client_id"])
    carbon_footprint = st.session_state["carbon_footprint"]

    st.title("Carbon Footprint Assessment made quick and accurate")
    st.write(
        "Obtain the most accurate data with our carbon footprint monitoring tool, supported and developed by our "
        "committed Climate team. Our web application calculates the carbon footprint based on the most important "
        "factors including Energy Usage, Waste and Business Travel of your company."
    )

    report_generator = ReportGenerator()

    # Energy emission
    st.subheader("Energy Usage")
    st.write("Please answer the following questions and type your answers in euros.")
    electricity = st.text_input("What is your average monthly electricity bill?")
    gas = st.text_input("What is your average monthly natural gas bill?")
    fuel = st.text_input("What is your average monthly fuel bill for transportation?")
    if st.button("Calculate Energy Emission"):
        handle_emission_calculation(
            carbon_footprint, "energy", [electricity, gas, fuel], carbon_footprint.calculate_energy_emission, ENERGY_BENCHMARK
        )

    # Waste emission
    st.subheader("Waste")
    waste_generate = st.text_input("How much do you generate per month in Kilograms?")
    waste_recycle = st.text_input("What percentage of that waste is recycled or composted?")
    if st.button("Calculate Waste Emission"):
        handle_emission_calculation(
            carbon_footprint, "waste", [waste_generate, waste_recycle], carbon_footprint.calculate_waste_emission, WASTE_BENCHMARK
        )

    # Travel emission
    st.subheader("Business Travel")
    travel_km = st.text_input("How many kilometers do your employees travel per year for business purposes?")
    fuel_efficiency = st.text_input("What is the average fuel efficiency of the vehicles used for business travel in liters per 100 kilometers?")
    if st.button("Calculate Travel Emission"):
        handle_emission_calculation(
            carbon_footprint, "travel", [travel_km, fuel_efficiency], carbon_footprint.calculate_travel_emission, TRAVEL_BENCHMARK
        )

    render_total_emission_section(carbon_footprint, report_generator)


if __name__ == "__main__":
    main()
