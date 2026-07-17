# Carbon Emission Calculator

## Project Description

The Carbon Emission Calculator is a Streamlit web application that calculates a company's carbon footprint from energy usage, waste generation, and business travel data. It compares each result to a benchmark, shows visual comparisons against other saved clients, and generates a downloadable PDF report with tailored recommendations.

## Features

- Calculate energy, waste, travel, and total carbon emissions from user inputs.
- Compare each emission category to a fixed benchmark and surface recommendations when it's exceeded.
- Visualize emissions data with interactive Plotly bar charts, highlighting the current client among all saved ones.
- Generate and download a PDF report with emissions data, recommendations, and charts.
- Persist every calculated report to a local SQLite database (`carbon_reports.db`) for historical comparison.

## Project Structure

| File | Responsibility |
|---|---|
| `app.py` | Streamlit UI: input forms, buttons, and page flow. |
| `emissions.py` | `CarbonFootprint` class: the emission calculations and benchmark comparisons. |
| `recommendations.py` | Static recommendation text shown when a benchmark is exceeded. |
| `reporting.py` | `ReportGenerator` (SQLite persistence), chart building, and PDF generation. |

## Technology Stack

- **Programming Language**: Python
- **Web Framework**: Streamlit
- **Data Manipulation**: Pandas
- **Data Storage**: SQLite (via `sqlite3` + pandas)
- **Data Visualization**: Plotly
- **PDF Generation**: ReportLab + Kaleido (chart-to-image export)

## Installation

```bash
pip install -r requirements.txt
```

## Usage

1. Run the app: `streamlit run app.py`
2. Enter your energy usage, waste generation, and business travel data in each section.
3. Click "Calculate Total Emission & Generate Report" to see the total, the benchmark comparisons, and the emissions charts.
4. Download the PDF report for your records.

Each report is saved to `carbon_reports.db` in the project directory; re-submitting the same values won't create duplicate rows.

## Error Handling

- **Input Validation**: Ensures all required fields are filled and numeric before performing calculations.
- **User Feedback**: Provides clear success, warning, and error messages throughout the flow.

## Contributing

Contributions are welcome! Please follow these steps to contribute:
1. Fork the repository.
2. Create a new branch (`git checkout -b feature-branch`).
3. Make your changes and commit them (`git commit -m 'Add new feature'`).
4. Push to the branch (`git push origin feature-branch`).
5. Open a pull request.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

## Contact Information

For any questions or feedback, please contact:
- Name: [Parisa Khosravi]
- Email: [Parisakhosravi39@gmail.com]
- GitHub: [(https://github.com/parisakh4)]
 
