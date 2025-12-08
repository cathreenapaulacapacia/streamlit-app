import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime, timedelta
import pickle
import time

# Page configuration
st.set_page_config(
    page_title="Water Quality Monitoring",
    page_icon="💧",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
    <style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1E40AF;
        text-align: center;
        padding: 1rem;
        background: linear-gradient(90deg, #3B82F6 0%, #06B6D4 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    .metric-card {
        background-color: #F0F9FF;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #3B82F6;
    }
    .warning-box {
        background-color: #FEF3C7;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #F59E0B;
    }
    .danger-box {
        background-color: #FEE2E2;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #EF4444;
    }
    .success-box {
        background-color: #D1FAE5;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #10B981;
    }
    </style>
""", unsafe_allow_html=True)

# Initialize session state
if 'historical_data' not in st.session_state:
    # Generate sample historical data
    dates = pd.date_range(end=datetime.now(), periods=100, freq='H')
    st.session_state.historical_data = pd.DataFrame({
        'timestamp': dates,
        'pH': 7.0 + np.random.randn(100) * 0.5,
        'temperature': 27.0 + np.random.randn(100) * 2,
        'ammonia': 0.2 + np.abs(np.random.randn(100) * 0.15)
    })

if 'real_time_mode' not in st.session_state:
    st.session_state.real_time_mode = False

if 'prediction_history' not in st.session_state:
    st.session_state.prediction_history = []

# ML Prediction Function (simplified model)
def predict_ammonia(ph, temperature):
    """
    Simplified ML prediction based on pH and temperature
    Replace this with your actual trained model
    """
    # Standardize inputs (using approximate means and stds)
    ph_scaled = (ph - 7.5) / 1.0
    temp_scaled = (temperature - 27.0) / 3.0
    
    # Simple linear combination (replace with actual model)
    prediction = 0.15 + (ph_scaled * 0.08) + (temp_scaled * 0.05)
    prediction = max(0, prediction + np.random.randn() * 0.02)
    
    return prediction

# Risk Assessment Function
def get_risk_level(ammonia):
    """Classify ammonia risk level"""
    if ammonia < 0.2:
        return "Low", "🟢", "success"
    elif ammonia < 0.4:
        return "Moderate", "🟡", "warning"
    else:
        return "High", "🔴", "danger"

# Prescriptive Analytics Function
def get_prescriptive_advice(ph, temperature, ammonia):
    """Generate prescriptive recommendations"""
    advice_list = []
    
    # Critical conditions
    if ph > 8.0 and temperature > 28.0:
        advice_list.append({
            'priority': 'High',
            'icon': '🔴',
            'message': 'Critical: Both pH and temperature are elevated',
            'action': 'Perform immediate 30-40% water change and increase aeration',
            'type': 'danger'
        })
    elif ph > 8.0:
        advice_list.append({
            'priority': 'Medium',
            'icon': '🟡',
            'message': 'pH is elevated, increasing ammonia toxicity',
            'action': 'Add pH buffer or perform gradual water change (20-30%)',
            'type': 'warning'
        })
    elif temperature > 28.0:
        advice_list.append({
            'priority': 'Medium',
            'icon': '🟡',
            'message': 'Water temperature is high',
            'action': 'Increase aeration, reduce feeding by 30%, check cooling system',
            'type': 'warning'
        })
    
    # Ammonia-specific advice
    if ammonia > 0.4:
        advice_list.append({
            'priority': 'High',
            'icon': '🔴',
            'message': 'High ammonia detected! Immediate action required',
            'action': 'Stop feeding for 24hrs, perform 50% water change, add ammonia neutralizer',
            'type': 'danger'
        })
    elif ammonia > 0.2:
        advice_list.append({
            'priority': 'Medium',
            'icon': '🟡',
            'message': 'Moderate ammonia levels detected',
            'action': 'Reduce feeding by 50%, increase monitoring frequency to 4x daily',
            'type': 'warning'
        })
    else:
        advice_list.append({
            'priority': 'Low',
            'icon': '🟢',
            'message': 'Water quality is within acceptable range',
            'action': 'Continue regular monitoring and maintenance schedule',
            'type': 'success'
        })
    
    return advice_list

# Header
st.markdown('<p class="main-header">💧 Water Quality Monitoring with Ammonia Prediction</p>', unsafe_allow_html=True)
st.markdown("##### Real-time ML Analytics for Aquaculture Management")

# Sidebar
with st.sidebar:
    st.header("⚙️ Control Panel")
    
    # Real-time mode toggle
    st.markdown("---")
    st.subheader("🔌 Sensor Connection")
    real_time_toggle = st.toggle("Enable Real-time Mode", value=st.session_state.real_time_mode)
    st.session_state.real_time_mode = real_time_toggle
    
    if st.session_state.real_time_mode:
        st.success("✅ Live monitoring active")
        st.info("📡 Receiving data from ESP32 sensors")
    else:
        st.warning("⚠️ Manual input mode")
    
    st.markdown("---")
    
    # Data refresh
    if st.button("🔄 Refresh Data"):
        st.rerun()
    
    st.markdown("---")
    st.subheader("📊 Data Settings")
    show_raw_data = st.checkbox("Show raw data table", value=False)
    chart_points = st.slider("Chart history points", 20, 100, 50)

# Main content
col1, col2 = st.columns(2)

# Input Section
with col1:
    st.subheader("🧪 Enter Sensor Readings")
    
    if st.session_state.real_time_mode:
        # Simulate real-time sensor data
        ph_value = round(7.0 + np.random.randn() * 0.8, 2)
        temp_value = round(27.0 + np.random.randn() * 2.5, 2)
        st.info("📡 Auto-updating from sensors...")
    else:
        ph_value = 7.5
        temp_value = 28.0
    
    # pH Input
    st.markdown("##### pH Level")
    ph = st.slider(
        "pH",
        min_value=0.0,
        max_value=14.0,
        value=float(ph_value),
        step=0.1,
        disabled=st.session_state.real_time_mode,
        label_visibility="collapsed"
    )
    st.metric("Current pH", f"{ph:.2f}")
    
    # Temperature Input
    st.markdown("##### Temperature (Celsius)")
    temperature = st.slider(
        "Temperature",
        min_value=0.0,
        max_value=40.0,
        value=float(temp_value),
        step=0.1,
        disabled=st.session_state.real_time_mode,
        label_visibility="collapsed"
    )
    st.metric("Current Temperature", f"{temperature:.2f}°C")
    
    # Predict Button
    if st.button("🔍 Predict Ammonia Level", type="primary", use_container_width=True):
        with st.spinner("Analyzing water quality..."):
            time.sleep(0.5)
            prediction = predict_ammonia(ph, temperature)
            
            # Store prediction
            st.session_state.prediction_history.append({
                'timestamp': datetime.now(),
                'pH': ph,
                'temperature': temperature,
                'ammonia': prediction
            })
            
            # Add to historical data
            new_row = pd.DataFrame({
                'timestamp': [datetime.now()],
                'pH': [ph],
                'temperature': [temperature],
                'ammonia': [prediction]
            })
            st.session_state.historical_data = pd.concat([
                st.session_state.historical_data,
                new_row
            ]).tail(200).reset_index(drop=True)

# Prediction Result Section
with col2:
    st.subheader("🔬 Prediction Result")
    
    if len(st.session_state.prediction_history) > 0:
        latest_prediction = st.session_state.prediction_history[-1]
        ammonia_value = latest_prediction['ammonia']
        risk_level, risk_icon, risk_type = get_risk_level(ammonia_value)
        
        # Display prediction
        st.markdown(f"### {risk_icon} {ammonia_value:.4f} mg/L")
        st.markdown(f"**Risk Level:** {risk_level}")
        
        # Metrics
        col_a, col_b, col_c = st.columns(3)
        with col_a:
            st.metric("pH Input", f"{latest_prediction['pH']:.2f}")
        with col_b:
            st.metric("Temperature", f"{latest_prediction['temperature']:.2f}°C")
        with col_c:
            st.metric("Risk", risk_level)
        
        # Risk indicator
        if risk_type == "success":
            st.success(f"{risk_icon} Low risk - Water quality is safe")
        elif risk_type == "warning":
            st.warning(f"{risk_icon} Moderate risk - Monitor closely")
        else:
            st.error(f"{risk_icon} High risk - Immediate action required!")
    else:
        st.info("👆 Click 'Predict Ammonia Level' to get started")

# Prescriptive Analytics Section (Phase 6)
st.markdown("---")
st.header("📋 Prescriptive Recommendations")

if len(st.session_state.prediction_history) > 0:
    latest = st.session_state.prediction_history[-1]
    advice_list = get_prescriptive_advice(
        latest['pH'],
        latest['temperature'],
        latest['ammonia']
    )
    
    for advice in advice_list:
        box_class = f"{advice['type']}-box"
        st.markdown(f"""
        <div class="{box_class}">
            <h4>{advice['icon']} {advice['message']}</h4>
            <p><strong>Recommended Action:</strong> {advice['action']}</p>
        </div>
        """, unsafe_allow_html=True)
        st.markdown("<br>", unsafe_allow_html=True)

# Statistics Section
st.markdown("---")
st.header("📊 Water Quality Statistics")

if len(st.session_state.historical_data) > 0:
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        avg_ph = st.session_state.historical_data['pH'].mean()
        st.metric("Average pH", f"{avg_ph:.2f}")
    
    with col2:
        avg_temp = st.session_state.historical_data['temperature'].mean()
        st.metric("Average Temperature", f"{avg_temp:.2f}°C")
    
    with col3:
        avg_ammonia = st.session_state.historical_data['ammonia'].mean()
        st.metric("Average Ammonia", f"{avg_ammonia:.3f} mg/L")
    
    with col4:
        max_ammonia = st.session_state.historical_data['ammonia'].max()
        st.metric("Peak Ammonia", f"{max_ammonia:.3f} mg/L")

# Historical Trends Chart (Phase 5)
st.markdown("---")
st.header("📈 Historical Trends")

if len(st.session_state.historical_data) > 0:
    # Prepare data
    chart_data = st.session_state.historical_data.tail(chart_points).copy()
    
    # Multi-line chart
    fig = go.Figure()
    
    fig.add_trace(go.Scatter(
        x=chart_data['timestamp'],
        y=chart_data['pH'],
        mode='lines+markers',
        name='pH Level',
        line=dict(color='#3B82F6', width=2),
        marker=dict(size=4)
    ))
    
    fig.add_trace(go.Scatter(
        x=chart_data['timestamp'],
        y=chart_data['temperature'],
        mode='lines+markers',
        name='Temperature (°C)',
        line=dict(color='#F97316', width=2),
        marker=dict(size=4),
        yaxis='y2'
    ))
    
    fig.add_trace(go.Scatter(
        x=chart_data['timestamp'],
        y=chart_data['ammonia'],
        mode='lines+markers',
        name='Ammonia (mg/L)',
        line=dict(color='#8B5CF6', width=2),
        marker=dict(size=4),
        yaxis='y3'
    ))
    
    fig.update_layout(
        title="Water Quality Parameters Over Time",
        xaxis=dict(title="Time"),
        yaxis=dict(title="pH", titlefont=dict(color='#3B82F6'), tickfont=dict(color='#3B82F6')),
        yaxis2=dict(title="Temperature (°C)", titlefont=dict(color='#F97316'), tickfont=dict(color='#F97316'), overlaying='y', side='right'),
        yaxis3=dict(title="Ammonia (mg/L)", titlefont=dict(color='#8B5CF6'), tickfont=dict(color='#8B5CF6'), overlaying='y', side='right', position=0.95),
        hovermode='x unified',
        height=400
    )
    
    st.plotly_chart(fig, use_container_width=True)

# Ammonia Risk Timeline
st.markdown("---")
st.header("🎯 Ammonia Risk Timeline")

if len(st.session_state.historical_data) > 0:
    chart_data = st.session_state.historical_data.tail(chart_points).copy()
    
    fig = go.Figure()
    
    fig.add_trace(go.Scatter(
        x=chart_data['timestamp'],
        y=chart_data['ammonia'],
        mode='lines',
        name='Ammonia Level',
        fill='tozeroy',
        line=dict(color='#8B5CF6', width=2),
        fillcolor='rgba(139, 92, 246, 0.3)'
    ))
    
    # Add risk threshold lines
    fig.add_hline(y=0.2, line_dash="dash", line_color="yellow", annotation_text="Moderate Risk Threshold")
    fig.add_hline(y=0.4, line_dash="dash", line_color="red", annotation_text="High Risk Threshold")
    
    fig.update_layout(
        title="Ammonia Concentration Timeline",
        xaxis_title="Time",
        yaxis_title="Ammonia (mg/L)",
        hovermode='x unified',
        height=300
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    # Risk legend
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown("🟢 **Safe:** < 0.2 mg/L")
    with col2:
        st.markdown("🟡 **Moderate:** 0.2 - 0.4 mg/L")
    with col3:
        st.markdown("🔴 **High:** > 0.4 mg/L")

# Raw Data Table
if show_raw_data:
    st.markdown("---")
    st.header("📊 Raw Data Table")
    st.dataframe(
        st.session_state.historical_data.tail(50),
        use_container_width=True,
        hide_index=True
    )

# Footer
st.markdown("---")
st.markdown("""
    <div style='text-align: center; padding: 2rem; background-color: #1F2937; color: white; border-radius: 0.5rem;'>
        <p style='margin: 0; font-size: 0.9rem;'>🌊 Water Quality Monitoring System</p>
        <p style='margin: 0.5rem 0 0 0; font-size: 0.75rem; color: #9CA3AF;'>
            Powered by ESP32, Firebase & ML Analytics | Phase 5: Visualization ✓ | Phase 6: Prescriptive Analytics ✓
        </p>
    </div>
""", unsafe_allow_html=True)

# Auto-refresh for real-time mode
if st.session_state.real_time_mode:
    time.sleep(3)
    st.rerun()
