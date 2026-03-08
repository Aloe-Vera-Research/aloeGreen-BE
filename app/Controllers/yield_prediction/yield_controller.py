from datetime import datetime
from pathlib import Path
import pandas as pd

from app.Model.weather_forecast.forecast_model import EnvironmentForecaster
from app.Model.yield_prediction.schemas import FutureYieldPredictionInput, FutureYieldPredictionResponse
from fastapi import APIRouter, HTTPException

from app.Model.yield_prediction.predictor import AloePredictor
from app.Model.yield_prediction.schemas import (
    BatchPredictionInput,
    BatchPredictionResponse,
    HealthResponse,
    ModelInfo,
    PredictionInput,
    PredictionOutput,
    PredictionResponse,
    ScenarioInput,
    ScenarioResponse,
    ScenarioResult,
)

from app.Utils.yield_feature_engineering import (
    calculate_derived_features,
    extract_time_features,
)

router = APIRouter(prefix="/yield", tags=["Yield"])

predictor = AloePredictor()
router = APIRouter(prefix="/yield", tags=["Yield"])

predictor = AloePredictor()
forecaster = EnvironmentForecaster()

@router.get("/health", response_model=HealthResponse)
async def health_check():
    return HealthResponse(
        status="healthy" if predictor.models_loaded else "degraded",
        models_loaded=predictor.models_loaded,
        ensemble_weights={
            "random_forest": predictor.w_rf,
            "xgboost": predictor.w_xgb,
        },
        api_version="1.0.0",
    )


@router.post("/predict", response_model=PredictionResponse)
async def predict(input_data: PredictionInput):
    try:
        data = input_data.model_dump()

        time_features = extract_time_features(data.get("timestamp"))
        data.update(time_features)

        data = calculate_derived_features(data)

        predictions = predictor.predict(data)

        return PredictionResponse(
            success=True,
            predictions=PredictionOutput(**predictions),
            gel_weight_g=predictions["ensemble"],
            timestamp=datetime.now().isoformat(),
            input_data=data,
        )

    except RuntimeError as e:
        raise HTTPException(status_code=503, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Prediction failed: {str(e)}")


@router.post("/predict/batch", response_model=BatchPredictionResponse)
async def predict_batch(batch_input: BatchPredictionInput):
    try:
        results = []

        for idx, sample in enumerate(batch_input.samples):
            try:
                data = sample.model_dump()

                time_features = extract_time_features(data.get("timestamp"))
                data.update(time_features)

                data = calculate_derived_features(data)

                predictions = predictor.predict(data)

                results.append(
                    {
                        "sample_id": idx + 1,
                        "predictions": predictions,
                        "gel_weight_g": predictions["ensemble"],
                        "success": True,
                    }
                )
            except Exception as e:
                results.append(
                    {
                        "sample_id": idx + 1,
                        "error": str(e),
                        "success": False,
                    }
                )

        successful_predictions = sum(
            1 for r in results if r.get("success", False)
        )

        return BatchPredictionResponse(
            success=successful_predictions > 0,
            count=len(results),
            results=results,
            timestamp=datetime.now().isoformat(),
        )

    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Batch prediction failed: {str(e)}")


@router.post("/scenario", response_model=ScenarioResponse)
async def scenario_analysis(scenario_input: ScenarioInput):
    try:
        base_data = scenario_input.base.model_dump()
        time_features = extract_time_features(base_data.get("timestamp"))
        base_data.update(time_features)
        base_data = calculate_derived_features(base_data)

        base_predictions = predictor.predict(base_data)
        base_ensemble = base_predictions["ensemble"]

        results = [
            ScenarioResult(
                name="Base Scenario",
                gel_weight_g=base_ensemble,
                changes={},
            )
        ]

        for scenario in scenario_input.scenarios:
            modified = base_data.copy()
            modified.update(scenario.changes)

            if "soil_moisture_pct" in scenario.changes or "temp_day_c" in scenario.changes:
                modified["water_stress_index"] = (
                    modified["soil_moisture_pct"] / (modified["temp_day_c"] + 1)
                )

            if "temp_day_c" in scenario.changes or "humidity_pct" in scenario.changes:
                modified["heat_stress_index"] = (
                    modified["temp_day_c"] * modified["humidity_pct"]
                )

            modified_predictions = predictor.predict(modified)
            modified_ensemble = modified_predictions["ensemble"]

            change = modified_ensemble - base_ensemble
            percent_change = (change / base_ensemble * 100) if base_ensemble != 0 else 0

            results.append(
                ScenarioResult(
                    name=scenario.name,
                    gel_weight_g=modified_ensemble,
                    change_from_base=change,
                    percent_change=percent_change,
                    changes=scenario.changes,
                )
            )

        return ScenarioResponse(
            success=True,
            results=results,
            timestamp=datetime.now().isoformat(),
        )

    except RuntimeError as e:
        raise HTTPException(status_code=503, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Scenario analysis failed: {str(e)}")


@router.get("/model/info", response_model=ModelInfo)
async def model_info():
    info = predictor.get_model_info()

    return ModelInfo(
        ensemble_config=info["ensemble_config"] if predictor.models_loaded else {},
        features=info["features"],
        models={
            "random_forest": {
                "weight": predictor.w_rf,
                "type": "RandomForestRegressor",
                "description": "Ensemble model component",
            },
            "xgboost": {
                "weight": predictor.w_xgb,
                "type": "XGBRegressor",
                "description": "Ensemble model component",
            },
        },
        soil_texture_encoding=info["soil_texture_encoding"],
    )

@router.post("/predict-future", response_model=FutureYieldPredictionResponse)
async def predict_future_yield(input_data: FutureYieldPredictionInput):
    try:
        target_ts = pd.to_datetime(input_data.target_timestamp)

        # CSV path: put your real file here
        csv_path = str(
            Path(__file__).resolve().parents[3] / "data" / "Hourly_environment_history_2023_2025.csv"
        )

        # Load latest known history from CSV to determine start point
        history = forecaster.load_history_from_csv(csv_path, history_hours=72)
        last_history_ts = pd.to_datetime(history[-1]["timestamp"])

        if target_ts <= last_history_ts:
            raise HTTPException(
                status_code=400,
                detail=f"target_timestamp must be after latest history timestamp ({last_history_ts.isoformat()})."
            )

        time_diff = target_ts - last_history_ts
        hours_ahead = int(time_diff.total_seconds() // 3600)

        if time_diff.total_seconds() % 3600 != 0:
            raise HTTPException(
                status_code=400,
                detail="target_timestamp must be aligned to an exact hour."
            )

        if hours_ahead < 1:
            raise HTTPException(
                status_code=400,
                detail="target_timestamp must be at least 1 hour ahead of latest history timestamp."
            )

        forecast = forecaster.forecast_from_csv(
            csv_path=csv_path,
            hours_ahead=hours_ahead,
            history_hours=72
        )

        target_forecast = forecast[-1]

        data = input_data.model_dump()

        merged = {
            "soil_ph": data["soil_ph"],
            "soil_organic_matter_pct": data["soil_organic_matter_pct"],
            "soil_moisture_pct": data["soil_moisture_pct"],
            "irrigation_mm": data["irrigation_mm"],
            "temp_day_c": target_forecast["temp_day_c"],
            "humidity_pct": target_forecast["humidity_pct"],
            "rainfall_mm": target_forecast["rainfall_mm"],
            "plant_age_months": data["plant_age_months"],
            "soil_texture_enc": data["soil_texture_enc"],
            "timestamp": input_data.target_timestamp,
        }

        time_features = extract_time_features(merged.get("timestamp"))
        merged.update(time_features)

        merged = calculate_derived_features(merged)

        predictions = predictor.predict(merged)

        return FutureYieldPredictionResponse(
            success=True,
            target_timestamp=input_data.target_timestamp,
            forecasted_environment={
                "temp_day_c": target_forecast["temp_day_c"],
                "humidity_pct": target_forecast["humidity_pct"],
                "rainfall_mm": target_forecast["rainfall_mm"],
            },
            predictions=PredictionOutput(**predictions),
            gel_weight_g=predictions["ensemble"],
            timestamp=datetime.now().isoformat(),
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Future yield prediction failed: {str(e)}")