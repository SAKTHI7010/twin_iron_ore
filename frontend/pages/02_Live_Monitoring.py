"""
Live Monitoring Page — Real-time process values, equipment status, and alarms
"""

import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime
from utils.api_client import get_process_state, get_alarms, get_history
from components.ui_components import (
    inject_custom_css, render_kpi_row, render_simulated_banner,
    render_alarm_banner, render_status_badge, render_equipment_card
)

st.set_page_config(page_title="Live Monitoring", page_icon="📡", layout="wide")
inject_custom_css()

st.markdown("""
<div style="display:flex;align-items:center;gap:12px;margin-bottom:5px;">
    <span style="font-size:2rem;">📡</span>
    <div>
        <div style="font-size:1.3rem;font-weight:800;color:#FAFAFA;">Live Monitoring</div>
        <div style="font-size:0.78rem;color:#6b7280;">Real-time process values, equipment status & alarms</div>
    </div>
</div>
""", unsafe_allow_html=True)

render_simulated_banner()

state = get_process_state()

if state:
    plant = state.get("plant", {})
    equipment = state.get("equipment", {})
    alarms_data = state.get("alarms", [])

    render_alarm_banner(alarms_data)
    render_kpi_row(plant)

    st.markdown("<br>", unsafe_allow_html=True)

    # ── Live Trend Charts ──────────────────────────────────────────────
    col_left, col_right = st.columns(2)

    history_resp = get_history(limit=50)
    records = history_resp.get("records", []) if history_resp else []

    if records:
        timestamps = [r.get("timestamp", "")[:19] for r in records]

        with col_left:
            st.markdown('<div class="section-header">📈 Fe Grade & Recovery Trend</div>', unsafe_allow_html=True)
            fig1 = go.Figure()
            fig1.add_trace(go.Scatter(
                x=timestamps, y=[r.get("fe_grade", 0) for r in records],
                mode='lines+markers', name='Fe Grade (%)',
                line=dict(color='#10b981', width=2),
                marker=dict(size=4)
            ))
            fig1.add_trace(go.Scatter(
                x=timestamps, y=[r.get("recovery", 0) for r in records],
                mode='lines+markers', name='Recovery (%)',
                line=dict(color='#8b5cf6', width=2),
                marker=dict(size=4), yaxis='y2'
            ))
            fig1.update_layout(
                template='plotly_dark',
                paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(26,29,41,0.8)',
                height=350, margin=dict(l=50, r=50, t=30, b=40),
                legend=dict(orientation='h', y=1.12),
                yaxis=dict(title='Fe Grade (%)', titlefont=dict(color='#10b981')),
                yaxis2=dict(title='Recovery (%)', titlefont=dict(color='#8b5cf6'),
                           overlaying='y', side='right'),
                xaxis=dict(showgrid=False),
            )
            st.plotly_chart(fig1, use_container_width=True)

        with col_right:
            st.markdown('<div class="section-header">📉 SiO₂ & Production Rate</div>', unsafe_allow_html=True)
            fig2 = go.Figure()
            fig2.add_trace(go.Scatter(
                x=timestamps, y=[r.get("sio2", 0) for r in records],
                mode='lines+markers', name='SiO₂ (%)',
                line=dict(color='#f59e0b', width=2),
                marker=dict(size=4)
            ))
            fig2.add_trace(go.Scatter(
                x=timestamps, y=[r.get("production_rate", 0) for r in records],
                mode='lines+markers', name='Production (t/h)',
                line=dict(color='#06b6d4', width=2),
                marker=dict(size=4), yaxis='y2'
            ))
            fig2.update_layout(
                template='plotly_dark',
                paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(26,29,41,0.8)',
                height=350, margin=dict(l=50, r=50, t=30, b=40),
                legend=dict(orientation='h', y=1.12),
                yaxis=dict(title='SiO₂ (%)', titlefont=dict(color='#f59e0b')),
                yaxis2=dict(title='Production (t/h)', titlefont=dict(color='#06b6d4'),
                           overlaying='y', side='right'),
                xaxis=dict(showgrid=False),
            )
            st.plotly_chart(fig2, use_container_width=True)

    else:
        st.info("No historical data yet. Start the simulation and wait for data to accumulate.")

    # ── Equipment Status Grid ──────────────────────────────────────────
    st.markdown('<div class="section-header">🏭 Equipment Status</div>', unsafe_allow_html=True)

    eq_list = list(equipment.items())
    cols_per_row = 3
    for i in range(0, len(eq_list), cols_per_row):
        cols = st.columns(cols_per_row)
        for j, col in enumerate(cols):
            idx = i + j
            if idx < len(eq_list):
                eq_id, eq_data = eq_list[idx]
                if isinstance(eq_data, dict):
                    with col:
                        render_equipment_card(eq_id, eq_data)

    # ── Alarm Log ──────────────────────────────────────────────────────
    st.markdown('<div class="section-header">🚨 Alarm Log</div>', unsafe_allow_html=True)
    alarms_resp = get_alarms()
    if alarms_resp:
        alarm_list = alarms_resp.get("alarms", [])
        if alarm_list:
            for alarm in alarm_list[-15:]:
                severity = alarm.get("severity", "INFO")
                icon = "🔴" if severity == "CRITICAL" else "🟡" if severity == "WARNING" else "🔵"
                st.markdown(f"""
                <div style="display:flex;gap:10px;padding:6px 0;border-bottom:1px solid rgba(255,255,255,0.04);font-size:0.82rem;">
                    <span>{icon}</span>
                    <span style="color:#6b7280;min-width:160px;">{alarm.get('timestamp', '')[:19]}</span>
                    <span style="color:#8892a4;min-width:120px;">{alarm.get('equipment', '')}</span>
                    <span style="color:#FAFAFA;">{alarm.get('message', '')}</span>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.success("✅ No active alarms")
    else:
        st.info("Alarm data unavailable")

else:
    st.error("Cannot connect to backend. Is the FastAPI server running?")

# Auto-refresh
st.markdown("---")
if st.checkbox("🔄 Auto-refresh (3s)", value=False, key="mon_refresh"):
    import time
    time.sleep(3)
    st.rerun()
