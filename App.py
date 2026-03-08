from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.Controllers.price import (
    data_controller,
    predict_controller,
    risk_controller,
    dashboard_controller,
)
from app.Controllers.yield_prediction import yield_controller
from app.Controllers.weather_forecast import forecast_controller

app = FastAPI(title="AloeGreen Backend API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Price module routes
app.include_router(data_controller.router, prefix="/data")
app.include_router(predict_controller.router, prefix="/api")
app.include_router(risk_controller.router, prefix="/api")
app.include_router(dashboard_controller.router, prefix="/api")
app.include_router(forecast_controller.router, prefix="/api")

# Yield module routes
app.include_router(yield_controller.router)

@app.get("/")
def root():
    return {
        "message": "FastAPI backend is live",
        "modules": ["price", "yield"]
    }