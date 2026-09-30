"""
Alarms API routes — anomaly detection and alarm management
"""

from fastapi import APIRouter, HTTPException
from typing import Dict, Any, List

router = APIRouter(prefix="/api", tags=["alarms"])

_simulator = None


def set_simulator(simulator):
    global _simulator
    _simulator = simulator


@router.get("/alarms")
async def get_alarms() -> Dict[str, Any]:
    """
    Return active alarms.
    All alarms are SIMULATED — based on rule-based thresholds applied to simulated data.
    """
    if _simulator is None:
        raise HTTPException(status_code=503, detail="Simulator not initialized")

    alarms = _simulator.get_alarms()
    return {
        "count": len(alarms),
        "data_source": "SIMULATED",
        "alarms": alarms,
    }
