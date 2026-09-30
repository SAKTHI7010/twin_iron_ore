"""
Iron Ore Beneficiation Digital Twin — FastAPI Backend
======================================================
Main application entry point.
All data is SIMULATED unless connected to a real plant data source.
"""

import os
from datetime import datetime, timezone
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from services.simulator import ProcessSimulator
from services.prediction_service import PredictionService
from api import process, equipment, prediction, alarms

# ── Initialize Application ─────────────────────────────────────────────

app = FastAPI(
    title="Iron Ore Beneficiation Digital Twin API",
    description=(
        "Backend API for the Iron Ore Beneficiation Digital Twin. "
        "All data is SIMULATED unless connected to a real plant data source."
    ),
    version="1.0.0",
)

# CORS — allow Streamlit frontend to connect
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, restrict to frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Initialize Services ────────────────────────────────────────────────

simulator = ProcessSimulator()
prediction_service = PredictionService(
    model_dir=os.path.join(os.path.dirname(__file__), "models")
)

# Inject dependencies into route modules
process.set_simulator(simulator)
equipment.set_simulator(simulator)
alarms.set_simulator(simulator)
prediction.set_prediction_service(prediction_service)

# Register routers
app.include_router(process.router)
app.include_router(equipment.router)
app.include_router(prediction.router)
app.include_router(alarms.router)


# ── Root & Health Endpoints ─────────────────────────────────────────────

@app.get("/")
async def root():
    return {
        "service": "Iron Ore Beneficiation Digital Twin API",
        "version": "1.0.0",
        "data_source": "SIMULATED",
        "docs": "/docs",
    }


@app.get("/health")
async def health():
    return {
        "status": "healthy",
        "service": "iron-ore-digital-twin-backend",
        "version": "1.0.0",
        "simulation_active": simulator.is_running,
        "data_source": "SIMULATED",
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }


# ── Auto-start simulation on boot ──────────────────────────────────────

@app.on_event("startup")
async def startup_event():
    """Start the simulator automatically on app startup"""
    simulator.start()


@app.on_event("shutdown")
async def shutdown_event():
    """Clean up on shutdown"""
    simulator.stop()
