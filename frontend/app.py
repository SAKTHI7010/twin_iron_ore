"""
Iron Ore Beneficiation Digital Twin — Streamlit Frontend
=========================================================
Home page: Project overview, KPI dashboard, process status.
All data is SIMULATED unless connected to a real plant data source.
"""

import streamlit as st
from utils.api_client import get_process_state, check_health, start_simulation, stop_simulation, reset_simulation
from components.ui_components import (
    inject_custom_css, render_kpi_row, render_simulated_banner,
    render_alarm_banner, render_status_badge
)

# ── Page Config ────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Iron Ore Beneficiation — Digital Twin",
    page_icon="🏭",
    layout="wide",
    initial_sidebar_state="expanded",
)

inject_custom_css()

# ── Sidebar ────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("""
    <div style="text-align:center;padding:10px 0 20px 0;">
        <div style="font-size:2.5rem;">🏭</div>
        <div style="font-size:1.1rem;font-weight:800;color:#FF6B35;letter-spacing:1px;margin-top:5px;">
            DIGITAL TWIN
        </div>
        <div style="font-size:0.7rem;color:#6b7280;margin-top:2px;">
            Iron Ore Beneficiation Plant
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("---")

    # Simulation controls
    st.markdown("##### ⚙️ Simulation Controls")
    col1, col2, col3 = st.columns(3)
    with col1:
        if st.button("▶ Start", use_container_width=True):
            start_simulation()
            st.success("Started")
    with col2:
        if st.button("⏹ Stop", use_container_width=True):
            stop_simulation()
            st.info("Stopped")
    with col3:
        if st.button("🔄 Reset", use_container_width=True):
            reset_simulation()
            st.info("Reset")

    st.markdown("---")

    # Health check
    health = check_health()
    if health:
        status = health.get("status", "unknown")
        sim_active = health.get("simulation_active", False)
        st.markdown(f"**Backend:** 🟢 Connected")
        st.markdown(f"**Simulation:** {'🟢 Active' if sim_active else '🔴 Stopped'}")
        st.markdown(f"**Data Source:** `{health.get('data_source', 'N/A')}`")
    else:
        st.markdown("**Backend:** 🔴 Disconnected")
        st.warning("Start the backend with:\n```\ncd backend\nuvicorn main:app --reload\n```")

    st.markdown("---")
    st.markdown(
        "<div style='font-size:0.65rem;color:#4b5563;text-align:center;'>"
        "v1.0.0 · Simulated Data Only<br>"
        "BHQ Ore — Hematite + Quartz"
        "</div>",
        unsafe_allow_html=True
    )

# ── Main Content ───────────────────────────────────────────────────────
st.markdown("""
<div style="display:flex;align-items:center;gap:14px;margin-bottom:15px;">
    <span style="font-size:2.2rem;">🏭</span>
    <div>
        <div style="font-size:1.5rem;font-weight:800;color:#FAFAFA;letter-spacing:0.5px;">
            Iron Ore Beneficiation Plant
        </div>
        <div style="font-size:0.82rem;color:#6b7280;">
            Digital Twin — Real-Time Process Monitoring & Analysis Dashboard
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

import os
banner_path = os.path.join(os.path.dirname(__file__), "assets", "banner.jpg")
if os.path.exists(banner_path):
    # Reduce image size by placing it in a centered column layout
    c1, c2, c3 = st.columns([1, 6, 1])
    with c2:
        st.image(banner_path, use_container_width=True)

render_simulated_banner()

# ── Fetch plant state ──────────────────────────────────────────────────
state = get_process_state()

if state:
    plant = state.get("plant", {})
    equipment = state.get("equipment", {})
    alarms = state.get("alarms", [])

    # Alarm banner
    render_alarm_banner(alarms)

    # KPI cards
    render_kpi_row(plant)

    st.markdown("<br>", unsafe_allow_html=True)

    # ── Process Overview ───────────────────────────────────────────────
    col_left, col_right = st.columns([2, 1])

    with col_left:
        st.markdown('<div class="section-header">🌍 Interactive 3D Digital Twin</div>', unsafe_allow_html=True)

        # Load and inject data into Three.js template
        import os
        import json
        import streamlit.components.v1 as components
        threejs_dir = os.path.join(os.path.dirname(__file__), "threejs")
        template_path = os.path.join(threejs_dir, "plant_3d.html")

        try:
            with open(template_path, "r", encoding="utf-8") as f:
                html_template = f.read()

            # Inject live data
            html_content = html_template.replace(
                "__EQUIPMENT_DATA__", json.dumps(equipment)
            ).replace(
                "__PLANT_DATA__", json.dumps(plant)
            )

            components.html(html_content, height=620, scrolling=False)
        except Exception as e:
            st.error(f"Could not load 3D model: {e}")

    with col_right:
        st.markdown('<div class="section-header">🏭 Plant Summary</div>', unsafe_allow_html=True)

        summary_items = [
            ("Feed Rate", f"{plant.get('feed_rate', 0)} t/h", "🪨"),
            ("Fe Grade", f"{plant.get('fe_grade', 0)}%", "📈"),
            ("SiO₂", f"{plant.get('sio2', 0)}%", "📉"),
            ("Recovery", f"{plant.get('recovery', 0)}%", "♻️"),
            ("Production", f"{plant.get('production_rate', 0)} t/h", "📦"),
            ("Water Recovery", f"{plant.get('water_recovery', 0)}%", "💧"),
            ("Availability", f"{plant.get('equipment_availability', 0)}%", "✅"),
        ]

        for label, value, icon in summary_items:
            st.markdown(f"""
<div class="eq-card-param" style="padding:8px 0;">
<span class="eq-card-param-label">{icon} {label}</span>
<span class="eq-card-param-value">{value}</span>
</div>
            """, unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)

        # Equipment status overview
        st.markdown('<div class="section-header">📋 Equipment Status</div>', unsafe_allow_html=True)
        for eq_id, eq_data in equipment.items():
            if isinstance(eq_data, dict):
                name = eq_data.get("name", eq_id)
                status = eq_data.get("status", "IDLE")
                badge = render_status_badge(status)
                st.markdown(f"""
                <div style="display:flex;justify-content:space-between;align-items:center;padding:5px 0;border-bottom:1px solid rgba(255,255,255,0.04);">
                    <span style="font-size:0.82rem;color:#8892a4;">{name}</span>
                    {badge}
                </div>
                """, unsafe_allow_html=True)

else:
    st.error("Unable to fetch plant state. Please ensure the backend is running.")
    st.info("""
    **To start the application:**
    1. Start backend: `cd backend && uvicorn main:app --reload --port 8000`
    2. Start frontend: `cd frontend && streamlit run app.py`
    """)

# ── Auto-refresh ───────────────────────────────────────────────────────
st.markdown("---")
auto_refresh = st.checkbox("🔄 Auto-refresh (every 3 seconds)", value=False)
if auto_refresh:
    import time
    time.sleep(3)
    st.rerun()
