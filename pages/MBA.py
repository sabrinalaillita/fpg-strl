import streamlit as st
from streamlit_authenticator import Authenticate
import yaml
from yaml.loader import SafeLoader
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from pyvis.network import Network
from mlxtend.preprocessing import TransactionEncoder
from mlxtend.frequent_patterns import fpgrowth, association_rules


custom_style = {'axes.facecolor':'#2a3d33',
                'figure.facecolor':'#2a3d33',
                'axes.labelcolor': 'white',
                'xtick.color': 'white',
                'ytick.color': 'white'}
sns.set_style("darkgrid", rc=custom_style)

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
    st.page_link("pages/MBA.py", label="Market Basket Analysis", icon="🛒")
    st.page_link("pages/EDA.py", label="Exploratory Data Analysis", icon="📈")
    st.write("##")
    authenticator.logout("Logout", "sidebar")
    
    
st.text(f"Welcome, {st.session_state.get("name")}👋")
st.title("Market Basket Analysis")

tab1, tab2, tab3 = st.tabs(["Data", "Frequent Itemset", "Result"])

df = pd.read_csv("Sales.csv")

with tab1:
    uploaded_file = st.file_uploader("Choose a CSV file", type="csv")
        # Check if a file is uploaded
    if uploaded_file is not None:
        # Load the CSV file into a pandas DataFrame
        df = pd.read_csv(uploaded_file)

        # Display the DataFrame as a table in the Streamlit app
        st.subheader("Data yang anda kirim:")
        total_data = len(df)
        st.write(f"Total data = {total_data} transaksi")
        
        st.dataframe(df)
    else:
        st.write("Silahan upload csv file untuk dianalisa.")
    
# ---------------------------------------------- DATA CLEANSING --------------------------------    
# Change 'Tanggal' data type to Datetime
df['Tanggal'] = pd.to_datetime(df['Tanggal'])

# Deleteing rows with 'status' = 'belum lunas'
df_clean = df.copy()
# print(df_clean[df_clean['Status'].str[:1]=='B'].count())
df_clean = df_clean[df_clean['Status'].str[:1]!='B']

# Deleteing rows with 'HeaderReturFaktur' > 0
# print(df_clean[df_clean['HeaderReturFaktur']>0].count())
df_clean = df_clean[df_clean['HeaderReturFaktur']==0]

# Check for missing value
df_clean.isnull().sum()
df_clean.ffill()

# Check for duplicated data
# print("Jumlah duplikasi: ", df_clean.duplicated().sum())
df_clean.drop_duplicates(keep=False)

# Resolving data inconsistencies
df_clean['Outlet'] = df_clean['Outlet'].str.title()
df_clean['NomorFaktur'] = df_clean['NomorFaktur'].str.upper()
df_clean['Status'] = df_clean['Status'].str.title()
df_clean['SKU_Produk'] = df_clean['SKU_Produk'].str.upper()
df_clean['NamaProduk'] = df_clean['NamaProduk'].str.title()

# ---------------------------------- CONVERT DATA FOR MARKET BASKET ANALYSIS ----------------------------

transactions = df_clean.groupby('NomorFaktur')['NamaProduk'].apply(list)

# Converting to a list of transactions
transactions_list = transactions.tolist()


# Step 1: Transform the transaction list into the right format
te = TransactionEncoder()
te_ary = te.fit(transactions_list).transform(transactions_list)
df_transactions = pd.DataFrame(te_ary, columns=te.columns_)

# TransactionEncoder: Converts the list of transactions into a one-hot encoded DataFrame, where each product is a column, and each row corresponds to a transaction.
# fpgrowth: This function applies the FP-Growth algorithm to find frequent itemsets that meet the minimum support threshold.

with tab2:
    col1, col2, col3 = st.columns([1,2,3])
    with col1:
        container = st.container(border=True)
        container.subheader("Minimum Support")
        min_support = container.slider("Nilai antara 0.00 hingga 1.00", min_value=0.00, max_value=1.00, value=0.01, step=0.01)
        container.write(f"Support sebesar: {min_support}")
    with col2:
            # Check if a file is uploaded
        if uploaded_file is not None:
            st.subheader("Frequent Itemsets")
            
            frequent_itemsets = fpgrowth(df_transactions, min_support=min_support, use_colnames=True)
            if not frequent_itemsets.empty:
                frequent_itemsets['itemsets'] = frequent_itemsets['itemsets'].apply(lambda x: ', '.join(list(x)))
                st.dataframe(frequent_itemsets)
            else:
                st.write("Tidak ada itemset yang ditemukan dengan minimum support yang diberikan.")
                
            # st.dataframe(frequent_itemsets)
        else:
            st.write("Silahan upload csv file di TAB DATA untuk dianalisa.")
            
    with col3:    
        if uploaded_file is not None:
            if not frequent_itemsets.empty:
                # Sort the itemsets by support
                top_itemsets = frequent_itemsets.sort_values(by='support', ascending=False).head(10)

                # Create a bar plot
                fig, ax = plt.subplots(figsize=(8, 5))
                sns.barplot(
                    x='support', 
                    y='itemsets', 
                    hue='itemsets', 
                    legend=False, 
                    data=top_itemsets,
                    palette='YlOrBr',
                    ax=ax)
                for index, value in enumerate(top_itemsets['support']):
                    plt.text(value, index, round(value, 3), va='center', ha='left', fontsize=10, color='white')
                ax.set_title('Top Frequent Itemsets by Support', fontsize=14, color='white')
                ax.set_xlabel('Support')
                ax.set_ylabel('Itemsets')
                # ax.tick_params(axis='x', labelsize=12)
                # ax.tick_params(axis='y', labelsize=12)
                st.pyplot(fig)
                
            else:
                st.write("")
        else:
            st.write("Silahan upload csv file di TAB DATA untuk dianalisa.")
            



with tab3:
    col1, col2 = st.columns([1,3])
    with col1:
        container = st.container(border=True)
        container.subheader("Minimum Confidence")
        min_confidence = container.slider("Nilai antara 0.00 hingga 1.00", min_value=0.00, max_value=1.00, value=0.05, step=0.01, key="min_confidence")
        container.write(f"Confidence sebesar: {min_confidence}")
        st.markdown("#####")
        container.subheader("Minimum Lift")
        min_lift = container.slider("Nilai antara 0 hingga 10", min_value=0, max_value=10, value=1, step=1, key="min_lift")
        container.write(f"Lift sebesar: {min_lift}")
    with col2:
        # Check if a file is uploaded
        if uploaded_file is not None:
            if not frequent_itemsets.empty:
                frequent_itemsets['itemsets'] = frequent_itemsets['itemsets'].apply(lambda x: frozenset(x.split(', ')))
                rules = association_rules(frequent_itemsets, metric="confidence", min_threshold=min_confidence)
                rules = rules[rules['lift'] >= min_lift]
                
                if not rules.empty:
                    rules['antecedents'] = rules['antecedents'].apply(lambda x: ', '.join(list(x)))
                    rules['consequents'] = rules['consequents'].apply(lambda x: ', '.join(list(x)))
                    st.subheader("Association Rules")
                    st.dataframe(rules[['antecedents', 'consequents', 'support', 'confidence', 'lift']])
                else:
                    st.write("Tidak ada association rules yang ditemukan dengan minimum confidence dan lift yang diberikan.")
            else:
                st.write("Frequent itemset tidak tersedia untuk pembuatan rules.")
        else:
            st.write("Silahan upload csv file di TAB DATA untuk dianalisa.")
    
    col3, col4 = st.columns(2)
    with col3:
        # Check if a file is uploaded
        if uploaded_file is not None:
            if not frequent_itemsets.empty:
                
                if not rules.empty:
                    heatmap_data = rules.pivot(index='antecedents', columns='consequents', values='lift')

                    # Plot the heatmap
                    fig, ax = plt.subplots(figsize=(12, 10))
                    sns.heatmap(
                        heatmap_data,
                        annot=True,
                        cmap="YlOrBr",
                        linewidths=.5,
                        ax=ax
                    )
                    ax.set_title('Heatmap of Itemset Correlations (Lift)', fontsize=14, color='white')
                    st.pyplot(fig)
                else:
                    st.write("Tidak ada association rules yang ditemukan dengan minimum confidence dan lift yang diberikan.")
            else:
                st.write("")
        else:
            st.write("Silahan upload csv file di TAB DATA untuk dianalisa.")
            
    with col4:
        # Check if a file is uploaded
        if uploaded_file is not None:
            if not frequent_itemsets.empty:
                
                if not rules.empty:
                    # Initialize PyVis Network with simplified settings
                    net = Network(height="750px", width="100%", bgcolor="#222222", font_color="white")

                    # Add nodes and edges to the Network
                    for _, rule in rules.iterrows():
                        antecedents = ''.join(list(rule['antecedents']))
                        consequents = ''.join(list(rule['consequents']))

                        # Add nodes with full labels
                        net.add_node(antecedents, label=antecedents, title=antecedents, color='blue')
                        net.add_node(consequents, label=consequents, title=consequents, color='red')

                        # Add an edge with rule metrics as a tooltip
                        net.add_edge(antecedents, consequents, 
                                    title=f"Lift: {rule['lift']:.2f}, Confidence: {rule['confidence']:.2f}, Support: {rule['support']:.2f}",
                                    value=rule['lift'])

                    # Save and display the Network graph in Streamlit
                    net.save_graph('network.html')
                    st.components.v1.html(open('network.html', 'r').read(), height=750)
                else:
                    st.write("Tidak ada association rules yang ditemukan dengan minimum confidence dan lift yang diberikan.")
            else:
                st.write("")
        else:
            st.write("Silahan upload csv file di TAB DATA untuk dianalisa.")