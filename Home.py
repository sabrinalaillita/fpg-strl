import streamlit as st
from streamlit_authenticator import Authenticate
import yaml
from yaml.loader import SafeLoader

# Load the configuration for authentication
with open('config.yaml') as file:
    config = yaml.load(file, Loader=SafeLoader)

# Set wide layout for the page
def wide_space_default():
    st.set_page_config(layout="wide")
wide_space_default()

# Initialize authenticator
authenticator = Authenticate(
    config['credentials'],
    config['cookie']['name'],
    config['cookie']['key'],
    config['cookie']['expiry_days']
)

left, mid, right = st.columns([1.5,0.5,2])
with left:
    st.markdown("#")
    st.markdown("#")
    name, authentication_status, username = authenticator.login('main', fields={'Form name': 'Login'})
# Show the logo and title if the user is not logged in
if authentication_status != True:
    with right:
        st.markdown("#")
        st.markdown("#")
        st.image("cropped-Logo-Kedai.png", width=150)
        st.header("Aplikasi Market Basket Analysis Algoritma FP-Growth")
        
        # st.markdown("#####")
        # spacer_left, form, spacer_right = st.columns([1, 0.8, 1])
        # with form:
        #     # Custom CSS to align the title
        #     st.markdown(
        #         """
        #         <style>
        #         .title {
        #             text-align: center;
        #         }
        #         </style>
        #         """,
        #         unsafe_allow_html=True
        #     )
        #     kiri, gambar, kanan = st.columns([1,1,1])
        #     with gambar:
        #         st.image("cropped-Logo-Kedai.png", width=150)
        #     st.markdown('<h2 class="title">Aplikasi Market Basket Analysis Algoritma FP-Growth</h2>', unsafe_allow_html=True)

# Show an error message if login fails
elif authentication_status == False:
    st.error("Username/password is incorrect")

# Show the main content only if the user is logged in
if authentication_status:
    st.text(f"Welcome, {name} 👋")
    
    col1, col2 = st.columns(2)
    with col1:
        st.title("Analisa data penjualan dengan Market Basket Analysis")
        st.write("Lorem ipsum dolor sit amet consectetur. Et mattis mauris sociis lectus. Eleifend tellus tellus lorem facilisis consequat. Etiam enim phasellus vitae in eu. Praesent gravida tristique odio est. Sed habitant egestas sed purus. Proin pellentesque placerat id consectetur sed habitant odio viverra id.")
    
    # Sidebar content
    with st.sidebar:
        _, col1, __ = st.columns([1, 3, 1])
        col1 = st.image("cropped-Logo-Kedai.png", width=150) 
        st.write("##")
        st.page_link("Home.py", label="Home", icon="🏠")
        st.page_link("pages/MBA.py", label="Market Basket Analysis", icon="🛒")
        st.page_link("pages/EDA.py", label="Exploratory Data Analysis", icon="📈")
        st.write("##")
        # Logout button
        authenticator.logout("Logout", "sidebar")
