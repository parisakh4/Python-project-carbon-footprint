import streamlit as st

st.title("Carbon Emission based on Energy usage")
st.write(st.session_state)
if "energy_emission" in st.session_state:
    st.write(f'Based on your input, the Carbon footprint of your company is {st.session_state['energy_emission']}')
else:
    st.write("No energy emission data found. Please go back and calculate it first.")