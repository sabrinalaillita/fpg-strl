import streamlit as st
from streamlit_authenticator import Authenticate
import yaml
from yaml.loader import SafeLoader
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# Load configuration
with open('config.yaml') as file:
    config = yaml.load(file, Loader=SafeLoader)

# Initialize the authenticator
authenticator = Authenticate(
    config['credentials'],
    config['cookie']['name'],
    config['cookie']['key'],
    config['cookie']['expiry_days']
)

# Assume this function checks if the user is authenticated
def is_user_authenticated():
    # This should check an actual condition in your app's session state or other state mechanism
    return st.session_state.get("authentication_status", False)

# Check if user is authenticated at the very top before any page logic
if not is_user_authenticated():
    st.error("You must be logged in to view this page.")
    st.stop()  # Prevents the execution of the rest of the script
    
with st.sidebar:
    
    st.image("cropped-Logo-Kedai.png", width=150)
    st.write("##")
    st.page_link("Home.py", label="Home", icon="🏠")
    st.page_link("pages/EDA.py", label="Exploratory Data Analysis", icon="📈")
    st.page_link("pages/MBA.py", label="Market Basket Analysis", icon="🛒")
    st.write("##")
    authenticator.logout("Logout", "sidebar")
    
    
st.text(f"Welcome, {st.session_state.get("name")}👋")
st.title("Market Basket Analysis")

tab1, tab2, tab3 = st.tabs(["Data", "Frequent Itemset", "Result"])
df = pd.read_csv("Sales.csv")
total_data = len(df)

with tab1:
    st.subheader("Data Penjualan Bulan Oktober 2023 - Februari 2024")
    st.write(f"Total data = {total_data} transaksi")
    st.dataframe(df)
    
    
    