"""
Prediction Page — ML predictions for process outputs
=====================================================
Uses SYNTHETIC-trained models for demonstration only.
"""

import streamlit as st
import plotly.graph_objects as go
from utils.api_client import run_prediction
from components.ui_components import inject_custom_css, render_simulated_banner, render_kpi_card

st.set_page_config(page_title="Prediction", page_icon="🔮", layout="wide")
inject_custom_css()

st.markdown("""
<div style="display:flex;align-items:center;gap:12px;margin-bottom:5px;">
    <span style="font-size:2rem;">🔮</span>
    <div>
        <div style="font-size:1.3rem;font-weight:800;color:#FAFAFA;">Process Prediction</div>
        <div style="font-size:0.78rem;color:#6b7280;">ML-based prediction of Fe grade, recovery, SiO₂ & production rate</div>
    </div>
</div>
""", unsafe_allow_html=True)

render_simulated_banner()

st.markdown("""
<div style="background:rgba(245,158,11,0.08);border:1px solid rgba(245,158,11,0.25);border-radius:10px;padding:10px 16px;font-size:0.78rem;color:#fcd34d;margin-bottom:18px;">
    ⚠️ <strong>DEMO MODEL</strong> — Predictions are from a model trained on synthetic data only.
    Do not use for real plant decisions. Replace with a validated model trained on real process data.
</div>
""", unsafe_allow_html=True)

# ── Input Parameters ───────────────────────────────────────────────────
st.markdown('<div class="section-header">📥 Input Operating Conditions</div>', unsafe_allow_html=True)

col1, col2, col3 = st.columns(3)

with col1:
    st.markdown("**Feed & Crushing**")
    feed_rate = st.slider("Feed Rate (t/h)", 60.0, 180.0, 120.0, 1.0)
    fe_pct = st.slider("Feed Fe (%)", 25.0, 45.0, 35.0, 0.5)
    sio2_pct = st.slider("Feed SiO₂ (%)", 30.0, 60.0, 45.0, 0.5)
    hpgr_pressure = st.slider("HPGR Pressure (bar)", 80.0, 220.0, 145.0, 5.0)

with col2:
    st.markdown("**Grinding & Separation**")
    motor_power = st.slider("HPGR Motor Power (kW)", 500.0, 1200.0, 850.0, 10.0)
    particle_size = st.slider("Particle Size P80 (mm)", 1.0, 5.0, 2.5, 0.1)
    slurry_flow = st.slider("Slurry Flow (m³/h)", 100.0, 300.0, 185.0, 5.0)

with col3:
    st.markdown("**Flotation**")
    reagent_dose = st.slider("Reagent Dose (kg/t)", 0.1, 0.7, 0.35, 0.01)
    ph = st.slider("Flotation pH", 7.5, 12.0, 9.5, 0.1)
    air_flow = st.slider("Air Flow (m³/min)", 20.0, 70.0, 45.0, 1.0)

# ── Run Prediction ─────────────────────────────────────────────────────
st.markdown("<br>", unsafe_allow_html=True)

if st.button("🔮 Run Prediction", type="primary", use_container_width=True):
    inputs = {
        "feed_rate": feed_rate,
        "fe_pct": fe_pct,
        "sio2_pct": sio2_pct,
        "hpgr_pressure": hpgr_pressure,
        "motor_power": motor_power,
        "particle_size": particle_size,
        "slurry_flow": slurry_flow,
        "reagent_dose": reagent_dose,
        "ph": ph,
        "air_flow": air_flow,
    }

    with st.spinner("Running prediction..."):
        result = run_prediction(inputs)

    if result:
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown('<div class="section-header">📤 Prediction Results</div>', unsafe_allow_html=True)

        # KPI-style result cards
        rcols = st.columns(4)
        predictions = [
            ("Predicted Fe Grade", result.get("predicted_fe_grade", 0), "%", "#10b981"),
            ("Predicted Recovery", result.get("predicted_recovery", 0), "%", "#8b5cf6"),
            ("Predicted SiO₂", result.get("predicted_sio2", 0), "%", "#f59e0b"),
            ("Predicted Production", result.get("predicted_production_rate", 0), "t/h", "#06b6d4"),
        ]
        for col, (label, value, unit, color) in zip(rcols, predictions):
            with col:
                render_kpi_card(label, round(value, 2), unit, color)

        st.markdown("<br>", unsafe_allow_html=True)

        # Gauge charts
        gcols = st.columns(4)
        gauge_configs = [
            ("Fe Grade", result.get("predicted_fe_grade", 0), 55, 70, "#10b981"),
            ("Recovery", result.get("predicted_recovery", 0), 60, 100, "#8b5cf6"),
            ("SiO₂", result.get("predicted_sio2", 0), 0, 10, "#f59e0b"),
            ("Production", result.get("predicted_production_rate", 0), 20, 120, "#06b6d4"),
        ]

        for col, (name, value, min_v, max_v, color) in zip(gcols, gauge_configs):
            with col:
                fig = go.Figure(go.Indicator(
                    mode="gauge+number",
                    value=value,
                    title={"text": name, "font": {"size": 14, "color": "#8892a4"}},
                    number={"font": {"size": 24, "color": "#FAFAFA"}},
                    gauge={
                        "axis": {"range": [min_v, max_v], "tickcolor": "#4b5563"},
                        "bar": {"color": color},
                        "bgcolor": "#1a1d29",
                        "bordercolor": "#2a2d3e",
                        "steps": [
                            {"range": [min_v, min_v + (max_v - min_v) * 0.33], "color": "rgba(239,68,68,0.15)"},
                            {"range": [min_v + (max_v - min_v) * 0.33, min_v + (max_v - min_v) * 0.66], "color": "rgba(245,158,11,0.1)"},
                            {"range": [min_v + (max_v - min_v) * 0.66, max_v], "color": "rgba(16,185,129,0.1)"},
                        ],
                    }
                ))
                fig.update_layout(
                    paper_bgcolor='rgba(0,0,0,0)',
                    font=dict(color='#FAFAFA'),
                    height=220, margin=dict(l=20, r=20, t=40, b=20),
                )
                st.plotly_chart(fig, use_container_width=True)

        # Model info
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown(f"""
        <div class="eq-card">
            <div class="eq-card-title">Model Information</div>
            <div class="eq-card-param"><span class="eq-card-param-label">Model Type</span><span class="eq-card-param-value">{result.get('model_type', 'N/A')}</span></div>
            <div class="eq-card-param"><span class="eq-card-param-label">Confidence</span><span class="eq-card-param-value">{result.get('confidence', 'N/A')}</span></div>
            <div class="eq-card-param"><span class="eq-card-param-label">Data Source</span><span class="eq-card-param-value">{'Simulated' if result.get('is_simulated') else 'Real'}</span></div>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.error("Prediction failed. Check backend connection.")

else:
    st.info("👆 Adjust the input parameters above and click **Run Prediction** to see results.")
