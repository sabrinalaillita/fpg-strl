import streamlit as st
from streamlit_authenticator import Authenticate

import yaml
from yaml.loader import SafeLoader
with open('config.yaml') as file:
    config = yaml.load(file, Loader=SafeLoader)
    
# Colours
# Primary: #2a3d33
# Secondary: #2D2926
# Action: #b78343

# emojis: https://www.webfx.com/tools/emoji-cheat-sheet/

#  TO RUN: streamlit run --client.showSidebarNavigation=False .\1_??_Home.py
def wide_space_default():
    st.set_page_config(layout="wide")
wide_space_default()


authenticator = Authenticate(
    config['credentials'],
    config['cookie']['name'],
    config['cookie']['key'],
    config['cookie']['expiry_days']
)

name, authentication_status, username = authenticator.login('main', fields = {'Form name': 'Halaman Login'})

if authentication_status == False:
    st.error("Username/password is incorrect")
    
if authentication_status:
    st.text(f"Welcome, {name}👋")
    col1, col2 = st.columns(2)
    with col1:
        st.title("Analisa data penjualan dengan Market Basket Analysis")
        st.write("Lorem ipsum dolor sit amet consectetur. Et mattis mauris sociis lectus. Eleifend tellus tellus lorem facilisis consequat. Etiam enim phasellus vitae in eu. Praesent gravida tristique odio est. Sed habitant egestas sed purus. Proin pellentesque placerat id consectetur sed habitant odio viverra id.")
    
    with st.sidebar:
        _,col1,__ = st.columns([1,3,1])
        col1 = st.image("cropped-Logo-Kedai.png", width=150) 
        st.write("##")
        st.page_link("Home.py", label="Home", icon="🏠")
        st.page_link("pages/MBA.py", label="Market Basket Analysis", icon="🛒")
        st.page_link("pages/EDA.py", label="Exploratory Data Analysis", icon="📈")
        st.write("##")
        authenticator.logout("Logout","sidebar")
        
        
        
    
