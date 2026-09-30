"""
Reusable Streamlit UI components for KPI cards, status indicators, and styling.
"""

import streamlit as st
from typing import Dict, Any, Optional


def inject_custom_css():
    """Inject premium custom CSS for the dashboard"""
    st.markdown("""
    <style>
        /* ── Global Styles ─────────────────────────────────────────── */
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');

        .stApp {
            font-family: 'Inter', sans-serif;
        }

        /* ── KPI Card ──────────────────────────────────────────────── */
        .kpi-card {
            background: linear-gradient(135deg, #1a1d29 0%, #252836 100%);
            border: 1px solid rgba(255, 107, 53, 0.15);
            border-radius: 16px;
            padding: 20px 24px;
            text-align: center;
            transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
            position: relative;
            overflow: hidden;
        }
        .kpi-card::before {
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            height: 3px;
            background: linear-gradient(90deg, #FF6B35, #FF8F65, #FF6B35);
        }
        .kpi-card:hover {
            border-color: rgba(255, 107, 53, 0.4);
            transform: translateY(-2px);
            box-shadow: 0 8px 25px rgba(255, 107, 53, 0.15);
        }
        .kpi-label {
            font-size: 0.75rem;
            font-weight: 600;
            text-transform: uppercase;
            letter-spacing: 1.2px;
            color: #8892a4;
            margin-bottom: 8px;
        }
        .kpi-value {
            font-size: 1.8rem;
            font-weight: 800;
            color: #FAFAFA;
            line-height: 1.1;
        }
        .kpi-unit {
            font-size: 0.8rem;
            font-weight: 400;
            color: #6b7280;
            margin-left: 4px;
        }

        /* ── Status Badge ──────────────────────────────────────────── */
        .status-badge {
            display: inline-flex;
            align-items: center;
            gap: 6px;
            padding: 4px 12px;
            border-radius: 20px;
            font-size: 0.72rem;
            font-weight: 600;
            text-transform: uppercase;
            letter-spacing: 0.8px;
        }
        .status-running {
            background: rgba(16, 185, 129, 0.15);
            color: #10b981;
            border: 1px solid rgba(16, 185, 129, 0.3);
        }
        .status-warning {
            background: rgba(245, 158, 11, 0.15);
            color: #f59e0b;
            border: 1px solid rgba(245, 158, 11, 0.3);
        }
        .status-fault {
            background: rgba(239, 68, 68, 0.15);
            color: #ef4444;
            border: 1px solid rgba(239, 68, 68, 0.3);
        }
        .status-idle {
            background: rgba(107, 114, 128, 0.15);
            color: #6b7280;
            border: 1px solid rgba(107, 114, 128, 0.3);
        }

        /* ── Alarm Banner ──────────────────────────────────────────── */
        .alarm-banner {
            background: linear-gradient(135deg, rgba(239, 68, 68, 0.1), rgba(245, 158, 11, 0.1));
            border: 1px solid rgba(239, 68, 68, 0.3);
            border-radius: 12px;
            padding: 12px 18px;
            margin-bottom: 16px;
            display: flex;
            align-items: center;
            gap: 10px;
        }
        .alarm-banner-critical {
            border-color: rgba(239, 68, 68, 0.5);
        }
        .alarm-banner-warning {
            border-color: rgba(245, 158, 11, 0.5);
        }

        /* ── Equipment Card ────────────────────────────────────────── */
        .eq-card {
            background: linear-gradient(135deg, #1a1d29 0%, #252836 100%);
            border: 1px solid rgba(255, 255, 255, 0.08);
            border-radius: 14px;
            padding: 18px 22px;
            margin-bottom: 12px;
            transition: all 0.3s ease;
        }
        .eq-card:hover {
            border-color: rgba(255, 107, 53, 0.35);
            box-shadow: 0 4px 15px rgba(0, 0, 0, 0.3);
        }
        .eq-card-title {
            font-size: 0.95rem;
            font-weight: 700;
            color: #FAFAFA;
            margin-bottom: 10px;
        }
        .eq-card-param {
            display: flex;
            justify-content: space-between;
            padding: 4px 0;
            border-bottom: 1px solid rgba(255, 255, 255, 0.04);
            font-size: 0.82rem;
        }
        .eq-card-param-label {
            color: #8892a4;
        }
        .eq-card-param-value {
            color: #FAFAFA;
            font-weight: 600;
        }

        /* ── Section Header ────────────────────────────────────────── */
        .section-header {
            font-size: 1.1rem;
            font-weight: 700;
            color: #FAFAFA;
            margin: 24px 0 12px 0;
            padding-bottom: 8px;
            border-bottom: 2px solid rgba(255, 107, 53, 0.3);
        }

        /* ── Simulated Data Warning ────────────────────────────────── */
        .sim-banner {
            background: rgba(59, 130, 246, 0.08);
            border: 1px solid rgba(59, 130, 246, 0.25);
            border-radius: 10px;
            padding: 10px 16px;
            font-size: 0.78rem;
            color: #93c5fd;
            margin-bottom: 18px;
            display: flex;
            align-items: center;
            gap: 8px;
        }

        /* ── Process Flow Node ─────────────────────────────────────── */
        .flow-node {
            background: linear-gradient(135deg, #1e2130 0%, #2a2d3e 100%);
            border: 2px solid rgba(255, 107, 53, 0.25);
            border-radius: 12px;
            padding: 14px;
            text-align: center;
            min-height: 90px;
            display: flex;
            flex-direction: column;
            justify-content: center;
            align-items: center;
            transition: all 0.3s ease;
        }
        .flow-node:hover {
            border-color: #FF6B35;
            transform: scale(1.03);
        }
        .flow-node-title {
            font-size: 0.72rem;
            font-weight: 700;
            color: #FAFAFA;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }
        .flow-node-value {
            font-size: 1rem;
            font-weight: 800;
            color: #FF6B35;
            margin-top: 4px;
        }
        .flow-arrow {
            font-size: 1.5rem;
            color: #FF6B35;
            text-align: center;
            padding: 5px 0;
        }

        /* ── Hide Streamlit Defaults ───────────────────────────────── */
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
        header {visibility: hidden;}
    </style>
    """, unsafe_allow_html=True)


def render_kpi_card(label: str, value: Any, unit: str = "", color: str = "#FAFAFA"):
    """Render a single KPI card"""
    st.markdown(f"""
    <div class="kpi-card">
        <div class="kpi-label">{label}</div>
        <div class="kpi-value" style="color: {color};">
            {value}<span class="kpi-unit">{unit}</span>
        </div>
    </div>
    """, unsafe_allow_html=True)


def render_kpi_row(plant_data: Dict[str, Any]):
    """Render a row of KPI cards from plant summary data"""
    kpis = [
        ("Feed Rate", plant_data.get("feed_rate", 0), "t/h", "#3b82f6"),
        ("Fe Grade", plant_data.get("fe_grade", 0), "%", "#10b981"),
        ("SiO₂", plant_data.get("sio2", 0), "%", "#f59e0b"),
        ("Recovery", plant_data.get("recovery", 0), "%", "#8b5cf6"),
        ("Production", plant_data.get("production_rate", 0), "t/h", "#06b6d4"),
        ("Water Recovery", plant_data.get("water_recovery", 0), "%", "#14b8a6"),
        ("Availability", plant_data.get("equipment_availability", 0), "%", "#22c55e"),
        ("Alarms", plant_data.get("active_alarms", 0), "", "#ef4444"),
    ]

    cols = st.columns(len(kpis))
    for col, (label, value, unit, color) in zip(cols, kpis):
        with col:
            render_kpi_card(label, value, unit, color)


def render_status_badge(status: str) -> str:
    """Return HTML for a status badge"""
    css_class = {
        "RUNNING": "status-running",
        "WARNING": "status-warning",
        "FAULT": "status-fault",
        "IDLE": "status-idle",
        "MAINTENANCE": "status-idle",
    }.get(status, "status-idle")

    dot_color = {
        "RUNNING": "#10b981",
        "WARNING": "#f59e0b",
        "FAULT": "#ef4444",
        "IDLE": "#6b7280",
    }.get(status, "#6b7280")

    return f"""<span class="status-badge {css_class}">
        <span style="width:7px;height:7px;border-radius:50%;background:{dot_color};display:inline-block;"></span>
        {status}
    </span>"""


def render_simulated_banner():
    """Show the simulated data disclaimer"""
    st.markdown("""
    <div class="sim-banner">
        🔬 <strong>SIMULATED DATA</strong> — All values shown are from a process simulator for demonstration purposes.
        Not connected to a real plant data source.
    </div>
    """, unsafe_allow_html=True)


def render_alarm_banner(alarms: list):
    """Render alarm banner if there are active alarms"""
    if not alarms:
        return

    for alarm in alarms[:5]:
        severity = alarm.get("severity", "WARNING")
        css = "alarm-banner-critical" if severity == "CRITICAL" else "alarm-banner-warning"
        icon = "🔴" if severity == "CRITICAL" else "🟡"
        st.markdown(f"""
        <div class="alarm-banner {css}">
            {icon} <strong>[{severity}]</strong> {alarm.get('message', 'Unknown alarm')}
        </div>
        """, unsafe_allow_html=True)


def render_equipment_card(eq_id: str, eq_data: Dict[str, Any]):
    """Render an equipment detail card"""
    name = eq_data.get("name", eq_id)
    status = eq_data.get("status", "IDLE")
    badge = render_status_badge(status)

    params_html = ""
    skip_keys = {"name", "status"}
    for key, value in eq_data.items():
        if key in skip_keys:
            continue
        label = key.replace("_", " ").title()
        params_html += f"""
        <div class="eq-card-param">
            <span class="eq-card-param-label">{label}</span>
            <span class="eq-card-param-value">{value}</span>
        </div>"""

    st.markdown(f"""
    <div class="eq-card">
        <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:10px;">
            <div class="eq-card-title">{name}</div>
            {badge}
        </div>
        {params_html}
    </div>
    """, unsafe_allow_html=True)
