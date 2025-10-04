"""
AirSense AI - Minimal Streamlit Version
100% Compatible - No dependency issues
Run: streamlit run app_minimal.py
"""

import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

# Page config
st.set_page_config(
    page_title="AirSense AI",
    page_icon="🌤️",
    layout="wide"
)

# Custom CSS
st.markdown("""
<style>
    .main {background: linear-gradient(135deg, #1e3a8a 0%, #3b82f6 100%);}
    h1, h2, h3, p {color: white !important;}
    .stMetric {background: rgba(255,255,255,0.1); padding: 15px; border-radius: 10px;}
</style>
""", unsafe_allow_html=True)

# Helper functions
def get_aqi_color(aqi):
    if aqi <= 50: return "#10b981"
    elif aqi <= 100: return "#84cc16"
    elif aqi <= 200: return "#f59e0b"
    elif aqi <= 300: return "#ef4444"
    elif aqi <= 400: return "#b91c1c"
    else: return "#7f1d1d"

def get_aqi_level(aqi):
    if aqi <= 50: return "Good"
    elif aqi <= 100: return "Satisfactory"
    elif aqi <= 200: return "Moderate"
    elif aqi <= 300: return "Poor"
    elif aqi <= 400: return "Very Poor"
    else: return "Severe"

# Initialize state
if 'aqi' not in st.session_state:
    st.session_state.aqi = 287

# Header
st.markdown("<h1 style='text-align: center;'>🌤️ AirSense AI</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center;'>Smart India Hackathon 2025 - AI Pollution Dashboard</p>", unsafe_allow_html=True)
st.markdown("---")

# Sidebar
with st.sidebar:
    st.markdown("### 🌆 Settings")
    city = st.selectbox("City", ["Delhi", "Gurugram", "Noida", "Faridabad"])
    view = st.radio("View", ["Dashboard", "Forecast", "Sources", "Policy"])
    
    st.markdown("---")
    st.markdown("### 🌡️ Current AQI")
    
    # Simulate real-time
    st.session_state.aqi += np.random.normal(0, 2)
    st.session_state.aqi = max(150, min(400, st.session_state.aqi))
    
    aqi_color = get_aqi_color(st.session_state.aqi)
    st.markdown(f"<h1 style='text-align:center;color:{aqi_color};'>{int(st.session_state.aqi)}</h1>", unsafe_allow_html=True)
    st.markdown(f"<p style='text-align:center;'>{get_aqi_level(st.session_state.aqi)}</p>", unsafe_allow_html=True)

# Alert
current_aqi = st.session_state.aqi
if current_aqi > 300:
    st.error("🚨 HEALTH ALERT: Very Poor air quality. Avoid outdoor activities!")
elif current_aqi > 200:
    st.warning("⚠️ WARNING: Poor air quality. Limit outdoor exposure.")
else:
    st.info("ℹ️ Air quality is moderate. Sensitive groups should be cautious.")

# Main content
if view == "Dashboard":
    st.markdown("## 📊 Dashboard Overview")
    
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Current AQI", f"{int(current_aqi)}", "+5")
    col2.metric("PM2.5", f"{int(current_aqi * 0.45)} µg/m³", "-12")
    col3.metric("PM10", f"{int(current_aqi * 0.75)} µg/m³", "+8")
    col4.metric("Forecast", f"{int(current_aqi + 15)}", "+15")
    
    st.markdown("---")
    
    # Source data
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 🏭 Pollution Sources")
        source_df = pd.DataFrame({
            'Source': ['Vehicular', 'Industrial', 'Construction', 'Biomass', 'Others'],
            'Percentage': [35, 25, 20, 12, 8]
        })
        st.bar_chart(source_df.set_index('Source'))
    
    with col2:
        st.markdown("### 📈 Monthly Trend")
        trend_df = pd.DataFrame({
            'Month': ['Oct', 'Nov', 'Dec', 'Jan', 'Feb', 'Mar'],
            'AQI': [320, 380, 340, 290, 250, 210]
        })
        st.line_chart(trend_df.set_index('Month'))
    
    # Hotspots
    st.markdown("### 🗺️ Pollution Hotspots")
    hotspots = pd.DataFrame({
        'Area': ['Anand Vihar', 'RK Puram', 'Dwarka', 'Rohini'],
        'AQI': [456, 389, 342, 298],
        'Level': ['Severe', 'Very Poor', 'Very Poor', 'Poor']
    })
    
    for idx, row in hotspots.iterrows():
        col1, col2, col3 = st.columns([3, 1, 2])
        with col1:
            st.write(f"**{row['Area']}**")
        with col2:
            st.write(f"**{row['AQI']}**")
        with col3:
            st.write(f"*{row['Level']}*")

elif view == "Forecast":
    st.markdown("## 📈 72-Hour Forecast")
    
    # Generate forecast
    hours = list(range(72))
    base = current_aqi
    forecast_aqi = [base + np.sin(i/12)*50 + np.random.normal(0,10) for i in hours]
    
    forecast_df = pd.DataFrame({
        'Hour': hours,
        'AQI': forecast_aqi
    })
    
    st.line_chart(forecast_df.set_index('Hour'))
    
    col1, col2, col3 = st.columns(3)
    col1.info(f"**Tomorrow 9AM**\nAQI: {int(forecast_aqi[9])}")
    col2.warning(f"**Peak**\nAQI: {int(max(forecast_aqi))}")
    col3.success(f"**Best Time**\nAQI: {int(min(forecast_aqi))}")

elif view == "Sources":
    st.markdown("## 🏭 Pollution Sources")
    
    source_df = pd.DataFrame({
        'Source': ['Vehicular', 'Industrial', 'Construction', 'Biomass', 'Others'],
        'Percentage': [35, 25, 20, 12, 8],
        'Emission Rate': [142.5, 102.0, 81.5, 48.9, 32.6]
    })
    
    st.bar_chart(source_df.set_index('Source')['Percentage'])
    
    st.markdown("### 📋 Detailed Analysis")
    st.dataframe(source_df, use_container_width=True)

elif view == "Policy":
    st.markdown("## 🏛️ Policy Impact")
    
    policy_df = pd.DataFrame({
        'Policy': ['Odd-Even', 'Construction Ban', 'Stubble Ban', 'BS-VI'],
        'Impact': [-15, -22, -8, -18],
        'Status': ['Active', 'Active', 'Partial', 'Active']
    })
    
    st.bar_chart(policy_df.set_index('Policy')['Impact'])
    
    st.markdown("### 📊 Policy Details")
    for idx, row in policy_df.iterrows():
        with st.expander(f"{row['Policy']} - {row['Status']}"):
            st.metric("AQI Reduction", f"{row['Impact']}%")

# Footer
st.markdown("---")
st.markdown("<p style='text-align:center;'>AirSense AI © 2025 | Team: [Your Team] | SIH 2025</p>", unsafe_allow_html=True)

# Auto-refresh
if st.sidebar.checkbox("🔄 Auto-refresh", value=False):
    import time
    time.sleep(15)
    st.rerun()
