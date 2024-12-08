import streamlit as st
import os
import pandas as pd
import uuid

#Generating Id for client
if "client_id" not in st.session_state:
    st.session_state["client_id"] = str(uuid.uuid4())
    st.sidebar.write(f"Your Client ID: {st.session_state['client_id']}")

#class for storing and managing client data
class CarbonFootprint:
    def __init__(self,client_id):
        self.client_id = client_id
        self.energy_emission = None
        self.waste_emission = None
        self.travel_emission = None
    
    def calculate_energy_emission(self, electricity, gass, fuel):
        try:
            self.energy_emission = electricity * 12 * 0.0005 + gass * 12 * 0.0053 + fuel * 12 * 2.23
            return self.energy_emission
        except ValueError:
            return None
        
    def calculate_waste_emission(self, waste_generate, waste_recycle):
        try:
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

    def save_report(self, carbon_footprint):
        total_emission = carbon_footprint.calculate_total_emission
        if total_emission is not None:
            client_data = [
                carbon_footprint.client_id,
                carbon_footprint.enerrgy_emission,
                carbon_footprint.waste_emission,
                carbon_footprint.travel_emission,
                total_emission]
            df = pd.read_csv(self.file_path)
            df = df.append(pd.Series(client_data, index=self.columns), ignore_index = True)
            df.to_csv(self.file_path, index = False)
        else:
            print("Incomplete data, cannot generate report.")

def main():

    st.title("Carbon Footprint Assessment made quick and accurate")
    st.write("Obtain the most accurate data with our carbon footprint monitotring tool, supported and develope by our commited Climate team. Our web application calcuates the carbon footprint based on the most important factors including Energy Usage, Waste and Business Travles of your company.  ")
    
    #creating a new instance for the report generator
    report_generator = ReportGnerator()
    client_id = "001"
    carbon_footprint = CarbonFootprint(client_id)

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

                carbon_footprint.calculate_energy_emission(electricity, gass, fuel)
                st.success(f"Energy carbon emission: {carbon_footprint.energy_emission:.2f} kgCO2/year.")
                
                #comparing to benchmark
                energy_benchmark= 3000 #put real value
                if carbon_footprint.energy_emission > energy_benchmark:
                    st.warning(f"Your energy usage exceeds the benchmark of {energy_benchmark} kgCO2/year.")
                else:
                    st.success(f"Your energy usage is within the benchmark of {energy_benchmark} kgCO2/year.")
            
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

                carbon_footprint.calculate_waste_emission(waste_generate, waste_recycle)
                st.success(f"Waste carbon emission: {carbon_footprint.waste_emission:.2f} kgCO2/year.")

                # Benchmark Comparison
                waste_benchmark = 300  # Example benchmark in kgCO2
                if carbon_footprint.waste_emission > waste_benchmark:
                        st.warning(f"Your waste management exceeds the benchmark of {waste_benchmark} kgCO2/year.")
                else:
                        st.success(f"Your waste management is within the benchmark.")
        

            except ValueError:
                st.error("Please enter valid numbers for all inputs.")
        else:
            st.warning("Please fill in all fields.")

    #travel emission calculation
    st.subheader("Business Travel")
    travel = st.text_input("How many kilometers do your employees travel per year for business purposes?")
    fuel_efficiency= st.text_input("What is the average fuel efficiency of the vehicles used for business travel in liters per 100 kilometers?")

    if st.button("Calculate Travel Emission"):
        
        if travel_km.strip() and fuel_efficiency.strip():
            try:
                travel_km = float(travel)
                fuel_efficiency = float(fuel_efficiency)

                carbon_footprint.calculate_travel_emission(travel_km, fuel_efficiency)
                st.success(f'Your carbon emission from business travels is {carbon_footprint.travel_emission:.2f} kgCO2. View the full review and solutions here. ')
        
                #benchmark comparison
                travel_benchmark = 10000
                if carbon_footprint.travel_emission > travel_benchmark:
                    st.warning(f"Your travel emission exceeds the benchmark of {travel_benchmark} kgCO2/year.")
                else:
                    st.success("Your travel emission is within the range.")

            except ValueError:
                st.error("Please enter valid numbers for all inputs.")
        else:
            st.warning("Please fill in all fields.")

    #Save and display the final report
    if st.button("Save Report"):
        report_generator.save_report(carbon_footprint)

    st.success(f'Total Carbon Footprint: {carbon_footprint.calculate_total_emission()}')

if __name__ == "__main__":
    main()