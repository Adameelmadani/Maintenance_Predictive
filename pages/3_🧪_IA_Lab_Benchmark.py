"""
PAGE 3: IA Lab Benchmark — Model Performance Comparison

Compares all 5 RUL regression models and 2 diagnostic classifiers
with detailed performance metrics, visualizations, and analysis.
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

st.set_page_config(page_title="IA Lab", page_icon="🧪", layout="wide")

st.markdown("# 🧪 IA LAB — MODEL BENCHMARKING")
st.markdown("**Predictive Model Performance Comparison & Analysis**")
st.divider()

# Get benchmark results
benchmark = st.session_state.benchmark_results

if benchmark is None:
    st.error("❌ Benchmark results not found. Please run train_models.py first.")
    st.stop()

# ============================================================================
# TABS FOR REGRESSION VS CLASSIFICATION
# ============================================================================

tab1, tab2 = st.tabs(["📈 Regression Models (RUL)", "🎯 Classification Models"])

# ============================================================================
# TAB 1: REGRESSION MODELS
# ============================================================================

with tab1:
    st.markdown("## RUL Prediction Model Benchmarks")
    
    rul_benchmarks = benchmark.get('RUL_Models', {}).get('benchmarks', {})
    rul_results = benchmark.get('RUL_Models', {}).get('detailed_results', {})
    
    # Performance comparison table
    st.markdown("### Performance Metrics Comparison")
    
    rul_df = pd.DataFrame(rul_benchmarks).T
    rul_df = rul_df.sort_values('MAE', ascending=True)
    
    # Add ranking
    rul_df['MAE Rank'] = range(1, len(rul_df) + 1)
    rul_df = rul_df[['MAE Rank', 'MAE', 'RMSE', 'R2', 'TrainTime_s']]
    
    st.dataframe(rul_df, use_container_width=True)
    
    # Highlight best models
    col1, col2, col3 = st.columns(3)
    
    with col1:
        best_mae = min(rul_benchmarks.items(), key=lambda x: x[1]['MAE'])
        st.info(f"✅ **Best MAE**: {best_mae[0]}\n{best_mae[1]['MAE']:.2f}")
    
    with col2:
        best_rmse = min(rul_benchmarks.items(), key=lambda x: x[1]['RMSE'])
        st.info(f"✅ **Best RMSE**: {best_rmse[0]}\n{best_rmse[1]['RMSE']:.2f}")
    
    with col3:
        best_r2 = max(rul_benchmarks.items(), key=lambda x: x[1]['R2'])
        st.warning(f"⚠️  **Best R²**: {best_r2[0]}\n{best_r2[1]['R2']:.4f} (Note: negative R² indicates room for improvement)")
    
    st.divider()
    
    # Radar chart
    st.markdown("### Performance Radar")
    
    # Normalize metrics for radar (they're on different scales)
    radar_data = {}
    for model, metrics in rul_benchmarks.items():
        radar_data[model] = {
            'MAE_inv': 100 / (metrics['MAE'] + 1),  # Inverse (higher is better)
            'RMSE_inv': 100 / (metrics['RMSE'] + 1),
            'R2_norm': max(0, metrics['R2'] * 100 + 100),  # Shift to positive
            'Speed': 100 / (metrics['TrainTime_s'] + 0.1)
        }
    
    categories = ['MAE Score', 'RMSE Score', 'R² Score', 'Speed']
    
    fig_radar = go.Figure()
    
    for model, scores in radar_data.items():
        fig_radar.add_trace(go.Scatterpolar(
            r=[scores['MAE_inv'], scores['RMSE_inv'], scores['R2_norm'], scores['Speed']],
            theta=categories,
            fill='toself',
            name=model
        ))
    
    fig_radar.update_layout(
        **PLOTLY_THEME,
        polar=dict(
            radialaxis=dict(
                visible=True,
                range=[0, 100],
                gridcolor="rgba(255,255,255,0.1)"
            ),
            angularaxis=dict(gridcolor="rgba(255,255,255,0.1)")
        ),
        height=500
    )
    
    st.plotly_chart(fig_radar, use_container_width=True)
    
    st.divider()
    
    # Predicted vs Actual
    st.markdown("### Predicted vs Actual RUL")
    
    selected_model = st.selectbox(
        "Select Model for Visualization",
        list(rul_benchmarks.keys()),
        key="rul_model_select"
    )
    
    if selected_model in rul_results:
        y_actual = np.array(rul_results[selected_model]['y_actual'])
        y_pred = np.array(rul_results[selected_model]['y_pred'])
        
        # Create predicted vs actual plot
        fig_pva = go.Figure()
        
        # Predicted vs Actual scatter
        fig_pva.add_trace(go.Scatter(
            x=y_actual,
            y=y_pred,
            mode='markers',
            marker=dict(
                size=6,
                color=np.abs(y_actual - y_pred),
                colorscale='Viridis',
                colorbar=dict(title="Error")
            ),
            name='Predictions',
            opacity=0.6
        ))
        
        # Perfect prediction line
        min_val = min(y_actual.min(), y_pred.min())
        max_val = max(y_actual.max(), y_pred.max())
        fig_pva.add_trace(go.Scatter(
            x=[min_val, max_val],
            y=[min_val, max_val],
            mode='lines',
            line=dict(color='#FF3366', width=2, dash='dash'),
            name='Perfect Prediction'
        ))
        
        fig_pva.update_layout(
            **PLOTLY_THEME,
            height=500,
            title=f"{selected_model} — Predicted vs Actual RUL",
            xaxis_title="Actual RUL (cycles)",
            yaxis_title="Predicted RUL (cycles)"
        )
        
        st.plotly_chart(fig_pva, use_container_width=True)
        
        # Residuals
        st.markdown("### Residuals Distribution")
        
        residuals = y_actual - y_pred
        
        fig_residuals = go.Figure(data=[
            go.Histogram(
                x=residuals,
                nbinsx=50,
                marker=dict(color='#00D4FF', opacity=0.7),
                name='Residuals'
            )
        ])
        
        # Add acceptable error zone
        fig_residuals.add_vrect(
            x0=-15, x1=15,
            fillcolor="#00FF88", opacity=0.1,
            layer="below", line_width=0,
            annotation_text="Acceptable Error ±15",
            annotation_position="top right"
        )
        
        fig_residuals.add_vline(x=0, line_dash="dash", line_color="#FF3366")
        
        fig_residuals.update_layout(
            **PLOTLY_THEME,
            height=400,
            title="Residuals Distribution",
            xaxis_title="Prediction Error (Actual - Predicted)",
            yaxis_title="Frequency"
        )
        
        st.plotly_chart(fig_residuals, use_container_width=True)

# ============================================================================
# TAB 2: CLASSIFICATION MODELS
# ============================================================================

with tab2:
    st.markdown("## Health Status Classification (Diagnostic)")
    
    cls_benchmarks = benchmark.get('Classification_Models', {}).get('benchmarks', {})
    cls_matrices = benchmark.get('Classification_Models', {}).get('confusion_matrices', {})
    
    if not cls_benchmarks:
        st.error("❌ Classification results not found.")
        st.stop()
    
    # Performance table
    st.markdown("### Performance Metrics")
    
    cls_df = pd.DataFrame(cls_benchmarks).T
    st.dataframe(cls_df, use_container_width=True)
    
    st.divider()
    
    # Confusion matrices side by side
    st.markdown("### Confusion Matrices")
    
    col1, col2 = st.columns(2)
    
    for idx, (model_name, cm_data) in enumerate(cls_matrices.items()):
        cm_array = np.array([
            [cm_data['TN'], cm_data['FP']],
            [cm_data['FN'], cm_data['TP']]
        ])
        
        fig_cm = go.Figure(data=go.Heatmap(
            z=cm_array,
            x=['Healthy', 'Degraded'],
            y=['Healthy', 'Degraded'],
            text=cm_array,
            texttemplate='%d',
            textfont={"size": 14},
            colorscale='Blues',
            showscale=False
        ))
        
        fig_cm.update_layout(
            **PLOTLY_THEME,
            title=f"{model_name} Confusion Matrix",
            height=400,
            xaxis_title="Predicted",
            yaxis_title="Actual"
        )
        
        if idx == 0:
            col1.plotly_chart(fig_cm, use_container_width=True)
        else:
            col2.plotly_chart(fig_cm, use_container_width=True)
    
    st.divider()
    
    # Metrics comparison
    st.markdown("### Classification Metrics Comparison")
    
    metrics_comparison = st.selectbox(
        "Select Metric to Compare",
        ['Accuracy', 'Precision', 'Recall', 'F1'],
        key="cls_metric_select"
    )
    
    metric_values = {model: metrics[metrics_comparison] for model, metrics in cls_benchmarks.items()}
    
    fig_comp = go.Figure(data=[
        go.Bar(
            x=list(metric_values.keys()),
            y=list(metric_values.values()),
            marker=dict(color=['#00D4FF', '#00FF88']),
            text=[f"{v:.4f}" for v in metric_values.values()],
            textposition='auto'
        )
    ])
    
    fig_comp.update_layout(
        **PLOTLY_THEME,
        title=f"{metrics_comparison} Comparison",
        height=400,
        showlegend=False,
        xaxis_title="Model",
        yaxis_title=metrics_comparison
    )
    
    st.plotly_chart(fig_comp, use_container_width=True)
