from fastapi import APIRouter, HTTPException

from app.Model.weather_forecast.forecast_model import EnvironmentForecaster
from app.Model.weather_forecast.forecast_schema import ForecastRequest

router = APIRouter(prefix="/weather", tags=["Weather Forecast"])

forecaster = EnvironmentForecaster()


@router.post("/forecast")
async def forecast_weather(payload: ForecastRequest):
    try:
        result = forecaster.forecast(
            history=[item.model_dump() for item in payload.history],
            hours_ahead=payload.hours_ahead,
        )
        return {
            "success": True,
            "hours_ahead": payload.hours_ahead,
            "forecast": result,
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))