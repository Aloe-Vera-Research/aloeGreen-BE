from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.Controllers.price import (
    data_controller,
    predict_controller,
    risk_controller,
    dashboard_controller
)

app = FastAPI(title="Aloe Price Prediction API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(data_controller.router, prefix="/data")
app.include_router(predict_controller.router, prefix="/api")
app.include_router(risk_controller.router, prefix="/api")
app.include_router(dashboard_controller.router, prefix="/api")

@app.get("/")
def root():
    return {"message": "FastAPI backend is live "}