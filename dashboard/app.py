"""
Streamlit Dashboard for Supply Chain Satisfaction Analysis
"""
import streamlit as st
import requests
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from typing import Dict, Any
import os

# Configuration
API_URL = os.getenv("API_URL", "http://localhost:8000")

# Page configuration
st.set_page_config(
    page_title="Supply Chain Satisfaction Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
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
    """Fetch statistics from API"""
    try:
        response = requests.get(f"{API_URL}/api/stats", timeout=5)
        if response.status_code == 200:
            return response.json()
    except Exception as e:
        st.error(f"Error fetching stats: {e}")
    
    # Return default data if API is unavailable
    return {
        "average_rating": 4.2,
        "total_reviews": 1000,
        "positive_reviews": 750,
        "negative_reviews": 150,
        "neutral_reviews": 100
    }

def fetch_reviews(limit: int = 10) -> list:
    """Fetch reviews from API"""
    try:
        response = requests.get(f"{API_URL}/api/reviews?limit={limit}", timeout=5)
        if response.status_code == 200:
            return response.json()
    except Exception as e:
        st.error(f"Error fetching reviews: {e}")
    
    # Return default data if API is unavailable
    return [
        {"id": 1, "company": "Company A", "rating": 4.5, "comment": "Great service", "date": "2025-11-01"},
        {"id": 2, "company": "Company B", "rating": 3.0, "comment": "Average experience", "date": "2025-11-02"}
    ]

def fetch_companies() -> list:
    """Fetch companies from API"""
    try:
        response = requests.get(f"{API_URL}/api/companies", timeout=5)
        if response.status_code == 200:
            return response.json().get("companies", [])
    except Exception as e:
        st.error(f"Error fetching companies: {e}")
    
    return [
        {"name": "Company A", "review_count": 450},
        {"name": "Company B", "review_count": 350},
        {"name": "Company C", "review_count": 200}
    ]

# Sidebar
with st.sidebar:
    st.title("Navigation")
    page = st.radio(
        "Select Page:",
        ["Overview", "Reviews", "Companies", "Analytics"]
    )
    
    st.markdown("---")
    st.markdown("### About")
    st.info("Supply Chain Satisfaction Analysis Dashboard")
    
    # API Status
    try:
        response = requests.get(f"{API_URL}/health", timeout=2)
        if response.status_code == 200:
            st.success("API Connected")
        else:
            st.warning("API Issues")
    except:
        st.error("API Offline")

# Main content
st.title("Supply Chain Satisfaction Dashboard")

if page == "Overview":
    st.header("Overview")
    
    # Fetch and display statistics
    stats = fetch_stats()
    
    # Metrics row
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Average Rating", f"{stats['average_rating']:.1f} ⭐")
    
    with col2:
        st.metric("Total Reviews", f"{stats['total_reviews']:,}")
    
    with col3:
        positive_pct = (stats['positive_reviews'] / stats['total_reviews'] * 100)
        st.metric("Positive Reviews", f"{positive_pct:.1f}%")
    
    with col4:
        negative_pct = (stats['negative_reviews'] / stats['total_reviews'] * 100)
        st.metric("Negative Reviews", f"{negative_pct:.1f}%")
    
    # Charts
    col1, col2 = st.columns(2)
    
    with col1:
        # Sentiment Distribution
        sentiment_data = pd.DataFrame({
            'Sentiment': ['Positive', 'Neutral', 'Negative'],
            'Count': [stats['positive_reviews'], stats['neutral_reviews'], stats['negative_reviews']]
        })
        
        fig = px.pie(
            sentiment_data,
            values='Count',
            names='Sentiment',
            title='Sentiment Distribution',
            color='Sentiment',
            color_discrete_map={'Positive': 'green', 'Neutral': 'gray', 'Negative': 'red'}
        )
        st.plotly_chart(fig, width='stretch')
    
    with col2:
        # Sample trend data
        trend_data = pd.DataFrame({
            'Date': pd.date_range(start='2025-01-01', periods=12, freq='ME'),
            'Rating': [4.0, 4.1, 4.2, 4.0, 4.3, 4.2, 4.4, 4.3, 4.5, 4.4, 4.2, 4.3]
        })
        
        fig = px.line(
            trend_data,
            x='Date',
            y='Rating',
            title='Average Rating Trend',
            markers=True
        )
        fig.update_yaxes(range=[3.5, 5.0])
        st.plotly_chart(fig, width='stretch')

elif page == "Reviews":
    st.header("Recent Reviews")
    
    # Filters
    col1, col2 = st.columns([1, 3])
    with col1:
        num_reviews = st.selectbox("Number of reviews", [10, 25, 50, 100], index=0)
    
    # Fetch and display reviews
    reviews = fetch_reviews(limit=num_reviews)
    
    if reviews:
        df = pd.DataFrame(reviews)
        
        # Display reviews
        for _, review in df.iterrows():
            with st.expander(f"⭐ {review['rating']} - {review['company']} ({review.get('date', 'N/A')})"):
                st.write(review['comment'])
    else:
        st.info("No reviews available")

elif page == "Companies":
    st.header("Company Analysis")
    
    companies = fetch_companies()
    
    if companies:
        df = pd.DataFrame(companies)
        
        # Bar chart
        fig = px.bar(
            df,
            x='name',
            y='review_count',
            title='Reviews by Company',
            labels={'name': 'Company', 'review_count': 'Number of Reviews'},
            color='review_count',
            color_continuous_scale='Blues'
        )
        st.plotly_chart(fig, width='stretch')
        
        # Data table
        st.subheader("Company Details")
        st.dataframe(df, width='stretch')
    else:
        st.info("No company data available")

elif page == "Analytics":
    st.header("Advanced Analytics")
    
    st.info("🚧 Advanced analytics features coming soon!")
    
    # Placeholder charts
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Rating Distribution")
        rating_dist = pd.DataFrame({
            'Rating': [1, 2, 3, 4, 5],
            'Count': [50, 100, 100, 350, 400]
        })
        fig = px.bar(rating_dist, x='Rating', y='Count')
        st.plotly_chart(fig, width='stretch')
    
    with col2:
        st.subheader("Top Keywords")
        keywords = pd.DataFrame({
            'Keyword': ['delivery', 'quality', 'service', 'price', 'support'],
            'Frequency': [450, 380, 320, 280, 210]
        })
        fig = px.bar(keywords, x='Frequency', y='Keyword', orientation='h')
        st.plotly_chart(fig, width='stretch')

# Footer
st.markdown("---")
st.markdown("Supply Chain Satisfaction Dashboard © 2025")
