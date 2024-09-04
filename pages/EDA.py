import streamlit as st
from streamlit_authenticator import Authenticate
import yaml
from yaml.loader import SafeLoader
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from pyvis.network import Network
sns.set(style='dark')

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

def is_user_authenticated():
    return st.session_state.get("authentication_status", False)

if not is_user_authenticated():
    st.error("You must be logged in to view this page.")
    st.stop()  # Prevents the execution of the rest of the script
    
# Sidebar for logout and navigation
with st.sidebar:
    st.image("cropped-Logo-Kedai.png", width=150)
    st.write("##")
    st.page_link("Home.py", label="Home", icon="🏠")
    st.page_link("pages/MBA.py", label="Market Basket Analysis", icon="🛒")
    st.page_link("pages/EDA.py", label="Exploratory Data Analysis", icon="📈")
    st.write("##")
    authenticator.logout("Logout", "sidebar")
    
def create_sum_order_items_df(df):
    sum_order_items_df = df.groupby("NamaProduk").Qty.sum().sort_values(ascending=False).reset_index()
    return sum_order_items_df

def create_monthly_orders_df(df):
    # mengubah frekuensi data -- melihat jumlah order dan total revenue yang diperoleh setiap bulannya
    monthly_orders_df = df.resample(rule='ME', on='Tanggal').agg({ #rule = M(Monthly), on = pada kolom
        "NomorFaktur": "nunique",
        "HeaderTotalFaktur": "sum"
    })
    monthly_orders_df.index = monthly_orders_df.index.strftime('%Y-%m')
    monthly_orders_df = monthly_orders_df.reset_index()
    monthly_orders_df.rename(columns={
        "NomorFaktur": "order_count",
        "HeaderTotalFaktur": "revenue"
    }, inplace=True)
    return monthly_orders_df

def create_sum_order_outlets_df(df):
    sum_order_outlets_df = df.groupby("Outlet").Qty.sum().sort_values(ascending=False).reset_index()
    return sum_order_outlets_df


# Placeholder for file uploader
if 'uploaded_file' not in st.session_state:
    st.header("Exploratory Data Analysis")
    st.text(f"Welcome, {st.session_state.get("name")}👋")
    uploaded_file = st.file_uploader("Choose a CSV file", type="csv")
    if uploaded_file is not None:
        # Store the file in session state so it's available after the page reloads
        st.session_state['uploaded_file'] = uploaded_file
        st.rerun()

# Check if a file has been uploaded (stored in session state)
if 'uploaded_file' in st.session_state:
    uploaded_file = st.session_state['uploaded_file']

    # Load the CSV file into a pandas DataFrame
    df = pd.read_csv(uploaded_file)

    # Clean and preprocess the data
    df['Tanggal'] = pd.to_datetime(df['Tanggal'])
    df_clean = df[df['Status'].str[:1] != 'B']  # Exclude rows with 'belum lunas' status
    df_clean = df_clean[df_clean['HeaderReturFaktur'] == 0]  # Exclude returns
    df_clean.drop_duplicates(keep=False, inplace=True)

    df_clean['Outlet'] = df_clean['Outlet'].str.title()
    df_clean['NomorFaktur'] = df_clean['NomorFaktur'].str.upper()
    df_clean['Status'] = df_clean['Status'].str.title()
    df_clean['SKU_Produk'] = df_clean['SKU_Produk'].str.upper()
    df_clean['NamaProduk'] = df_clean['NamaProduk'].str.title()

    df_clean.sort_values(by="Tanggal", inplace=True)
    df_clean.reset_index(inplace=True, drop=True)

    # Get min and max date for the date range
    min_date = df_clean["Tanggal"].min()
    max_date = df_clean["Tanggal"].max()

    # Sidebar: allow the user to choose a date range
    with st.sidebar:
        st.write("##")
        start_date, end_date = st.date_input(
            label='Rentang Waktu', min_value=min_date,
            max_value=max_date, value=[min_date, max_date]
        )

    # Filter the data based on the date range
    main_df = df_clean[(df_clean["Tanggal"] >= pd.to_datetime(start_date)) &
                       (df_clean["Tanggal"] <= pd.to_datetime(end_date))]

    # Display filtered data and EDA results
    st.subheader("Filtered Data")
    st.write(f"Data from {start_date} to {end_date}")
    st.dataframe(main_df.head())

    # Summarize order items
    st.subheader("Order Items Summary")
    sum_order_items_df = df_clean.groupby("NamaProduk").Qty.sum().sort_values(ascending=False).reset_index()
    st.dataframe(sum_order_items_df)

    # Summarize order outlets
    st.subheader("Order Outlets Summary")
    sum_order_outlets_df = df_clean.groupby("Outlet").Qty.sum().sort_values(ascending=False).reset_index()
    st.dataframe(sum_order_outlets_df)

    # Show monthly orders
    st.subheader("Monthly Orders and Revenue")
    monthly_orders_df = df_clean.resample(rule='ME', on='Tanggal').agg({
        "NomorFaktur": "nunique",
        "HeaderTotalFaktur": "sum"
    }).reset_index().rename(columns={"NomorFaktur": "order_count", "HeaderTotalFaktur": "revenue"})
    monthly_orders_df.index = monthly_orders_df["Tanggal"].dt.strftime('%Y-%m')
    st.dataframe(monthly_orders_df)

    # Plot revenue over time
    st.subheader("Revenue Over Time")
    plt.figure(figsize=(10, 5))
    sns.lineplot(x=monthly_orders_df.index, y=monthly_orders_df['revenue'], marker="o")
    plt.title('Monthly Revenue')
    plt.xlabel('Month')
    plt.ylabel('Revenue')
    plt.xticks(rotation=45)
    st.pyplot(plt)

    

