from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from app.Utils.iot_mqtt_to_mongo import start_mqtt_to_mongo_worker

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
from app.Controllers.iot import iot_controller
from app.Controllers.environment import environment_controller

mqtt_client_instance = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    global mqtt_client_instance

    print("Starting MQTT to MongoDB worker...")
    mqtt_client_instance = start_mqtt_to_mongo_worker()

    yield

    print("Shutting down MQTT worker...")
    if mqtt_client_instance:
        try:
            mqtt_client_instance.loop_stop()
            mqtt_client_instance.disconnect()
        except Exception as e:
            print("Error while stopping MQTT client:", e)


app = FastAPI(
    title="AloeGreen Backend API",
    lifespan=lifespan
)

# -----------------------------
# Enable CORS
# -----------------------------
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

# -----------------------------
# Weather forecast module
# -----------------------------
app.include_router(forecast_controller.router, prefix="/api")

# -----------------------------
# Yield module
# -----------------------------
app.include_router(yield_controller.router)

# -----------------------------
# IoT module
# -----------------------------
app.include_router(iot_controller.router, prefix="/api/iot", tags=["iot"])

# -----------------------------
# Environment latest data module
# Frontend URL: /environment/latest
# -----------------------------
app.include_router(environment_controller.router)

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
            "weather_forecast",
            "disease",
            "community_alert",
            "iot",
            "environment"
        ]
    }