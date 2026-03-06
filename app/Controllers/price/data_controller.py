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

    # Auto-detect disaster regardless of what the client may have sent.
    data["naturalDisaster"] = detect_natural_disaster()
    data["createdAt"] = datetime.utcnow()

    result = await data_collection.insert_one(data)

    return {
        "message": "Data saved successfully",
        "naturalDisaster": data["naturalDisaster"],
        "predictedPrice": data.get("predictedPrice"),
        "id": str(result.inserted_id)
    }
