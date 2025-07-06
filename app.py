# app.py – Étape 1 : Importation via DuckDB avec 1 fichier
import streamlit as st
import duckdb
import plotly.express as px
import base64
import pandas as pd
from PIL import Image

# --- STYLISATION DE LA PAGE ---

st.set_page_config(page_title="Shopdern - Dashboard", layout="centered")

# Chargement des images
# --- Chargement du logo ---
logo = Image.open("images/logo.png")
st.image(logo, width=400)  # Affichage du logo

# --- Fonction d'encodage base64 ---
def get_base64_img(path):
    with open(path, "rb") as f:
        return base64.b64encode(f.read()).decode()

# --- Encodage des images ---
# --- Encodage du logo pour le fond ---
img_base64 = get_base64_img("images/image1.png")

# --- CSS : logo utilisé comme image de fond ---
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

# --- TITRE DE LA PAGE ---
st.markdown(
    "<h1 style='color: #98FB98; font-size: 52px;'>Étape 1️⃣ – Importation des données.</h1>",
    unsafe_allow_html=True
)
# Connexion à DuckDB (en mémoire)
@st.cache_resource
def init_db():
    con = duckdb.connect(database=':memory:')
    con.execute("""
        CREATE TABLE shopping AS
        SELECT * FROM read_csv_auto('data/shopping_behavior_updated.csv', header=True)
    """)
    return con

con = init_db()

# Aperçu des données
st.markdown(
    "<h1 style='color: #C9E42F; font-size: 52px;'>📄 Données : Comportement d’achat.</h1>",
    unsafe_allow_html=True
)   
df = con.execute("SELECT * FROM shopping LIMIT 10").df()
st.dataframe(df, use_container_width=True)

# app.py – Étape 2 : Nettoyage


gender_colors = {'Male': '#1f77b4', 'Female': '#ff7f0e'}
st.set_page_config(page_title="Nettoyage des données", layout="wide")
st.title("Étape 2️⃣ – Nettoyage des colonnes et formatage")

# Connexion DuckDB
@st.cache_resource
def init_db():
    con = duckdb.connect(database=':memory:')
    con.execute("""
        CREATE TABLE shopping AS
        SELECT * FROM read_csv_auto('data/shopping_behavior_updated.csv', header=True)
    """)
    return con

con = init_db()

# Charger les données dans pandas pour traitement
df = con.execute("SELECT * FROM shopping").df()

# Étape 1 : Renommage des colonnes (uniformisation)
renaming = {
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
}

df.rename(columns=renaming, inplace=True)

# Étape 2 : Suppression des doublons
before = df.shape[0]
df.drop_duplicates(inplace=True)
after = df.shape[0]
nb_doublons = before - after

st.subheader("📁 Types de données")
st.dataframe(df.dtypes.astype(str).reset_index().rename(columns={"index": "Colonne", 0: "Type"}))

# Étape 3

# Étape 3 : Analyse exploratoire
st.header("Étape 3️⃣ – Analyse exploratoire")

tab1, tab2, tab3 = st.tabs(["Genre", "Catégorie", "Tailles & Couleurs"])

with tab1:
    st.subheader("📊 Répartition par Genre")

    # Histogramme du genre
    genre_count = df['Gender'].value_counts().reset_index()
    genre_count.columns = ['Gender', 'Count']
    st.bar_chart(genre_count.set_index("Gender"))

    # Prix moyen par genre
    mean_price = df.groupby('Gender')['Purchase_Amount_USD'].mean().reset_index()
    st.subheader("💰 Montant moyen par Genre")
    st.dataframe(mean_price)

with tab2:
    st.subheader("📦 Articles achetés par Catégorie")

    cat_count = df['Category'].value_counts().reset_index()
    cat_count.columns = ['Category', 'Count']
    st.bar_chart(cat_count.set_index("Category"))

    st.subheader("🎯 Catégories préférées par Genre")
    cross_tab = pd.crosstab(df['Category'], df['Gender'])
    st.dataframe(cross_tab)

with tab3:
    st.subheader("🧵 Tailles d’articles")
    size_dist = df['Size'].value_counts().reset_index()
    size_dist.columns = ['Size', 'Count']
    st.bar_chart(size_dist.set_index("Size"))

    st.subheader("🎨 Couleurs les plus vendues")
    color_dist = df['Color'].value_counts().head(10).reset_index()
    color_dist.columns = ['Color', 'Count']
    st.bar_chart(color_dist.set_index("Color"))
st.subheader("2️⃣ Prix moyen des articles par genre")
mean_price_gender = df.groupby('Gender')['Purchase_Amount_USD'].mean().reset_index()
st.bar_chart(mean_price_gender.set_index("Gender"))

st.header("Étape 4️⃣ – Analyse par Indicateurs Clés (KPI)")
st.markdown("Visualisation détaillée des comportements d'achat selon différents axes (genre, âge, saison, etc.)")

# 1️⃣ Répartition des catégories par genre
st.subheader("1️⃣ Répartition des catégories par genre")
fig1 = px.histogram(
    df, x='Category', color='Gender', barmode='group',
    color_discrete_map=gender_colors,
    title="Distribution des catégories selon le genre"
)
st.plotly_chart(fig1, use_container_width=True)

# 2️⃣ Prix moyen des articles par genre
st.subheader("2️⃣ Prix moyen des articles par genre")
mean_price_gender = df.groupby('Gender')['Purchase_Amount_USD'].mean().reset_index()
fig2 = px.bar(
    mean_price_gender, x='Gender', y='Purchase_Amount_USD',
    color='Gender', color_discrete_map=gender_colors,
    title="Prix moyen d'achat par genre"
)
st.plotly_chart(fig2, use_container_width=True)

# 3️⃣ Distribution des âges
st.subheader("3️⃣ Distribution des âges des clients")
fig3 = px.histogram(df, x='Age', nbins=20, color_discrete_sequence=['#636EFA'], title='Distribution des âges')
st.plotly_chart(fig3, use_container_width=True)

# 4️⃣ Articles achetés par genre
st.subheader("4️⃣ Articles achetés selon le genre")
fig4 = px.histogram(
    df, x='Item_Purchased', color='Gender', barmode='group',
    color_discrete_map=gender_colors,
    title="Produits achetés selon le genre"
)
fig4.update_layout(xaxis_tickangle=-45)
st.plotly_chart(fig4, use_container_width=True)

# 5️⃣ Ventes par saison
st.subheader("5️⃣ Ventes par saison")
fig5 = px.histogram(
    df, x='Season', color_discrete_sequence=['#FFA15A'],
    title="Nombre d'achats par saison"
)
st.plotly_chart(fig5, use_container_width=True)

# 6️⃣ Ventes par genre et saison
st.subheader("6️⃣ Répartition des ventes par saison et genre")
fig6 = px.histogram(
    df, x='Season', color='Gender', barmode='group',
    color_discrete_map=gender_colors,
    title="Genre vs Saison des achats"
)
st.plotly_chart(fig6, use_container_width=True)

# 7️⃣ Articles vendus par taille
st.subheader("7️⃣ Répartition des tailles achetées")
fig7 = px.histogram(
    df, x='Size', color='Gender', barmode='group',
    color_discrete_map=gender_colors,
    title="Tailles achetées par genre"
)
st.plotly_chart(fig7, use_container_width=True)

# 8️⃣ Articles vendus par couleur (top 10)
st.subheader("8️⃣ Couleurs d’articles les plus achetées")
top_colors = df['Color'].value_counts().nlargest(10).index
fig8 = px.histogram(
    df[df['Color'].isin(top_colors)], x='Color', color='Gender', barmode='group',
    color_discrete_map=gender_colors,
    title="Couleurs d’articles achetés (Top 10)"
)
fig8.update_layout(xaxis_tickangle=-45)
st.plotly_chart(fig8, use_container_width=True)

# 9️⃣ Montant moyen d’achat selon remise
st.subheader("9️⃣ Montant moyen d’achat selon remise")
discount_stats = df.groupby("Discount_Applied")["Purchase_Amount_USD"].mean().reset_index()
fig9 = px.bar(
    discount_stats, x="Discount_Applied", y="Purchase_Amount_USD",
    color="Discount_Applied", color_discrete_sequence=['#1f77b4', '#ff7f0e'],
    title="Montant moyen d’achat selon remise"
)
st.plotly_chart(fig9, use_container_width=True)

# 🔟 Remise par genre
st.subheader("🔟 Remise appliquée par genre")
fig10 = px.histogram(
    df, x="Discount_Applied", color="Gender", barmode='group',
    color_discrete_map=gender_colors,
    title="Remise appliquée par genre"
)
st.plotly_chart(fig10, use_container_width=True)
