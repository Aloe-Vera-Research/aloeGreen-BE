from fastapi import APIRouter
from datetime import datetime
from app.Utils.db import data_collection
from app.Model.price.data_model import PriceData
from app.Utils.weather import detect_natural_disaster
from bson import ObjectId

router = APIRouter()

@router.get("/data")
async def get_all_data():
    """
    Fetch all production records sorted by creation date (newest first).
    Excludes internal MongoDB _id field for cleaner JSON.
    """
    records = []
    async for doc in data_collection.find().sort("createdAt", -1):
        doc["id"] = str(doc["_id"])
        del doc["_id"]
        records.append(doc)
    return {"records": records, "count": len(records)}

@router.post("/data")
async def add_data(payload: PriceData):
    # Exclude None fields so we don't insert nulls for optional dates.
    data = payload.dict(exclude_none=True)

    # Detect weather condition using provided lat/lon or fallback
    weather_info = detect_natural_disaster(payload.latitude, payload.longitude)

    # Add weather and location data to the record
    data["naturalDisaster"] = weather_info["disaster"]
    data["advice"] = weather_info["advice"]
    data["location"] = weather_info["location"]
    data["locationName"] = weather_info["locationName"]
    data["createdAt"] = datetime.utcnow()

    result = await data_collection.insert_one(data)

    return {
        "message": "Data saved successfully",
        "predictedPrice": data.get("predictedPrice"),
        "naturalDisaster": data["naturalDisaster"],
        "advice": data["advice"],
        "location": data["location"],
        "locationName": data["locationName"],
        "id": str(result.inserted_id)
    }
