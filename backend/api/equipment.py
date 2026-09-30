"""
Equipment API routes — individual equipment details
"""

from fastapi import APIRouter, HTTPException
from typing import Dict, Any

router = APIRouter(prefix="/api", tags=["equipment"])

_simulator = None


def set_simulator(simulator):
    global _simulator
    _simulator = simulator


EQUIPMENT_IDS = [
    "rom_feed", "hpgr", "coarse_mag_sep", "fine_grinding",
    "fine_mag_sep", "further_grinding", "flotation",
    "thickener", "final_product", "water_recovery"
]


@router.get("/equipment")
async def list_equipment() -> Dict[str, Any]:
    """List all available equipment IDs"""
    return {
        "equipment_ids": EQUIPMENT_IDS,
        "count": len(EQUIPMENT_IDS),
    }


@router.get("/equipment/{equipment_id}")
async def get_equipment(equipment_id: str) -> Dict[str, Any]:
    """Get detailed parameters for a specific equipment unit"""
    if _simulator is None:
        raise HTTPException(status_code=503, detail="Simulator not initialized")

    if equipment_id not in EQUIPMENT_IDS:
        raise HTTPException(
            status_code=404,
            detail=f"Equipment '{equipment_id}' not found. Available: {', '.join(EQUIPMENT_IDS)}"
        )

    result = _simulator.get_equipment_detail(equipment_id)
    if result is None:
        raise HTTPException(status_code=404, detail=f"No data for equipment '{equipment_id}'")

    return result
