import pickle
from pathlib import Path

import streamlit as st
from streamlit_authenticator import Authenticate

import yaml
from yaml.loader import SafeLoader
with open('config.yaml') as file:
    config = yaml.load(file, Loader=SafeLoader)

# emojis: https://www.webfx.com/tools/emoji-cheat-sheet/
st.set_page_config(
    page_title="Login",
    page_icon="🔑"
)

# # --- USER AUTHENTICATION ---
# names = ["Admin", "CEO"]
# usernames = ["Admin", "CEO"]

# # --- LOAD HASED PASSWORD ---
# file_path = Path(__file__).parent / "hashed_pw.pkl"
# with file_path.open("rb") as file:
#     hashed_passwords = pickle.load(file)
    
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
    authenticator.logout("Logout", "sidebar")
    st.subheader(f"Welcome, {name}👋")
    st.title("Market Basket Analysis")
    