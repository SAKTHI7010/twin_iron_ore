"""
Shared Pydantic schemas for the Iron Ore Beneficiation Digital Twin.
Used by both frontend and backend to ensure consistent data structures.
All values are SIMULATED / DEMO data unless connected to a real plant data source.
"""

from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from enum import Enum
from datetime import datetime


class EquipmentStatus(str, Enum):
    RUNNING = "RUNNING"
    IDLE = "IDLE"
    WARNING = "WARNING"
    FAULT = "FAULT"
    MAINTENANCE = "MAINTENANCE"


class AlarmSeverity(str, Enum):
    INFO = "INFO"
    WARNING = "WARNING"
    CRITICAL = "CRITICAL"


# ── Equipment Detail Schemas ──────────────────────────────────────────────

class ROMFeedSchema(BaseModel):
    """Run of Mine - BHQ Ore (Hematite + Quartz)"""
    status: EquipmentStatus = EquipmentStatus.RUNNING
    feed_rate: float = Field(default=120.0, description="Feed rate (t/h)")
    fe_pct: float = Field(default=35.0, description="Fe content (%)")
    sio2_pct: float = Field(default=45.0, description="SiO2 content (%)")
    moisture: float = Field(default=4.5, description="Moisture (%)")


class HPGRSchema(BaseModel):
    """High Pressure Grinding Rolls"""
    status: EquipmentStatus = EquipmentStatus.RUNNING
    pressure: float = Field(default=145.0, description="Roll pressure (bar)")
    motor_power: float = Field(default=850.0, description="Motor power (kW)")
    throughput: float = Field(default=118.0, description="Throughput (t/h)")
    particle_size: float = Field(default=2.5, description="Product P80 (mm)")
    specific_energy: float = Field(default=2.8, description="Specific energy (kWh/t)")
    roll_speed: float = Field(default=22.5, description="Roll speed (rpm)")
    roll_gap: float = Field(default=28.0, description="Roll gap (mm)")


class CoarseMagSepSchema(BaseModel):
    """Coarse Magnetic Separation (LIMS)"""
    status: EquipmentStatus = EquipmentStatus.RUNNING
    slurry_flow: float = Field(default=185.0, description="Feed slurry flow (m³/h)")
    magnetic_intensity: float = Field(default=0.12, description="Magnetic intensity (T)")
    concentrate_flow: float = Field(default=95.0, description="Concentrate flow (t/h)")
    tails_flow: float = Field(default=23.0, description="Tails flow (t/h)")
    fe_recovery: float = Field(default=92.0, description="Fe recovery (%)")
    mass_pull: float = Field(default=80.5, description="Mass pull (%)")


class FineGrindingSchema(BaseModel):
    """Fine Grinding (Fine Tower Mill)"""
    status: EquipmentStatus = EquipmentStatus.RUNNING
    motor_power: float = Field(default=620.0, description="Motor power (kW)")
    density: float = Field(default=1.85, description="Slurry density (t/m³)")
    particle_size: float = Field(default=0.075, description="Product P80 (mm)")
    throughput: float = Field(default=90.0, description="Throughput (t/h)")
    specific_energy: float = Field(default=6.9, description="Specific energy (kWh/t)")
    media_charge: float = Field(default=78.0, description="Media charge level (%)")


class FineMagSepSchema(BaseModel):
    """Fine Magnetic Separation"""
    status: EquipmentStatus = EquipmentStatus.RUNNING
    slurry_flow: float = Field(default=145.0, description="Feed slurry flow (m³/h)")
    intensity: float = Field(default=0.18, description="Magnetic intensity (T)")
    fe_pct: float = Field(default=56.0, description="Concentrate Fe (%)")
    fe_recovery: float = Field(default=88.0, description="Fe recovery (%)")
    concentrate_flow: float = Field(default=78.0, description="Concentrate flow (t/h)")


class FurtherGrindingSchema(BaseModel):
    """Further Grinding (FTM + S/M Thickener)"""
    status: EquipmentStatus = EquipmentStatus.RUNNING
    power: float = Field(default=480.0, description="Motor power (kW)")
    density: float = Field(default=1.92, description="Slurry density (t/m³)")
    flow: float = Field(default=125.0, description="Slurry flow (m³/h)")
    particle_size: float = Field(default=0.045, description="Product P80 (mm)")
    specific_energy: float = Field(default=8.5, description="Specific energy (kWh/t)")


class FlotationSchema(BaseModel):
    """Flotation - Silica Rejection"""
    status: EquipmentStatus = EquipmentStatus.RUNNING
    air_flow: float = Field(default=45.0, description="Air flow (m³/min)")
    reagent_dose: float = Field(default=0.35, description="Reagent dosage (kg/t)")
    ph: float = Field(default=9.5, description="pH")
    fe_pct: float = Field(default=64.0, description="Concentrate Fe (%)")
    sio2_pct: float = Field(default=3.2, description="Concentrate SiO2 (%)")
    sio2_rejection: float = Field(default=85.0, description="SiO2 rejection (%)")
    cell_level: float = Field(default=72.0, description="Cell level (%)")


class ThickenerSchema(BaseModel):
    """Concentrate Thickener"""
    status: EquipmentStatus = EquipmentStatus.RUNNING
    bed_level: float = Field(default=2.8, description="Bed level (m)")
    underflow_density: float = Field(default=1.95, description="Underflow density (t/m³)")
    overflow_flow: float = Field(default=85.0, description="Overflow flow (m³/h)")
    flocculant_dose: float = Field(default=12.0, description="Flocculant dose (g/t)")
    torque: float = Field(default=45.0, description="Rake torque (%)")


class FinalProductSchema(BaseModel):
    """Final Product - High Grade Iron Concentrate"""
    status: EquipmentStatus = EquipmentStatus.RUNNING
    fe_grade: float = Field(default=65.5, description="Fe grade (%)")
    sio2_pct: float = Field(default=2.8, description="SiO2 (%)")
    al2o3_pct: float = Field(default=0.8, description="Al2O3 (%)")
    recovery: float = Field(default=82.0, description="Overall recovery (%)")
    production_rate: float = Field(default=75.0, description="Production rate (t/h)")
    moisture: float = Field(default=9.5, description="Moisture (%)")


class WaterRecoverySchema(BaseModel):
    """Water Recovery and Recycle"""
    status: EquipmentStatus = EquipmentStatus.RUNNING
    overflow_flow: float = Field(default=85.0, description="Overflow flow (m³/h)")
    water_recovery_pct: float = Field(default=91.0, description="Water recovery (%)")
    recycle_flow: float = Field(default=77.0, description="Recycled water flow (m³/h)")
    ph: float = Field(default=7.8, description="Water pH")
    tss: float = Field(default=45.0, description="Total suspended solids (mg/L)")


# ── Aggregate Schemas ─────────────────────────────────────────────────────

class EquipmentState(BaseModel):
    """All equipment states combined"""
    rom_feed: ROMFeedSchema = Field(default_factory=ROMFeedSchema)
    hpgr: HPGRSchema = Field(default_factory=HPGRSchema)
    coarse_mag_sep: CoarseMagSepSchema = Field(default_factory=CoarseMagSepSchema)
    fine_grinding: FineGrindingSchema = Field(default_factory=FineGrindingSchema)
    fine_mag_sep: FineMagSepSchema = Field(default_factory=FineMagSepSchema)
    further_grinding: FurtherGrindingSchema = Field(default_factory=FurtherGrindingSchema)
    flotation: FlotationSchema = Field(default_factory=FlotationSchema)
    thickener: ThickenerSchema = Field(default_factory=ThickenerSchema)
    final_product: FinalProductSchema = Field(default_factory=FinalProductSchema)
    water_recovery: WaterRecoverySchema = Field(default_factory=WaterRecoverySchema)


class PlantSummary(BaseModel):
    """High-level plant KPIs"""
    feed_rate: float = Field(default=120.0, description="Plant feed rate (t/h)")
    fe_grade: float = Field(default=65.5, description="Final Fe grade (%)")
    sio2: float = Field(default=2.8, description="Final SiO2 (%)")
    recovery: float = Field(default=82.0, description="Overall Fe recovery (%)")
    production_rate: float = Field(default=75.0, description="Production rate (t/h)")
    water_recovery: float = Field(default=91.0, description="Water recovery (%)")
    equipment_availability: float = Field(default=95.0, description="Equipment availability (%)")
    active_alarms: int = Field(default=0, description="Number of active alarms")


class AlarmSchema(BaseModel):
    """Alarm / anomaly event"""
    id: str
    timestamp: str
    equipment: str
    variable: str
    value: float
    threshold: float
    severity: AlarmSeverity
    message: str
    is_simulated: bool = True


class PlantStateResponse(BaseModel):
    """Complete plant state returned by /api/process/state"""
    timestamp: str
    simulation_running: bool
    data_source: str = "SIMULATED"
    plant: PlantSummary
    equipment: EquipmentState
    alarms: List[AlarmSchema] = []


class SimulationUpdateRequest(BaseModel):
    """Request to update simulation operating conditions"""
    feed_rate: Optional[float] = None
    fe_pct: Optional[float] = None
    sio2_pct: Optional[float] = None
    hpgr_pressure: Optional[float] = None
    hpgr_motor_power: Optional[float] = None
    flotation_reagent_dose: Optional[float] = None
    flotation_ph: Optional[float] = None
    flotation_air_flow: Optional[float] = None


class PredictionRequest(BaseModel):
    """Request for ML prediction"""
    feed_rate: float = 120.0
    fe_pct: float = 35.0
    sio2_pct: float = 45.0
    hpgr_pressure: float = 145.0
    motor_power: float = 850.0
    particle_size: float = 2.5
    slurry_flow: float = 185.0
    reagent_dose: float = 0.35
    ph: float = 9.5
    air_flow: float = 45.0


class PredictionResponse(BaseModel):
    """ML prediction response"""
    predicted_fe_grade: float
    predicted_recovery: float
    predicted_sio2: float
    predicted_production_rate: float
    confidence: str = "DEMO — synthetic model"
    model_type: str = "RandomForestRegressor"
    is_simulated: bool = True
    input_conditions: Dict[str, float] = {}


class HistoryRecord(BaseModel):
    """Single historical data point"""
    timestamp: str
    feed_rate: float
    fe_grade: float
    sio2: float
    recovery: float
    production_rate: float
    water_recovery: float


class HealthResponse(BaseModel):
    """Health check response"""
    status: str = "healthy"
    service: str = "iron-ore-digital-twin-backend"
    version: str = "1.0.0"
    simulation_active: bool = False
    data_source: str = "SIMULATED"
    timestamp: str = ""
