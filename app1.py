"""
VayuTrack - Pollution Monitoring Dashboard
Main Entry Point: Run with 'streamlit run app.py'
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime, timedelta
import time

# Page Configuration
st.set_page_config(
    page_title="VayuTrack - Pollution Dashboard",
    page_icon="🌤️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main {
        background: linear-gradient(135deg, #1e3a8a 0%, #3b82f6 100%);
    }
    .stMetric {
        background-color: rgba(255, 255, 255, 0.1);
        padding: 15px;
        border-radius: 10px;
        backdrop-filter: blur(10px);
    }
    .css-1d391kg {
        padding: 2rem 1rem;
    }
    h1, h2, h3 {
        color: white;
    }
    .stAlert {
        background-color: rgba(239, 68, 68, 0.2);
        border: 2px solid #ef4444;
    }
    .safe-zone {
        background: linear-gradient(135deg, #10b981 0%, #059669 100%);
        padding: 20px;
        border-radius: 15px;
        color: white;
        margin: 10px 0;
    }
</style>
""", unsafe_allow_html=True)

# Helper Functions
def get_aqi_color(aqi):
    """Get color based on AQI value"""
    if aqi <= 50:
        return "#10b981"
    elif aqi <= 100:
        return "#84cc16"
    elif aqi <= 200:
        return "#f59e0b"
    elif aqi <= 300:
        return "#ef4444"
    elif aqi <= 400:
        return "#b91c1c"
    else:
        return "#7f1d1d"

def get_aqi_level(aqi):
    """Get AQI level from numeric value"""
    if aqi <= 50:
        return "Good"
    elif aqi <= 100:
        return "Satisfactory"
    elif aqi <= 200:
        return "Moderate"
    elif aqi <= 300:
        return "Poor"
    elif aqi <= 400:
        return "Very Poor"
    else:
        return "Severe"

def get_health_advisory(aqi):
    """Get health advisory based on AQI"""
    if aqi <= 50:
        return "✅ Air quality is good. Enjoy outdoor activities!"
    elif aqi <= 100:
        return "😊 Air quality is acceptable for most people."
    elif aqi <= 200:
        return "⚠️ Sensitive groups should limit outdoor exposure."
    elif aqi <= 300:
        return "🚨 Everyone should limit outdoor activities."
    elif aqi <= 400:
        return "⛔ Avoid outdoor activities. Use N95 masks."
    else:
        return "🚫 EMERGENCY: Stay indoors. Health alert for all!"

# Generate Mock Data
@st.cache_data
def generate_forecast_data(hours=72):
    """Generate forecast data"""
    base_aqi = 250
    data = []
    for i in range(hours):
        aqi = base_aqi + np.sin(i / 12) * 50 + np.random.normal(0, 10)
        data.append({
            'Hour': i,
            'AQI': max(50, min(500, aqi)),
            'PM2.5': aqi * 0.45,
            'Time': (datetime.now() + timedelta(hours=i)).strftime('%d %b %H:%M')
        })
    return pd.DataFrame(data)

@st.cache_data
def generate_source_data():
    """Generate pollution source data"""
    return pd.DataFrame({
        'Source': ['Vehicular', 'Industrial', 'Construction', 'Biomass', 'Others'],
        'Percentage': [35, 25, 20, 12, 8],
        'Emission Rate': [142.5, 102.0, 81.5, 48.9, 32.6]
    })

@st.cache_data
def generate_hotspots():
    """Generate hotspot data"""
    return pd.DataFrame({
        'Area': ['Anand Vihar', 'RK Puram', 'Dwarka', 'Rohini', 'Punjabi Bagh', 'Lodhi Road', 'ITO', 'Nehru Nagar'],
        'AQI': [456, 389, 342, 298, 276, 189, 156, 123],
        'Latitude': [28.6469, 28.5632, 28.5921, 28.7495, 28.6692, 28.5919, 28.6273, 28.5677],
        'Longitude': [77.3163, 77.1837, 77.0460, 77.0736, 77.1310, 77.2189, 77.2502, 77.2545],
        'Category': ['High Risk', 'High Risk', 'High Risk', 'Moderate Risk', 'Moderate Risk', 'Safe', 'Safe', 'Safe']
    })

@st.cache_data
def generate_trend_data():
    """Generate historical trend data"""
    months = ['Oct', 'Nov', 'Dec', 'Jan', 'Feb', 'Mar']
    aqi_values = [320, 380, 340, 290, 250, 210]
    return pd.DataFrame({
        'Month': months,
        'AQI': aqi_values,
        'Policies': [0, 1, 1, 2, 2, 2]
    })

@st.cache_data
def generate_policy_data():
    """Generate policy impact data"""
    return pd.DataFrame({
        'Policy': ['Odd-Even Scheme', 'Construction Ban', 'Stubble Ban', 'BS-VI Norms'],
        'Impact': [-15, -22, -8, -18],
        'Status': ['Active', 'Active', 'Partial', 'Active'],
        'Cost Effectiveness': [0.78, 0.92, 0.45, 0.83]
    })

def get_safe_zones(hotspots_df):
    """Get areas with low AQI (safe zones)"""
    return hotspots_df[hotspots_df['AQI'] < 200].sort_values('AQI')

# Initialize Session State
if 'current_aqi' not in st.session_state:
    st.session_state.current_aqi = 287
if 'last_update' not in st.session_state:
    st.session_state.last_update = datetime.now()
if 'user_mode' not in st.session_state:
    st.session_state.user_mode = 'Government'

# Sidebar
with st.sidebar:
    st.markdown("### 🌤️ VayuTrack")
    st.markdown("Intelligent Pollution Monitoring")
    st.markdown("---")
    
    # User Mode Selection
    user_mode = st.radio(
        "👤 Select Dashboard",
        ["Government Dashboard", "Citizen Dashboard"],
        key='dashboard_mode'
    )
    st.session_state.user_mode = user_mode
    
    st.markdown("---")
    
    # City Selection
    selected_city = st.selectbox(
        "🌆 Select City",
        ["Delhi", "Gurugram", "Noida", "Faridabad", "Ghaziabad"]
    )
    
    # View Selection (Only for Government Dashboard)
    if user_mode == "Government Dashboard":
        view_mode = st.radio(
            "📊 Dashboard View",
            ["Overview", "Forecast", "Sources", "Policy Impact"]
        )
    
    st.markdown("---")
    
    # Real-time AQI
    st.markdown("### 🌡️ Real-time AQI")
    aqi_placeholder = st.empty()
    
    # Simulate real-time update
    st.session_state.current_aqi += np.random.normal(0, 2)
    st.session_state.current_aqi = max(150, min(400, st.session_state.current_aqi))
    
    aqi_color = get_aqi_color(st.session_state.current_aqi)
    aqi_placeholder.markdown(
        f"<h1 style='text-align: center; color: {aqi_color};'>{int(st.session_state.current_aqi)}</h1>",
        unsafe_allow_html=True
    )
    st.markdown(f"<p style='text-align: center; color: white;'>{get_aqi_level(st.session_state.current_aqi)}</p>", unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Last Updated
    st.caption(f"🕒 Last Updated: {datetime.now().strftime('%H:%M:%S')}")
    
    # Auto-refresh toggle
    auto_refresh = st.checkbox("🔄 Auto-refresh (15s)", value=False)

# Main Header
st.markdown("""
    <h1 style='text-align: center; color: white; text-shadow: 2px 2px 4px rgba(0,0,0,0.3);'>
        🌤️ VayuTrack
    </h1>
    <p style='text-align: center; color: #93c5fd; font-size: 18px;'>
        Intelligent Pollution Monitoring Dashboard
    </p>
""", unsafe_allow_html=True)

st.markdown("---")

# Health Alert
current_aqi = st.session_state.current_aqi
if current_aqi > 300:
    st.error(f"🚨 **HEALTH ALERT:** {get_health_advisory(current_aqi)}")
elif current_aqi > 200:
    st.warning(f"⚠️ **WARNING:** {get_health_advisory(current_aqi)}")
else:
    st.info(f"ℹ️ {get_health_advisory(current_aqi)}")

# ==================== CITIZEN DASHBOARD ====================
if user_mode == "Citizen Dashboard":
    st.markdown("## 👥 Citizen Dashboard - Your Air Quality Guide")
    
    # Key Metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Current AQI", f"{int(current_aqi)}", f"{int(np.random.normal(0, 5))} from yesterday")
    
    with col2:
        st.metric("PM2.5", f"{int(current_aqi * 0.45)} µg/m³", "-12 µg/m³")
    
    with col3:
        st.metric("PM10", f"{int(current_aqi * 0.75)} µg/m³", "+8 µg/m³")
    
    with col4:
        st.metric("Next 24h Peak", f"{int(current_aqi + 15)}", "+15 AQI")
    
    st.markdown("---")
    
    # Safe Zones Recommendation
    st.markdown("## 🌿 Recommended Safe Areas (Low AQI)")
    
    hotspots = generate_hotspots()
    safe_zones = get_safe_zones(hotspots)
    
    if len(safe_zones) > 0:
        st.markdown(f"""
        <div class="safe-zone">
            <h3>✅ Best Area to Visit: {safe_zones.iloc[0]['Area']}</h3>
            <h2>AQI: {int(safe_zones.iloc[0]['AQI'])} - {get_aqi_level(safe_zones.iloc[0]['AQI'])}</h2>
            <p>This area has the lowest pollution levels in your city. Perfect for outdoor activities!</p>
        </div>
        """, unsafe_allow_html=True)
        
        # Top 3 Safe Zones
        col1, col2, col3 = st.columns(3)
        
        for idx, (col, (_, row)) in enumerate(zip([col1, col2, col3], safe_zones.head(3).iterrows())):
            if idx < len(safe_zones):
                with col:
                    st.success(f"""
                    **{row['Area']}**  
                    AQI: {int(row['AQI'])}  
                    Status: {get_aqi_level(row['AQI'])}  
                    ✅ Safe for outdoor activities
                    """)
    else:
        st.warning("⚠️ No safe zones available currently. All areas have elevated pollution levels.")
    
    st.markdown("---")
    
    # Interactive Map with All Locations
    st.markdown("### 🗺️ Live Air Quality Map")
    
    fig_map = px.scatter_mapbox(
        hotspots,
        lat='Latitude',
        lon='Longitude',
        size='AQI',
        color='AQI',
        hover_name='Area',
        hover_data={'AQI': True, 'Latitude': False, 'Longitude': False, 'Category': True},
        color_continuous_scale=[
            [0, '#10b981'],      # Green (Good)
            [0.2, '#84cc16'],    # Light Green (Satisfactory)
            [0.4, '#f59e0b'],    # Orange (Moderate)
            [0.6, '#ef4444'],    # Red (Poor)
            [0.8, '#b91c1c'],    # Dark Red (Very Poor)
            [1, '#7f1d1d']       # Darkest Red (Severe)
        ],
        size_max=30,
        zoom=10,
        title=f"Air Quality across {selected_city}"
    )
    
    fig_map.update_layout(
        mapbox_style="open-street-map",
        height=500,
        margin={"r":0,"t":40,"l":0,"b":0},
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(color='white'),
        title_font_size=20
    )
    
    st.plotly_chart(fig_map, use_container_width=True)
    
    st.markdown("---")
    
    # Bar Chart - Area-wise AQI Comparison
    st.markdown("### 📊 Area-wise AQI Comparison")
    
    hotspots_sorted = hotspots.sort_values('AQI', ascending=True)
    
    fig_bar = go.Figure()
    fig_bar.add_trace(go.Bar(
        x=hotspots_sorted['Area'],
        y=hotspots_sorted['AQI'],
        marker_color=[get_aqi_color(aqi) for aqi in hotspots_sorted['AQI']],
        text=hotspots_sorted['AQI'].apply(lambda x: f"{int(x)}"),
        textposition='outside',
        hovertemplate='<b>%{x}</b><br>AQI: %{y}<extra></extra>'
    ))
    
    fig_bar.update_layout(
        height=400,
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(color='white'),
        xaxis_title="Area",
        yaxis_title="AQI Level",
        title="Which areas are safest?",
        xaxis=dict(showgrid=False, tickangle=-45),
        yaxis=dict(showgrid=True, gridcolor='rgba(255,255,255,0.1)')
    )
    
    st.plotly_chart(fig_bar, use_container_width=True)
    
    st.markdown("---")
    
    # Line Chart - 24 Hour Forecast
    st.markdown("### 📈 Your 24-Hour AQI Forecast")
    
    forecast_data = generate_forecast_data(24)
    
    fig_line = go.Figure()
    fig_line.add_trace(go.Scatter(
        x=forecast_data['Hour'],
        y=forecast_data['AQI'],
        mode='lines+markers',
        name='AQI Forecast',
        line=dict(color='#3b82f6', width=3),
        marker=dict(size=8, color='#60a5fa'),
        fill='tozeroy',
        fillcolor='rgba(59, 130, 246, 0.2)',
        hovertemplate='Hour %{x}<br>AQI: %{y:.0f}<extra></extra>'
    ))
    
    # Add threshold lines
    fig_line.add_hline(y=200, line_dash="dash", line_color="orange", 
                       annotation_text="Moderate Threshold", annotation_position="right")
    fig_line.add_hline(y=300, line_dash="dash", line_color="red", 
                       annotation_text="Poor Threshold", annotation_position="right")
    
    fig_line.update_layout(
        height=400,
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(color='white'),
        xaxis_title="Hours from Now",
        yaxis_title="AQI",
        title="Plan your outdoor activities wisely",
        hovermode='x unified',
        xaxis=dict(showgrid=False),
        yaxis=dict(showgrid=True, gridcolor='rgba(255,255,255,0.1)')
    )
    
    st.plotly_chart(fig_line, use_container_width=True)
    
    # Forecast Summary
    col1, col2, col3 = st.columns(3)
    
    peak_aqi = forecast_data['AQI'].max()
    peak_hour = forecast_data.loc[forecast_data['AQI'].idxmax(), 'Hour']
    best_aqi = forecast_data['AQI'].min()
    best_hour = forecast_data.loc[forecast_data['AQI'].idxmin(), 'Hour']
    
    with col1:
        st.info(f"""
        **Right Now**  
        AQI: {int(current_aqi)}  
        {get_aqi_level(current_aqi)}
        """)
    
    with col2:
        st.warning(f"""
        **Worst Time**  
        In {int(peak_hour)} hours  
        AQI: {int(peak_aqi)}
        """)
    
    with col3:
        st.success(f"""
        **Best Time**  
        In {int(best_hour)} hours  
        AQI: {int(best_aqi)}
        """)
    
    st.markdown("---")
    
    # Detailed Area Information
    st.markdown("### 📍 Detailed Area Information")
    
    # Create color-coded table
    def color_aqi(val):
        color = get_aqi_color(val)
        return f'background-color: {color}; color: white; font-weight: bold;'
    
    display_df = hotspots[['Area', 'AQI', 'Category']].copy()
    display_df['Status'] = display_df['AQI'].apply(get_aqi_level)
    display_df = display_df.sort_values('AQI')
    
    st.dataframe(
        display_df.style.applymap(color_aqi, subset=['AQI']),
        use_container_width=True,
        height=350
    )

# ==================== GOVERNMENT DASHBOARD ====================
elif user_mode == "Government Dashboard":
    
    if view_mode == "Overview":
        st.markdown("## 📊 Dashboard Overview")
        
        # Key Metrics
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Current AQI", f"{int(current_aqi)}", f"{int(np.random.normal(0, 5))} from yesterday")
        
        with col2:
            st.metric("PM2.5", f"{int(current_aqi * 0.45)} µg/m³", "-12 µg/m³")
        
        with col3:
            st.metric("PM10", f"{int(current_aqi * 0.75)} µg/m³", "+8 µg/m³")
        
        with col4:
            st.metric("Forecast (24h)", f"{int(current_aqi + 15)}", "+15 AQI")
        
        st.markdown("---")
        
        # Bar Chart - Pollution Sources
        st.markdown("### 📊 Pollution Source Distribution (Bar Chart)")
        
        source_data = generate_source_data()
        
        fig_bar = go.Figure()
        fig_bar.add_trace(go.Bar(
            x=source_data['Source'],
            y=source_data['Percentage'],
            marker_color=['#3b82f6', '#8b5cf6', '#f59e0b', '#ef4444', '#6b7280'],
            text=source_data['Percentage'].apply(lambda x: f"{x}%"),
            textposition='outside',
            hovertemplate='<b>%{x}</b><br>Contribution: %{y}%<extra></extra>'
        ))
        
        fig_bar.update_layout(
            height=400,
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            font=dict(color='white'),
            xaxis_title="Pollution Source",
            yaxis_title="Contribution (%)",
            xaxis=dict(showgrid=False),
            yaxis=dict(showgrid=True, gridcolor='rgba(255,255,255,0.1)')
        )
        
        st.plotly_chart(fig_bar, use_container_width=True)
        
        st.markdown("---")
        
        # Line Chart - Historical Trend
        st.markdown("### 📈 6-Month AQI Trend (Line Chart)")
        
        trend_data = generate_trend_data()
        
        fig_line = go.Figure()
        fig_line.add_trace(go.Scatter(
            x=trend_data['Month'],
            y=trend_data['AQI'],
            mode='lines+markers',
            name='AQI Trend',
            line=dict(color='#3b82f6', width=3),
            marker=dict(size=12, color='#60a5fa'),
            hovertemplate='%{x}<br>AQI: %{y}<extra></extra>'
        ))
        
        fig_line.update_layout(
            height=400,
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            font=dict(color='white'),
            xaxis_title="Month",
            yaxis_title="Average AQI",
            hovermode='x unified',
            xaxis=dict(showgrid=False),
            yaxis=dict(showgrid=True, gridcolor='rgba(255,255,255,0.1)')
        )
        
        st.plotly_chart(fig_line, use_container_width=True)
        
        st.markdown("---")
        
        # Hotspots
        st.markdown("### 🗺️ Pollution Hotspots")
        hotspots = generate_hotspots()
        
        for idx, row in hotspots.head(4).iterrows():
            col1, col2, col3 = st.columns([3, 1, 1])
            with col1:
                st.markdown(f"**{row['Area']}**")
            with col2:
                st.markdown(f"<span style='color: {get_aqi_color(row['AQI'])};'>AQI: {int(row['AQI'])}</span>", unsafe_allow_html=True)
            with col3:
                st.markdown(f"*{get_aqi_level(row['AQI'])}*")

    elif view_mode == "Forecast":
        st.markdown("## 📈 72-Hour AQI Forecast")
        
        forecast_data = generate_forecast_data(72)
        
        # Forecast Chart
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=forecast_data['Hour'],
            y=forecast_data['AQI'],
            mode='lines',
            name='AQI Forecast',
            line=dict(color='#3b82f6', width=3),
            fill='tozeroy',
            fillcolor='rgba(59, 130, 246, 0.2)'
        ))
        fig.add_trace(go.Scatter(
            x=forecast_data['Hour'],
            y=forecast_data['PM2.5'],
            mode='lines',
            name='PM2.5',
            line=dict(color='#8b5cf6', width=2, dash='dash')
        ))
        fig.update_layout(
            height=500,
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            font=dict(color='white'),
            xaxis_title="Hours from Now",
            yaxis_title="AQI / PM2.5",
            hovermode='x unified'
        )
        st.plotly_chart(fig, use_container_width=True)
        
        # Forecast Summary
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.info(f"**Tomorrow 9 AM**\nAQI: {int(forecast_data.iloc[9]['AQI'])}\n{get_aqi_level(forecast_data.iloc[9]['AQI'])}")
        
        with col2:
            peak_aqi = forecast_data['AQI'].max()
            peak_hour = forecast_data.loc[forecast_data['AQI'].idxmax(), 'Hour']
            st.warning(f"**Peak Expected**\nAQI: {int(peak_aqi)}\nIn {int(peak_hour)} hours")
        
        with col3:
            best_aqi = forecast_data['AQI'].min()
            best_hour = forecast_data.loc[forecast_data['AQI'].idxmin(), 'Hour']
            st.success(f"**Best Time**\nAQI: {int(best_aqi)}\nIn {int(best_hour)} hours")

    elif view_mode == "Sources":
        st.markdown("## 🏭 Pollution Source Attribution")
        
        source_data = generate_source_data()
        
        # Bar Chart
        fig = px.bar(
            source_data,
            x='Source',
            y='Percentage',
            color='Source',
            text='Percentage',
            color_discrete_map={
                'Vehicular': '#3b82f6',
                'Industrial': '#8b5cf6',
                'Construction': '#f59e0b',
                'Biomass': '#ef4444',
                'Others': '#6b7280'
            }
        )
        fig.update_traces(texttemplate='%{text}%', textposition='outside')
        fig.update_layout(
            height=400,
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            font=dict(color='white'),
            showlegend=False,
            xaxis_title="Pollution Source",
            yaxis_title="Contribution (%)"
        )
        st.plotly_chart(fig, use_container_width=True)
        
        # Detailed Table
        st.markdown("### 📋 Detailed Source Analysis")
        st.dataframe(
            source_data.style.background_gradient(subset=['Percentage'], cmap='RdYlGn_r'),
            use_container_width=True
        )

    elif view_mode == "Policy Impact":
        st.markdown("## 🏛️ Policy Intervention Impact")
        
        policy_data = generate_policy_data()
        
        # Impact Chart
        fig = go.Figure()
        fig.add_trace(go.Bar(
            x=policy_data['Policy'],
            y=policy_data['Impact'],
            marker_color=['#10b981' if x < 0 else '#ef4444' for x in policy_data['Impact']],
            text=policy_data['Impact'],
            texttemplate='%{text}%',
            textposition='outside'
        ))
        fig.update_layout(
            height=400,
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            font=dict(color='white'),
            xaxis_title="Policy",
            yaxis_title="AQI Reduction (%)",
            title="Policy Effectiveness"
        )
        st.plotly_chart(fig, use_container_width=True)
        
        # Policy Details
        st.markdown("### 📊 Policy Details")
        for idx, row in policy_data.iterrows():
            with st.expander(f"{row['Policy']} - {row['Status']}"):
                col1, col2 = st.columns(2)
                with col1:
                    st.metric("AQI Reduction", f"{row['Impact']}%")
                with col2:
                    st.metric("Cost Effectiveness", f"{row['Cost Effectiveness']:.2f}")

# Footer
st.markdown("---")
st.markdown("""
    <div style='text-align: center; color: #93c5fd;'>
        <p>VayuTrack - Real-time Pollution Monitoring | Data updates every 15 minutes</p>
    </div>
""", unsafe_allow_html=True)

# Auto-refresh logic
if auto_refresh:
    time.sleep(15)
    st.rerun()
