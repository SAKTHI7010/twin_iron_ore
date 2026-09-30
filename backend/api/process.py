"""
Process API routes — simulation control and plant state
"""

from fastapi import APIRouter, HTTPException
from typing import Dict, Any

router = APIRouter(prefix="/api", tags=["process"])

# Simulator instance will be injected from main.py
_simulator = None


def set_simulator(simulator):
    global _simulator
    _simulator = simulator


@router.get("/process/state")
async def get_process_state() -> Dict[str, Any]:
    """Get current simulated plant state"""
    if _simulator is None:
        raise HTTPException(status_code=503, detail="Simulator not initialized")
    return _simulator.get_state()


@router.post("/process/start")
async def start_simulation() -> Dict[str, str]:
    """Start the process simulation"""
    if _simulator is None:
        raise HTTPException(status_code=503, detail="Simulator not initialized")
    _simulator.start()
    return {"status": "started", "message": "Simulation started successfully"}


@router.post("/process/stop")
async def stop_simulation() -> Dict[str, str]:
    """Stop the process simulation"""
    if _simulator is None:
        raise HTTPException(status_code=503, detail="Simulator not initialized")
    _simulator.stop()
    return {"status": "stopped", "message": "Simulation stopped"}


@router.post("/process/reset")
async def reset_simulation() -> Dict[str, str]:
    """Reset the simulation to default values"""
    if _simulator is None:
        raise HTTPException(status_code=503, detail="Simulator not initialized")
    _simulator.reset()
    return {"status": "reset", "message": "Simulation reset to defaults"}


@router.post("/simulation/update")
async def update_simulation(updates: Dict[str, Any]) -> Dict[str, str]:
    """Update simulation operating conditions"""
    if _simulator is None:
        raise HTTPException(status_code=503, detail="Simulator not initialized")

    valid_keys = {
        "feed_rate", "feed_fe_pct", "feed_sio2_pct",
        "hpgr_pressure", "hpgr_motor_power",
        "flotation_reagent_dose", "flotation_ph", "flotation_air_flow"
    }

    filtered = {k: v for k, v in updates.items() if k in valid_keys}
    if not filtered:
        raise HTTPException(
            status_code=400,
            detail=f"No valid parameters. Use: {', '.join(sorted(valid_keys))}"
        )

    _simulator.update_config(filtered)
    return {
        "status": "updated",
        "message": f"Updated parameters: {', '.join(filtered.keys())}",
    }


@router.get("/history")
async def get_history(limit: int = 100) -> Dict[str, Any]:
    """Get historical simulated data"""
    if _simulator is None:
        raise HTTPException(status_code=503, detail="Simulator not initialized")
    records = _simulator.get_history(limit=min(limit, 500))
    return {
        "count": len(records),
        "data_source": "SIMULATED",
        "records": records,
    }
