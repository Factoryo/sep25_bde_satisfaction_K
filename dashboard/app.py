import streamlit as st
import requests
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from typing import Dict, Any
import os

API_URL = os.getenv("API_URL", "http://localhost:8000")

st.set_page_config(
    page_title="Tableau de Bord - Satisfaction Client",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
    <style>
    .main {
        padding: 0rem 1rem;
    }
    .stMetric {
        background-color: #f0f2f6;
        padding: 15px;
        border-radius: 5px;
    }
    </style>
    """, unsafe_allow_html=True)

def fetch_stats() -> Dict[str, Any]:
    try:
        response = requests.get(f"{API_URL}/api/stats", timeout=5)
        if response.status_code == 200:
            return response.json()
    except Exception as e:
        st.error(f"Erreur lors de la récupération des statistiques: {e}")
    
    return {
        "average_rating": 4.2,
        "total_reviews": 1000,
        "positive_reviews": 750,
        "negative_reviews": 150,
        "neutral_reviews": 100
    }

def fetch_reviews(limit: int = 10, company: str | None = None) -> list:
    try:
        url = f"{API_URL}/api/reviews?limit={limit}&shuffle=true"
        if company:
            url += f"&company={company}"
        response = requests.get(url, timeout=5)
        if response.status_code == 200:
            return response.json()
    except Exception as e:
        st.error(f"Erreur lors de la récupération des avis: {e}")
    
    return []

def fetch_companies() -> list:
    try:
        response = requests.get(f"{API_URL}/api/companies", timeout=5)
        if response.status_code == 200:
            return response.json().get("companies", [])
    except Exception as e:
        st.error(f"Erreur lors de la récupération des entreprises: {e}")
    
    return [
        {"name": "Entreprise A", "review_count": 450},
        {"name": "Entreprise B", "review_count": 350},
        {"name": "Entreprise C", "review_count": 200}
    ]

with st.sidebar:
    st.title("Navigation")
    page = st.radio(
        "Sélectionner une page:",
        ["Vue d'ensemble", "Avis", "Entreprises", "Analyses"]
    )
    
    st.markdown("---")
    st.markdown("### À propos")
    st.info("Tableau de bord d'analyse de satisfaction client")
    
    try:
        response = requests.get(f"{API_URL}/health", timeout=2)
        if response.status_code == 200:
            st.success("API Connectée")
        else:
            st.warning("Problèmes API")
    except:
        st.error("API Hors ligne")

st.title("Tableau de Bord - Satisfaction Client")

if page == "Vue d'ensemble":
    st.header("Vue d'ensemble")
    
    stats = fetch_stats()
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Note Moyenne", f"{stats['average_rating']:.1f} ⭐")
    
    with col2:
        st.metric("Total des Avis", f"{stats['total_reviews']:,}")
    
    with col3:
        positive_pct = (stats['positive_reviews'] / stats['total_reviews'] * 100)
        st.metric("Avis Positifs", f"{positive_pct:.1f}%")
    
    with col4:
        negative_pct = (stats['negative_reviews'] / stats['total_reviews'] * 100)
        st.metric("Avis Négatifs", f"{negative_pct:.1f}%")
    
    col1, col2 = st.columns(2)
    
    with col1:
        sentiment_data = pd.DataFrame({
            'Sentiment': ['Positif', 'Neutre', 'Négatif'],
            'Count': [stats['positive_reviews'], stats['neutral_reviews'], stats['negative_reviews']]
        })
        
        fig = px.pie(
            sentiment_data,
            values='Count',
            names='Sentiment',
            title='Distribution des Sentiments',
            color='Sentiment',
            color_discrete_map={'Positif': 'green', 'Neutre': 'gray', 'Négatif': 'red'}
        )
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        trend_data = pd.DataFrame({
            'Date': pd.date_range(start='2025-01-01', periods=12, freq='ME'),
            'Note': [4.0, 4.1, 4.2, 4.0, 4.3, 4.2, 4.4, 4.3, 4.5, 4.4, 4.2, 4.3]
        })
        
        fig = px.line(
            trend_data,
            x='Date',
            y='Note',
            title='Évolution de la Note Moyenne',
            markers=True
        )
        fig.update_yaxes(range=[3.5, 5.0])
        st.plotly_chart(fig, use_container_width=True)

elif page == "Avis":
    st.header("Avis Récents")
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col1:
        num_reviews = st.selectbox("Nombre d'avis", [10, 25, 50, 100], index=0)
    with col2:
        companies = fetch_companies()
        company_names = ["Toutes"] + [c['name'] for c in companies]
        selected_company = st.selectbox("Entreprise", company_names, index=0)
    
    company_filter = None if selected_company == "Toutes" else selected_company
    reviews = fetch_reviews(limit=num_reviews, company=company_filter)
    
    if reviews:
        df = pd.DataFrame(reviews)
        
        for _, review in df.iterrows():
            with st.expander(f"⭐ {review['rating']} - {review['company']} ({review.get('date', 'N/A')})"):
                st.write(review['comment'])
    else:
        st.info("Aucun avis disponible")

elif page == "Entreprises":
    st.header("Analyse par Entreprise")
    
    companies = fetch_companies()
    
    if companies:
        df = pd.DataFrame(companies)
        
        fig = px.bar(
            df,
            x='name',
            y='review_count',
            title='Avis par Entreprise',
            labels={'name': 'Entreprise', 'review_count': 'Nombre d\'Avis'},
            color='review_count',
            color_continuous_scale='Blues'
        )
        st.plotly_chart(fig, use_container_width=True)
        
        st.subheader("Détails des Entreprises")
        st.dataframe(df, use_container_width=True)
    else:
        st.info("Aucune donnée d'entreprise disponible")

elif page == "Analyses":
    st.header("Analyses Avancées")
    
    st.info("🚧 Fonctionnalités d'analyses avancées à venir !")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Distribution des Notes")
        rating_dist = pd.DataFrame({
            'Note': [1, 2, 3, 4, 5],
            'Nombre': [50, 100, 100, 350, 400]
        })
        fig = px.bar(rating_dist, x='Note', y='Nombre')
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.subheader("Mots-clés les Plus Fréquents")
        keywords = pd.DataFrame({
            'Mot-clé': ['livraison', 'qualité', 'service', 'prix', 'support'],
            'Fréquence': [450, 380, 320, 280, 210]
        })
        fig = px.bar(keywords, x='Fréquence', y='Mot-clé', orientation='h')
        st.plotly_chart(fig, use_container_width=True)

st.markdown("---")
st.markdown("Tableau de Bord - Satisfaction Client © 2025")