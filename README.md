# 🏭 Iron Ore Beneficiation Digital Twin

> **Digital Twin** of an iron ore beneficiation plant (BHQ Ore — Hematite + Quartz)
> with interactive 3D visualization, simulated real-time monitoring, ML predictions,
> and process analysis.

⚠️ **All data is SIMULATED** for demonstration purposes. Not connected to a real plant.

---

## 🖼️ Features

| Feature | Description |
|---------|-------------|
| **3D Digital Twin** | Interactive Three.js visualization with animated material flow |
| **Live Monitoring** | Real-time KPIs, equipment status, and alarm dashboard |
| **Process Analysis** | Historical trends, distributions, correlations, and statistics |
| **ML Prediction** | Fe grade, recovery, SiO₂, and production rate predictions |
| **What-if Simulation** | Adjust operating conditions and observe downstream effects |
| **Equipment Details** | Detailed parameters for all 10 process stages |
| **Anomaly Detection** | Rule-based alarm thresholds with simulated alerts |

## 🏗️ Architecture

```
User Browser
    → Streamlit Frontend (Python)
    → FastAPI Backend (Python)
    → Process Simulator / ML Models
```

### Future Architecture
```
Plant Sensors → PLC/SCADA → OPC UA → Data Ingestion
    → PostgreSQL/TimescaleDB → FastAPI → Streamlit Digital Twin
```

## 📊 Beneficiation Process

1. **ROM Feed** — BHQ Ore (Hematite + Quartz)
2. **HPGR** — High Pressure Grinding Rolls
3. **Coarse Magnetic Separation** — LIMS
4. **Fine Grinding** — Fine Tower Mill
5. **Fine Magnetic Separation**
6. **Further Grinding** — FTM + S/M Thickener
7. **Flotation** — Silica Rejection
8. **Concentrate Thickener**
9. **Final Product** — High Grade Iron Concentrate
10. **Water Recovery** — Recycle to process

## 🛠️ Technology Stack

| Component | Technology |
|-----------|-----------|
| Frontend | Streamlit |
| Backend | FastAPI |
| 3D Visualization | Three.js |
| Charts | Plotly |
| Data Processing | Pandas, NumPy |
| ML | Scikit-learn |
| Model Persistence | joblib |
| Deployment | Render |

## 🚀 Quick Start

### Prerequisites
- Python 3.9+
- pip

### 1. Clone the Repository
```bash
git clone <your-repo-url>
cd iron-ore-digital-twin
```

### 2. Start the Backend
```bash
cd backend
pip install -r requirements.txt
uvicorn main:app --reload --port 8000
```

The backend will be available at `http://localhost:8000`.
Check health: `http://localhost:8000/health`
API docs: `http://localhost:8000/docs`

### 3. Start the Frontend
In a **new terminal**:
```bash
cd frontend
pip install -r requirements.txt
streamlit run app.py
```

The frontend will open at `http://localhost:8501`.

### 4. Verify Connection
- Open `http://localhost:8501`
- Check the sidebar shows "Backend: 🟢 Connected"
- The simulation auto-starts on backend boot

## 🌐 Render Deployment

### Backend Service
| Setting | Value |
|---------|-------|
| Root Directory | `backend` |
| Build Command | `pip install -r requirements.txt` |
| Start Command | `uvicorn main:app --host 0.0.0.0 --port $PORT` |
| Health Check | `/health` |

### Frontend Service
| Setting | Value |
|---------|-------|
| Root Directory | `frontend` |
| Build Command | `pip install -r requirements.txt` |
| Start Command | `streamlit run app.py --server.address 0.0.0.0 --server.port $PORT` |
| Env Variable | `BACKEND_URL=https://<your-backend>.onrender.com` |

### Deployment Steps
1. Push code to GitHub
2. Deploy backend on Render → confirm `/health` returns 200
3. Copy backend URL
4. Deploy frontend on Render → set `BACKEND_URL` environment variable
5. Redeploy frontend
6. Open frontend URL and test

## 🔌 API Endpoints

| Method | Endpoint | Purpose |
|--------|----------|---------|
| `GET` | `/` | Backend info |
| `GET` | `/health` | Health check |
| `GET` | `/api/process/state` | Current plant state |
| `POST` | `/api/process/start` | Start simulation |
| `POST` | `/api/process/stop` | Stop simulation |
| `POST` | `/api/process/reset` | Reset to defaults |
| `GET` | `/api/equipment/{id}` | Equipment details |
| `POST` | `/api/simulation/update` | Update operating conditions |
| `POST` | `/api/prediction` | ML prediction |
| `GET` | `/api/alarms` | Active alarms |
| `GET` | `/api/history` | Historical data |

## 📁 Project Structure

```
digitaltwin/
├── backend/
│   ├── main.py                  # FastAPI application
│   ├── requirements.txt
│   ├── api/
│   │   ├── process.py           # Process/simulation endpoints
│   │   ├── equipment.py         # Equipment endpoints
│   │   ├── prediction.py        # ML prediction endpoints
│   │   └── alarms.py            # Alarm endpoints
│   ├── services/
│   │   ├── simulator.py         # Material-flow process simulator
│   │   └── prediction_service.py # ML prediction service
│   ├── models/                  # Trained ML models (.joblib)
│   └── tests/
│       └── test_api.py          # Tests for simulator & API
│
├── frontend/
│   ├── app.py                   # Streamlit main app (Home page)
│   ├── requirements.txt
│   ├── .streamlit/config.toml   # Streamlit configuration
│   ├── pages/
│   │   ├── 01_Digital_Twin.py   # 3D/2D visualization
│   │   ├── 02_Live_Monitoring.py # Real-time monitoring
│   │   ├── 03_Process_Analysis.py # Historical analysis
│   │   ├── 04_Prediction.py     # ML predictions
│   │   ├── 05_Simulation.py     # What-if scenarios
│   │   ├── 06_Equipment_Details.py # Equipment details
│   │   └── 07_About.py         # Project info
│   ├── components/
│   │   └── ui_components.py     # Reusable UI components
│   ├── threejs/
│   │   └── plant_3d.html        # Three.js 3D visualization
│   └── utils/
│       └── api_client.py        # FastAPI client
│
├── shared/
│   └── schemas.py               # Pydantic data schemas
│
├── .gitignore
├── render.yaml                  # Render deployment config
└── README.md
```

## 🧪 Running Tests

```bash
cd backend
pip install pytest httpx
pytest tests/ -v
```

## ⚠️ Important Notes

- All values are **SIMULATED** from a process simulator
- ML models are trained on **SYNTHETIC** data only
- Do not use predictions for real plant decisions
- The simulator uses simplified material-balance assumptions
- All alarms are labeled as **simulated anomalies**

## 🔮 Future Roadmap

1. **Real Plant Data** — Replace simulator with OPC-UA/PLC/SCADA
2. **TimescaleDB** — Persistent historical storage
3. **Advanced ML** — Train on real validated process data
4. **WebSocket Streaming** — Real-time data without polling
5. **Access Control** — Role-based security
6. **Mobile Support** — Responsive dashboard design

---

**Built with ❤️ using Streamlit, FastAPI & Three.js**
