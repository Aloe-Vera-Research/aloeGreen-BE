from fastapi import APIRouter, HTTPException
from app.Utils.db import environmental_logs_collection

router = APIRouter(prefix="/environment", tags=["Environment"])


@router.get("/latest")
async def get_latest_environment():
    latest = await environmental_logs_collection.find_one(
        sort=[("timestamp", -1)]
    )

    if not latest:
        raise HTTPException(
            status_code=404,
            detail="No environment data found"
        )

    return {
        "temperature": latest.get("temperature"),
        "humidity": latest.get("humidity"),
        "soil_moisture": latest.get("soil_moisture"),
        "soil_ph": latest.get("soil_ph"),
        "rainfall_mm": latest.get("rainfall_mm", 0),
        "irrigation_mm": latest.get("irrigation_mm", 4),
        "soil_texture_enc": latest.get("soil_texture_enc", 1),
        "soil_organic_matter_pct": latest.get("soil_organic_matter_pct", 2.8),
        "timestamp": latest.get("timestamp"),
    }