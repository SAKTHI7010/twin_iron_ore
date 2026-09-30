"""
Simulation Page — What-if scenario analysis
=============================================
Change operating conditions and observe downstream effects.
"""

import streamlit as st
import plotly.graph_objects as go
from utils.api_client import get_process_state, update_simulation, start_simulation, stop_simulation, reset_simulation
from components.ui_components import (
    inject_custom_css, render_kpi_row, render_simulated_banner, render_kpi_card
)

st.set_page_config(page_title="Simulation", page_icon="🧪", layout="wide")
inject_custom_css()

st.markdown("""
<div style="display:flex;align-items:center;gap:12px;margin-bottom:5px;">
    <span style="font-size:2rem;">🧪</span>
    <div>
        <div style="font-size:1.3rem;font-weight:800;color:#FAFAFA;">Process Simulation</div>
        <div style="font-size:0.78rem;color:#6b7280;">What-if scenario analysis — adjust parameters and observe effects</div>
    </div>
</div>
""", unsafe_allow_html=True)

render_simulated_banner()

# ── Simulation Controls ────────────────────────────────────────────────
st.markdown('<div class="section-header">⚙️ Simulation Controls</div>', unsafe_allow_html=True)

ctrl_cols = st.columns(4)
with ctrl_cols[0]:
    if st.button("▶️ Start Simulation", use_container_width=True, type="primary"):
        start_simulation()
        st.success("Simulation started!")
with ctrl_cols[1]:
    if st.button("⏹️ Stop Simulation", use_container_width=True):
        stop_simulation()
        st.info("Simulation stopped")
with ctrl_cols[2]:
    if st.button("🔄 Reset to Defaults", use_container_width=True):
        reset_simulation()
        st.info("Simulation reset")
with ctrl_cols[3]:
    auto_apply = st.checkbox("Auto-apply changes", value=False)

st.markdown("<br>", unsafe_allow_html=True)

# ── Operating Parameters ───────────────────────────────────────────────
st.markdown('<div class="section-header">🎛️ Operating Parameters</div>', unsafe_allow_html=True)

col1, col2, col3 = st.columns(3)

with col1:
    st.markdown("**Feed Parameters**")
    feed_rate = st.slider("Feed Rate (t/h)", 60.0, 180.0, 120.0, 1.0, key="sim_feed")
    fe_pct = st.slider("Feed Fe (%)", 25.0, 45.0, 35.0, 0.5, key="sim_fe")
    sio2_pct = st.slider("Feed SiO₂ (%)", 30.0, 60.0, 45.0, 0.5, key="sim_sio2")

with col2:
    st.markdown("**HPGR Parameters**")
    hpgr_pressure = st.slider("HPGR Pressure (bar)", 80.0, 220.0, 145.0, 5.0, key="sim_press")
    hpgr_power = st.slider("HPGR Motor Power (kW)", 500.0, 1200.0, 850.0, 10.0, key="sim_power")

with col3:
    st.markdown("**Flotation Parameters**")
    reagent = st.slider("Reagent Dose (kg/t)", 0.1, 0.7, 0.35, 0.01, key="sim_reagent")
    flot_ph = st.slider("Flotation pH", 7.5, 12.0, 9.5, 0.1, key="sim_ph")
    air_flow = st.slider("Air Flow (m³/min)", 20.0, 70.0, 45.0, 1.0, key="sim_air")

# Build update payload
params = {
    "feed_rate": feed_rate,
    "feed_fe_pct": fe_pct,
    "feed_sio2_pct": sio2_pct,
    "hpgr_pressure": hpgr_pressure,
    "hpgr_motor_power": hpgr_power,
    "flotation_reagent_dose": reagent,
    "flotation_ph": flot_ph,
    "flotation_air_flow": air_flow,
}

# Apply changes
if auto_apply or st.button("📤 Apply Changes", type="primary", use_container_width=True):
    result = update_simulation(params)
    if result:
        if not auto_apply:
            st.success(f"✅ {result.get('message', 'Parameters updated')}")

st.markdown("<br>", unsafe_allow_html=True)

# ── Current Process State After Changes ────────────────────────────────
st.markdown('<div class="section-header">📊 Current Process Output</div>', unsafe_allow_html=True)

state = get_process_state()

if state:
    plant = state.get("plant", {})
    render_kpi_row(plant)

    st.markdown("<br>", unsafe_allow_html=True)

    # Comparison visualization
    col_l, col_r = st.columns(2)

    with col_l:
        st.markdown('<div class="section-header">📥 Input Summary</div>', unsafe_allow_html=True)

        input_items = [
            ("Feed Rate", f"{feed_rate} t/h"),
            ("Feed Fe", f"{fe_pct}%"),
            ("Feed SiO₂", f"{sio2_pct}%"),
            ("HPGR Pressure", f"{hpgr_pressure} bar"),
            ("HPGR Motor Power", f"{hpgr_power} kW"),
            ("Reagent Dose", f"{reagent} kg/t"),
            ("Flotation pH", f"{flot_ph}"),
            ("Air Flow", f"{air_flow} m³/min"),
        ]

        for label, value in input_items:
            st.markdown(f"""
            <div class="eq-card-param" style="padding:6px 0;">
                <span class="eq-card-param-label">{label}</span>
                <span class="eq-card-param-value">{value}</span>
            </div>
            """, unsafe_allow_html=True)

    with col_r:
        st.markdown('<div class="section-header">📤 Output Summary</div>', unsafe_allow_html=True)

        # Radar chart of process outputs
        categories = ['Fe Grade', 'Recovery', 'Production', 'Water Recovery', 'Availability']
        values = [
            plant.get("fe_grade", 0) / 70 * 100,  # Normalize to 0-100
            plant.get("recovery", 0),
            plant.get("production_rate", 0) / 120 * 100,
            plant.get("water_recovery", 0),
            plant.get("equipment_availability", 0),
        ]
        values.append(values[0])  # Close the polygon
        categories.append(categories[0])

        fig = go.Figure()
        fig.add_trace(go.Scatterpolar(
            r=values, theta=categories,
            fill='toself', fillcolor='rgba(255, 107, 53, 0.15)',
            line=dict(color='#FF6B35', width=2),
            name='Current State'
        ))
        fig.update_layout(
            polar=dict(
                bgcolor='rgba(26,29,41,0.8)',
                radialaxis=dict(visible=True, range=[0, 100], tickfont=dict(color='#4b5563')),
                angularaxis=dict(tickfont=dict(color='#8892a4')),
            ),
            paper_bgcolor='rgba(0,0,0,0)',
            showlegend=False,
            height=350, margin=dict(l=60, r=60, t=30, b=30),
        )
        st.plotly_chart(fig, use_container_width=True)

else:
    st.error("Cannot fetch process state. Is the backend running?")

# Auto-refresh
st.markdown("---")
if st.checkbox("🔄 Auto-refresh (3s)", value=False, key="sim_refresh"):
    import time
    time.sleep(3)
    st.rerun()
