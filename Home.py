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

def card_desc(title, desc, formula, add):
    with st.expander(title):
        st.write(desc)
        st.latex(formula)
        st.write(add)

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
        st.image("logo_jvld_w.png", width=220)
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
    st.text(f"Selamat Datang, {name} 👋")
    
    col1, col2 = st.columns(2)
    with col1:
        st.title("Analisa data penjualan dengan Market Basket Analysis")
        st.write("Market Basket Analysis adalah teknik analisis data yang digunakan untuk mengidentifikasi pola pembelian pelanggan. Dengan menggunakan algoritma yang tepat, kita dapat mengetahui produk mana saja yang sering dibeli bersamaan, sehingga bisa membantu dalam pengambilan keputusan bisnis seperti pengaturan produk di toko atau kampanye promosi. Analisis ini membantu bisnis untuk lebih memahami perilaku konsumen dan meningkatkan penjualan.")
    
    with col2:
        card_desc("Support",
                    "Support mengukur seberapa sering sebuah kombinasi item (atau produk) muncul dalam keseluruhan data transaksi. Nilai support dihitung dengan rumus:",
                    r'''
                    Support(A \Rightarrow B) = \frac{\text{Jumlah Transaksi yang Mengandung A dan B}}{\text{Total Transaksi}}
                    ''',
                    "Semakin tinggi nilai support, semakin sering kombinasi produk tersebut dibeli bersama.")
        card_desc("Confidence",
                    "Confidence adalah ukuran probabilitas bahwa item B dibeli ketika item A dibeli. Ini dihitung dengan rumus:",
                    r'''
                    Confidence(A \Rightarrow B) = \frac{\text{Jumlah Transaksi yang Mengandung A dan B}}{\text{Jumlah Transaksi yang Mengandung A}}
                    ''',
                    "Confidence menunjukkan seberapa kuat hubungan antara dua produk.")
        card_desc("Lift",
                    "Lift mengukur sejauh mana dua item saling terkait lebih dari yang diharapkan jika keduanya dibeli secara independen. Rumus lift adalah:",
                    r'''
                    Lift(A \Rightarrow B) = \frac{\text{Confidence(A }\Rightarrow {\text B)}}{\text{Support(B)}}
                    ''',
                    "Nilai lift lebih besar dari 1 menunjukkan bahwa item A dan B memiliki hubungan yang kuat, sementara nilai kurang dari 1 menunjukkan bahwa mereka kemungkinan besar tidak dibeli bersamaan.")
        
            
    # Sidebar content
    with st.sidebar:
        _, col1, __ = st.columns([1, 3, 1])
        col1 = st.image("logo_jvld_w.png", width=220) 
        st.write("##")
        st.page_link("Home.py", label="Home", icon="🏠")
        st.page_link("pages/MBA.py", label="Market Basket Analysis", icon="🛒")
        st.page_link("pages/EDA.py", label="Exploratory Data Analysis", icon="📈")
        st.write("##")
        # Logout button
        authenticator.logout("Logout", "sidebar")
