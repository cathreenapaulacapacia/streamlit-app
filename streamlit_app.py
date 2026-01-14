import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import time
import pickle
from scipy.linalg import pinv

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

# ELM PREDICTION FUNCTION (FOR ELM MODELS)
def ELM_predict(model, X_test):
    """Predicts using the trained ELM model."""
    H_test = model['activation'](np.dot(X_test, model['Win']) + model['B'])
    y_pred = np.dot(H_test, model['Beta'])
    return y_pred

# LOAD ACTUAL TRAINED ML MODEL
@st.cache_resource
def load_ml_model():
    """Load the trained ML model from pickle file."""
    try:
        with open('final_ml_model.pkl', 'rb') as f:
            model_info = pickle.load(f)
        return model_info
    except FileNotFoundError:
        st.error("❌ Model file 'final_ml_model.pkl' not found!")
        st.info("Please upload your trained model file to the same directory as this script.")
        return None
    except Exception as e:
        st.error(f"❌ Error loading model: {str(e)}")
        return None

# Load model at startup
model_info = load_ml_model()

# REAL ML PREDICTION FUNCTION
def predict_ammonia_real(ph, temperature):
    """
    Use the ACTUAL trained ML model to predict ammonia.
    This replaces the fake prediction function.
    """
    if model_info is None:
        st.error("Model not loaded. Cannot make predictions.")
        return 0.0
    
    try:
        # Get scaler and model
        scaler = model_info['scaler_X']
        model = model_info['model']
        
        # Prepare input data
        input_data = np.array([[ph, temperature]])
        input_scaled = scaler.transform(input_data)
        
        # Check if it's an ELM model or sklearn model
        if isinstance(model, dict) and 'Win' in model:
            # ELM Model
            prediction = ELM_predict(model, input_scaled)
            if prediction.ndim > 1:
                prediction = prediction.ravel()[0]
            else:
                prediction = float(prediction)
        else:
            # Random Forest or GBRT
            prediction = model.predict(input_scaled)[0]
        
        return max(0, float(prediction))  # Ensure non-negative
        
    except Exception as e:
        st.error(f"Prediction error: {str(e)}")
        return 0.0

# RISK ASSESSMENT FUNCTION
def get_risk_level(ammonia):
    """Classify ammonia risk level"""
    if ammonia < 0.2:
        return "Low", "🟢", "success"
    elif ammonia < 0.4:
        return "Moderate", "🟡", "warning"
    else:
        return "High", "🔴", "danger"

# PRESCRIPTIVE ANALYTICS FUNCTION
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

# INITIALIZE SESSION STATE
if 'historical_data' not in st.session_state:
    # Generate sample historical data (replace with Firebase data later)
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

# HEADER
st.markdown('<p class="main-header">💧 Taal Lake Water Quality Monitoring</p>', unsafe_allow_html=True)
st.markdown("##### Real-time ML Analytics for Aquaculture Management")

# Show model info
if model_info:
    model_type = "ELM" if isinstance(model_info['model'], dict) and 'Win' in model_info['model'] else type(model_info['model']).__name__
    st.success(f"✅ ML Model Loaded: **{model_type}**")
else:
    st.error("❌ ML Model not loaded. Please check 'final_ml_model.pkl' file.")

# SIDEBAR
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

# MAIN CONTENT
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
    st.metric("Current Temperature", f"{temperature:.2f} °C")
    
    # Predict Button
    if st.button("🔍 Predict Ammonia Level", type="primary", use_container_width=True):
        if model_info is None:
            st.error("Cannot predict: Model not loaded!")
        else:
            with st.spinner("Analyzing water quality with ML model..."):
                time.sleep(0.5)
                # USE REAL ML MODEL
                prediction = predict_ammonia_real(ph, temperature)
                
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
    st.subheader("🔬 ML Prediction Result")
    
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
            st.metric("Temperature", f"{latest_prediction['temperature']:.2f} °C")
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

# PRESCRIPTIVE ANALYTICS SECTION
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

# STATISTICS SECTION
st.markdown("---")
st.header("📊 Water Quality Statistics")

if len(st.session_state.historical_data) > 0:
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        avg_ph = st.session_state.historical_data['pH'].mean()
        st.metric("Average pH", f"{avg_ph:.2f}")
    
    with col2:
        avg_temp = st.session_state.historical_data['temperature'].mean()
        st.metric("Average Temp", f"{avg_temp:.2f} °C")
    
    with col3:
        avg_ammonia = st.session_state.historical_data['ammonia'].mean()
        st.metric("Average Ammonia", f"{avg_ammonia:.3f} mg/L")
    
    with col4:
        max_ammonia = st.session_state.historical_data['ammonia'].max()
        st.metric("Peak Ammonia", f"{max_ammonia:.3f} mg/L")

# HISTORICAL TRENDS CHART
st.markdown("---")
st.header("📈 Historical Trends")

if len(st.session_state.historical_data) > 0:
    # Prepare data
    chart_data = st.session_state.historical_data.tail(chart_points).copy()
    
    # Create tabs for different parameters
    tab1, tab2, tab3 = st.tabs(["All Parameters", "pH & Temperature", "Ammonia"])
    
    with tab1:
        # All parameters in one chart
        display_df = chart_data.set_index('timestamp')[['pH', 'temperature', 'ammonia']]
        st.line_chart(display_df, height=400)
    
    with tab2:
        # pH and Temperature
        display_df = chart_data.set_index('timestamp')[['pH', 'temperature']]
        st.line_chart(display_df, height=400)
    
    with tab3:
        # Ammonia only
        display_df = chart_data.set_index('timestamp')[['ammonia']]
        st.area_chart(display_df, height=400)

# AMMONIA RISK TIMELINE
st.markdown("---")
st.header("🎯 Ammonia Risk Timeline")

if len(st.session_state.historical_data) > 0:
    chart_data = st.session_state.historical_data.tail(chart_points).copy()
    
    # Area chart for ammonia
    display_df = chart_data.set_index('timestamp')[['ammonia']]
    st.area_chart(display_df, height=300, color='#8B5CF6')
    
    # Risk legend
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown("🟢 **Safe:** < 0.2 mg/L")
    with col2:
        st.markdown("🟡 **Moderate:** 0.2 - 0.4 mg/L")
    with col3:
        st.markdown("🔴 **High:** > 0.4 mg/L")

# RECENT PREDICTIONS TABLE
st.markdown("---")
st.header("🕐 Recent Predictions")

if len(st.session_state.prediction_history) > 0:
    recent_predictions = pd.DataFrame(st.session_state.prediction_history[-10:])
    recent_predictions['timestamp'] = recent_predictions['timestamp'].dt.strftime('%Y-%m-%d %H:%M:%S')
    recent_predictions['pH'] = recent_predictions['pH'].round(2)
    recent_predictions['temperature'] = recent_predictions['temperature'].round(2)
    recent_predictions['ammonia'] = recent_predictions['ammonia'].round(4)
    
    st.dataframe(
        recent_predictions,
        use_container_width=True,
        hide_index=True,
        column_config={
            "timestamp": "Time",
            "pH": "pH",
            "temperature": "Temp (°C)",
            "ammonia": "Ammonia (mg/L)"
        }
    )

# RAW DATA TABLE
if show_raw_data:
    st.markdown("---")
    st.header("📊 Raw Historical Data")
    display_data = st.session_state.historical_data.tail(50).copy()
    display_data['timestamp'] = display_data['timestamp'].dt.strftime('%Y-%m-%d %H:%M:%S')
    st.dataframe(
        display_data,
        use_container_width=True,
        hide_index=True
    )

# FOOTER
st.markdown("---")
st.markdown("""
    <div style='text-align: center; padding: 2rem; background-color: #1F2937; color: white; border-radius: 0.5rem;'>
        <p style='margin: 0; font-size: 0.9rem;'>🌊 Taal Lake Water Quality Monitoring System</p>
        <p style='margin: 0.5rem 0 0 0; font-size: 0.75rem; color: #9CA3AF;'>
            Powered by ESP32, Firebase & Real ML Model (RF/GBRT/ELM) | Using Trained Model ✓
        </p>
    </div>
""", unsafe_allow_html=True)

# Auto-refresh for real-time mode
if st.session_state.real_time_mode:
    time.sleep(3)
    st.rerun()
