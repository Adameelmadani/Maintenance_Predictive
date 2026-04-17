"""
PAGE 2: Monitoring Signal — Sensor Data Analysis & FFT Spectrum

Displays raw signal analysis, rolling statistics, FFT spectrum, and sensor heatmaps
for detailed sensor-level monitoring and anomaly detection.
"""

import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
import numpy as np
import pandas as pd
from src.feature_engineering import FeatureEngineer


PLOTLY_THEME = dict(
    template="plotly_dark",
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(15,22,41,0.8)",
    font=dict(family="Rajdhani, sans-serif", color="#E8F4FD"),
    colorway=["#00D4FF", "#00FF88", "#FF6B35", "#FF3366", "#7B2FBE"],
    xaxis=dict(gridcolor="rgba(255,255,255,0.05)", showline=True, linecolor="rgba(0,212,255,0.3)"),
    yaxis=dict(gridcolor="rgba(255,255,255,0.05)", showline=True, linecolor="rgba(0,212,255,0.3)"),
)

st.set_page_config(page_title="Signal Monitoring", page_icon="📡", layout="wide")

st.markdown("# 📡 SIGNAL MONITORING & ANALYSIS")
st.markdown("**Sensor Data Visualization | FFT Analysis | Anomaly Detection**")
st.divider()

# Get data from session state
data = st.session_state.data
df_test = data['df_test']

# Get list of remaining sensors
sensor_cols = [col for col in df_test.columns if col.startswith('sensor_') and '_rolling' not in col]

# ============================================================================
# SIDEBAR CONTROLS
# ============================================================================

with st.sidebar:
    st.markdown("### 📡 Sensor Analysis Controls")
    
    selected_engine = st.selectbox(
        "Select Engine",
        sorted(df_test['engine_id'].unique()),
        help="Choose which engine to analyze"
    )
    
    selected_sensor = st.selectbox(
        "Select Sensor",
        sensor_cols,
        help="Choose sensor to analyze"
    )
    
    window_size = st.slider(
        "Rolling Window (cycles)",
        min_value=5,
        max_value=50,
        value=30,
        step=5
    )
    
    live_mode = st.toggle(
        "Live Simulation Mode",
        value=False,
        help="Enable real-time data streaming"
    )

# ============================================================================
# GET ENGINE DATA
# ============================================================================

engine_data = df_test[df_test['engine_id'] == selected_engine].copy()

if len(engine_data) == 0:
    st.error(f"Engine {selected_engine} not found in test set")
    st.stop()

st.success(f"Engine {selected_engine} - {len(engine_data)} operational cycles")

# ============================================================================
# RAW SIGNAL + ROLLING ANALYTICS
# ============================================================================

st.markdown("## 📊 Raw Sensor Signal & Analysis")

if selected_sensor in engine_data.columns:
    signal = engine_data[selected_sensor].values
    cycles = engine_data['cycle'].values
    
    # Calculate rolling statistics
    df_temp = pd.DataFrame({'signal': signal})
    df_temp['rolling_mean'] = df_temp['signal'].rolling(window=window_size, min_periods=1).mean()
    df_temp['rolling_std'] = df_temp['signal'].rolling(window=window_size, min_periods=1).std().fillna(0)
    df_temp['upper_bound'] = df_temp['rolling_mean'] + df_temp['rolling_std']
    df_temp['lower_bound'] = df_temp['rolling_mean'] - df_temp['rolling_std']
    
    # Create signal plot
    fig_signal = go.Figure()
    
    # Raw signal
    fig_signal.add_trace(go.Scatter(
        x=cycles,
        y=signal,
        mode='lines',
        name='Raw Signal',
        line=dict(color='#00D4FF', width=1, dash='solid'),
        opacity=0.7
    ))
    
    # Rolling mean
    fig_signal.add_trace(go.Scatter(
        x=cycles,
        y=df_temp['rolling_mean'],
        mode='lines',
        name=f'Rolling Mean ({window_size})',
        line=dict(color='#00FF88', width=2, dash='dash')
    ))
    
    # Confidence band
    fig_signal.add_trace(go.Scatter(
        x=np.concatenate([cycles, cycles[::-1]]),
        y=np.concatenate([df_temp['upper_bound'], df_temp['lower_bound'][::-1]]),
        fill='toself',
        name='±1 Std Dev',
        fillcolor='rgba(123,47,190,0.2)',
        line=dict(color='rgba(255,255,255,0)'),
        showlegend=True
    ))
    
    # RUL threshold line (if available)
    if 'RUL' in engine_data.columns:
        rul_threshold_cycle = engine_data[engine_data['RUL'] <= 30]['cycle'].min()
        if not pd.isna(rul_threshold_cycle):
            fig_signal.add_vline(
                x=rul_threshold_cycle,
                line_dash="dash",
                line_color="#FF3366",
                annotation_text="RUL=30 Threshold",
                annotation_position="top right"
            )
    
    fig_signal.update_layout(
        **PLOTLY_THEME,
        height=400,
        title=f"Signal: {selected_sensor} (Engine {selected_engine})",
        xaxis_title="Cycle",
        yaxis_title="Normalized Value",
        hovermode='x unified'
    )
    
    st.plotly_chart(fig_signal, use_container_width=True)

# ============================================================================
# STATISTICAL INDICATORS
# ============================================================================

st.markdown("## 📈 Statistical Indicators")

if selected_sensor in engine_data.columns:
    from scipy import stats
    
    signal = engine_data[selected_sensor].values
    
    # Current cycle stats
    current_value = signal[-1]
    prev_10_mean = signal[-11:-1].mean() if len(signal) > 10 else signal.mean()
    prev_10_std = signal[-11:-1].std() if len(signal) > 10 else signal.std()
    
    # Statistical metrics
    rms = np.sqrt(np.mean(signal ** 2))
    kurtosis = stats.kurtosis(signal)
    p2p = np.ptp(signal)
    skewness = stats.skew(signal)
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        delta_val = current_value - prev_10_mean
        st.metric(
            "RMS",
            f"{rms:.3f}",
            delta=f"{delta_val:.4f}",
            delta_color="inverse"
        )
    
    with col2:
        kurtosis_interpretation = "Heavy Tails ⚠️" if kurtosis > 3 else "Normal"
        st.metric(
            "Kurtosis",
            f"{kurtosis:.2f}",
            delta=kurtosis_interpretation
        )
    
    with col3:
        st.metric(
            "Peak-to-Peak",
            f"{p2p:.3f}"
        )
    
    with col4:
        st.metric(
            "Skewness",
            f"{skewness:.3f}"
        )

st.divider()

# ============================================================================
# FFT SPECTRUM ANALYSIS
# ============================================================================

st.markdown("## 🔬 FFT Frequency Domain Analysis")

if selected_sensor in engine_data.columns:
    signal = engine_data[selected_sensor].values
    signal = signal[~np.isnan(signal)]
    
    # Compute FFT
    feature_eng = FeatureEngineer()
    fft_result = feature_eng.compute_fft_spectrum(signal, fs=1.0, n_freq=10)
    
    # Create FFT plot
    fig_fft = go.Figure(data=[
        go.Bar(
            x=fft_result['frequencies'],
            y=fft_result['amplitudes'],
            marker=dict(
                color=fft_result['amplitudes'],
                colorscale='Viridis',
                showscale=True
            ),
            name='Amplitude'
        )
    ])
    
    fig_fft.update_layout(
        **PLOTLY_THEME,
        height=400,
        title=f"FFT Spectrum: {selected_sensor}",
        xaxis_title="Frequency (Hz)",
        yaxis_title="Magnitude",
        showlegend=False
    )
    
    st.plotly_chart(fig_fft, use_container_width=True)
    
    # Display top frequencies
    st.markdown("#### Top Dominant Frequencies")
    freq_df = pd.DataFrame({
        'Frequency (Hz)': fft_result['top_freqs'],
        'Amplitude': fft_result['top_amps']
    })
    st.dataframe(freq_df, use_container_width=True, hide_index=True)
    
    if fft_result['dominant_freq'] > 0:
        st.info(f"🎯 **Dominant Frequency:** {fft_result['dominant_freq']:.2f} Hz")

st.divider()

# ============================================================================
# MULTI-SENSOR HEATMAP
# ============================================================================

st.markdown("## 🔥 Sensor Correlation Heatmap (Last 50 Cycles)")

# Get last 50 cycles
last_50 = engine_data.tail(50).copy()

# Extract sensor data
heatmap_data = last_50[sensor_cols].T

fig_heatmap = go.Figure(data=go.Heatmap(
    z=heatmap_data.values,
    x=list(range(heatmap_data.shape[1])),
    y=heatmap_data.index,
    colorscale='Viridis',
    colorbar=dict(title='Normalized Value')
))

fig_heatmap.update_layout(
    **PLOTLY_THEME,
    height=400,
    title=f"Sensor Values Heatmap - Engine {selected_engine} (Last 50 Cycles)",
    xaxis_title="Cycle (relative)",
    yaxis_title="Sensor"
)

st.plotly_chart(fig_heatmap, use_container_width=True)
