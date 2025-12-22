import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import time

# ===============================
# CONFIGURATION PAGE
# ===============================
st.set_page_config(
    page_title="Tableau de bord E-commerce",
    layout="wide"
)

st.title("📊 Tableau de bord E-commerce")
st.markdown("Analyse des événements, produits et catégories")

# ===============================
# LOADER (SPINNER)
# ===============================
with st.spinner("⏳ Chargement des données, veuillez patienter..."):

    # Simule un petit délai (optionnel mais visuel)
    time.sleep(1)

    # Chargement des données
    events = pd.read_csv("data/cleaning/events_donnees_nettoyees.csv", sep=';')
    items = pd.read_csv("data/cleaning/item_properties_donnees_nettoyees.csv", sep=';')
    categories = pd.read_csv("data/cleaning/category_tree_donnees_nettoyees.csv", sep=';')

    # Normalisation
    events['itemid'] = events['itemid'].astype(str)
    items['itemid'] = items['itemid'].astype(str)
    categories['categoryid'] = categories['categoryid'].astype(str)

    # Pivot des items
    items_pivot = items.pivot_table(
        index='itemid',
        columns='property',
        values='value',
        aggfunc='first'
    ).reset_index()

    items_pivot.columns.name = None

    if 'name' not in items_pivot.columns:
        items_pivot['name'] = items_pivot['itemid']

    items_pivot['categoryid'] = items_pivot['categoryid'].astype(str)

    # Merge
    df = events.merge(
        items_pivot[['itemid', 'name', 'categoryid']],
        on='itemid',
        how='left'
    )

    df = df.merge(
        categories,
        on='categoryid',
        how='left'
    )

# ===============================
# MESSAGE APRÈS CHARGEMENT
# ===============================
st.success("✅ Données chargées avec succès")

# ===============================
# FILTRES
# ===============================
st.sidebar.header("🎯 Filtres")

event_filter = st.sidebar.multiselect(
    "Type d'événement",
    df['event'].unique(),
    default=df['event'].unique()
)

category_filter = st.sidebar.selectbox(
    "Catégorie",
    ['Toutes'] + sorted(df['categoryid'].dropna().unique())
)

filtered_df = df[df['event'].isin(event_filter)]

if category_filter != 'Toutes':
    filtered_df = filtered_df[filtered_df['categoryid'] == category_filter]

# ===============================
# APERÇU
# ===============================
st.subheader("🔍 Aperçu des données")
st.dataframe(filtered_df.head(500))

# ===============================
# KPI
# ===============================
st.subheader("📈 Indicateurs clés")
col1, col2, col3 = st.columns(3)

col1.metric("👀 Vues", filtered_df[filtered_df['event'] == 'view'].shape[0])
col2.metric("🛒 Add to cart", filtered_df[filtered_df['event'] == 'addtocart'].shape[0])
col3.metric("💳 Transactions", filtered_df[filtered_df['event'] == 'transaction'].shape[0])

# ===============================
# GRAPHIQUES
# ===============================
st.subheader("📊 Répartition des événements")
st.bar_chart(filtered_df['event'].value_counts())

st.subheader("🏆 Top produits (Add to cart)")
top_products = (
    filtered_df[filtered_df['event'] == 'addtocart']
    .groupby('name')
    .size()
    .sort_values(ascending=False)
    .head(10)
)
st.bar_chart(top_products)
