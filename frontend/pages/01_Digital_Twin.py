"""
Digital Twin Page — Interactive 3D/2D Process Visualization
============================================================
Embeds Three.js 3D plant visualization with animated material flow.
Falls back to 2D process flow if WebGL is unavailable.
"""

import streamlit as st
import streamlit.components.v1 as components
import json
import os
from utils.api_client import get_process_state
from components.ui_components import (
    inject_custom_css, render_kpi_row, render_simulated_banner,
    render_alarm_banner, render_equipment_card, render_status_badge
)

st.set_page_config(page_title="Digital Twin — 3D Plant", page_icon="🏭", layout="wide")
inject_custom_css()

st.markdown("""
<div style="display:flex;align-items:center;gap:12px;margin-bottom:5px;">
    <span style="font-size:2rem;">🏭</span>
    <div>
        <div style="font-size:1.3rem;font-weight:800;color:#FAFAFA;">Interactive Digital Twin</div>
        <div style="font-size:0.78rem;color:#6b7280;">3D Process Visualization — Click equipment for details</div>
    </div>
</div>
""", unsafe_allow_html=True)

render_simulated_banner()

state = get_process_state()

if state:
    plant = state.get("plant", {})
    equipment = state.get("equipment", {})
    alarms = state.get("alarms", [])

    render_alarm_banner(alarms)
    render_kpi_row(plant)

    st.markdown("<br>", unsafe_allow_html=True)

    # ── 3D Visualization ───────────────────────────────────────────────
    use_3d = st.toggle("🎮 3D Visualization", value=True, help="Toggle between 3D (Three.js) and 2D process flow")

    if use_3d:
        # Load and inject data into Three.js template
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

        except FileNotFoundError:
            st.warning("3D visualization template not found. Showing 2D fallback.")
            use_3d = False
        except Exception as e:
            st.warning(f"3D visualization error: {e}. Showing 2D fallback.")
            use_3d = False

    if not use_3d:
        # ── 2D Fallback Process Flow ───────────────────────────────────
        st.markdown('<div class="section-header">🔄 Process Flow (2D View)</div>', unsafe_allow_html=True)

        stages = [
            ("🪨", "ROM Feed", "rom_feed"),
            ("⚙️", "HPGR", "hpgr"),
            ("🧲", "Coarse Mag Sep", "coarse_mag_sep"),
            ("🔄", "Fine Grinding", "fine_grinding"),
            ("🧲", "Fine Mag Sep", "fine_mag_sep"),
            ("🔄", "Further Grinding", "further_grinding"),
            ("🫧", "Flotation", "flotation"),
            ("🏗️", "Thickener", "thickener"),
            ("✅", "Final Product", "final_product"),
            ("💧", "Water Recovery", "water_recovery"),
        ]

        for i in range(0, len(stages), 5):
            cols = st.columns(5)
            for j, col in enumerate(cols):
                idx = i + j
                if idx < len(stages):
                    icon, name, eq_id = stages[idx]
                    eq_data = equipment.get(eq_id, {})
                    status = eq_data.get("status", "IDLE")
                    badge = render_status_badge(status)

                    with col:
                        st.markdown(f"""
                        <div class="flow-node">
                            <div style="font-size:1.6rem;">{icon}</div>
                            <div class="flow-node-title">{name}</div>
                            {badge}
                        </div>
                        """, unsafe_allow_html=True)

            if i == 0:
                st.markdown('<div class="flow-arrow">⬇</div>', unsafe_allow_html=True)

    # ── Equipment Detail Panel ─────────────────────────────────────────
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown('<div class="section-header">📋 Equipment Details</div>', unsafe_allow_html=True)

    eq_options = {eq_data.get("name", eq_id): eq_id
                  for eq_id, eq_data in equipment.items() if isinstance(eq_data, dict)}
    selected_name = st.selectbox("Select Equipment", list(eq_options.keys()))

    if selected_name:
        selected_id = eq_options[selected_name]
        eq_data = equipment.get(selected_id, {})
        render_equipment_card(selected_id, eq_data)

else:
    st.error("Cannot load plant data. Is the backend running?")

# Auto-refresh
st.markdown("---")
if st.checkbox("🔄 Auto-refresh (3s)", value=False, key="dt_refresh"):
    import time
    time.sleep(3)
    st.rerun()
