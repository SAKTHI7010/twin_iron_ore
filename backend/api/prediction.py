"""
Prediction API routes — ML prediction endpoints
"""

from fastapi import APIRouter, HTTPException
from typing import Dict, Any

router = APIRouter(prefix="/api", tags=["prediction"])

_prediction_service = None


def set_prediction_service(service):
    global _prediction_service
    _prediction_service = service


@router.post("/prediction")
async def run_prediction(inputs: Dict[str, float]) -> Dict[str, Any]:
    """
    Run ML prediction with given input conditions.
    All predictions are from SYNTHETIC-trained models — demo only.
    """
    if _prediction_service is None:
        raise HTTPException(status_code=503, detail="Prediction service not initialized")

    required_fields = [
        "feed_rate", "fe_pct", "sio2_pct", "hpgr_pressure",
        "motor_power", "particle_size", "slurry_flow",
        "reagent_dose", "ph", "air_flow"
    ]

    # Provide defaults for missing fields
    defaults = {
        "feed_rate": 120.0, "fe_pct": 35.0, "sio2_pct": 45.0,
        "hpgr_pressure": 145.0, "motor_power": 850.0, "particle_size": 2.5,
        "slurry_flow": 185.0, "reagent_dose": 0.35, "ph": 9.5, "air_flow": 45.0,
    }

    for field in required_fields:
        if field not in inputs:
            inputs[field] = defaults[field]

    try:
        result = _prediction_service.predict(inputs)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Prediction failed: {str(e)}")
