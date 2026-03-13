from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class PredictionInput(BaseModel):
    soil_ph: float = Field(..., ge=4.0, le=9.0)
    soil_organic_matter_pct: float = Field(..., ge=0.0, le=10.0)
    soil_moisture_pct: float = Field(..., ge=10.0, le=100.0)
    irrigation_mm: float = Field(..., ge=0.0, le=50.0)
    temp_day_c: float = Field(..., ge=15.0, le=45.0)
    humidity_pct: float = Field(..., ge=20.0, le=100.0)
    rainfall_mm: float = Field(..., ge=0.0, le=100.0)
    plant_age_months: int = Field(..., ge=1, le=120)
    soil_texture_enc: int = Field(..., ge=0, le=2)
    timestamp: Optional[str] = None

    class Config:
        json_schema_extra = {
            "example": {
                "soil_ph": 6.5,
                "soil_organic_matter_pct": 2.8,
                "soil_moisture_pct": 38.0,
                "irrigation_mm": 4.0,
                "temp_day_c": 32.5,
                "humidity_pct": 70.0,
                "rainfall_mm": 1.2,
                "plant_age_months": 14,
                "soil_texture_enc": 1,
                "timestamp": "2024-06-15T10:30:00",
            }
        }


class PredictionOutput(BaseModel):
    random_forest: float
    xgboost: float
    ensemble: float


class PredictionResponse(BaseModel):
    success: bool
    predictions: PredictionOutput
    gel_weight_g: float
    timestamp: str
    input_data: Optional[Dict[str, Any]] = None


class BatchPredictionInput(BaseModel):
    samples: List[PredictionInput]


class BatchPredictionResponse(BaseModel):
    success: bool
    count: int
    results: List[Dict[str, Any]]
    timestamp: str


class ScenarioChange(BaseModel):
    name: str
    changes: Dict[str, float]


class ScenarioInput(BaseModel):
    base: PredictionInput
    scenarios: List[ScenarioChange]

    class Config:
        json_schema_extra = {
            "example": {
                "base": {
                    "soil_ph": 6.5,
                    "soil_organic_matter_pct": 2.8,
                    "soil_moisture_pct": 38.0,
                    "irrigation_mm": 4.0,
                    "temp_day_c": 32.5,
                    "humidity_pct": 70.0,
                    "rainfall_mm": 1.2,
                    "plant_age_months": 14,
                    "soil_texture_enc": 1,
                },
                "scenarios": [
                    {
                        "name": "High Irrigation",
                        "changes": {"irrigation_mm": 7.0},
                    },
                    {
                        "name": "Low Temperature",
                        "changes": {"temp_day_c": 28.0},
                    },
                ],
            }
        }


class ScenarioResult(BaseModel):
    name: str
    gel_weight_g: float
    change_from_base: Optional[float] = None
    percent_change: Optional[float] = None
    changes: Dict[str, float]


class ScenarioResponse(BaseModel):
    success: bool
    results: List[ScenarioResult]
    timestamp: str


class HealthResponse(BaseModel):
    status: str
    models_loaded: bool
    ensemble_weights: Dict[str, float]
    api_version: str


class ModelInfo(BaseModel):
    ensemble_config: Dict[str, Any]
    features: List[str]
    models: Dict[str, Any]
    soil_texture_encoding: Dict[str, str]

class FutureYieldPredictionInput(BaseModel):
    target_timestamp: str
    soil_ph: float
    soil_organic_matter_pct: float
    soil_moisture_pct: float
    irrigation_mm: float
    plant_age_months: int
    soil_texture_enc: int


class FutureYieldPredictionResponse(BaseModel):
    success: bool
    target_timestamp: str
    forecasted_environment: Dict[str, float]
    predictions: PredictionOutput
    gel_weight_g: float
    timestamp: str