"""
API Client for communicating with the FastAPI backend.
"""

import os
import requests
import streamlit as st
from typing import Dict, Any, Optional

# Try to get BACKEND_URL from Streamlit secrets first, then environment variables
try:
    BACKEND_URL = st.secrets["BACKEND_URL"]
except (FileNotFoundError, KeyError):
    BACKEND_URL = os.environ.get("BACKEND_URL", "http://localhost:8000")

# Clean the URL to prevent errors if the user accidentally added /docs or /
BACKEND_URL = BACKEND_URL.strip()
if BACKEND_URL.endswith("/docs"):
    BACKEND_URL = BACKEND_URL[:-5]
if BACKEND_URL.endswith("/"):
    BACKEND_URL = BACKEND_URL[:-1]

REQUEST_TIMEOUT = 10  # seconds


def _get(endpoint: str, params: Optional[Dict] = None) -> Optional[Dict[str, Any]]:
    """Make a GET request to the backend"""
    try:
        url = f"{BACKEND_URL}{endpoint}"
        response = requests.get(url, params=params, timeout=REQUEST_TIMEOUT)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.ConnectionError:
        st.error(f"⚠️ Cannot connect to backend at {BACKEND_URL}. Is the backend running?")
        return None
    except requests.exceptions.Timeout:
        st.error("⚠️ Backend request timed out.")
        return None
    except Exception as e:
        st.error(f"⚠️ API Error: {str(e)}")
        return None


def _post(endpoint: str, json_data: Optional[Dict] = None) -> Optional[Dict[str, Any]]:
    """Make a POST request to the backend"""
    try:
        url = f"{BACKEND_URL}{endpoint}"
        response = requests.post(url, json=json_data, timeout=REQUEST_TIMEOUT)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.ConnectionError:
        st.error(f"⚠️ Cannot connect to backend at {BACKEND_URL}. Is the backend running?")
        return None
    except requests.exceptions.Timeout:
        st.error("⚠️ Backend request timed out.")
        return None
    except Exception as e:
        st.error(f"⚠️ API Error: {str(e)}")
        return None


# ── Public API Functions ───────────────────────────────────────────────

def check_health() -> Optional[Dict]:
    return _get("/health")


def get_process_state() -> Optional[Dict]:
    return _get("/api/process/state")


def start_simulation() -> Optional[Dict]:
    return _post("/api/process/start")


def stop_simulation() -> Optional[Dict]:
    return _post("/api/process/stop")


def reset_simulation() -> Optional[Dict]:
    return _post("/api/process/reset")


def get_equipment(equipment_id: str) -> Optional[Dict]:
    return _get(f"/api/equipment/{equipment_id}")


def list_equipment() -> Optional[Dict]:
    return _get("/api/equipment")


def update_simulation(params: Dict[str, float]) -> Optional[Dict]:
    return _post("/api/simulation/update", json_data=params)


def run_prediction(inputs: Dict[str, float]) -> Optional[Dict]:
    return _post("/api/prediction", json_data=inputs)


def get_alarms() -> Optional[Dict]:
    return _get("/api/alarms")


def get_history(limit: int = 100) -> Optional[Dict]:
    return _get("/api/history", params={"limit": limit})
