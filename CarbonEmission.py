import streamlit as st
import os
import pandas as pd
import uuid
from datetime import datetime
import plotly.express as px
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
import io
import plotly.io as pio
import tempfile
import kaleido
from reportlab.lib.pagesizes import letter
from reportlab.lib.utils import simpleSplit
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image
import re


# Convert Plotly figures to images
def save_figures_as_images(figures):
    image_files = []
    for i, fig in enumerate(figures):
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".png")
        pio.write_image(fig, temp_file.name, engine="kaleido")
        image_files.append(temp_file.name)
    return image_files

def generate_pdf(client_data, image_files, recommendations):
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter)
    elements = []
    styles = getSampleStyleSheet()

    # Add client data
    elements.append(Paragraph(f"Client ID: {client_data['client_id']}", styles['Normal']))
    elements.append(Paragraph(f"Energy Emission: {client_data['energy_emission']} kgCO2/year", styles['Normal']))
    elements.append(Paragraph(f"Waste Emission: {client_data['waste_emission']} kgCO2/year", styles['Normal']))
    elements.append(Paragraph(f"Travel Emission: {client_data['travel_emission']} kgCO2/year", styles['Normal']))
    elements.append(Paragraph(f"Total Emission: {client_data['total_emission']} kgCO2/year", styles['Normal']))
    elements.append(Paragraph(f"Report Date: {client_data['report_date']}", styles['Normal']))
    elements.append(Spacer(1, 0.2 * inch))

    # Add recommendations with HTML formatting
    elements.append(Paragraph("Recommendations:", styles['Heading2']))
    for key, recommendation in recommendations.items():
        # Replace <br> with <br/> to ensure proper handling
        formatted_recommendation = recommendation.replace("<br>", "<br/>")
        # Convert Markdown-style bolding to HTML tags
        formatted_recommendation = re.sub(r'\*\*(.*?)\*\*', r'<b>\1</b>', formatted_recommendation)
        # Remove HTML links
        formatted_recommendation = re.sub(r'<a href="[^"]+">([^<]+)</a>', r'\1', formatted_recommendation)
        elements.append(Paragraph(f"<b>{key.capitalize()}:</b> {formatted_recommendation}", styles['Normal']))
        elements.append(Spacer(1, 0.2 * inch))

    # Add charts
    for image_file in image_files:
        elements.append(Spacer(1, 0.2 * inch))
        elements.append(Image(image_file, width=400, height=200))

    # Build PDF
    doc.build(elements)
    buffer.seek(0)
    return buffer

#for colored bar for the active client in the bar chart
def plot_colored_bar_chart(data, active_client_id, emission_type, title):
    #Adding a column to distinguish active client
    data['color'] = data['client_id'].apply(
        lambda x: 'orange' if x == active_client_id else 'steelblue'
    )

    #Creatinh Plotly bar chart
    fig = px.bar(
        data,
        x='short_client_id',
        y=emission_type,
        color='color',
        color_discrete_map={'orange': 'orange', 'steelblue': 'steelblue'},
        title=title,
        labels={'short_client_id': 'Client ID', emission_type: f'{title} Emission'}
    )
    return fig


#class for storing and managing client data
class CarbonFootprint:
    def __init__(self,client_id):
        self.client_id = client_id
        self.energy_emission = None
        self.waste_emission = None
        self.travel_emission = None
    
    #calculating carbon emissions 
    def calculate_energy_emission(self, electricity, gass, fuel):
        try:
            self.energy_emission = electricity * 12 * 0.0005 + gass * 12 * 0.0053 + fuel * 12 * 2.23
            return self.energy_emission
        except ValueError:
            return None
        
    def calculate_waste_emission(self, waste_generate, waste_recycle):
        try:
            #Converting waste_recycle to percentages if provided as whole number
            waste_recycle = waste_recycle / 100 if waste_recycle > 1 else waste_recycle
            self.waste_emission = waste_generate * 12 * (0.57 - waste_recycle)
            return self.waste_emission
        except ValueError:
            return None
        
    def calculate_travel_emission(self, travel_km, fuel_efficiency):
        try:
            self.travel_emission = travel_km * (1 / fuel_efficiency) * 2.31
            return self.travel_emission
        except ValueError:
            return None
        
    def calculate_total_emission(self):
        if self.energy_emission is not None and self.waste_emission is not None and self.travel_emission is not None:
            return self.energy_emission + self.waste_emission + self.travel_emission
        else:
            return None

    #generate recommendations
    def get_energy_recommendations(self):
        energy_recommendations ="""Recommendations for reducing carbon emissions from energy usage in commercial buildings:<br><br> 
                                 **Energy Management Systems:**<br> Implement effective energy management systems to monitor and control energy usage efficiently.<br><br> ​
                                **HVAC Systems:**<br> Upgrade to energy-efficient HVAC systems, including the use of heat recovery, natural ventilation, ground source heat pumps, high-efficiency chillers, and variable frequency drives (VFD) for pumps.<br><br> ​
                                **Lighting Systems:**<br> Use energy-efficient lighting solutions such as compact fluorescent bulbs, LED lights, and automated lighting controls.<br><br> ​
                                **Building Envelope Improvements:**<br> Enhance building insulation, adopt cool roof technology, and use environmentally friendly construction materials to improve thermal performance and reduce energy consumption.<br><br> ​
                                **Occupant Behavior:**<br> Train occupants, building managers, and tenants on energy efficiency practices and encourage behavior changes to reduce energy usage.<br><br> ​
                                **Energy Monitoring:**<br> Install sensors, sub-meters, and CO2 sensors to optimize energy usage and improve energy efficiency.<br><br> ​
                                **Renewable Energy:**<br> Integrate renewable energy sources such as solar panels and combined cooling, heating, and power (CCHP) systems to reduce reliance on fossil fuels. <br><br>​
                                **Retrofits and Upgrades:**<br> Conduct energy audits and retrofits to identify and implement energy-saving measures, such as upgrading data centers and server rooms, and improving the energy efficiency of motors and on-site generation.<br><br> ​
                                **Government Support and Incentives:**<br> Leverage government programs, incentives, and guidelines to support the implementation of energy-saving measures and promote the adoption of green building practices.<br><br> ​
                                These recommendations aim to reduce energy consumption and, consequently, carbon emissions from commercial buildings.<br> Sources:[Renewable and Sustainable Energy Reviews](https://www.sciencedirect.com/science/article/pii/S1364032119307531?casa_token=JVgGp10Cn1QAAAAA:4WsyKrseSoDtFCIBbjuDQuobv6m-edBWj0kFDvgm4JPbY8oWTBm9FddwkVYI4f3sm2EphfQBbks), [Energy and Buildings](https://www.sciencedirect.com/science/article/pii/S037877881930595X?casa_token=thtFaPllaYYAAAAA:Utb84qtEZV-PcYsPPpT5SnN56QQi2EK0yzD3tX8n9Qfl44pbRMysqsIysJxzjAxWZ2w72904kDw) ​ """
        return energy_recommendations
    
    def get_waste_recommendations(self):
        waste_recommendations = """Recommendations for Reducing Waste Emissions in Commercial Buildings To effectively reduce waste emissions in commercial buildings, the following inclusive recommendations are proposed:<br><br>
                                    **Implement Separate Collection Models:**<br>
                                    Adopt the dry-wet separate collection model within commercial buildings. Ensure that waste segregation bins are easily accessible and clearly labeled to facilitate the removal of dry recyclables and the composting of organic waste.<br><br>
                                    **Promote Composting:**<br>
                                    Establish on-site or off-site composting programs for organic waste generated in commercial buildings, such as food scraps from cafeterias and landscaping waste. Use the matured compost as a substitute fertilizer for landscaping or offer it to local agricultural projects.<br><br> ​
                                    **Controlled Waste Disposal:**<br>
                                    Ensure that non-recyclable and non-compostable waste is disposed of in controlled landfills. Implement waste audits to identify and minimize the amount of waste sent to landfills.<br><br>
                                    **Support Organized Recycling Programs:**<br>
                                    Develop and support organized recycling programs within commercial buildings. Provide training and resources to employees to encourage participation in recycling activities. Partner with local recycling facilities to ensure proper processing of recyclable materials.<br><br> ​
                                    **Develop and Implement Green Building Certifications:**<br>
                                    Pursue green building certifications such as LEED (Leadership in Energy and Environmental Design) or BREEAM (Building Research Establishment Environmental Assessment Method) that include waste management criteria. Implement practices that align with these certifications to reduce waste emissions.<br><br> ​
                                    **Enhance Financial and Institutional Support:**<br>
                                    Apply economic instruments such as waste disposal fees, recycling credits, and subsidies to incentivize better waste management practices within commercial buildings. ​ Ensure these instruments are fair, enforced, and adapted to the specific needs of commercial properties.<br><br> ​
                                    Strengthen policies and guidelines for integrated waste management in commercial buildings and secure adequate funding for waste management services.
                                    **Increase Public Awareness and Education:**<br>
                                    Conduct awareness programs and training sessions for building occupants and staff to educate them on the importance of waste segregation, recycling, and composting. Promote environmental awareness and the benefits of sustainable waste management practices.<br><br> ​
                                    **Encourage Public-Private Partnerships:**<br>
                                    Foster public-private partnerships to enhance waste management services in commercial buildings. ​ Involve private sector companies in recycling and waste diversion activities, and ensure their participation is regulated and monitored.<br><br>
                                    **Local Involvement and Customization:**<br>
                                    Engage building management and occupants in the design and implementation of waste management systems. Tailor solutions to the specific needs and conditions of the commercial building to ensure effective and sustainable waste management practices.<br><br>
                                    **Monitor and Evaluate:**<br>
                                    Establish robust monitoring and evaluation mechanisms to track the effectiveness of waste management strategies and carbon emission reductions in commercial buildings. Use data to continuously improve practices and policies.<br><br>
        
                                    By implementing these recommendations, commercial buildings can significantly reduce waste emissions, improve environmental quality, and promote sustainable business practices. <br> Source:[Waste Manageent](https://www.sciencedirect.com/science/article/pii/S0956053X10002229?casa_token=4cmTS-biZmoAAAAA:jo_geg3FXEVFtM9NB3Sw__ay1SmBxeA8uoRFBvnWD-crXpu-1G0a1OcQpNCGgdEB2FhaJCGQdGg)"""
        return waste_recommendations
    def get_travel_recommendations(self):
        travel_recommendations= """Recommendations for reducing carbon emissions from business travels:<br><br>
                                **Reduce the Need for Travel:**<br>
                                Implement policies that prioritize virtual meetings over physical travel whenever possible. ​<br>
                                Encourage employees to replace at least one face-to-face meeting with a virtual meeting to save costs and reduce carbon emissions. ​<br><br>
                                **Change Travel Modes:**<br>
                                Promote the use of less carbon-intensive travel modes, such as trains instead of flights or cars.<br> ​
                                Provide incentives for employees to use public transportation or carpooling for business trips.<br><br>
                                **Optimize Travel Policies:**<br>
                                Reduce the class of air travel from business to economy to make flying less attractive and encourage alternative modes of travel.<br> ​
                                Re-negotiate contracts with travel management companies to include sustainability criteria.<br><br>
                                **Improve Meeting Management:**<br>
                                Implement better meeting management practices to ensure that meetings are productive and time-efficient, reducing the need for extended travel.<br> ​
                                Set realistic agendas and objectives for meetings to maximize their effectiveness.<br><br> ​
                                **Benefit from Technology:**<br>
                                Utilize new communication methods such as social media, smart phones, and collaborative tools to facilitate remote work and reduce the need for travel.<br><br ​
                                Encourage the use of desktop video conferencing and instant messaging for quick and efficient communication.<br><br>
                                **Address Organizational Culture and Behaviors:**<br>
                                Foster a culture that values sustainability and supports the use of virtual communication tools.<br> ​
                                Provide training and support to employees to help them become comfortable with using virtual meeting technologies.<br><br>
                                **Public Accountability and Reporting:**<br>
                                Participate in external reporting frameworks like the Carbon Reduction Commitment and the Carbon Disclosure Project to drive internal changes and maintain a good reputation with customers and stakeholders.<br> ​
                                Set and monitor carbon budgets or targets for business travel to encourage responsible travel practices.<br><br> ​
                                **Customer Engagement:**<br>
                                Work with customers to manage expectations and promote the use of virtual meetings for supplier interactions.<br> ​
                                Educate customers on the benefits of reducing carbon emissions from business travel and encourage their participation in sustainability initiatives.<br><br>
                                **Support Work-Life Balance:**<br>
                                Develop policies that support flexible working arrangements and reduce the need for frequent travel, improving employees' work-life balance.<br> ​
                                Encourage home working and remote collaboration to minimize the necessity of physical presence.<br><br> ​
                                By implementing these recommendations, organizations can effectively reduce carbon emissions from business travel while maintaining productivity and meeting business objectives.<br> Source: [Transportation Research Part A: Policy and Practice](https://www.sciencedirect.com/science/article/pii/S096585641400202X?casa_token=I8YVgZJoUh4AAAAA:3Gy5FpCCnQA5fiJr9KODugw7n-MxPESsu_31tT5dDq6onkoewG9xNh4yPxtZ4bC4h0szEOKbKBU) ​ """
        return travel_recommendations

    
    #benchmark comparison 
    def compare_to_benchmark(self, emission_type, emission_value, benchmark):
        if emission_value > benchmark:
            message= f"Your {emission_type} emission exceeds the benchmark of {benchmark} kgCO2/year."
            if emission_type == "total":
                recommendations = None
            else:
                recommendations = getattr(self, f"get_{emission_type}_recommendations")()
            return message, recommendations, True
        else:
            message = f"Your {emission_type} emission is within the benchmark of {benchmark} kgCO2/year."
            return message, None, False
        
#class for generating and saving reports
class ReportGnerator:
    def __init__(self):
        self.columns = ["clinet_id","energy_emission", "waste_emission", "travel_emission", "total_emission", "report_date"]
        self.file_path = "client_data.csv"
        self._ensure_file_exists()

    def _ensure_file_exists(self):
        if not os.path.exists(self.file_path):
          df = pd.DataFrame(columns = self.columns)  
          df.to_csv(self.file_path, index = False)

    def save_report(self, client_data):
        total_emission = client_data.get("total_emission")  # Get the total emission from the dictionary
        if total_emission is not None:
            # Read the existing data from the CSV file
            df = pd.read_csv(self.file_path)
            
            # Convert the client_data dictionary into a DataFrame and append it to the existing DataFrame
            new_data = pd.DataFrame([client_data])
            df = pd.concat([df, new_data], ignore_index=True)
            
            # Save the updated DataFrame back to the CSV file
            df.to_csv(self.file_path, index=False)
        else:
            print("Incomplete data, cannot generate report.")
    
    def load_all_reports(self):
        return pd.read_csv(self.file_path)

def main():

    #Generating Id for client
    if "client_id" not in st.session_state:
        st.session_state["client_id"] = str(uuid.uuid4())
        
    #Set active client ID for tracking
    if "active_client_id" not in st.session_state:
        st.session_state["active_client_id"] = st.session_state["client_id"]

    if "charts" not in st.session_state:
        st.session_state["charts"] = []
        
    #Shorten the displayed client ID
    short_id = st.session_state["client_id"][:8]
    st.title("Carbon Footprint Assessment made quick and accurate")
    st.write("Obtain the most accurate data with our carbon footprint monitotring tool, supported and develope by our commited Climate team. Our web application calcuates the carbon footprint based on the most important factors including Energy Usage, Waste and Business Travles of your company.  ")
    
    #creating a new instance for the report generator
    report_generator = ReportGnerator()
    client_id = st.session_state["client_id"]
    carbon_footprint = CarbonFootprint(client_id)

    if "carbon_footprint" not in st.session_state:
        st.session_state["carbon_footprint"] = CarbonFootprint(st.session_state["client_id"])

    carbon_footprint = st.session_state["carbon_footprint"]

    #energy emission calculation
    st.subheader("Energy Usage")
    st.write("Please answer the following questions and type your answers in euros." )

    electricity = st.text_input("What is your average monthly electricity bill?")
    gass = st.text_input("What is your average monthly natural gas bill?")
    fuel = st.text_input("What is your avarage monthly fuel bill for transportation?")


    if st.button("Calculate Energy Emission"):
        
        if electricity.strip() and gass.strip() and fuel.strip():
            try:
                electricity = float(electricity)
                gass = float(gass)
                fuel = float(fuel)

                energy_emission = carbon_footprint.calculate_energy_emission(electricity, gass, fuel)
                st.session_state["energy_emission"] = energy_emission #storing in session state
                st.success(f"Energy carbon emission: {carbon_footprint.energy_emission:.2f} kgCO2/year.")
                
                #comparing to benchmark
                energy_benchmark= 352500    
                benchmark_message , recommendations, exceeds_benchmark = carbon_footprint.compare_to_benchmark("energy", carbon_footprint.energy_emission, energy_benchmark)
                st.warning(benchmark_message)

                if exceeds_benchmark:
                    with st.expander("See recommendations for Improvements"):
                        st.write(recommendations, unsafe_allow_html=True)
            
            except ValueError:
                st.error("Please enter valid numbers for all inputs.")
        else:
            st.warning("Please fill in all fields.")


    #waste_emission_calculation
    st.subheader("Waste")
    waste_generate = st.text_input("How much do you generate per month in Kilograms?")
    waste_recycle = st.text_input("What percentage of that waste is recycled or composed?")

    if st.button("Calculate Waste Emission"):
        
        if waste_generate.strip() and waste_recycle.strip():
            try:
                waste_generate = float(waste_generate)
                waste_recycle = float(waste_recycle)

                waste_emission = carbon_footprint.calculate_waste_emission(waste_generate, waste_recycle)
                st.session_state["waste_emission"] = waste_emission #storing 
                st.success(f"Waste carbon emission: {carbon_footprint.waste_emission:.2f} kgCO2/year.")

                # Benchmark Comparison
                waste_benchmark = 152750
                benchmark_message , recommendations, exceeds_benchmark = carbon_footprint.compare_to_benchmark("waste", carbon_footprint.waste_emission, waste_benchmark)
                st.warning(benchmark_message)

                if exceeds_benchmark:
                    with st.expander("See recommendations for Improvements"):
                        st.write(recommendations, unsafe_allow_html=True)
            
            except ValueError:
                st.error("Please enter valid numbers for all inputs.")
        else:
            st.warning("Please fill in all fields.")

    #travel emission calculation
    st.subheader("Business Travel")
    travel_km = st.text_input("How many kilometers do your employees travel per year for business purposes?")
    fuel_efficiency= st.text_input("What is the average fuel efficiency of the vehicles used for business travel in liters per 100 kilometers?")

    if st.button("Calculate Travel Emission"):
        
        if travel_km.strip() and fuel_efficiency.strip():
            try:
                travel_km = float(travel_km)
                fuel_efficiency = float(fuel_efficiency)

                travel_emission = carbon_footprint.calculate_travel_emission(travel_km, fuel_efficiency)
                st.session_state["travel_emission"] = travel_emission 
                st.success(f'Your carbon emission from business travels is {carbon_footprint.travel_emission:.2f} kgCO2. ')
        
                #benchmark comparison
                travel_benchmark = 76100
                benchmark_message , recommendations, exceeds_benchmark = carbon_footprint.compare_to_benchmark("travel", carbon_footprint.travel_emission, travel_benchmark)
                st.warning(benchmark_message)

                if exceeds_benchmark:
                    with st.expander("See recommendations for Improvements"):
                        st.write(recommendations, unsafe_allow_html=True)

            except ValueError:
                st.error("Please enter valid numbers for all inputs.")
        else:
            st.warning("Please fill in all fields.")

    st.subheader("Total Carbon Footprint")
    st.write("Click the button below to calculate the total carbon footprint and see the overview and comparisons. You can also save your results as a report.")
    
    total_emission = carbon_footprint.calculate_total_emission()
    st.session_state["total_emission"] = total_emission  # Store total emission
    
    if st.button("Total Emission Overview and Report- Click twice"):
        # Validate inputs
        if not all([st.session_state.get("energy_emission"), st.session_state.get("waste_emission"), st.session_state.get("travel_emission")]):
            st.error("Please fill in all fields.")
        else:
            
            st.success(f"Total carbon emission: {total_emission:.2f} kgCO2/year.")

            # Compare total emission to benchmark
            total_benchmark = 581350
            benchmark_message, recommendations, exceeds_benchmark = carbon_footprint.compare_to_benchmark("total", total_emission, total_benchmark)
            st.warning(benchmark_message)

            if total_emission is not None:
                st.session_state["client_data"] = {
                        "client_id": st.session_state["active_client_id"], 
                        "energy_emission": carbon_footprint.energy_emission,
                        "waste_emission": carbon_footprint.waste_emission,
                        "travel_emission": carbon_footprint.travel_emission,
                        "total_emission": total_emission,
                        "report_date": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    }



                all_reports = report_generator.load_all_reports()
                # Remove rows where any emission data is missing
                all_reports = all_reports.dropna(subset=["energy_emission", "waste_emission", "travel_emission"])

                all_reports['short_client_id'] = all_reports['client_id'].apply(lambda x: x[:8])
                
                # Ensure active client data is included if complete
                active_client_id = st.session_state["active_client_id"]
                if active_client_id in all_reports["client_id"].values:
                    active_client_data = all_reports[all_reports["client_id"] == active_client_id]
                    if active_client_data.dropna(subset=["energy_emission", "waste_emission", "travel_emission"]).empty:
                        # Remove active client row if incomplete
                        all_reports = all_reports[all_reports["client_id"] != active_client_id]

                charts = []

                if not all_reports.empty:
                    # Bar chart for energy emissions
                    energy_chart = plot_colored_bar_chart(all_reports, st.session_state["active_client_id"], "energy_emission", "Energy Emissions Comparison")
                    st.plotly_chart(energy_chart)
                    charts.append(energy_chart)

                    # Bar chart for waste emissions
                    waste_chart = plot_colored_bar_chart(all_reports, st.session_state["active_client_id"], "waste_emission", "Waste Emissions Comparison")
                    st.plotly_chart(waste_chart)
                    charts.append(waste_chart)

                    # Bar chart for travel emissions
                    travel_chart = plot_colored_bar_chart(all_reports, st.session_state["active_client_id"], "travel_emission", "Travel Emissions Comparison")
                    st.plotly_chart(travel_chart)
                    charts.append(travel_chart)

                    # Bar chart for total emissions
                    total_chart = plot_colored_bar_chart(all_reports, st.session_state["active_client_id"], "total_emission", "Total Emissions Comparison")
                    st.plotly_chart(total_chart)
                    charts.append(total_chart)

                st.session_state["charts"] = charts

        
                report_generator.save_report(st.session_state["client_data"])

                # Capture recommendations
                energy_recommendations = carbon_footprint.get_energy_recommendations()
                waste_recommendations = carbon_footprint.get_waste_recommendations()
                travel_recommendations = carbon_footprint.get_travel_recommendations()

                recommendations = {
                    "energy": energy_recommendations,
                    "waste": waste_recommendations,
                    "travel": travel_recommendations
                }

                # Convert charts to images
                image_files = save_figures_as_images(st.session_state["charts"])
                
                # Generate PDF
                pdf_buffer = generate_pdf(st.session_state["client_data"], image_files, recommendations)
                
                # Download button for PDF
                st.download_button(
                    label="Download Report as PDF",
                    data=pdf_buffer,
                    file_name=f"report_{st.session_state['client_data']['client_id']}.pdf",
                    mime="application/pdf"
            )
if __name__ == "__main__":
    main()