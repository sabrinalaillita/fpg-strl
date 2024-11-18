import streamlit as st
from streamlit_authenticator import Authenticate
import yaml
from yaml.loader import SafeLoader
from time import sleep
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import altair as alt

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
    st.switch_page("Home.py")
    
    
# Sidebar for logout and navigation
with st.sidebar:
    st.image("logo_jvld_w.png", width=220)
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
    st.text(f"Selamat Datang, {st.session_state.get("name")}👋")
    st.header("Exploratory Data Analysis")
    st.markdown("")
    uploaded_file = st.file_uploader("Pilih file CSV", type="csv")
    if uploaded_file is not None:
        # Store the file in session state so it's available after the page reloads
        st.session_state['uploaded_file'] = uploaded_file
        st.rerun()

# Check if a file has been uploaded (stored in session state)
if 'uploaded_file' in st.session_state:
    uploaded_file = st.session_state['uploaded_file']

    # Load the CSV file into a pandas DataFrame
    df = pd.read_csv(uploaded_file)
    uploaded_file.seek(0)

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
    start_date = min_date.strftime("%B %d, %Y")
    end_date = max_date.strftime("%B %d, %Y")
    filtered_dates = """
                    <p style="text-align: center;">📅 {} - {}</p>  
                    """.format(start_date,end_date)
    
    # # Filter the data based on the date range
    # main_df = df_clean[(df_clean["Tanggal"] >= pd.to_datetime(min_date)) &
    #                    (df_clean["Tanggal"] <= pd.to_datetime(max_date))]

    # Display EDA results
    head,_,__, date = st.columns([2,2,1,2])
    with head:
        st.header("Overview Dashboard")
        st.markdown("#####")
    with date:
        container = st.container(border=True)
        container.markdown(filtered_dates, unsafe_allow_html=True)

    
    # Show monthly orders
    # st.subheader("Monthly Orders and Revenue")
    monthly_orders_df = df_clean.resample(rule='ME', on='Tanggal').agg({
        "NomorFaktur": "nunique",
        "HeaderTotalFaktur": "sum"
    }).reset_index().rename(columns={"NomorFaktur": "order_count", "HeaderTotalFaktur": "revenue"})
    monthly_orders_df["Tanggal"] = pd.to_datetime(monthly_orders_df["Tanggal"])

    metric1, metric2 = st.columns(2)
    with metric1:
        # Get the most recent two months to calculate the sales difference
        if len(monthly_orders_df) >= 2:
            # Sort by date to ensure proper comparison
            monthly_orders_df = monthly_orders_df.sort_values(by="Tanggal", ascending=False)

            current_month_sales = monthly_orders_df.iloc[0]['order_count']  # Most recent month's order_count
            previous_month_sales = monthly_orders_df.iloc[1]['order_count']  # Previous month's order_count

            # Calculate the absolute delta (difference) and percentage change
            delta = current_month_sales - previous_month_sales
            delta_percentage = (delta / previous_month_sales) * 100

            # Use st.metric to display the current month's sales and the change
            st.metric(label="Penjualan", value=f"{current_month_sales:,}", delta=f"{delta:,} ({delta_percentage:.2f}%)")
        else:
            st.write("Tidak cukup data untuk menghitung perubahan penjualan bulanan.")
    
    with metric2:
        # Get the most recent two months to calculate the sales difference
        if len(monthly_orders_df) >= 2:
            # Sort by date to ensure proper comparison
            monthly_orders_df = monthly_orders_df.sort_values(by="Tanggal", ascending=False)

            current_month_revenue = monthly_orders_df.iloc[0]['revenue']  # Most recent month's revenue
            previous_month_revenue = monthly_orders_df.iloc[1]['revenue']  # Previous month's revenue

            # Calculate the absolute delta (difference) and percentage change
            delta = current_month_revenue - previous_month_revenue
            delta_percentage = (delta / previous_month_revenue) * 100

            # Use st.metric to display the current month's sales and the change
            st.metric(label="Pendapatan", value=f"{current_month_revenue:,.2f} IDR", delta=f"{delta:,.2f} IDR ({delta_percentage:.2f}%)")
        else:
            st.write("Tidak cukup data untuk menghitung perubahan pendapatan bulanan.")
    
    # # Display the dataframe
    # st.dataframe(monthly_orders_df)
    numOrder, numRev = st.columns(2)
    # Create line chart using Altair with title and y-axis limits
    with numOrder:
        st.subheader("Jumlah Penjualan per Bulan")
        chart = alt.Chart(monthly_orders_df).mark_line(point=True).encode(
            color=alt.value("#b78343"),
            x=alt.X('yearmonth(Tanggal):T', title='Bulan'),
            y=alt.Y('order_count:Q', title='Penjualan', scale=alt.Scale(domain=[5000, 9000]))
        ).properties(
            width=550,
            height=400
        )

        # Display the Altair chart in Streamlit
        st.altair_chart(chart)
        
    with numRev:
        st.subheader("Total Pendapatan per Bulan")
        chart2 = alt.Chart(monthly_orders_df).mark_line(point=True).encode(
            color=alt.value("#b78343"),
            x=alt.X('yearmonth(Tanggal):T', title='Bulan'),
            y=alt.Y('revenue:Q', title='Pendapatan', scale=alt.Scale(domain=[2000000000, 5000000000]))
        ).properties(
            width=550,
            height=400
        )

        # Display the Altair chart in Streamlit
        st.altair_chart(chart2)
    
    # Summarize order items
    sum_order_items_df = df_clean.groupby("NamaProduk").Qty.sum().sort_values(ascending=False).reset_index()

    bestProd, worstProd = st.columns(2)
    
    with bestProd:
        # Best Performing Products (Top 5)
        st.subheader("Produk dengan Penjualan Terbaik")

        # Assuming `sum_order_items_df` has already been created with the top products and their quantities
        best_products = sum_order_items_df.head(10)
        # st.dataframe(best_products)

        # Create the Altair bar chart
        best_products_chart = alt.Chart(best_products).mark_bar().encode(
            x=alt.X('Qty:Q', title='Jumlah Terjual'),
            y=alt.Y('NamaProduk:N', sort='-x', title=None, axis=alt.Axis(labelLimit=500)),  # Sorting by Qty, removing y-axis title
            color=alt.condition(
                alt.datum.NamaProduk == best_products.iloc[0]['NamaProduk'],  # Highlight top product
                alt.value('#b78343'),  # Color for the best product
                alt.value('#D3D3D3')  # Color for the other products
            )
        ).properties(
            width=600,
            height=600
        )

        # Display the chart in Streamlit
        st.altair_chart(best_products_chart)

    with worstProd:
        # Worst Performing Products (Bottom 5)
        st.subheader("Produk dengan Penjualan Terburuk")

        # Assuming `sum_order_items_df` has already been created with the worst products and their quantities
        worst_products = sum_order_items_df.tail(10).sort_values(by="Qty", ascending=True)
        # st.dataframe(worst_products)

        # Create the Altair bar chart
        worst_products_chart = alt.Chart(worst_products).mark_bar().encode(
            x=alt.X('Qty:Q', title='Jumlah Terjual'),
            y=alt.Y('NamaProduk:N', sort='-x', title=None, axis=alt.Axis(labelLimit=500)),  # Sorting by Qty, removing y-axis title
            color=alt.condition(
                alt.datum.NamaProduk == worst_products.iloc[0]['NamaProduk'],  # Highlight worst product
                alt.value('#b78343'),  # Color for the worst product
                alt.value('#D3D3D3')  # Color for the other products
            )
        ).properties(
            width=600,
            height=600
        )

        # Display the chart in Streamlit
        st.altair_chart(worst_products_chart)
        

    # Summarize order outlets
    st.subheader("Total Penjualan per Outlet")
    sum_order_outlets_df = df_clean.groupby("Outlet").Qty.sum().sort_values(ascending=False).reset_index()
    # st.dataframe(sum_order_outlets_df)

    # Define the max and min values
    max_qty = sum_order_outlets_df['Qty'].max()
    min_qty = sum_order_outlets_df['Qty'].min()

    # Create a new column for color encoding
    def color_condition(qty, max_qty, min_qty):
        if qty == max_qty:
            return '#b78343'  # Gold color for highest value
        elif qty == min_qty:
            return '#982B1C'  # Red color for lowest value
        else:
            return 'lightgrey'  # Light grey for all others

    # Apply the color condition to each row
    sum_order_outlets_df['color'] = sum_order_outlets_df['Qty'].apply(lambda qty: color_condition(qty, max_qty, min_qty))

    # Create the Altair bar chart using the color column
    bar_chart = alt.Chart(sum_order_outlets_df).mark_bar().encode(
        x=alt.X('Qty:Q', title='Total Penjualan'),
        y=alt.Y('Outlet:N', sort='-x', title='Outlet',
            axis=alt.Axis(labelLimit=500)),  # Increase label limit to show full names
            color=alt.Color('color:N', scale=None)  # Use the color column directly
    ).properties(
        width=1100,
        height=500
    )

    # Display the chart in Streamlit
    st.altair_chart(bar_chart)

    _,button,__ = st.columns([4,1,4])
    
    with button:        
        if st.button("Ubah Dataset"):
            del st.session_state['uploaded_file']
            st.info("Mengalihkan halaman")
            sleep(0.5)
            st.rerun()

    

