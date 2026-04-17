"""
PAGE 1: Overview — Mission Control Dashboard

Shows fleet-wide status, KPIs, health gauge, and recent alerts.
Real-time visualization of engine health across the entire fleet.
"""

import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
import numpy as np
import pandas as pd


PLOTLY_THEME = dict(
    template="plotly_dark",
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(15,22,41,0.8)",
    font=dict(family="Rajdhani, sans-serif", color="#E8F4FD"),
    colorway=["#00D4FF", "#00FF88", "#FF6B35", "#FF3366", "#7B2FBE"],
    xaxis=dict(gridcolor="rgba(255,255,255,0.05)", showline=True, linecolor="rgba(0,212,255,0.3)"),
    yaxis=dict(gridcolor="rgba(255,255,255,0.05)", showline=True, linecolor="rgba(0,212,255,0.3)"),
)


st.set_page_config(page_title="Mission Control", page_icon="🏠", layout="wide")

st.markdown("# 🏠 MISSION CONTROL")
st.markdown("**Fleet Status Dashboard — Real-Time Engine Monitoring**")
st.divider()

# Get data from session state
data = st.session_state.data
models = st.session_state.models
alert_manager = st.session_state.alert_manager

# Get test data with RUL labels
df_test = data['df_test']
y_rul_test = data['y_rul_test']

# Get all engine IDs from test set
engine_ids = sorted(df_test['engine_id'].unique())[:5]  # Show first 5 engines

# ============================================================================
# KPI METRICS ROW
# ============================================================================

# Calculate fleet statistics
fleet_ruls = []
for engine_id in engine_ids:
    engine_data = df_test[df_test['engine_id'] == engine_id]
    if len(engine_data) > 0:
        # Get last RUL for this engine
        last_rul = engine_data.iloc[-1]['RUL']
        fleet_ruls.append(last_rul)

if fleet_ruls:
    avg_health = 100 * (np.mean(fleet_ruls) / 125)  # Normalized to max clip value
    min_rul = min(fleet_ruls)
    critical_count = sum(1 for rul in fleet_ruls if rul <= 30)
else:
    avg_health = 100
    min_rul = 0
    critical_count = 0

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric(
        "🟢 Fleet Health",
        f"{avg_health:.1f}%",
        delta=f"{avg_health - 50:.1f}%" if avg_health > 50 else None,
        delta_color="normal" if avg_health > 50 else "inverse"
    )

with col2:
    st.metric(
        "⏱️  Minimum RUL",
        f"{min_rul:.0f}",
        delta="CRITICAL" if min_rul < 30 else "WARNING" if min_rul < 50 else "OK"
    )

with col3:
    st.metric(
        "⚠️  Engines in Zone",
        critical_count,
        delta="RUL ≤ 30" if critical_count > 0 else "All Safe"
    )

with col4:
    active_alerts = len(alert_manager.get_active_alerts('WARNING'))
    st.metric(
        "🔔 Active Alerts",
        active_alerts,
        delta="High Priority" if active_alerts > 2 else "Normal"
    )

st.divider()

# ============================================================================
# FLEET STATUS CIRCLES (Engine Health)
# ============================================================================

st.markdown("## 🚨 Fleet Health Status")

cols = st.columns(5)
for idx, engine_id in enumerate(engine_ids):
    with cols[idx]:
        engine_data = df_test[df_test['engine_id'] == engine_id]
        
        if len(engine_data) > 0:
            last_rul = engine_data.iloc[-1]['RUL']
            
            # Determine status
            if last_rul > 50:
                status = "🟢 HEALTHY"
                color = "#00FF88"
            elif last_rul > 30:
                status = "🟡 WARNING"
                color = "#FF6B35"
            else:
                status = "🔴 CRITICAL"
                color = "#FF3366"
            
            # Display as HTML circle
            st.markdown(f"""
            <div style='text-align: center; padding: 20px; background: rgba(15,22,41,0.8); 
                        border: 2px solid {color}; border-radius: 20px; margin: 10px 0;'>
                <div style='font-size: 28px; font-weight: bold; color: {color};'>EN{engine_id:03d}</div>
                <div style='font-size: 32px; margin: 10px 0;'>●</div>
                <div style='font-size: 14px; color: #E8F4FD;'>{status}</div>
                <div style='font-size: 18px; color: {color}; font-weight: bold; margin-top: 10px;'>
                    RUL: {last_rul:.1f} cycles
                </div>
            </div>
            """, unsafe_allow_html=True)

st.divider()

# ============================================================================
# HEALTH GAUGE CHART
# ============================================================================

col1, col2 = st.columns([2, 1])

with col1:
    st.markdown("### Fleet Health Index Gauge")
    
    # Create gauge chart
    fig_gauge = go.Figure(data=[go.Indicator(
        mode="gauge+number+delta",
        value=avg_health,
        title={"text": "Fleet Health %"},
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
    st.markdown("### Status Legend")
    st.markdown("""
    #### 🟢 Healthy (60-100%)
    - RUL > 50 cycles
    - Normal operation
    - No action needed
    
    #### 🟡 Warning (30-60%)
    - 30 < RUL ≤ 50
    - Plan maintenance
    - Monitor closely
    
    #### 🔴 Critical (0-30%)
    - RUL ≤ 30 cycles
    - Urgent action needed
    - Schedule immediately
    """)

st.divider()

# ============================================================================
# RUL DISTRIBUTION
# ============================================================================

st.markdown("### 📊 RUL Distribution by Engine")

rul_data = []
for engine_id in engine_ids:
    engine_data = df_test[df_test['engine_id'] == engine_id]
    if len(engine_data) > 0:
        last_rul = engine_data.iloc[-1]['RUL']
        rul_data.append({'Engine': f'EN{engine_id:03d}', 'RUL': last_rul})

if rul_data:
    df_rul = pd.DataFrame(rul_data)
    df_rul['Color'] = df_rul['RUL'].apply(
        lambda x: '#00FF88' if x > 50 else ('#FF6B35' if x > 30 else '#FF3366')
    )
    
    fig_bar = go.Figure(data=[
        go.Bar(
            y=df_rul['Engine'],
            x=df_rul['RUL'],
            orientation='h',
            marker=dict(color=df_rul['Color']),
            text=df_rul['RUL'].apply(lambda x: f'{x:.1f}'),
            textposition='auto'
        )
    ])
    
    fig_bar.update_layout(
        **PLOTLY_THEME,
        height=300,
        showlegend=False,
        xaxis_title="RUL (cycles)",
        yaxis_title="Engine"
    )
    
    st.plotly_chart(fig_bar, use_container_width=True)

st.divider()

# ============================================================================
# RECENT ALERTS
# ============================================================================

st.markdown("### 🔔 Recent Alerts (Latest 3)")

alerts_df = alert_manager.get_log_as_dataframe()

if len(alerts_df) > 0:
    recent_alerts = alerts_df.head(3)
    
    for idx, alert in recent_alerts.iterrows():
        severity = alert.get('severity', 'INFO')
        
        # Color based on severity
        if severity == 'CRITICAL':
            color = "#FF3366"
            emoji = "🚨"
        elif severity == 'WARNING':
            color = "#FF6B35"
            emoji = "⚠️"
        else:
            color = "#00FF88"
            emoji = "👁️"
        
        st.markdown(f"""
        <div style='background: rgba(15,22,41,0.8); border-left: 4px solid {color}; 
                    padding: 15px; margin: 10px 0; border-radius: 8px;'>
            <div style='color: {color}; font-weight: bold; font-size: 14px;'>
                {emoji} {severity} - Engine {alert.get('engine_id', 'N/A')}
            </div>
            <div style='color: #E8F4FD; margin: 5px 0; font-size: 13px;'>
                {alert.get('message', 'N/A')}
            </div>
            <div style='color: #8899AA; font-size: 12px;'>
                ⚙️  Action: {alert.get('action', 'N/A')}
            </div>
        </div>
        """, unsafe_allow_html=True)
else:
    st.info("✅ No active alerts. Fleet operating normally.")
