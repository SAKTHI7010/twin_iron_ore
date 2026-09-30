"""
Equipment Details Page — Detailed parameters for all equipment units
"""

import streamlit as st
import plotly.graph_objects as go
from utils.api_client import get_process_state, get_equipment
from components.ui_components import (
    inject_custom_css, render_simulated_banner, render_equipment_card, render_status_badge
)

st.set_page_config(page_title="Equipment Details", page_icon="🔧", layout="wide")
inject_custom_css()

st.markdown("""
<div style="display:flex;align-items:center;gap:12px;margin-bottom:5px;">
    <span style="font-size:2rem;">🔧</span>
    <div>
        <div style="font-size:1.3rem;font-weight:800;color:#FAFAFA;">Equipment Details</div>
        <div style="font-size:0.78rem;color:#6b7280;">Detailed parameters for HPGR, separators, mills, flotation & thickener</div>
    </div>
</div>
""", unsafe_allow_html=True)

render_simulated_banner()

state = get_process_state()

if state:
    equipment = state.get("equipment", {})

    # Equipment selector
    EQUIPMENT_INFO = {
        "rom_feed": {"icon": "🪨", "description": "Run of Mine — BHQ Ore (Hematite + Quartz). Raw ore feed to the plant."},
        "hpgr": {"icon": "⚙️", "description": "High Pressure Grinding Rolls — Size reduction of ROM ore using high-pressure rollers."},
        "coarse_mag_sep": {"icon": "🧲", "description": "Coarse Magnetic Separation (LIMS) — Low intensity magnetic separation of coarse ground material."},
        "fine_grinding": {"icon": "🔄", "description": "Fine Grinding (FTM) — Fine tower mill grinding to liberate iron minerals from gangue."},
        "fine_mag_sep": {"icon": "🧲", "description": "Fine Magnetic Separation — Magnetic concentration of fine ground slurry."},
        "further_grinding": {"icon": "🔄", "description": "Further Grinding (FTM + S/M Thickener) — Additional grinding for further liberation."},
        "flotation": {"icon": "🫧", "description": "Flotation — Silica rejection through reverse flotation using amine-based collectors."},
        "thickener": {"icon": "🏗️", "description": "Concentrate Thickener — Dewatering of concentrate slurry."},
        "final_product": {"icon": "✅", "description": "Final Product — High-grade iron concentrate output."},
        "water_recovery": {"icon": "💧", "description": "Water Recovery & Recycle — Process water recovery for reuse."},
    }

    # Tab per equipment
    eq_ids = list(equipment.keys())
    eq_names = [equipment[eid].get("name", eid) if isinstance(equipment[eid], dict) else eid for eid in eq_ids]

    tabs = st.tabs([f"{EQUIPMENT_INFO.get(eid, {}).get('icon', '🏭')} {name}" for eid, name in zip(eq_ids, eq_names)])

    for tab, eq_id in zip(tabs, eq_ids):
        with tab:
            eq_data = equipment.get(eq_id, {})
            if not isinstance(eq_data, dict):
                continue

            info = EQUIPMENT_INFO.get(eq_id, {})
            status = eq_data.get("status", "IDLE")

            # Header
            col_h1, col_h2 = st.columns([3, 1])
            with col_h1:
                st.markdown(f"""
                <div style="font-size:0.85rem;color:#8892a4;margin-bottom:12px;">
                    {info.get('description', '')}
                </div>
                """, unsafe_allow_html=True)
            with col_h2:
                st.markdown(f"""
                <div style="text-align:right;">
                    {render_status_badge(status)}
                </div>
                """, unsafe_allow_html=True)

            # Parameters in two columns
            skip_keys = {"name", "status"}
            params = {k: v for k, v in eq_data.items() if k not in skip_keys}

            col_l, col_r = st.columns(2)

            param_items = list(params.items())
            mid = len(param_items) // 2 + len(param_items) % 2

            with col_l:
                render_equipment_card(eq_id, {**{k: v for k, v in param_items[:mid]}, "name": eq_data.get("name", ""), "status": status})

            with col_r:
                if param_items[mid:]:
                    # Bar chart of parameters
                    labels = [k.replace("_", " ").title() for k, _ in param_items]
                    values = [float(v) if isinstance(v, (int, float)) else 0 for _, v in param_items]

                    fig = go.Figure()
                    fig.add_trace(go.Bar(
                        x=labels, y=values,
                        marker_color=['#FF6B35' if i % 2 == 0 else '#3b82f6' for i in range(len(values))],
                        marker_line_width=0,
                        opacity=0.85,
                    ))
                    fig.update_layout(
                        template='plotly_dark',
                        paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(26,29,41,0.8)',
                        height=300, margin=dict(l=40, r=20, t=20, b=80),
                        xaxis=dict(showgrid=False, tickangle=-45, tickfont=dict(size=10)),
                        yaxis=dict(showgrid=True, gridcolor='rgba(255,255,255,0.05)'),
                        showlegend=False,
                    )
                    st.plotly_chart(fig, use_container_width=True)

else:
    st.error("Cannot load equipment data. Is the backend running?")

# Auto-refresh
st.markdown("---")
if st.checkbox("🔄 Auto-refresh (3s)", value=False, key="eq_refresh"):
    import time
    time.sleep(3)
    st.rerun()
