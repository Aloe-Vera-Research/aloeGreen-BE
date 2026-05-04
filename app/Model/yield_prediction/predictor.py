import json
from pathlib import Path
from typing import Dict, List

import joblib
import pandas as pd


FEATURE_COLS = [
    "soil_ph",
    "soil_organic_matter_pct",
    "soil_moisture_pct",
    "irrigation_mm",
    "temp_day_c",
    "humidity_pct",
    "rainfall_mm",
    "plant_age_months",
    "hour",
    "day",
    "month",
    "water_stress_index",
    "heat_stress_index",
    "soil_texture_enc",
]


import pandas as pd
import json
import joblib
from pathlib import Path


class AloePredictor:

    def __init__(self):

        current_file = Path(__file__).resolve()

        self.model_dir = current_file.parents[2] / "MLModels" / "yield_prediction"

        try:
            self.rf_model = joblib.load(self.model_dir / "rf_initial.pkl")
            self.xgb_model = joblib.load(self.model_dir / "xgb_initial.pkl")

            with open(self.model_dir / "ensemble_config.json") as f:
                config = json.load(f)

            self.w_rf = config["rf_weight"]
            self.w_xgb = config["xgb_weight"]

            self.models_loaded = True

        except Exception as e:
            print("Model loading failed:", e)
            self.models_loaded = False
            self.w_rf = 0.5
            self.w_xgb = 0.5

        self.feature_cols = [
            "soil_ph",
            "soil_organic_matter_pct",
            "soil_moisture_pct",
            "irrigation_mm",
            "temp_day_c",
            "humidity_pct",
            "rainfall_mm",
            "plant_age_months",
            "hour",
            "day",
            "month",
            "water_stress_index",
            "heat_stress_index",
            "soil_texture_enc",
        ]

    def predict(self, data):

        if not self.models_loaded:
            raise RuntimeError("Models not loaded")

        X = pd.DataFrame([data])[self.feature_cols]

        rf_pred = self.rf_model.predict(X)[0]
        xgb_pred = self.xgb_model.predict(X)[0]

        ensemble = (self.w_rf * rf_pred) + (self.w_xgb * xgb_pred)

        return {
            "random_forest": float(rf_pred),
            "xgboost": float(xgb_pred),
            "ensemble": float(ensemble),
        }

    def get_model_info(self):

        return {
            "ensemble_config": {
                "rf_weight": self.w_rf,
                "xgb_weight": self.w_xgb,
            },
            "features": self.feature_cols,
            "soil_texture_encoding": {
                "0": "Clay",
                "1": "Loamy",
                "2": "Sandy",
            },
        }
    def __init__(self):
        current_file = Path(__file__).resolve()
        self.model_dir = current_file.parents[2] / "MLModels" / "yield_prediction"

        self.rf_model = None
        self.xgb_model = None
        self.w_rf = 0.5
        self.w_xgb = 0.5
        self.feature_cols = FEATURE_COLS
        self.ensemble_config = {}
        self.models_loaded = False

        self._load_models()

    def _load_models(self):
        try:
            self.rf_model = joblib.load(self.model_dir / "rf_initial.pkl")
            self.xgb_model = joblib.load(self.model_dir / "xgb_initial.pkl")

            with open(self.model_dir / "ensemble_config.json", "r") as f:
                self.ensemble_config = json.load(f)

            self.w_rf = self.ensemble_config.get("rf_weight", 0.5)
            self.w_xgb = self.ensemble_config.get("xgb_weight", 0.5)
            self.models_loaded = True

            print(" Yield models loaded successfully")
            print(f"   RF weight: {self.w_rf:.4f}, XGB weight: {self.w_xgb:.4f}")

        except FileNotFoundError as e:
            self.models_loaded = False
            print(f" Yield model file not found: {e}")

        except Exception as e:
            self.models_loaded = False
            print(f" Error loading yield models: {e}")

    def predict(self, data: Dict) -> Dict[str, float]:
        if not self.models_loaded:
            raise RuntimeError("Yield models are not loaded.")

        X = pd.DataFrame([data])[self.feature_cols]

        rf_pred = self.rf_model.predict(X)[0]
        xgb_pred = self.xgb_model.predict(X)[0]
        ensemble_pred = (self.w_rf * rf_pred) + (self.w_xgb * xgb_pred)

        return {
            "random_forest": float(rf_pred),
            "xgboost": float(xgb_pred),
            "ensemble": float(ensemble_pred),
        }

    def predict_batch(self, data_list: List[Dict]) -> List[Dict[str, float]]:
        return [self.predict(data) for data in data_list]

    def get_model_info(self) -> Dict:
        return {
            "models_loaded": self.models_loaded,
            "ensemble_config": self.ensemble_config,
            "features": self.feature_cols,
            "weights": {
                "random_forest": self.w_rf,
                "xgboost": self.w_xgb,
            },
            "soil_texture_encoding": {
                "0": "Clay",
                "1": "Loamy",
                "2": "Sandy",
            },
        }