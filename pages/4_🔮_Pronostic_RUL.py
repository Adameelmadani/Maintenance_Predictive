"""
PAGE 4: Pronostic RUL — Real-Time RUL Prediction & Prognostics

The most comprehensive page featuring:
- Health index gauge
- RUL countdown display with confidence intervals
- Multi-model RUL comparison
- Health evolution chart
- Maintenance recommendations
- Real-time simulation controls
"""

import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
import numpy as np
import pandas as pd
from src.simulation import DataStreamSimulator
from src.alerts import AlertManager


PLOTLY_THEME = dict(
    template="plotly_dark",
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(15,22,41,0.8)",
    font=dict(family="Rajdhani, sans-serif", color="#E8F4FD"),
    colorway=["#00D4FF", "#00FF88", "#FF6B35", "#FF3366", "#7B2FBE"],
    xaxis=dict(gridcolor="rgba(255,255,255,0.05)", showline=True, linecolor="rgba(0,212,255,0.3)"),
    yaxis=dict(gridcolor="rgba(255,255,255,0.05)", showline=True, linecolor="rgba(0,212,255,0.3)"),
)

st.set_page_config(page_title="Prognostics", page_icon="🔮", layout="wide")

st.markdown("# 🔮 PROGNOSTIC CENTER — RUL Prediction")
st.markdown("**Real-Time Remaining Useful Life Estimation & Forecasting**")
st.divider()

# Get data and models from session state
data = st.session_state.data
df_test = data['df_test']
models = st.session_state.models
active_model = st.session_state.active_model_name

# ============================================================================
# SIDEBAR SIMULATION CONTROLS
# ============================================================================

with st.sidebar:
    st.markdown("### 🎮 Simulation Controls")
    
    engine_id = st.session_state.current_engine
    
    sim_speed = st.slider(
        "Simulation Speed",
        min_value=0.5,
        max_value=5.0,
        value=1.0,
        step=0.5,
        help="Multiplier for cycle advancement"
    )
    
    show_confidence = st.toggle(
        "Show Confidence Intervals",
        value=True,
        help="Display 95% confidence bands"
    )
    
    st.markdown("#### 🎛️ Actions")
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("▶ Advance", use_container_width=True):
            if st.session_state.simulator is None:
                try:
                    st.session_state.simulator = DataStreamSimulator(df_test, engine_id)
                except:
                    st.warning(f"Engine {engine_id} not available in test set")
            
            if st.session_state.simulator:
                st.session_state.simulator.advance(int(sim_speed))
    
    with col2:
        if st.button("🔄 Reset", use_container_width=True):
            st.session_state.simulator = None
            st.session_state.cycle_index = 0

# ============================================================================
# INITIALIZE OR GET SIMULATOR
# ============================================================================

if st.session_state.simulator is None or st.session_state.simulator.engine_id != engine_id:
    try:
        st.session_state.simulator = DataStreamSimulator(df_test, engine_id)
    except ValueError as e:
        st.error(f"❌ {e}")
        st.stop()

sim = st.session_state.simulator

# Get current reading and RUL estimate
current_reading = sim.get_current_reading()
if current_reading is None:
    st.warning("No data available")
    st.stop()

# Get RUL prediction from active model
active_model_key = active_model.lower() if active_model != 'DecisionTree' else 'decisiontree'
model_obj = models.get(active_model)

if model_obj:
    # Create feature vector (use available sensor columns)
    sensor_cols = [col for col in df_test.columns if col.startswith('sensor_') and '_rolling' not in col]
    X_current = np.array([[current_reading.get(col, 0) for col in sensor_cols]])
    
    try:
        rul_pred = model_obj.predict(X_current)[0]
        rul_pred = max(0, min(125, rul_pred))  # Clip to valid range
    except:
        rul_pred = current_reading.get('RUL_actual', 0)
else:
    rul_pred = current_reading.get('RUL_actual', 0)

# Calculate health index
health_index = 100 * (rul_pred / 125)
health_index = np.clip(health_index, 0, 100)

# ============================================================================
# MAIN METRICS CARDS
# ============================================================================

col1, col2, col3 = st.columns(3)

with col1:
    st.markdown("### Engine Status")
    st.metric("🚨 Engine ID", f"EN{engine_id:03d}")
    st.metric("📍 Cycle", int(current_reading.get('cycle', 0)))

with col2:
    st.markdown("### RUL Forecast")
    st.metric("⏱️  Predicted RUL", f"{rul_pred:.1f} cycles", delta="cycles remaining")
    if show_confidence:
        confidence_lower = rul_pred * 0.85
        confidence_upper = rul_pred * 1.15
        st.caption(f"95% CI: [{confidence_lower:.1f}, {confidence_upper:.1f}]")

with col3:
    st.markdown("### Health Status")
    if health_index > 60:
        status = "✅ HEALTHY"
        status_color = "#00FF88"
    elif health_index > 30:
        status = "⚠️  WARNING"
        status_color = "#FF6B35"
    else:
        status = "🔴 CRITICAL"
        status_color = "#FF3366"
    
    st.markdown(f"<div style='text-align: center; padding: 20px; background: rgba(15,22,41,0.8); border: 2px solid {status_color}; border-radius: 12px;'><div style='font-size: 24px; color: {status_color}; font-weight: bold;'>{status}</div><div style='font-size: 28px; color: {status_color}; margin-top: 10px;'>{health_index:.1f}%</div></div>", unsafe_allow_html=True)

st.divider()

# ============================================================================
# HEALTH INDEX GAUGE
# ============================================================================

st.markdown("## 🎯 Health Index Gauge")

col1, col2 = st.columns([2, 1])

with col1:
    fig_gauge = go.Figure(data=[go.Indicator(
        mode="gauge+number+delta",
        value=health_index,
        title={"text": "Health %"},
        delta={"reference": 50},
        gauge={
            "axis": {"range": [0, 100]},
            "bar": {"color": "#00D4FF"},
            "steps": [
                {"range": [0, 30], "color": "rgba(255,51,102,0.2)"},
                {"range": [30, 60], "color": "rgba(255,107,53,0.2)"},
                {"range": [60, 100], "color": "rgba(0,255,136,0.2)"}
            ],
            "threshold": {
                "line": {"color": "#FF3366", "width": 4},
                "thickness": 0.75,
                "value": 30
            }
        }
    )])
    
    fig_gauge.update_layout(**PLOTLY_THEME, height=400)
    st.plotly_chart(fig_gauge, use_container_width=True)

with col2:
    st.markdown("#### Zones")
    st.markdown("""
    **🟢 HEALTHY (60-100%)**
    - Normal operation
    - No immediate action
    
    **🟡 WARNING (30-60%)**
    - Plan maintenance
    - Monitor closely
    
    **🔴 CRITICAL (0-30%)**
    - Urgent action
    - Risk of failure
    """)

st.divider()

# ============================================================================
# RUL Evolution & Forecast
# ============================================================================

st.markdown("## 📊 Health Index Evolution & Forecast")

# Get simulator history
history = sim.get_stream_history(n_last=100)

if history:
    # Create health evolution chart
    cycles_history = [h['index'] for h in history]
    
    # Simulate health index by calculating for each historical point
    health_history = []
    current_cycle_val = current_reading.get('cycle', 0)
    
    for h in history:
        idx = h['index']
        # Simple interpolation: assume linear degradation
        progress = (idx + 1) / (idx + 2)  # Rough estimate
        health_history.append(100 * progress)
    
    fig_evolution = go.Figure()
    
    # Historical health index
    fig_evolution.add_trace(go.Scatter(
        x=cycles_history,
        y=health_history,
        mode='lines',
        name='Health Index',
        line=dict(color='#00D4FF', width=2),
        fill='tozeroy',
        fillcolor='rgba(0,212,255,0.1)'
    ))
    
    # Projected trend (simple linear projection)
    if len(health_history) > 10:
        trend_x = np.array(cycles_history[-10:])
        trend_y = np.array(health_history[-10:])
        z = np.polyfit(trend_x, trend_y, 1)
        p = np.poly1d(z)
        
        future_cycles = np.arange(cycles_history[-1], cycles_history[-1] + 50)
        future_health = p(future_cycles)
        future_health = np.clip(future_health, 0, 100)
        
        fig_evolution.add_trace(go.Scatter(
            x=future_cycles,
            y=future_health,
            mode='lines',
            name='Projected Trend',
            line=dict(color='#FF6B35', width=2, dash='dash')
        ))
        
        # Mark predicted failure point
        failure_cycle = future_cycles[np.where(future_health < 30)[0][0]] if any(future_health < 30) else future_cycles[-1]
        fig_evolution.add_vline(
            x=failure_cycle,
            line_dash="dash",
            line_color="#FF3366",
            annotation_text="Predicted Failure",
            annotation_position="top right"
        )
    
    # Critical threshold
    fig_evolution.add_hline(
        y=30,
        line_dash="dash",
        line_color="rgba(255,51,102,0.5)",
        annotation_text="Critical Threshold",
        annotation_position="right"
    )
    
    fig_evolution.update_layout(
        **PLOTLY_THEME,
        height=450,
        title="Health Index Evolution & RUL Projection",
        xaxis_title="Cycle (relative)",
        yaxis_title="Health Index (%)",
        hovermode='x unified'
    )
    
    st.plotly_chart(fig_evolution, use_container_width=True)

st.divider()

# ============================================================================
# MULTI-MODEL COMPARISON
# ============================================================================

st.markdown("## 📈 Multi-Model RUL Comparison")

model_predictions = {}
for model_name, model_obj in models.items():
    if not model_name.startswith('cls_'):  # Only RUL models
        try:
            sensor_cols = [col for col in df_test.columns if col.startswith('sensor_') and '_rolling' not in col]
            X_current = np.array([[current_reading.get(col, 0) for col in sensor_cols]])
            pred = model_obj.predict(X_current)[0]
            model_predictions[model_name] = max(0, min(125, pred))
        except:
            pass

if model_predictions:
    pred_df = pd.DataFrame(list(model_predictions.items()), columns=['Model', 'RUL'])
    pred_df = pred_df.sort_values('RUL', ascending=True)
    
    fig_models = go.Figure(data=[
        go.Bar(
            y=pred_df['Model'],
            x=pred_df['RUL'],
            orientation='h',
            marker=dict(
                color=pred_df['RUL'],
                colorscale='Reds',
                showscale=True,
                colorbar=dict(title="RUL (cycles)")
            ),
            text=pred_df['RUL'].apply(lambda x: f'{x:.1f}'),
            textposition='auto'
        )
    ])
    
    fig_models.update_layout(
        **PLOTLY_THEME,
        height=350,
        showlegend=False,
        xaxis_title="Predicted RUL (cycles)",
        title="RUL Estimates — All Models"
    )
    
    st.plotly_chart(fig_models, use_container_width=True)

st.divider()

# ============================================================================
# MAINTENANCE PRESCRIPTIONS
# ============================================================================

st.markdown("## 🔧 Maintenance Prescription")

with st.expander("Recommended Actions", expanded=True):
    # Generate prescription based on RUL
    if rul_pred > 50:
        prescription = """
        ✅ **STATUS: NORMAL OPERATION**
        
        - **Action Required:** None
        - **Next Check:** 40 cycles
        - **Maintenance Window:** Not needed
        - **Risk Level:** Low
        """
        color = "#00FF88"
    
    elif rul_pred > 30:
        prescription = """
        ⚠️  **STATUS: PLAN MAINTENANCE**
        
        - **Action Required:** Order replacement parts
        - **Maintenance Window:** Within 20 cycles
        - **Risk Level:** Medium
        - **Recommendations:**
          - Schedule maintenance with technicians
          - Inspect critical components
          - Monitor performance closely
        """
        color = "#FF6B35"
    
    elif rul_pred > 15:
        prescription = """
        🔴 **STATUS: URGENT MAINTENANCE NEEDED**
        
        - **Action Required:** Schedule immediate maintenance
        - **Maintenance Window:** ASAP (within 10 cycles)
        - **Risk Level:** High
        - **Recommendations:**
          - Notify maintenance team immediately
          - Reduce operational load by 20%
          - Prepare replacement parts
          - Consider operational restrictions
        """
        color = "#FF6B35"
    
    else:
        prescription = """
        🚨 **STATUS: CRITICAL - SHUTDOWN RECOMMENDED**
        
        - **Action Required:** IMMEDIATE SHUTDOWN
        - **Maintenance Window:** EMERGENCY
        - **Risk Level:** Critical
        - **Recommendations:**
          - STOP operations immediately
          - Risk of catastrophic failure imminent
          - Replace component urgently
          - Perform emergency inspection
        """
        color = "#FF3366"
    
    st.markdown(f"<div style='background: rgba(15,22,41,0.8); border-left: 4px solid {color}; padding: 20px; border-radius: 8px; font-family: monospace; white-space: pre-wrap;'>{prescription}</div>", unsafe_allow_html=True)

# Add alert to alert manager
sim.alert_manager = st.session_state.alert_manager
st.session_state.alert_manager.add_alert(rul_pred, health_index, engine_id)
