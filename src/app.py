
 # app.py
import streamlit as st
import pandas as pd
import plotly.express as px
from data_pipeline import load_complaints_sample, clean_complaint_data

# Page configuration
st.set_page_config(
    page_title="CFPB Complaint Analyst",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Title and description
st.title("📊 CFPB Consumer Complaint Analysis")
st.markdown("""
Analyze trends and patterns in consumer financial complaints. 
Use this dashboard to identify common issues, monitor company performance, and explore consumer narratives.
""")

# Load data with caching to avoid reloading on every interaction
@st.cache_data
def load_data():
    """Load and cache the complaint data."""
    raw_data = load_complaints_sample("data/consumer_complaints.csv", sample_size=10000)
    if raw_data is not None:
        return clean_complaint_data(raw_data)
    return None

# Load the data
with st.spinner("Loading complaint data..."):
    df = load_data()

if df is None:
    st.error("Failed to load data. Please check your data file.")
    st.stop()

# Sidebar filters
st.sidebar.header("🔍 Filters")

# Initialize filter variables with safe defaults
selected_companies = []
selected_products = []
date_range = []

# Company filter - safely get unique companies
if 'company' in df.columns:
    companies = sorted(df['company'].dropna().unique())
    selected_companies = st.sidebar.multiselect(
        "Companies",
        options=companies,
        default=companies[:5] if len(companies) > 5 else companies
    )
else:
    st.sidebar.warning("Company data not available")

# Product filter - safely get unique products
if 'product' in df.columns:
    products = sorted(df['product'].dropna().unique())
    selected_products = st.sidebar.multiselect(
        "Products",
        options=products,
        default=products
    )
else:
    st.sidebar.warning("Product data not available")

# Date range filter - safely handle dates
if 'date_received' in df.columns and df['date_received'].notna().any():
    min_date = df['date_received'].min()
    max_date = df['date_received'].max()
    date_range = st.sidebar.date_input(
        "Date Range",
        value=(min_date, max_date),
        min_value=min_date,
        max_value=max_date
    )
else:
    st.sidebar.info("Date information not available")

# Apply filters
filtered_df = df.copy()

if selected_companies:
    filtered_df = filtered_df[filtered_df['company'].isin(selected_companies)]
    
if selected_products:
    filtered_df = filtered_df[filtered_df['product'].isin(selected_products)]
    
if 'date_received' in df.columns and len(date_range) == 2:
    filtered_df = filtered_df[
        (filtered_df['date_received'] >= pd.to_datetime(date_range[0])) &
        (filtered_df['date_received'] <= pd.to_datetime(date_range[1]))
    ]

# Main dashboard
st.header("📈 Overview Metrics")

col1, col2, col3, col4 = st.columns(4)
with col1:
    st.metric("Total Complaints", len(filtered_df))
with col2:
    st.metric("Unique Companies", filtered_df['company'].nunique() if 'company' in filtered_df.columns else 0)
with col3:
    st.metric("Product Types", filtered_df['product'].nunique() if 'product' in filtered_df.columns else 0)
with col4:
    if 'consumer_complaint_narrative' in filtered_df.columns:
        narrative_count = filtered_df['consumer_complaint_narrative'].str.strip().ne('').sum()
        st.metric("With Narratives", narrative_count)
    else:
        st.metric("With Narratives", 0)

# Complaints over time
st.header("📅 Complaints Over Time")
if 'date_received' in filtered_df.columns and filtered_df['date_received'].notna().any():
    time_series = filtered_df.groupby(filtered_df['date_received'].dt.to_period('M')).size().reset_index()
    time_series['date_received'] = time_series['date_received'].dt.to_timestamp()
    fig = px.line(time_series, x='date_received', y=0, 
                 title='Monthly Complaint Volume',
                 labels={'date_received': 'Date', '0': 'Number of Complaints'})
    st.plotly_chart(fig, use_container_width=True)
else:
    st.info("Date information not available for time series analysis.")

# Top companies
st.header("🏢 Top Companies by Complaints")
if 'company' in filtered_df.columns and filtered_df['company'].notna().any():
    company_counts = filtered_df['company'].value_counts().head(10)
    fig = px.bar(company_counts, x=company_counts.index, y=company_counts.values,
                 title='Top 10 Companies with Most Complaints',
                 labels={'x': 'Company', 'y': 'Number of Complaints'})
    st.plotly_chart(fig, use_container_width=True)
else:
    st.info("Company data not available for analysis")

# Product distribution
st.header("💳 Complaint Distribution by Product")
if 'product' in filtered_df.columns and filtered_df['product'].notna().any():
    product_counts = filtered_df['product'].value_counts()
    fig = px.pie(product_counts, values=product_counts.values, names=product_counts.index,
                 title='Complaints by Product Type')
    st.plotly_chart(fig, use_container_width=True)
else:
    st.info("Product data not available for analysis")

# State distribution (if available)
if 'state' in filtered_df.columns and filtered_df['state'].notna().any():
    st.header("🗺️ Complaints by State")
    state_counts = filtered_df['state'].value_counts().head(15)
    fig = px.bar(state_counts, x=state_counts.index, y=state_counts.values,
                 title='Top 15 States by Complaints',
                 labels={'x': 'State', 'y': 'Number of Complaints'})
    st.plotly_chart(fig, use_container_width=True)

# Raw data preview
st.header("🔍 Data Preview")
st.dataframe(filtered_df.head(100), use_container_width=True)

st.sidebar.markdown("---")
st.sidebar.info("💡 Tip: Use the filters to focus on specific companies or products.")
