"""
Process Analysis Page — Historical trends, distributions, correlations, KPI analysis
"""

import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
import numpy as np
from utils.api_client import get_history, get_process_state
from components.ui_components import inject_custom_css, render_simulated_banner

st.set_page_config(page_title="Process Analysis", page_icon="📊", layout="wide")
inject_custom_css()

st.markdown("""
<div style="display:flex;align-items:center;gap:12px;margin-bottom:5px;">
    <span style="font-size:2rem;">📊</span>
    <div>
        <div style="font-size:1.3rem;font-weight:800;color:#FAFAFA;">Process Analysis</div>
        <div style="font-size:0.78rem;color:#6b7280;">Historical trends, distributions & KPI correlation analysis</div>
    </div>
</div>
""", unsafe_allow_html=True)

render_simulated_banner()

import os
analysis_path = os.path.join(os.path.dirname(__file__), "..", "assets", "analysis.jpg")
if os.path.exists(analysis_path):
    st.image(analysis_path, use_container_width=True)

# Fetch historical data
history_resp = get_history(limit=200)
records = history_resp.get("records", []) if history_resp else []

if records and len(records) > 5:
    df = pd.DataFrame(records)
    df["timestamp"] = pd.to_datetime(df["timestamp"], errors="coerce")

    # ── Tab Layout ─────────────────────────────────────────────────────
    tab1, tab2, tab3, tab4 = st.tabs(["📈 Trends", "📊 Distributions", "🔗 Correlations", "📋 Statistics"])

    with tab1:
        st.markdown('<div class="section-header">📈 Historical Trends</div>', unsafe_allow_html=True)

        variables = {
            "Fe Grade (%)": "fe_grade",
            "SiO₂ (%)": "sio2",
            "Recovery (%)": "recovery",
            "Production Rate (t/h)": "production_rate",
            "Feed Rate (t/h)": "feed_rate",
            "Water Recovery (%)": "water_recovery",
        }

        selected_vars = st.multiselect(
            "Select variables to plot",
            list(variables.keys()),
            default=["Fe Grade (%)", "Recovery (%)"]
        )

        if selected_vars:
            fig = go.Figure()
            colors = ['#10b981', '#f59e0b', '#8b5cf6', '#06b6d4', '#3b82f6', '#14b8a6']

            for i, var_name in enumerate(selected_vars):
                col_name = variables[var_name]
                if col_name in df.columns:
                    fig.add_trace(go.Scatter(
                        x=df["timestamp"], y=df[col_name],
                        mode='lines', name=var_name,
                        line=dict(color=colors[i % len(colors)], width=2),
                    ))

            fig.update_layout(
                template='plotly_dark',
                paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(26,29,41,0.8)',
                height=450, margin=dict(l=50, r=30, t=30, b=40),
                legend=dict(orientation='h', y=1.1),
                xaxis=dict(showgrid=False, title="Time"),
                yaxis=dict(showgrid=True, gridcolor='rgba(255,255,255,0.05)'),
            )
            st.plotly_chart(fig, use_container_width=True)

    with tab2:
        st.markdown('<div class="section-header">📊 Value Distributions</div>', unsafe_allow_html=True)

        dist_cols = st.columns(3)
        dist_vars = [
            ("fe_grade", "Fe Grade (%)", "#10b981"),
            ("sio2", "SiO₂ (%)", "#f59e0b"),
            ("recovery", "Recovery (%)", "#8b5cf6"),
            ("production_rate", "Production (t/h)", "#06b6d4"),
            ("feed_rate", "Feed Rate (t/h)", "#3b82f6"),
            ("water_recovery", "Water Recovery (%)", "#14b8a6"),
        ]

        for i, (col_name, label, color) in enumerate(dist_vars):
            with dist_cols[i % 3]:
                if col_name in df.columns:
                    fig = go.Figure()
                    fig.add_trace(go.Histogram(
                        x=df[col_name], nbinsx=20,
                        marker_color=color, opacity=0.8, name=label,
                    ))
                    fig.update_layout(
                        template='plotly_dark',
                        paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(26,29,41,0.8)',
                        height=250, margin=dict(l=40, r=20, t=35, b=30),
                        title=dict(text=label, font=dict(size=12)),
                        xaxis=dict(showgrid=False),
                        yaxis=dict(showgrid=False, title='Count'),
                        showlegend=False,
                    )
                    st.plotly_chart(fig, use_container_width=True)

    with tab3:
        st.markdown('<div class="section-header">🔗 Variable Correlations</div>', unsafe_allow_html=True)

        numeric_cols = ["fe_grade", "sio2", "recovery", "production_rate", "feed_rate", "water_recovery"]
        available_cols = [c for c in numeric_cols if c in df.columns]

        if len(available_cols) >= 2:
            corr_df = df[available_cols].corr()

            labels_map = {
                "fe_grade": "Fe Grade", "sio2": "SiO₂", "recovery": "Recovery",
                "production_rate": "Production", "feed_rate": "Feed Rate",
                "water_recovery": "Water Recovery"
            }

            fig = go.Figure(data=go.Heatmap(
                z=corr_df.values,
                x=[labels_map.get(c, c) for c in corr_df.columns],
                y=[labels_map.get(c, c) for c in corr_df.index],
                colorscale=[[0, '#1e3a5f'], [0.5, '#0E1117'], [1, '#FF6B35']],
                zmin=-1, zmax=1,
                text=np.round(corr_df.values, 2),
                texttemplate='%{text}',
                textfont=dict(size=12, color='white'),
            ))
            fig.update_layout(
                template='plotly_dark',
                paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(26,29,41,0.8)',
                height=450, margin=dict(l=80, r=30, t=30, b=80),
            )
            st.plotly_chart(fig, use_container_width=True)

            # Scatter plot
            st.markdown('<div class="section-header">🔍 Scatter Analysis</div>', unsafe_allow_html=True)
            col1, col2 = st.columns(2)
            with col1:
                x_var = st.selectbox("X Axis", available_cols, index=0, format_func=lambda x: labels_map.get(x, x))
            with col2:
                y_var = st.selectbox("Y Axis", available_cols, index=1, format_func=lambda x: labels_map.get(x, x))

            fig_scatter = px.scatter(
                df, x=x_var, y=y_var,
                labels={x_var: labels_map.get(x_var, x_var), y_var: labels_map.get(y_var, y_var)},
                trendline="ols",
                color_discrete_sequence=['#FF6B35'],
            )
            fig_scatter.update_layout(
                template='plotly_dark',
                paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(26,29,41,0.8)',
                height=400, margin=dict(l=50, r=30, t=30, b=40),
            )
            st.plotly_chart(fig_scatter, use_container_width=True)

    with tab4:
        st.markdown('<div class="section-header">📋 Statistical Summary</div>', unsafe_allow_html=True)

        stats_df = df[available_cols].describe().round(2)
        stats_df.index = ["Count", "Mean", "Std Dev", "Min", "25%", "50%", "75%", "Max"]
        stats_df.columns = [labels_map.get(c, c) for c in stats_df.columns]

        st.dataframe(stats_df, use_container_width=True)

        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown('<div class="section-header">📥 Export Data</div>', unsafe_allow_html=True)

        csv = df.to_csv(index=False)
        st.download_button(
            "📥 Download Historical Data (CSV)",
            csv, "process_history.csv", "text/csv",
            use_container_width=True
        )

else:
    st.info("📊 Not enough historical data for analysis. Start the simulation and let it run to accumulate data points.")
    st.info("**Tip:** Enable auto-refresh on the Home page to generate data, then return here.")
