import streamlit as st
import duckdb
import pandas as pd
import matplotlib.pyplot as plt
from PIL import Image
import base64
import plotly.express as px

# --- Configuration de la page ---
st.set_page_config(page_title="Shopdern Dashboard", layout="centered")

# --- Chargement du logo (facultatif) ---
logo = Image.open("images/logo.png")
st.image(logo, width=300)

# --- Chargement de l'image de fond ---
def get_base64_img(path):
    with open(path, "rb") as f:
        return base64.b64encode(f.read()).decode()

img_base64 = get_base64_img("images/image1.png")

# --- STYLE global + fond d’écran ---
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
    h1, h2, h3, .stMarkdown {{
        color: #b30059;
    }}
    </style>
    """,
    unsafe_allow_html=True
)

# --- Titre principal ---
st.markdown("""
    <h1 style='text-align: center; font-size: 3em;'>
        🛍️ <span style='color:#e15759;'>Shopdern</span> - Dashboard d’analyse
    </h1>
""", unsafe_allow_html=True)

# --- Chargement des données avec DuckDB ---
@st.cache_data
def load_data():
    con = duckdb.connect(database=':memory:')
    con.execute("""
        SELECT * FROM read_csv_auto('data/shopping_behavior_updated.csv', HEADER=TRUE)
    """)
    df = con.fetch_df()
    return df

df = load_data()

# --- Nettoyage des noms de colonnes
df.rename(columns={
    "Customer ID": "Customer_ID",
    "Purchase Amount (USD)": "Purchase_Amount_USD",
    "Subscription Status": "Subscription_Status"
}, inplace=True)

# --- Filtres dynamiques ---
st.markdown("## 🎛️ Filtres interactifs")

regions = df["Location"].dropna().unique().tolist()
categories = df["Category"].dropna().unique().tolist()

selected_regions = st.multiselect("Filtrer par région :", sorted(regions), default=regions)
selected_categories = st.multiselect("Filtrer par catégorie :", sorted(categories), default=categories)

df = df[df["Location"].isin(selected_regions) & df["Category"].isin(selected_categories)]

if df.empty:
    st.warning("Aucune donnée ne correspond aux filtres sélectionnés.")
    st.stop()

# --- KPI ---
st.markdown("## 🔍 Indicateurs clés de performance (KPI)")

# 1. Ventes par catégorie
st.subheader("1. 💰 Ventes totales par catégorie")
sales_by_category = df.groupby("Category")["Purchase_Amount_USD"].sum().sort_values(ascending=True)
fig, ax = plt.subplots()
colors = plt.get_cmap('Set3').colors
ax.barh(sales_by_category.index, sales_by_category.values, color=colors[:len(sales_by_category)])
for i, v in enumerate(sales_by_category.values):
    ax.text(v + 1, i, f"${v:,.0f}", va='center')
ax.set_xlabel("Montant total des ventes (USD)")
ax.set_ylabel("Catégorie")
st.pyplot(fig)

# 2. Panier moyen par saison
avg_basket = df.groupby("Season")["Purchase_Amount_USD"].mean().round(2).reset_index()
fig = px.bar(avg_basket, x="Season", y="Purchase_Amount_USD",
             text="Purchase_Amount_USD",
             color="Season",
             color_discrete_sequence=px.colors.qualitative.Pastel)

fig.update_traces(texttemplate="$%{text:.2f}", textposition="outside")
fig.update_layout(yaxis_title="Panier moyen (USD)", title="Panier moyen par saison")
st.plotly_chart(fig, use_container_width=True)

# 3. Clients par région
st.subheader("3. 🌍 Top 10 régions avec le plus de clients")
top_regions = df.groupby("Location")["Customer_ID"].nunique().sort_values(ascending=False).head(10)
fig, ax = plt.subplots()
colors = plt.get_cmap('Paired').colors
bars = ax.bar(top_regions.index, top_regions.values, color=colors[:len(top_regions)])
for i, (region, count) in enumerate(top_regions.items()):
    ax.text(i, count + 1, str(count), ha='center', va='bottom')
ax.set_ylabel("Nombre de clients")
ax.set_xlabel("Région")
ax.set_xticklabels(top_regions.index, rotation=45, ha='right')
st.pyplot(fig)

# 4. Abonnés vs non abonnés
st.subheader("4. 📬 Abonnés vs Non abonnés")
df["Subscription_Status"] = df["Subscription_Status"].map({True: "Abonnés", False: "Non Abonnés"})
subscription_counts = df["Subscription_Status"].value_counts()
fig, ax = plt.subplots()
ax.pie(subscription_counts, labels=subscription_counts.index, autopct='%1.1f%%', startangle=90)
ax.axis('equal')
st.pyplot(fig)

# --- Analyse exploratoire ---
st.markdown("## 🔎 Analyse exploratoire")
tab1, tab2, tab3 = st.tabs(["Genre", "Catégorie", "Taille & Couleur"])

with tab1:
    st.subheader("📊 Répartition par Genre")
    genre_count = df['Gender'].value_counts().reset_index()
    genre_count.columns = ['Gender', 'Count']
    fig, ax = plt.subplots()
    ax.bar(genre_count['Gender'], genre_count['Count'], color=plt.get_cmap('Set2').colors)
    ax.set_title("Répartition par Genre")
    ax.set_ylabel("Nombre de clients")
    st.pyplot(fig)

    st.subheader("💰 Montant moyen par Genre")
    mean_price = df.groupby('Gender')['Purchase_Amount_USD'].mean().reset_index()
    st.dataframe(mean_price)

with tab2:
    st.subheader("📦 Articles achetés par Catégorie")
    cat_count = df['Category'].value_counts().reset_index()
    cat_count.columns = ['Category', 'Count']
    fig, ax = plt.subplots()
    ax.bar(cat_count['Category'], cat_count['Count'], color=plt.get_cmap('tab10').colors)
    ax.set_xticklabels(cat_count['Category'], rotation=45, ha='right')
    ax.set_ylabel("Nombre d'articles")
    st.pyplot(fig)

with tab3:
    st.subheader("🧵 Répartition des tailles")
    size_dist = df['Size'].value_counts().reset_index()
    size_dist.columns = ['Size', 'Count']
    fig, ax = plt.subplots()
    ax.bar(size_dist['Size'], size_dist['Count'], color=plt.get_cmap('Pastel1').colors)
    ax.set_ylabel("Quantité")
    st.pyplot(fig)
