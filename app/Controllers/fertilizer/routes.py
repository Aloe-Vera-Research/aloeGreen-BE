from fastapi import APIRouter, HTTPException, Query
from bson import ObjectId
from bson.errors import InvalidId
from datetime import datetime, timezone

from app.Model.fertilizer.request import FertilizerRequest
from app.Controllers.fertilizer.predictor import predict_fertilizer
from app.Utils.db import fertilizer_history_collection


router = APIRouter(prefix="/api/fertilizer", tags=["Fertilizer"])


def serialize_history_record(record):
    """
    Convert MongoDB document into JSON-friendly format.
    """
    return {
        "id": str(record["_id"]),
        "input_data": record.get("input_data"),
        "prediction_result": record.get("prediction_result"),
        "created_at": record.get("created_at").isoformat() if record.get("created_at") else None,
    }


@router.post("/predict")
async def predict(request: FertilizerRequest):
    """
    Predict fertilizer recommendation and save prediction history.
    """
    input_data = request.model_dump()

    result = predict_fertilizer(input_data)

    history_doc = {
        "input_data": input_data,
        "prediction_result": result,
        "created_at": datetime.now(timezone.utc),
    }

    insert_result = await fertilizer_history_collection.insert_one(history_doc)

    return {
        "success": True,
        "message": "Fertilizer prediction completed and saved to history.",
        "data": {
            "history_id": str(insert_result.inserted_id),
            "prediction": result,
        },
    }


@router.get("/history")
async def get_fertilizer_history(
    limit: int = Query(default=20, ge=1, le=100),
    skip: int = Query(default=0, ge=0)
):
    """
    Get fertilizer prediction history.
    Latest records are returned first.
    """
    cursor = (
        fertilizer_history_collection
        .find()
        .sort("created_at", -1)
        .skip(skip)
        .limit(limit)
    )

    records = await cursor.to_list(length=limit)

    return {
        "success": True,
        "count": len(records),
        "data": [serialize_history_record(record) for record in records],
    }


@router.get("/history/{history_id}")
async def get_fertilizer_history_by_id(history_id: str):
    """
    Get one fertilizer prediction history record by ID.
    """
    try:
        object_id = ObjectId(history_id)
    except InvalidId:
        raise HTTPException(status_code=400, detail="Invalid history ID format.")

    record = await fertilizer_history_collection.find_one({"_id": object_id})

    if not record:
        raise HTTPException(status_code=404, detail="Fertilizer history record not found.")

    return {
        "success": True,
        "data": serialize_history_record(record),
    }


@router.delete("/history/{history_id}")
async def delete_fertilizer_history(history_id: str):
    """
    Delete one fertilizer prediction history record.
    """
    try:
        object_id = ObjectId(history_id)
    except InvalidId:
        raise HTTPException(status_code=400, detail="Invalid history ID format.")

    result = await fertilizer_history_collection.delete_one({"_id": object_id})

    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Fertilizer history record not found.")

    return {
        "success": True,
        "message": "Fertilizer history record deleted successfully.",
    }