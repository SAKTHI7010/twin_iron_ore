"""
Iron Ore Beneficiation Process Simulator
=========================================
Material-flow simulation where upstream conditions influence downstream values.
All values are SIMULATED assumptions — not validated plant physics.

Process Flow:
  ROM Feed → HPGR → Coarse Mag Sep → Fine Grinding → Fine Mag Sep →
  Further Grinding → Flotation → Thickener → Final Product + Water Recovery
"""

import random
import math
import time
import threading
from datetime import datetime, timezone
from typing import Dict, Any, Optional, List
import numpy as np


class ProcessSimulator:
    """
    Realistic material-balance process simulator.
    Upstream values influence downstream values through configurable relationships.
    Bounded noise is added for realism.
    """

    # ── Configurable base assumptions ──────────────────────────────────
    DEFAULT_CONFIG = {
        "feed_rate": 120.0,         # t/h
        "feed_fe_pct": 35.0,        # %
        "feed_sio2_pct": 45.0,      # %
        "feed_moisture": 4.5,       # %
        "hpgr_pressure": 145.0,     # bar
        "hpgr_motor_power": 850.0,  # kW
        "flotation_reagent_dose": 0.35,  # kg/t
        "flotation_ph": 9.5,
        "flotation_air_flow": 45.0,  # m³/min
    }

    # Operating limits for anomaly detection
    OPERATING_LIMITS = {
        "hpgr_motor_power": {"low": 600, "high": 1100, "unit": "kW"},
        "hpgr_pressure": {"low": 100, "high": 200, "unit": "bar"},
        "hpgr_throughput": {"low": 80, "high": 160, "unit": "t/h"},
        "feed_rate": {"low": 60, "high": 180, "unit": "t/h"},
        "fe_grade": {"low": 60, "high": 70, "unit": "%"},
        "sio2_final": {"low": 1.0, "high": 5.0, "unit": "%"},
        "recovery": {"low": 70, "high": 95, "unit": "%"},
        "flotation_ph": {"low": 8.5, "high": 11.0, "unit": "pH"},
        "thickener_bed_level": {"low": 1.0, "high": 5.0, "unit": "m"},
        "water_recovery": {"low": 80, "high": 98, "unit": "%"},
    }

    def __init__(self):
        self.config = dict(self.DEFAULT_CONFIG)
        self._running = False
        self._state: Dict[str, Any] = {}
        self._history: List[Dict[str, Any]] = []
        self._alarms: List[Dict[str, Any]] = []
        self._alarm_counter = 0
        self._tick_count = 0
        self._lock = threading.Lock()
        self._timer: Optional[threading.Timer] = None

        # Initialize state
        self._compute_state()

    # ── Public Control Methods ─────────────────────────────────────────

    def start(self):
        """Start continuous simulation"""
        with self._lock:
            self._running = True
        self._schedule_tick()

    def stop(self):
        """Stop continuous simulation"""
        with self._lock:
            self._running = False
        if self._timer:
            self._timer.cancel()
            self._timer = None

    def reset(self):
        """Reset to default configuration"""
        self.stop()
        with self._lock:
            self.config = dict(self.DEFAULT_CONFIG)
            self._history.clear()
            self._alarms.clear()
            self._alarm_counter = 0
            self._tick_count = 0
            self._compute_state()

    @property
    def is_running(self) -> bool:
        return self._running

    def get_state(self) -> Dict[str, Any]:
        """Get current plant state (thread-safe)"""
        with self._lock:
            if self._running:
                self._compute_state()
            return dict(self._state)

    def get_history(self, limit: int = 100) -> List[Dict[str, Any]]:
        """Get historical state records"""
        with self._lock:
            return list(self._history[-limit:])

    def get_alarms(self) -> List[Dict[str, Any]]:
        """Get active alarms"""
        with self._lock:
            return list(self._alarms[-50:])

    def update_config(self, updates: Dict[str, Any]):
        """Update operating conditions"""
        with self._lock:
            for key, value in updates.items():
                if key in self.config and value is not None:
                    self.config[key] = float(value)
            self._compute_state()

    def get_equipment_detail(self, equipment_id: str) -> Optional[Dict[str, Any]]:
        """Get detailed state for a specific equipment"""
        with self._lock:
            equipment = self._state.get("equipment", {})
            if equipment_id in equipment:
                return {
                    "equipment_id": equipment_id,
                    "data": equipment[equipment_id],
                    "timestamp": self._state.get("timestamp", ""),
                    "data_source": "SIMULATED"
                }
            return None

    # ── Simulation Tick ────────────────────────────────────────────────

    def _schedule_tick(self):
        """Schedule next simulation tick"""
        if self._running:
            self._timer = threading.Timer(2.0, self._tick)
            self._timer.daemon = True
            self._timer.start()

    def _tick(self):
        """Execute one simulation tick"""
        with self._lock:
            self._compute_state()
            self._record_history()
            self._check_alarms()
            self._tick_count += 1
        self._schedule_tick()

    # ── Core Material-Flow Simulation ──────────────────────────────────

    def _noise(self, base: float, pct: float = 0.02) -> float:
        """Add bounded Gaussian noise"""
        return base * (1.0 + random.gauss(0, pct))

    def _clamp(self, value: float, low: float, high: float) -> float:
        return max(low, min(high, value))

    def _compute_state(self):
        """
        Compute complete plant state using material-flow dependencies.
        Each downstream stage depends on upstream outputs.
        """
        now = datetime.now(timezone.utc).isoformat()
        cfg = self.config

        # ── 1. ROM Feed ───────────────────────────────────────────────
        feed_rate = self._noise(cfg["feed_rate"], 0.03)
        feed_fe = self._noise(cfg["feed_fe_pct"], 0.02)
        feed_sio2 = self._noise(cfg["feed_sio2_pct"], 0.02)
        feed_moisture = self._noise(cfg["feed_moisture"], 0.05)

        rom_status = self._equipment_status(feed_rate, 60, 180)

        # ── 2. HPGR ──────────────────────────────────────────────────
        hpgr_pressure = self._noise(cfg["hpgr_pressure"], 0.03)
        hpgr_motor_power = self._noise(cfg["hpgr_motor_power"], 0.04)

        # Throughput depends on feed rate and pressure
        pressure_efficiency = self._clamp(hpgr_pressure / 150.0, 0.7, 1.2)
        hpgr_throughput = self._noise(feed_rate * 0.985 * pressure_efficiency, 0.02)

        # Particle size reduction depends on pressure and motor power
        power_factor = self._clamp(hpgr_motor_power / 900.0, 0.6, 1.3)
        hpgr_particle_size = self._noise(
            self._clamp(3.5 / (pressure_efficiency * power_factor), 1.5, 5.0), 0.05
        )
        hpgr_specific_energy = self._noise(hpgr_motor_power / max(hpgr_throughput, 1), 0.02)
        hpgr_roll_speed = self._noise(22.5, 0.02)
        hpgr_roll_gap = self._noise(28.0 / pressure_efficiency, 0.03)

        hpgr_status = self._equipment_status(hpgr_motor_power, 600, 1100)

        # ── 3. Coarse Magnetic Separation (LIMS) ──────────────────────
        # Performance depends on particle size from HPGR
        size_factor = self._clamp(1.0 - (hpgr_particle_size - 2.5) * 0.1, 0.75, 1.0)
        mag_slurry_flow = self._noise(hpgr_throughput * 1.6, 0.03)
        mag_intensity = self._noise(0.12, 0.03)
        mag_recovery = self._noise(self._clamp(92.0 * size_factor, 80, 97), 0.02)
        mag_concentrate_flow = self._noise(hpgr_throughput * mag_recovery / 100.0, 0.02)
        mag_tails_flow = self._noise(hpgr_throughput - mag_concentrate_flow, 0.05)
        mag_mass_pull = self._noise(mag_concentrate_flow / max(hpgr_throughput, 1) * 100, 0.02)

        # Fe content increases after magnetic separation
        mag_fe_factor = self._clamp(1.35 + (mag_recovery - 85) * 0.005, 1.2, 1.55)

        coarse_mag_status = self._equipment_status(mag_recovery, 75, 98)

        # ── 4. Fine Grinding (FTM) ────────────────────────────────────
        fg_throughput = self._noise(mag_concentrate_flow * 0.95, 0.03)
        fg_motor_power = self._noise(620.0 * (fg_throughput / 90.0), 0.04)
        fg_density = self._noise(1.85, 0.02)

        # Particle size depends on power applied
        fg_power_ratio = self._clamp(fg_motor_power / 620.0, 0.5, 1.5)
        fg_particle_size = self._noise(
            self._clamp(0.075 / fg_power_ratio, 0.04, 0.15), 0.05
        )
        fg_specific_energy = self._noise(fg_motor_power / max(fg_throughput, 1), 0.02)
        fg_media_charge = self._noise(78.0, 0.03)

        fg_status = self._equipment_status(fg_motor_power, 350, 900)

        # ── 5. Fine Magnetic Separation ───────────────────────────────
        # Better with finer particle sizes
        fine_size_factor = self._clamp(1.0 - (fg_particle_size - 0.075) * 5.0, 0.7, 1.05)
        fine_mag_slurry = self._noise(fg_throughput * 1.7, 0.03)
        fine_mag_intensity = self._noise(0.18, 0.03)
        fine_mag_fe = self._noise(
            self._clamp(feed_fe * mag_fe_factor * fine_size_factor * 1.15, 48, 62), 0.015
        )
        fine_mag_recovery = self._noise(
            self._clamp(88.0 * fine_size_factor, 75, 95), 0.02
        )
        fine_mag_concentrate = self._noise(fg_throughput * fine_mag_recovery / 100.0, 0.02)

        fine_mag_status = self._equipment_status(fine_mag_recovery, 70, 96)

        # ── 6. Further Grinding (FTM + S/M Thickener) ────────────────
        fug_flow = self._noise(fine_mag_concentrate * 1.65, 0.03)
        fug_power = self._noise(480.0 * (fine_mag_concentrate / 78.0), 0.04)
        fug_density = self._noise(1.92, 0.02)
        fug_power_ratio = self._clamp(fug_power / 480.0, 0.5, 1.5)
        fug_particle_size = self._noise(
            self._clamp(0.045 / fug_power_ratio, 0.02, 0.08), 0.05
        )
        fug_specific_energy = self._noise(fug_power / max(fine_mag_concentrate, 1), 0.02)

        fug_status = self._equipment_status(fug_power, 250, 700)

        # ── 7. Flotation (Silica Rejection) ───────────────────────────
        air_flow = self._noise(cfg["flotation_air_flow"], 0.04)
        reagent_dose = self._noise(cfg["flotation_reagent_dose"], 0.05)
        flot_ph = self._noise(cfg["flotation_ph"], 0.02)

        # SiO2 rejection depends on reagent dose, pH, air flow, and particle size
        reagent_factor = self._clamp(reagent_dose / 0.35, 0.6, 1.4)
        ph_factor = self._clamp(1.0 - abs(flot_ph - 9.5) * 0.08, 0.6, 1.1)
        air_factor = self._clamp(air_flow / 45.0, 0.7, 1.3)
        size_liberation = self._clamp(1.0 - (fug_particle_size - 0.045) * 8.0, 0.6, 1.1)

        sio2_rejection = self._noise(
            self._clamp(85.0 * reagent_factor * ph_factor * air_factor * size_liberation, 60, 96), 0.02
        )

        # Calculate Fe grade after flotation
        intermediate_fe = fine_mag_fe * 1.15
        flot_fe = self._noise(
            self._clamp(intermediate_fe * (1 + (sio2_rejection - 85) * 0.002), 58, 68), 0.01
        )
        flot_sio2 = self._noise(
            self._clamp(feed_sio2 * (1 - sio2_rejection / 100.0) * 0.35, 1.5, 8.0), 0.03
        )
        flot_cell_level = self._noise(72.0, 0.04)

        flot_status = self._equipment_status(flot_ph, 8.0, 11.5)

        # ── 8. Concentrate Thickener ──────────────────────────────────
        thick_bed_level = self._noise(2.8, 0.06)
        thick_underflow_density = self._noise(1.95, 0.02)
        thick_overflow = self._noise(fine_mag_concentrate * 1.1, 0.04)
        thick_flocculant = self._noise(12.0, 0.05)
        thick_torque = self._noise(45.0, 0.05)

        thick_status = self._equipment_status(thick_bed_level, 0.5, 5.5)

        # ── 9. Final Product ──────────────────────────────────────────
        final_fe = self._noise(
            self._clamp(flot_fe * 1.02, 60, 69), 0.008
        )
        final_sio2 = self._noise(
            self._clamp(flot_sio2 * 0.9, 1.0, 6.0), 0.02
        )
        final_al2o3 = self._noise(0.8, 0.05)

        # Recovery depends on cumulative efficiencies
        cumulative_recovery = (
            (mag_recovery / 100.0)
            * (fine_mag_recovery / 100.0)
            * (sio2_rejection / 100.0)
            * 1.08  # correction factor
        ) * 100.0
        final_recovery = self._noise(
            self._clamp(cumulative_recovery, 65, 95), 0.015
        )
        final_production = self._noise(
            feed_rate * final_recovery / 100.0 * 0.65, 0.02
        )
        final_moisture = self._noise(9.5, 0.04)

        final_status = "RUNNING"

        # ── 10. Water Recovery ────────────────────────────────────────
        water_overflow = self._noise(thick_overflow * 0.95, 0.03)
        water_recovery_pct = self._noise(
            self._clamp(91.0 - (thick_bed_level - 2.8) * 2.0, 80, 98), 0.02
        )
        water_recycle = self._noise(water_overflow * water_recovery_pct / 100.0, 0.02)
        water_ph = self._noise(7.8, 0.03)
        water_tss = self._noise(45.0, 0.08)

        water_status = self._equipment_status(water_recovery_pct, 78, 99)

        # ── Assemble Full State ───────────────────────────────────────
        self._state = {
            "timestamp": now,
            "simulation_running": self._running,
            "data_source": "SIMULATED",
            "plant": {
                "feed_rate": round(feed_rate, 1),
                "fe_grade": round(final_fe, 1),
                "sio2": round(final_sio2, 2),
                "recovery": round(final_recovery, 1),
                "production_rate": round(final_production, 1),
                "water_recovery": round(water_recovery_pct, 1),
                "equipment_availability": round(self._calc_availability(), 1),
                "active_alarms": len(self._alarms),
            },
            "equipment": {
                "rom_feed": {
                    "name": "Run of Mine Feed",
                    "status": rom_status,
                    "feed_rate": round(feed_rate, 1),
                    "fe_pct": round(feed_fe, 1),
                    "sio2_pct": round(feed_sio2, 1),
                    "moisture": round(feed_moisture, 1),
                },
                "hpgr": {
                    "name": "High Pressure Grinding Rolls",
                    "status": hpgr_status,
                    "pressure": round(hpgr_pressure, 1),
                    "motor_power": round(hpgr_motor_power, 1),
                    "throughput": round(hpgr_throughput, 1),
                    "particle_size": round(hpgr_particle_size, 2),
                    "specific_energy": round(hpgr_specific_energy, 2),
                    "roll_speed": round(hpgr_roll_speed, 1),
                    "roll_gap": round(hpgr_roll_gap, 1),
                },
                "coarse_mag_sep": {
                    "name": "Coarse Magnetic Separation (LIMS)",
                    "status": coarse_mag_status,
                    "slurry_flow": round(mag_slurry_flow, 1),
                    "magnetic_intensity": round(mag_intensity, 3),
                    "concentrate_flow": round(mag_concentrate_flow, 1),
                    "tails_flow": round(mag_tails_flow, 1),
                    "fe_recovery": round(mag_recovery, 1),
                    "mass_pull": round(mag_mass_pull, 1),
                },
                "fine_grinding": {
                    "name": "Fine Grinding (FTM)",
                    "status": fg_status,
                    "motor_power": round(fg_motor_power, 1),
                    "density": round(fg_density, 2),
                    "particle_size": round(fg_particle_size, 4),
                    "throughput": round(fg_throughput, 1),
                    "specific_energy": round(fg_specific_energy, 2),
                    "media_charge": round(fg_media_charge, 1),
                },
                "fine_mag_sep": {
                    "name": "Fine Magnetic Separation",
                    "status": fine_mag_status,
                    "slurry_flow": round(fine_mag_slurry, 1),
                    "intensity": round(fine_mag_intensity, 3),
                    "fe_pct": round(fine_mag_fe, 1),
                    "fe_recovery": round(fine_mag_recovery, 1),
                    "concentrate_flow": round(fine_mag_concentrate, 1),
                },
                "further_grinding": {
                    "name": "Further Grinding (FTM + Thickener)",
                    "status": fug_status,
                    "power": round(fug_power, 1),
                    "density": round(fug_density, 2),
                    "flow": round(fug_flow, 1),
                    "particle_size": round(fug_particle_size, 4),
                    "specific_energy": round(fug_specific_energy, 2),
                },
                "flotation": {
                    "name": "Flotation — Silica Rejection",
                    "status": flot_status,
                    "air_flow": round(air_flow, 1),
                    "reagent_dose": round(reagent_dose, 3),
                    "ph": round(flot_ph, 1),
                    "fe_pct": round(flot_fe, 1),
                    "sio2_pct": round(flot_sio2, 2),
                    "sio2_rejection": round(sio2_rejection, 1),
                    "cell_level": round(flot_cell_level, 1),
                },
                "thickener": {
                    "name": "Concentrate Thickener",
                    "status": thick_status,
                    "bed_level": round(thick_bed_level, 2),
                    "underflow_density": round(thick_underflow_density, 2),
                    "overflow_flow": round(thick_overflow, 1),
                    "flocculant_dose": round(thick_flocculant, 1),
                    "torque": round(thick_torque, 1),
                },
                "final_product": {
                    "name": "Final Product — High Grade Concentrate",
                    "status": final_status,
                    "fe_grade": round(final_fe, 1),
                    "sio2_pct": round(final_sio2, 2),
                    "al2o3_pct": round(final_al2o3, 2),
                    "recovery": round(final_recovery, 1),
                    "production_rate": round(final_production, 1),
                    "moisture": round(final_moisture, 1),
                },
                "water_recovery": {
                    "name": "Water Recovery & Recycle",
                    "status": water_status,
                    "overflow_flow": round(water_overflow, 1),
                    "water_recovery_pct": round(water_recovery_pct, 1),
                    "recycle_flow": round(water_recycle, 1),
                    "ph": round(water_ph, 1),
                    "tss": round(water_tss, 1),
                },
            },
            "alarms": self._alarms[-10:],
        }

    # ── Helper Methods ─────────────────────────────────────────────────

    def _equipment_status(self, value: float, low: float, high: float) -> str:
        """Determine equipment status based on value within operating range"""
        if value < low * 0.8 or value > high * 1.2:
            return "FAULT"
        elif value < low * 0.9 or value > high * 1.1:
            return "WARNING"
        else:
            return "RUNNING"

    def _calc_availability(self) -> float:
        """Calculate overall equipment availability"""
        if not self._state.get("equipment"):
            return 95.0
        equipment = self._state["equipment"]
        total = len(equipment)
        running = sum(1 for eq in equipment.values()
                      if isinstance(eq, dict) and eq.get("status") == "RUNNING")
        return round(running / max(total, 1) * 100, 1)

    def _record_history(self):
        """Record current state to history"""
        plant = self._state.get("plant", {})
        record = {
            "timestamp": self._state.get("timestamp", ""),
            "feed_rate": plant.get("feed_rate", 0),
            "fe_grade": plant.get("fe_grade", 0),
            "sio2": plant.get("sio2", 0),
            "recovery": plant.get("recovery", 0),
            "production_rate": plant.get("production_rate", 0),
            "water_recovery": plant.get("water_recovery", 0),
        }
        self._history.append(record)
        # Keep only last 500 records
        if len(self._history) > 500:
            self._history = self._history[-500:]

    def _check_alarms(self):
        """Check for alarm conditions based on operating limits"""
        now = self._state.get("timestamp", "")
        plant = self._state.get("plant", {})
        equipment = self._state.get("equipment", {})

        checks = [
            ("HPGR", "motor_power", equipment.get("hpgr", {}).get("motor_power", 0),
             self.OPERATING_LIMITS["hpgr_motor_power"]),
            ("HPGR", "pressure", equipment.get("hpgr", {}).get("pressure", 0),
             self.OPERATING_LIMITS["hpgr_pressure"]),
            ("ROM Feed", "feed_rate", plant.get("feed_rate", 0),
             self.OPERATING_LIMITS["feed_rate"]),
            ("Final Product", "fe_grade", plant.get("fe_grade", 0),
             self.OPERATING_LIMITS["fe_grade"]),
            ("Final Product", "sio2", plant.get("sio2", 0),
             self.OPERATING_LIMITS["sio2_final"]),
            ("Flotation", "ph", equipment.get("flotation", {}).get("ph", 0),
             self.OPERATING_LIMITS["flotation_ph"]),
            ("Thickener", "bed_level", equipment.get("thickener", {}).get("bed_level", 0),
             self.OPERATING_LIMITS["thickener_bed_level"]),
            ("Water Recovery", "water_recovery", plant.get("water_recovery", 0),
             self.OPERATING_LIMITS["water_recovery"]),
        ]

        # Clear old alarms (keep only recent)
        new_alarms = []
        for eq_name, var_name, value, limits in checks:
            if value < limits["low"]:
                self._alarm_counter += 1
                new_alarms.append({
                    "id": f"ALM-{self._alarm_counter:04d}",
                    "timestamp": now,
                    "equipment": eq_name,
                    "variable": var_name,
                    "value": round(value, 2),
                    "threshold": limits["low"],
                    "severity": "WARNING" if value > limits["low"] * 0.8 else "CRITICAL",
                    "message": f"[SIMULATED] {eq_name} {var_name} ({value:.1f} {limits['unit']}) below lower limit ({limits['low']} {limits['unit']})",
                    "is_simulated": True,
                })
            elif value > limits["high"]:
                self._alarm_counter += 1
                new_alarms.append({
                    "id": f"ALM-{self._alarm_counter:04d}",
                    "timestamp": now,
                    "equipment": eq_name,
                    "variable": var_name,
                    "value": round(value, 2),
                    "threshold": limits["high"],
                    "severity": "WARNING" if value < limits["high"] * 1.2 else "CRITICAL",
                    "message": f"[SIMULATED] {eq_name} {var_name} ({value:.1f} {limits['unit']}) above upper limit ({limits['high']} {limits['unit']})",
                    "is_simulated": True,
                })

        if new_alarms:
            self._alarms.extend(new_alarms)
            # Keep only last 100 alarms
            if len(self._alarms) > 100:
                self._alarms = self._alarms[-100:]

        # Update alarm count in plant summary
        if "plant" in self._state:
            self._state["plant"]["active_alarms"] = len(new_alarms)
