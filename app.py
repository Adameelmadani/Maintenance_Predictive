"""
Main Streamlit Application Entry Point

Predictive Maintenance Platform - Cyberpunk-themed AI monitoring dashboard
for NASA C-MAPSS turbofan engine degradation simulation and analysis
"""

import streamlit as st
import pandas as pd
import numpy as np
from pathlib import Path
import joblib
from datetime import datetime

# Import custom modules
from src.data_loader import DataLoader
from src.simulation import DataStreamSimulator
from src.alerts import AlertManager
from src.models.model_utils import ModelUtils


# ============================================================================
# STREAMLIT PAGE CONFIGURATION
# ============================================================================

st.set_page_config(
    page_title="PredMaint AI | ENSAM Meknès",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded",
)


# ============================================================================
# GLOBAL CSS DESIGN SYSTEM (Cyberpunk Theme)
# ============================================================================

def inject_custom_css():
    """Inject custom CSS for cyberpunk theme throughout the app."""
    st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;700;900&family=Rajdhani:wght@300;400;600;700&display=swap');

    :root {
        --bg-primary: #0A0E1A;
        --bg-card: #0F1629;
        --bg-card2: #141B2D;
        --accent-cyan: #00D4FF;
        --accent-green: #00FF88;
        --accent-orange: #FF6B35;
        --accent-red: #FF3366;
        --accent-purple: #7B2FBE;
        --text-primary: #E8F4FD;
        --text-secondary: #8899AA;
        --border-glow: rgba(0, 212, 255, 0.3);
    }

    .stApp {
        background: var(--bg-primary);
        font-family: 'Rajdhani', sans-serif;
        color: var(--text-primary);
    }

    h1, h2, h3, h4, h5, h6 {
        font-family: 'Orbitron', monospace;
        color: var(--accent-cyan);
        text-shadow: 0 0 10px rgba(0, 212, 255, 0.5);
    }

    /* Metric cards with glow */
    .metric-card {
        background: var(--bg-card);
        border: 1px solid var(--border-glow);
        border-radius: 12px;
        padding: 20px;
        box-shadow: 0 0 20px rgba(0, 212, 255, 0.1), inset 0 1px 0 rgba(255,255,255,0.05);
        transition: all 0.3s ease;
    }

    .metric-card:hover {
        box-shadow: 0 0 35px rgba(0, 212, 255, 0.25);
        transform: translateY(-2px);
    }

    /* Status badges */
    .badge {
        border-radius: 20px;
        padding: 6px 16px;
        font-weight: 700;
        font-size: 0.9em;
        display: inline-block;
    }

    .badge-healthy {
        background: rgba(0,255,136,0.15);
        color: #00FF88;
        border: 1px solid #00FF88;
    }

    .badge-warning {
        background: rgba(255,107,53,0.15);
        color: #FF6B35;
        border: 1px solid #FF6B35;
    }

    .badge-critical {
        background: rgba(255,51,102,0.15);
        color: #FF3366;
        border: 1px solid #FF3366;
        animation: pulse 1.5s infinite;
    }

    @keyframes pulse {
        0%, 100% { opacity: 1; }
        50% { opacity: 0.5; }
    }

    /* Sidebar styling */
    [data-testid="stSidebar"] {
        background: var(--bg-card2) !important;
        border-right: 1px solid var(--border-glow);
    }

    /* Plot background */
    .js-plotly-plot .plotly .main-svg {
        background: transparent !important;
    }

    /* Input elements styling */
    .stTextInput > div > div > input,
    .stNumberInput > div > div > input,
    .stSelectbox > div > div,
    .stSlider > div > div > div {
        background-color: var(--bg-card) !important;
        color: var(--text-primary) !important;
        border-color: var(--border-glow) !important;
    }

    /* Button styling */
    .stButton > button {
        background: linear-gradient(135deg, var(--accent-cyan), var(--accent-purple));
        color: var(--bg-primary) !important;
        font-weight: 700;
        border: none;
        border-radius: 8px;
        transition: all 0.3s ease;
    }

    .stButton > button:hover {
        box-shadow: 0 0 20px rgba(0, 212, 255, 0.6);
        transform: scale(1.05);
    }

    /* Expander styling */
    .streamlit-expanderHeader {
        background-color: var(--bg-card) !important;
        border: 1px solid var(--border-glow) !important;
    }

    /* Dataframe styling */
    .dataframe {
        background-color: var(--bg-card) !important;
    }

    .dataframe th {
        background-color: var(--bg-card2) !important;
        color: var(--accent-cyan) !important;
    }

    /* Alerts */
    .streamlit-info {
        background-color: rgba(0, 212, 255, 0.1) !important;
        border-color: var(--accent-cyan) !important;
    }

    .streamlit-warning {
        background-color: rgba(255, 107, 53, 0.1) !important;
        border-color: var(--accent-orange) !important;
    }

    .streamlit-error {
        background-color: rgba(255, 51, 102, 0.1) !important;
        border-color: var(--accent-red) !important;
    }
    </style>
    """, unsafe_allow_html=True)


# ============================================================================
# CACHING FUNCTIONS
# ============================================================================

@st.cache_resource
def load_all_models():
    """Load all trained models from disk."""
    models_dir = Path('models')
    models = {}
    
    rul_models = ['huber', 'decisiontree', 'mlp', 'randomforest', 'xgboost']
    for model_name in rul_models:
        path = models_dir / f'rul_{model_name}.pkl'
        if path.exists():
            models[model_name.replace('decisiontree', 'DecisionTree')
                           .replace('randomforest', 'RandomForest')
                           .replace('xgboost', 'XGBoost')
                           .replace('mlp', 'MLP')
                           .replace('huber', 'Huber')] = joblib.load(path)
    
    cls_models = ['randomforest', 'svm']
    for model_name in cls_models:
        path = models_dir / f'cls_{model_name}.pkl'
        if path.exists():
            display_name = 'RandomForest' if model_name == 'randomforest' else 'SVM'
            models[f'cls_{display_name}'] = joblib.load(path)
    
    return models


@st.cache_data
def load_processed_data():
    """Load preprocessed datasets."""
    data_dir = Path('data/processed')
    
    X_train = np.load(data_dir / 'X_train.npy')
    X_test = np.load(data_dir / 'X_test.npy')
    y_rul_train = np.load(data_dir / 'y_rul_train.npy')
    y_rul_test = np.load(data_dir / 'y_rul_test.npy')
    y_cls_train = np.load(data_dir / 'y_cls_train.npy')
    
    df_train = pd.read_csv(data_dir / 'train_processed.csv')
    df_test = pd.read_csv(data_dir / 'test_processed.csv')
    
    return {
        'X_train': X_train,
        'X_test': X_test,
        'y_rul_train': y_rul_train,
        'y_rul_test': y_rul_test,
        'y_cls_train': y_cls_train,
        'df_train': df_train,
        'df_test': df_test
    }


@st.cache_data
def load_benchmark_results():
    """Load model benchmark results."""
    try:
        with open('models/benchmark_results.json', 'r') as f:
            import json
            return json.load(f)
    except:
        return None


# ============================================================================
# SESSION STATE INITIALIZATION
# ============================================================================

def initialize_session_state():
    """Initialize all session state variables."""
    # Data and models
    if 'models' not in st.session_state:
        st.session_state.models = load_all_models()
    
    if 'data' not in st.session_state:
        st.session_state.data = load_processed_data()
    
    if 'benchmark_results' not in st.session_state:
        st.session_state.benchmark_results = load_benchmark_results()
    
    # Simulator and alerts
    if 'simulator' not in st.session_state:
        st.session_state.simulator = None
    
    if 'alert_manager' not in st.session_state:
        st.session_state.alert_manager = AlertManager()
    
    # UI state
    if 'active_model_name' not in st.session_state:
        st.session_state.active_model_name = 'XGBoost'
    
    if 'current_engine' not in st.session_state:
        st.session_state.current_engine = 1
    
    if 'simulation_running' not in st.session_state:
        st.session_state.simulation_running = False
    
    if 'cycle_index' not in st.session_state:
        st.session_state.cycle_index = 0


# ============================================================================
# MAIN APP
# ============================================================================

def main():
    """Main Streamlit application."""
    
    # Inject custom CSS
    inject_custom_css()
    
    # Initialize session state
    initialize_session_state()
    
    # Sidebar configuration
    with st.sidebar:
        st.markdown("### ⚡ PREDICTIVE MAINTENANCE")
        st.markdown("**Platform: NASA C-MAPSS Turbofan**")
        st.markdown("**Version: 1.0**")
        st.markdown("**ENSAM Meknès - 4ème Année IA**")
        st.divider()
        
        # Global controls
        st.markdown("#### 🎮 Global Controls")
        
        st.session_state.current_engine = st.selectbox(
            "Select Engine ID",
            range(1, 101),
            index=st.session_state.current_engine - 1,
            help="Choose which engine to monitor"
        )
        
        st.session_state.active_model_name = st.selectbox(
            "Active RUL Model",
            ['Huber', 'DecisionTree', 'MLP', 'RandomForest', 'XGBoost'],
            index=['Huber', 'DecisionTree', 'MLP', 'RandomForest', 'XGBoost'].index(st.session_state.active_model_name),
            help="Select primary RUL prediction model"
        )
        
        st.divider()
        st.markdown("#### 📊 Platform Info")
        st.markdown(f"**Last Refresh:** {datetime.now().strftime('%H:%M:%S')}")
        st.markdown(f"**Models Loaded:** {len(st.session_state.models)}")
        st.markdown(f"**Alerts Count:** {len(st.session_state.alert_manager.log)}")
        
        st.divider()
        st.markdown("#### 📖 Navigation")
        st.markdown("""
        Use the page selector above to navigate:
        - 🏠 **Overview** - Mission Control dashboard
        - 📡 **Monitoring** - Signal analysis & FFT
        - 🧪 **IA Lab** - Model benchmarks
        - 🔮 **Pronostic** - RUL prediction
        - 📋 **Log** - Maintenance events
        """)
    
    # Main content area
    st.markdown("# ⚡ PREDICTIVE MAINTENANCE PLATFORM")
    st.markdown("**NASA C-MAPSS Turbofan Engine | Real-Time AI Monitoring**")
    st.divider()
    
    # Display platform status
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("🟢 Models Ready", len(st.session_state.models))
    
    with col2:
        st.metric("📊 Data Samples", len(st.session_state.data['X_test']))
    
    with col3:
        active_alerts = len(st.session_state.alert_manager.get_active_alerts('WARNING'))
        st.metric("⚠️  Active Alerts", active_alerts)
    
    with col4:
        st.metric("🔧 Active Engine", st.session_state.current_engine)
    
    st.divider()
    
    st.info("👈 **Use the sidebar to navigate pages and select your active engine and model. Each page offers different insights into the predictive maintenance system.**")


if __name__ == "__main__":
    main()
