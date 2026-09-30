"""
ML Prediction Service for Iron Ore Beneficiation Digital Twin
==============================================================
Uses synthetic training data for demonstration purposes.
Model accuracy claims are NOT made — this is a demo pipeline only.
"""

import numpy as np
import os
import joblib
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from typing import Dict, Any, Optional


class PredictionService:
    """
    ML prediction service for process outputs.
    Trained on SYNTHETIC data for demonstration only.
    """

    FEATURE_NAMES = [
        "feed_rate", "fe_pct", "sio2_pct", "hpgr_pressure",
        "motor_power", "particle_size", "slurry_flow",
        "reagent_dose", "ph", "air_flow"
    ]

    TARGET_NAMES = [
        "fe_grade", "recovery", "sio2_out", "production_rate"
    ]

    def __init__(self, model_dir: str = "models"):
        self.model_dir = model_dir
        os.makedirs(model_dir, exist_ok=True)
        self.models: Dict[str, Any] = {}
        self.scalers: Dict[str, StandardScaler] = {}
        self._load_or_train()

    def _generate_synthetic_data(self, n_samples: int = 2000) -> tuple:
        """
        Generate synthetic training data based on process physics assumptions.
        NOT real plant data — for pipeline demonstration only.
        """
        np.random.seed(42)

        # Input features with realistic ranges
        feed_rate = np.random.uniform(80, 160, n_samples)
        fe_pct = np.random.uniform(28, 42, n_samples)
        sio2_pct = np.random.uniform(35, 55, n_samples)
        hpgr_pressure = np.random.uniform(100, 200, n_samples)
        motor_power = np.random.uniform(600, 1100, n_samples)
        particle_size = np.random.uniform(1.5, 4.0, n_samples)
        slurry_flow = np.random.uniform(120, 250, n_samples)
        reagent_dose = np.random.uniform(0.15, 0.55, n_samples)
        ph = np.random.uniform(8.0, 11.0, n_samples)
        air_flow = np.random.uniform(25, 65, n_samples)

        X = np.column_stack([
            feed_rate, fe_pct, sio2_pct, hpgr_pressure,
            motor_power, particle_size, slurry_flow,
            reagent_dose, ph, air_flow
        ])

        # Synthetic targets based on simplified process relationships
        noise = lambda scale: np.random.normal(0, scale, n_samples)

        # Fe grade depends on feed Fe, pressure, reagent, particle size
        fe_grade = (
            45.0
            + fe_pct * 0.35
            + hpgr_pressure * 0.02
            + reagent_dose * 8.0
            - particle_size * 1.5
            - np.abs(ph - 9.5) * 0.8
            + noise(0.8)
        )
        fe_grade = np.clip(fe_grade, 58, 69)

        # Recovery depends on feed quality, grinding, magnetic sep
        recovery = (
            55.0
            + fe_pct * 0.4
            + hpgr_pressure * 0.05
            - particle_size * 3.0
            + motor_power * 0.01
            + reagent_dose * 15.0
            - np.abs(ph - 9.5) * 1.5
            + noise(1.2)
        )
        recovery = np.clip(recovery, 65, 95)

        # SiO2 in concentrate — lower is better
        sio2_out = (
            8.0
            + sio2_pct * 0.05
            - reagent_dose * 6.0
            + particle_size * 0.8
            + np.abs(ph - 9.5) * 0.5
            - air_flow * 0.02
            + noise(0.4)
        )
        sio2_out = np.clip(sio2_out, 1.0, 8.0)

        # Production rate
        production_rate = (
            feed_rate * recovery / 100.0 * 0.65
            + noise(1.5)
        )
        production_rate = np.clip(production_rate, 20, 120)

        y = np.column_stack([fe_grade, recovery, sio2_out, production_rate])

        return X, y

    def _load_or_train(self):
        """Load existing models or train new ones"""
        all_loaded = True
        for target in self.TARGET_NAMES:
            model_path = os.path.join(self.model_dir, f"{target}_model.joblib")
            scaler_path = os.path.join(self.model_dir, f"{target}_scaler.joblib")
            if os.path.exists(model_path) and os.path.exists(scaler_path):
                self.models[target] = joblib.load(model_path)
                self.scalers[target] = joblib.load(scaler_path)
            else:
                all_loaded = False
                break

        if not all_loaded:
            self._train_models()

    def _train_models(self):
        """Train ML models on synthetic data"""
        X, y = self._generate_synthetic_data()

        for i, target in enumerate(self.TARGET_NAMES):
            scaler = StandardScaler()
            X_scaled = scaler.fit_transform(X)

            X_train, X_test, y_train, y_test = train_test_split(
                X_scaled, y[:, i], test_size=0.2, random_state=42
            )

            model = GradientBoostingRegressor(
                n_estimators=100,
                max_depth=5,
                learning_rate=0.1,
                random_state=42
            )
            model.fit(X_train, y_train)

            self.models[target] = model
            self.scalers[target] = scaler

            # Save models
            model_path = os.path.join(self.model_dir, f"{target}_model.joblib")
            scaler_path = os.path.join(self.model_dir, f"{target}_scaler.joblib")
            joblib.dump(model, model_path)
            joblib.dump(scaler, scaler_path)

    def predict(self, inputs: Dict[str, float]) -> Dict[str, Any]:
        """
        Run prediction given input conditions.
        Returns predicted process outputs.
        All predictions are from SYNTHETIC-trained models — demo only.
        """
        # Build feature vector
        feature_values = []
        for fname in self.FEATURE_NAMES:
            feature_values.append(inputs.get(fname, 0.0))

        X = np.array([feature_values])

        predictions = {}
        for target in self.TARGET_NAMES:
            if target in self.models and target in self.scalers:
                X_scaled = self.scalers[target].transform(X)
                pred = self.models[target].predict(X_scaled)[0]
                predictions[target] = round(float(pred), 2)

        return {
            "predicted_fe_grade": predictions.get("fe_grade", 0.0),
            "predicted_recovery": predictions.get("recovery", 0.0),
            "predicted_sio2": predictions.get("sio2_out", 0.0),
            "predicted_production_rate": predictions.get("production_rate", 0.0),
            "confidence": "DEMO — synthetic model, not validated",
            "model_type": "GradientBoostingRegressor",
            "is_simulated": True,
            "input_conditions": inputs,
        }
