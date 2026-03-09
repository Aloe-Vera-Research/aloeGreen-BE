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

from app.Controllers.fertilizer.routes import router as fertilizer_router
from app.Controllers.disease import disease_controller
from app.Controllers.community_alert import alert_controller

app = FastAPI(title="AloeGreen Backend API")

# Enable CORS (allow mobile app requests)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# -----------------------------
# Price module routes
# -----------------------------
app.include_router(data_controller.router, prefix="/data")
app.include_router(predict_controller.router, prefix="/api")
app.include_router(risk_controller.router, prefix="/api")
app.include_router(dashboard_controller.router, prefix="/api")

# -----------------------------
# Community Alert module
# -----------------------------
app.include_router(alert_controller.router, prefix="/api")

# -----------------------------
# Disease detection module
# -----------------------------
app.include_router(disease_controller.router, prefix="/api")

# -----------------------------
# Fertilizer module
# -----------------------------
app.include_router(fertilizer_router)
app.include_router(forecast_controller.router, prefix="/api")
app.include_router(yield_controller.router)

# -----------------------------
# Root endpoint
# -----------------------------
@app.get("/")
def root():
    return {
        "message": "FastAPI backend is live",
        "modules": [
            "price",
            "fertilizer",
            "yield",
            "disease",
            "community_alert"
        ]
    }