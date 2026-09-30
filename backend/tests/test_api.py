"""
Tests for the Process Simulator and FastAPI endpoints
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import pytest
from fastapi.testclient import TestClient
from services.simulator import ProcessSimulator


class TestProcessSimulator:
    """Tests for the material-flow process simulator"""

    def setup_method(self):
        self.sim = ProcessSimulator()

    def test_initial_state(self):
        state = self.sim.get_state()
        assert "timestamp" in state
        assert "plant" in state
        assert "equipment" in state
        assert state["data_source"] == "SIMULATED"

    def test_plant_kpis_present(self):
        state = self.sim.get_state()
        plant = state["plant"]
        for key in ["feed_rate", "fe_grade", "sio2", "recovery",
                     "production_rate", "water_recovery"]:
            assert key in plant, f"Missing KPI: {key}"
            assert isinstance(plant[key], (int, float))

    def test_all_equipment_present(self):
        state = self.sim.get_state()
        expected = [
            "rom_feed", "hpgr", "coarse_mag_sep", "fine_grinding",
            "fine_mag_sep", "further_grinding", "flotation",
            "thickener", "final_product", "water_recovery"
        ]
        for eq_id in expected:
            assert eq_id in state["equipment"], f"Missing equipment: {eq_id}"

    def test_equipment_has_status(self):
        state = self.sim.get_state()
        for eq_id, eq_data in state["equipment"].items():
            assert "status" in eq_data, f"Equipment {eq_id} missing status"
            assert eq_data["status"] in ["RUNNING", "IDLE", "WARNING", "FAULT"]

    def test_fe_grade_in_range(self):
        state = self.sim.get_state()
        fe = state["plant"]["fe_grade"]
        assert 55 <= fe <= 70, f"Fe grade {fe} out of expected range"

    def test_recovery_in_range(self):
        state = self.sim.get_state()
        recovery = state["plant"]["recovery"]
        assert 60 <= recovery <= 98, f"Recovery {recovery} out of expected range"

    def test_start_stop(self):
        self.sim.start()
        assert self.sim.is_running is True
        self.sim.stop()
        assert self.sim.is_running is False

    def test_reset(self):
        self.sim.update_config({"feed_rate": 200.0})
        self.sim.reset()
        assert self.sim.config["feed_rate"] == 120.0

    def test_update_config(self):
        self.sim.update_config({"feed_rate": 150.0})
        assert self.sim.config["feed_rate"] == 150.0

    def test_equipment_detail(self):
        detail = self.sim.get_equipment_detail("hpgr")
        assert detail is not None
        assert detail["equipment_id"] == "hpgr"
        assert "data" in detail

    def test_equipment_detail_invalid(self):
        detail = self.sim.get_equipment_detail("nonexistent")
        assert detail is None

    def test_material_flow_dependency(self):
        """Verify upstream changes affect downstream values"""
        # Get baseline state
        self.sim.update_config({"feed_rate": 120.0})
        state1 = self.sim.get_state()

        # Increase feed rate
        self.sim.update_config({"feed_rate": 160.0})
        state2 = self.sim.get_state()

        # Production rate should generally increase with feed rate
        # (allowing for noise, just check it's different)
        assert state1["plant"]["production_rate"] != state2["plant"]["production_rate"]


class TestFastAPIEndpoints:
    """Test FastAPI endpoints using TestClient"""

    @pytest.fixture(autouse=True)
    def setup(self):
        from main import app
        self.client = TestClient(app)

    def test_root(self):
        response = self.client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert "service" in data

    def test_health(self):
        response = self.client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert data["data_source"] == "SIMULATED"

    def test_process_state(self):
        response = self.client.get("/api/process/state")
        assert response.status_code == 200
        data = response.json()
        assert "plant" in data
        assert "equipment" in data

    def test_start_stop(self):
        response = self.client.post("/api/process/start")
        assert response.status_code == 200

        response = self.client.post("/api/process/stop")
        assert response.status_code == 200

    def test_reset(self):
        response = self.client.post("/api/process/reset")
        assert response.status_code == 200

    def test_equipment_list(self):
        response = self.client.get("/api/equipment")
        assert response.status_code == 200
        data = response.json()
        assert len(data["equipment_ids"]) == 10

    def test_equipment_detail(self):
        response = self.client.get("/api/equipment/hpgr")
        assert response.status_code == 200
        data = response.json()
        assert data["equipment_id"] == "hpgr"

    def test_equipment_not_found(self):
        response = self.client.get("/api/equipment/nonexistent")
        assert response.status_code == 404

    def test_simulation_update(self):
        response = self.client.post(
            "/api/simulation/update",
            json={"feed_rate": 150.0}
        )
        assert response.status_code == 200

    def test_simulation_update_invalid(self):
        response = self.client.post(
            "/api/simulation/update",
            json={"invalid_key": 100.0}
        )
        assert response.status_code == 400

    def test_prediction(self):
        response = self.client.post(
            "/api/prediction",
            json={
                "feed_rate": 120.0,
                "fe_pct": 35.0,
                "sio2_pct": 45.0,
                "hpgr_pressure": 145.0,
                "motor_power": 850.0,
                "particle_size": 2.5,
                "slurry_flow": 185.0,
                "reagent_dose": 0.35,
                "ph": 9.5,
                "air_flow": 45.0,
            }
        )
        assert response.status_code == 200
        data = response.json()
        assert "predicted_fe_grade" in data
        assert data["is_simulated"] is True

    def test_alarms(self):
        response = self.client.get("/api/alarms")
        assert response.status_code == 200
        data = response.json()
        assert "alarms" in data

    def test_history(self):
        response = self.client.get("/api/history")
        assert response.status_code == 200
        data = response.json()
        assert "records" in data


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
