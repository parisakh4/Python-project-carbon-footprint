import streamlit as st
import pandas as pd

if "energy_emission" not in st.session_state:
    st.session_state["energy_emission"] = None

st.title("Carbon Footprint Assessment made quick and accurate")
st.write("Obtain the most accurate data with our carbon footprint monitotring tool, supported and develope by our commited Climate team. Our web application calcuates the carbon footprint based on the most important factors including Energy Usage, Waste and Business Travles of your company.  ")

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

            energy_emission = electricity * 12 * 0.0005 + gass * 12 * 0.0053 + fuel * 12 * 2.23
            st.session_state["energy_emission"] = energy_emission
            st.success(f'Your carbon emission from energy usage is {energy_emission:.2f} kgCO2. You can see the full report and solutions [here](energyusage).')
            
        except ValueError:
            st.error("Please enter valid numbers for all inputs.")
    else:
        st.warning("Please fill in all fields.")

st.subheader("Waste")
waste_generate = st.text_input("How much do you generate per month in Kilograms?")
waste_recycle = st.text_input("What percentage of that waste is recycled or composed?")

if st.button("Calculate Waste Emission"):
    
    if waste_generate.strip() and waste_recycle.strip():
        try:
            waste_generate = float(waste_generate)
            waste_recycle = float(waste_recycle)

            waste_emission = waste_generate * 12 * (0.57 - waste_recycle)
            st.success(f'Your carbon emission from waste is {waste_emission:.2f} kgCO2. View the full report and solutions here.')
    

        except ValueError:
            st.error("Please enter valid numbers for all inputs.")
    else:
        st.warning("Please fill in all fields.")


st.subheader("Business Travel")
travel = st.text_input("How many kilometers do your employees travel per year for business purposes?")
feul_efficiency= st.text_input("What is the average fuel efficiency of the vehicles used for business travel in liters per 100 kilometers?")

if st.button("Calculate Travel Emission"):
    
    if travel.strip() and feul_efficiency.strip():
        try:
            travel = float(travel)
            feul_efficiency = float(feul_efficiency)

            travel_emission = travel * (1/feul_efficiency) * 2.31
            st.success(f'Your carbon emission from business travels is {travel_emission:.2f} kgCO2. View the full review and solutions here. ')
    

        except ValueError:
            st.error("Please enter valid numbers for all inputs.")
    else:
        st.warning("Please fill in all fields.")

st.header("Total Carbon Footprint")
st.write("To see the total amount of your carbon foot print and read the final report click on the button below.")