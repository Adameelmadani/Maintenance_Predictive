"""
PAGE 5: Log & Maintenance — Event Tracking & Analytics

Displays complete maintenance event log, historical alerts, 
statistics, and export functionality for audit trails.
"""

import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
import numpy as np
import pandas as pd
from datetime import datetime, timedelta


PLOTLY_THEME = dict(
    template="plotly_dark",
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(15,22,41,0.8)",
    font=dict(family="Rajdhani, sans-serif", color="#E8F4FD"),
    colorway=["#00D4FF", "#00FF88", "#FF6B35", "#FF3366", "#7B2FBE"],
    xaxis=dict(gridcolor="rgba(255,255,255,0.05)", showline=True, linecolor="rgba(0,212,255,0.3)"),
    yaxis=dict(gridcolor="rgba(255,255,255,0.05)", showline=True, linecolor="rgba(0,212,255,0.3)"),
)

st.set_page_config(page_title="Maintenance Log", page_icon="📋", layout="wide")

st.markdown("# 📋 MAINTENANCE LOG & ANALYTICS")
st.markdown("**Event History | Alert Tracking | Maintenance Analytics**")
st.divider()

# Get alert manager from session state
alert_manager = st.session_state.alert_manager

# ============================================================================
# FILTERS
# ============================================================================

st.markdown("## 🔍 Filter Events")

col1, col2, col3 = st.columns(3)

with col1:
    severity_filter = st.multiselect(
        "Severity Level",
        ["CRITICAL", "WARNING", "WATCH", "INFO"],
        default=["CRITICAL", "WARNING"],
        help="Filter alerts by severity"
    )

with col2:
    date_range = st.date_input(
        "Date Range",
        value=(datetime.now() - timedelta(days=7), datetime.now()),
        help="Filter by date range"
    )

with col3:
    engine_filter = st.text_input(
        "Engine ID Search",
        placeholder="e.g., 1, 5, 10",
        help="Filter by engine ID (or leave blank for all)"
    )

st.divider()

# ============================================================================
# ALERT LOG TABLE
# ============================================================================

st.markdown("## 📊 Event Log")

alerts_df = alert_manager.get_log_as_dataframe()

if len(alerts_df) == 0:
    st.info("✅ No alerts logged yet. Platform operating normally.")
else:
    # Apply filters
    filtered_df = alerts_df.copy()
    
    if severity_filter:
        filtered_df = filtered_df[filtered_df['severity'].isin(severity_filter)]
    
    if engine_filter:
        try:
            engine_ids = [int(x.strip()) for x in engine_filter.split(',')]
            filtered_df = filtered_df[filtered_df['engine_id'].isin(engine_ids)]
        except:
            pass
    
    # Apply date range filter if available
    if 'timestamp' in filtered_df.columns and len(date_range) == 2:
        filtered_df = filtered_df[
            (filtered_df['timestamp'].dt.date >= date_range[0]) &
            (filtered_df['timestamp'].dt.date <= date_range[1])
        ]
    
    # Display filtered results count
    st.caption(f"Showing {len(filtered_df)} of {len(alerts_df)} total alerts")
    
    # Create styled dataframe display
    display_df = filtered_df[[
        'timestamp', 'engine_id', 'severity', 'rul', 'health_index', 'message', 'action'
    ]].copy()
    
    # Format timestamp
    if 'timestamp' in display_df.columns:
        display_df['timestamp'] = display_df['timestamp'].dt.strftime('%Y-%m-%d %H:%M:%S')
    
    st.dataframe(
        display_df,
        use_container_width=True,
        hide_index=True
    )
    
    st.divider()
    
    # ========================================================================
    # STATISTICS
    # ========================================================================
    
    st.markdown("## 📈 Alert Statistics")
    
    stats = alert_manager.get_statistics()
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("📊 Total Alerts", stats['total_alerts'])
    
    with col2:
        st.metric("🚨 Critical Alerts", stats['critical_count'])
    
    with col3:
        st.metric("⚠️  Warnings", stats['warning_count'])
    
    with col4:
        st.metric("👁️  Watch Alerts", stats['watch_count'])
    
    # Alert distribution charts
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### Alerts by Severity")
        
        severity_counts = alerts_df['severity'].value_counts()
        
        fig_severity = go.Figure(data=[
            go.Pie(
                labels=severity_counts.index,
                values=severity_counts.values,
                marker=dict(colors=['#FF3366', '#FF6B35', '#00FF88', '#00D4FF']),
                hole=0.4
            )
        ])
        
        fig_severity.update_layout(**PLOTLY_THEME, height=400)
        st.plotly_chart(fig_severity, use_container_width=True)
    
    with col2:
        st.markdown("### Alerts by Engine")
        
        if 'engine_id' in alerts_df.columns:
            engine_counts = alerts_df['engine_id'].value_counts().head(10)
            
            fig_engine = go.Figure(data=[
                go.Bar(
                    x=engine_counts.index.astype(str),
                    y=engine_counts.values,
                    marker=dict(
                        color=engine_counts.values,
                        colorscale='Reds'
                    ),
                    text=engine_counts.values,
                    textposition='auto'
                )
            ])
            
            fig_engine.update_layout(
                **PLOTLY_THEME,
                height=400,
                showlegend=False,
                xaxis_title="Engine ID",
                yaxis_title="Alert Count",
                title="Most Problematic Engines"
            )
            
            st.plotly_chart(fig_engine, use_container_width=True)
    
    st.divider()
    
    # ========================================================================
    # DETAILED STATISTICS
    # ========================================================================
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if 'engine_id' in alerts_df.columns:
            affected_engines = alerts_df['engine_id'].nunique()
            st.info(f"**Affected Engines:** {affected_engines}")
    
    with col2:
        if 'timestamp' in alerts_df.columns:
            latest_alert = alerts_df['timestamp'].max()
            if pd.notna(latest_alert):
                st.info(f"**Latest Alert:** {latest_alert.strftime('%Y-%m-%d %H:%M:%S')}")
    
    with col3:
        # Calculate MTBF-like metric
        mtbf_estimate = len(alerts_df) / max(1, (stats['critical_count'] or 1))
        st.info(f"**Avg Alerts per Critical:** {mtbf_estimate:.1f}")
    
    st.divider()
    
    # ========================================================================
    # ALERT TIMELINE
    # ========================================================================
    
    st.markdown("## ⏰ Alert Timeline")
    
    if 'timestamp' in alerts_df.columns and 'engine_id' in alerts_df.columns:
        timeline_df = alerts_df.copy()
        timeline_df['timestamp'] = pd.to_datetime(timeline_df['timestamp'])
        timeline_df = timeline_df.sort_values('timestamp')
        
        # Map severity to numeric value for y-axis
        severity_map = {'CRITICAL': 3, 'WARNING': 2, 'WATCH': 1, 'INFO': 0}
        timeline_df['severity_val'] = timeline_df['severity'].map(severity_map)
        
        fig_timeline = go.Figure()
        
        for severity in ['CRITICAL', 'WARNING', 'WATCH', 'INFO']:
            df_sev = timeline_df[timeline_df['severity'] == severity]
            color_map = {
                'CRITICAL': '#FF3366',
                'WARNING': '#FF6B35',
                'WATCH': '#00FF88',
                'INFO': '#00D4FF'
            }
            
            fig_timeline.add_trace(go.Scatter(
                x=df_sev['timestamp'],
                y=df_sev['engine_id'],
                mode='markers',
                name=severity,
                marker=dict(
                    size=10,
                    color=color_map[severity]
                ),
                text=df_sev.apply(lambda r: f"Engine {r['engine_id']}<br>{r['severity']}<br>RUL: {r['rul']:.1f}", axis=1),
                hovertemplate='%{text}<extra></extra>'
            ))
        
        fig_timeline.update_layout(
            **PLOTLY_THEME,
            height=400,
            title="Alert Timeline — Historical View",
            xaxis_title="Time",
            yaxis_title="Engine ID",
            hovermode='closest'
        )
        
        st.plotly_chart(fig_timeline, use_container_width=True)
    
    st.divider()
    
    # ========================================================================
    # EXPORT
    # ========================================================================
    
    st.markdown("## 💾 Export Data")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Export filtered CSV
        csv_data = filtered_df.to_csv(index=False)
        st.download_button(
            label="📥 Download Filtered Log (CSV)",
            data=csv_data,
            file_name=f"maintenance_log_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
            mime="text/csv",
            use_container_width=True
        )
    
    with col2:
        # Export all CSV
        csv_all = alerts_df.to_csv(index=False)
        st.download_button(
            label="📥 Download All Log (CSV)",
            data=csv_all,
            file_name=f"maintenance_log_complete_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
            mime="text/csv",
            use_container_width=True
        )

st.divider()

st.markdown("### 📝 Platform Info")
st.caption(f"""
- **Last Updated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
- **Total Events Tracked:** {len(alerts_df)}
- **Active Engine Being Monitored:** EN{st.session_state.current_engine:03d}
- **Active Model:** {st.session_state.active_model_name}
""")
