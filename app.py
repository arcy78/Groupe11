# app.py – Shopdern Dashboard
import streamlit as st
import duckdb
import plotly.express as px
import base64
import pandas as pd
from PIL import Image

# --- CONFIGURATION ---
st.set_page_config(page_title="Shopdern - Dashboard", layout="wide")

# --- STYLISATION DU TITRE PRINCIPAL ---
st.markdown("""
    <h1 style='text-align: center; color: #98FB98; font-size: 70px;'>
        🛍️ Shopdern - Dashboard d’analyse
    </h1>
""", unsafe_allow_html=True)

# --- Chargement des images ---
logo = Image.open("images/logo.png")
st.image(logo, width=400)

def get_base64_img(path):
    with open(path, "rb") as f:
        return base64.b64encode(f.read()).decode()

img_base64 = get_base64_img("images/image1.png")

# --- Fond d'écran ---
st.markdown(
    f"""
    <style>
    .stApp {{
        background-image: url("data:image/png;base64,{img_base64}");
        background-size: cover;
        background-position: center;
        background-repeat: no-repeat;
        background-attachment: fixed;
    }}
    </style>
    """,
    unsafe_allow_html=True
)

# --- FONCTION DE CENTRAGE DES GRAPHIQUES ---
def center_chart(fig):
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.plotly_chart(fig, use_container_width=True)

# --- COULEURS POUR LES GENRES ---
gender_colors = {'Male': '#C9E42F', 'Female': '#98FB98'}

# --- ÉTAPE 1 : IMPORTATION DES DONNÉES ---
st.markdown(
    "<h1 style='text-align: center; color: #1A237E; font-size: 52px;'>Étape 1️⃣ – Importation des données.</h1>",
    unsafe_allow_html=True
)

@st.cache_resource
def init_db():
    con = duckdb.connect(database=':memory:')
    con.execute("""
        CREATE TABLE shopping AS
        SELECT * FROM read_csv_auto('data/shopping_behavior_updated.csv', header=True)
    """)
    return con

con = init_db()
df = con.execute("SELECT * FROM shopping LIMIT 10").df()

st.markdown(
    "<h2 style='text-align: center; color: #3E2723; font-size: 45px;'>📄 Données : Comportement d’achat.</h2>",
    unsafe_allow_html=True
)
st.dataframe(df, use_container_width=True)

# --- ÉTAPE 2 : NETTOYAGE DES DONNÉES ---
st.markdown(
    "<h1 style='text-align: center; color: #1A237E; font-size: 52px;'>Étape 2️⃣ – Nettoyage des colonnes et formatage</h1>",
    unsafe_allow_html=True
)

df = con.execute("SELECT * FROM shopping").df()

df.rename(columns={
    "Customer ID": "Customer_ID",
    "Item Purchased": "Item_Purchased",
    "Purchase Amount (USD)": "Purchase_Amount_USD",
    "Review Rating": "Review_Rating",
    "Subscription Status": "Subscription_Status",
    "Payment Method": "Payment_Method",
    "Shipping Type": "Shipping_Type",
    "Discount Applied": "Discount_Applied",
    "Promo Code Used": "Promo_Code_Used",
    "Previous Purchases": "Previous_Purchases",
    "Preferred Payment Method": "Preferred_Payment_Method",
    "Frequency of Purchases": "Frequency_of_Purchases"
}, inplace=True)

df.drop_duplicates(inplace=True)

st.markdown(
    "<h2 style='text-align: center; color: #3E2723; font-size: 45px;'>📁 Types de données</h2>",
    unsafe_allow_html=True
)
st.dataframe(df.dtypes.astype(str).reset_index().rename(columns={"index": "Colonne", 0: "Type"}))

# --- ÉTAPE 3 : ANALYSE PAR KPI ---
st.markdown(
    "<h1 style='text-align: center; color: #1A237E; font-size: 52px;'>Étape 3️⃣ 📈 – Analyse par Indicateurs Clés (KPI) 📈</h1>",
    unsafe_allow_html=True
)

# KPI 1 : Transactions par catégorie et genre
st.markdown("<h2 style='text-align: center; color: #3E2723; font-size: 45px;'> 🎯 Transactions par catégorie & genre 🎯</h2>", unsafe_allow_html=True)
fig1 = px.histogram(df, x='Category', color='Gender', barmode='group', color_discrete_map=gender_colors)
center_chart(fig1)

# KPI 2 : Montant moyen par méthode de paiement
st.markdown("<h2 style='text-align: center; color: #3E2723; font-size: 45px;'>💳 Montant moyen par méthode de paiement 💳</h2>", unsafe_allow_html=True)
fig2 = px.box(df, x='Payment_Method', y='Purchase_Amount_USD', color='Gender', color_discrete_map=gender_colors)
center_chart(fig2)

# KPI 3 : Statut d’abonnement selon le genre
st.markdown("<h2 style='text-align: center; color: #3E2723; font-size: 45px;'>✉️ Abonnements par genre ✉️</h2>", unsafe_allow_html=True)
fig3 = px.histogram(df, x='Subscription_Status', color='Gender', barmode='group', color_discrete_map=gender_colors)
center_chart(fig3)

# KPI 4 : Répartition des évaluations (Review)
st.markdown("<h2 style='text-align: center; color: #3E2723; font-size: 45px;'> ⭐️ Répartition des avis clients ⭐️</h2>", unsafe_allow_html=True)
fig4 = px.histogram(df, x='Review_Rating', nbins=5, color='Gender', barmode='group', color_discrete_map=gender_colors)
center_chart(fig4)

# KPI 5 : Code promo utilisé (par genre)
st.markdown("<h2 style='text-align: center; color: #3E2723; font-size: 45px;'>🏷️ Utilisation de codes promo 🏷️</h2>", unsafe_allow_html=True)
fig5 = px.histogram(df, x='Promo_Code_Used', color='Gender', barmode='group', color_discrete_map=gender_colors)
center_chart(fig5)

# KPI 6 : Répartition des tailles
st.markdown("<h2 style='text-align: center; color: #3E2723; font-size: 45px;'>👕 👗Répartition des tailles 👖</h2>", unsafe_allow_html=True)
fig6 = px.histogram(df, x='Size', color='Gender', barmode='group', color_discrete_map=gender_colors)
center_chart(fig6)

# KPI 7 : Fréquence des achats
st.markdown("<h2 style='text-align: center; color: #3E2723; font-size: 45px;'>📊 🛒Fréquence des achats par genre 📈</h2>", unsafe_allow_html=True)
fig7 = px.histogram(df, x='Frequency_of_Purchases', color='Gender', barmode='group', color_discrete_map=gender_colors)
center_chart(fig7)

# KPI 8 : Type de livraison préféré
st.markdown("<h2 style='text-align: center; color: #3E2723; font-size: 45px;'>🚚 Types de livraison préférés 🚚</h2>", unsafe_allow_html=True)
fig8 = px.histogram(df, x='Shipping_Type', color='Gender', barmode='group', color_discrete_map=gender_colors)
center_chart(fig8)

