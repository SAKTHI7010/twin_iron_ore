"""
About Page — Project architecture, technology stack, and deployment information
"""

import streamlit as st
from utils.api_client import check_health
from components.ui_components import inject_custom_css, render_simulated_banner

st.set_page_config(page_title="About", page_icon="ℹ️", layout="wide")
inject_custom_css()

st.markdown("""
<div style="display:flex;align-items:center;gap:12px;margin-bottom:5px;">
    <span style="font-size:2rem;">ℹ️</span>
    <div>
        <div style="font-size:1.3rem;font-weight:800;color:#FAFAFA;">About This Project</div>
        <div style="font-size:0.78rem;color:#6b7280;">Architecture, technology stack & deployment information</div>
    </div>
</div>
""", unsafe_allow_html=True)

render_simulated_banner()

# ── Project Overview ───────────────────────────────────────────────────
st.markdown("""
### 🏭 Iron Ore Beneficiation Digital Twin

This application is a **Digital Twin** of an iron ore beneficiation plant processing
**BHQ Ore (Hematite + Quartz)**. It provides:

- **Interactive 3D Visualization** of the complete beneficiation process
- **Real-time Monitoring** with simulated process data
- **Process Analysis** with historical trends and correlations
- **ML Predictions** for Fe grade, recovery, SiO₂, and production rate
- **What-if Simulation** for operating condition analysis
- **Anomaly Detection** with configurable alarm thresholds

---

### 📊 Beneficiation Process Flow

```
ROM Feed (BHQ Ore)
    ↓
HPGR (High Pressure Grinding Rolls)
    ↓
Coarse Magnetic Separation (LIMS)
    ↓
Fine Grinding (FTM)
    ↓
Fine Magnetic Separation
    ↓
Further Grinding (FTM + S/M Thickener)
    ↓
Flotation (Silica Rejection)
    ↓
Concentrate Thickener
    ↓
Final Product (High-Grade Iron Concentrate)
    ↓
Water Recovery → Recycled to Process
```

---
""")

# ── Architecture ───────────────────────────────────────────────────────
col1, col2 = st.columns(2)

with col1:
    st.markdown("""
    ### 🏗️ Architecture

    | Component | Technology |
    |-----------|-----------|
    | Frontend | Streamlit |
    | Backend | FastAPI |
    | 3D Visualization | Three.js |
    | Charts | Plotly |
    | Data Processing | Pandas / NumPy |
    | ML Models | Scikit-learn |
    | Model Persistence | joblib |
    | Deployment | Render |
    | Version Control | GitHub |

    #### Current Architecture
    ```
    User Browser
        → Streamlit Frontend
        → FastAPI Backend
        → Process Simulator / ML Models
    ```

    #### Future Architecture
    ```
    Plant Sensors → PLC/SCADA
        → OPC UA
        → Data Ingestion
        → PostgreSQL/TimescaleDB
        → FastAPI
        → Streamlit Digital Twin
    ```
    """)

with col2:
    st.markdown("""
    ### 🔌 API Endpoints

    | Method | Endpoint | Purpose |
    |--------|----------|---------|
    | GET | `/` | Backend info |
    | GET | `/health` | Health check |
    | GET | `/api/process/state` | Plant state |
    | POST | `/api/process/start` | Start sim |
    | POST | `/api/process/stop` | Stop sim |
    | POST | `/api/process/reset` | Reset sim |
    | GET | `/api/equipment/{id}` | Equipment detail |
    | POST | `/api/simulation/update` | Update params |
    | POST | `/api/prediction` | ML prediction |
    | GET | `/api/alarms` | Active alarms |
    | GET | `/api/history` | Historical data |
    """)

st.markdown("---")

# ── Deployment ─────────────────────────────────────────────────────────
st.markdown("""
### 🚀 Deployment

#### Local Development
```bash
# Start Backend
cd backend
pip install -r requirements.txt
uvicorn main:app --reload --port 8000

# Start Frontend (in a new terminal)
cd frontend
pip install -r requirements.txt
streamlit run app.py
```

#### Render Deployment
- **Backend:** Deploy as a Web Service with `uvicorn main:app --host 0.0.0.0 --port $PORT`
- **Frontend:** Deploy as a Web Service with `streamlit run app.py --server.address 0.0.0.0 --server.port $PORT`
- Set `BACKEND_URL` environment variable on the frontend service

---

### 🔮 Future Upgrades

1. **Real Plant Data Integration** — Replace simulator with OPC-UA/PLC/SCADA data
2. **PostgreSQL/TimescaleDB** — Persistent historical data storage
3. **Advanced ML Models** — Train on real process data
4. **WebSocket Streaming** — Replace REST polling with real-time streaming
5. **Role-Based Access Control** — Secure access to plant data
6. **Mobile-Responsive Design** — Dashboard for mobile devices
""")

# ── Backend Status ─────────────────────────────────────────────────────
st.markdown("---")
st.markdown("### 🔗 Backend Connection Status")

health = check_health()
if health:
    st.success(f"✅ Backend connected — {health.get('service', 'N/A')} v{health.get('version', 'N/A')}")
    st.json(health)
else:
    st.error("❌ Backend not connected")

st.markdown("""
---
<div style="text-align:center;padding:20px;color:#4b5563;font-size:0.75rem;">
    Iron Ore Beneficiation Digital Twin v1.0.0 · Built with Streamlit, FastAPI & Three.js<br>
    All data is <strong>SIMULATED</strong> for demonstration purposes only.<br>
    BHQ Ore — Hematite + Quartz
</div>
""", unsafe_allow_html=True)
