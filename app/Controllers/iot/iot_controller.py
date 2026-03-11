from fastapi import APIRouter, Query
from pymongo import MongoClient
from dotenv import load_dotenv
import os

load_dotenv()

router = APIRouter()

MONGO_URI = os.getenv("MONGO_URI")
DB_NAME = os.getenv("DB_NAME", "aloeveradb")

client = MongoClient(MONGO_URI)
db = client[DB_NAME]
environmental_logs = db["environmental_logs"]


def serialize_doc(doc):
    if not doc:
        return None

    doc["_id"] = str(doc["_id"])

    if "timestamp" in doc and doc["timestamp"]:
        doc["timestamp"] = doc["timestamp"].isoformat()

    if "created_at" in doc and doc["created_at"]:
        doc["created_at"] = doc["created_at"].isoformat()

    return doc


@router.get("/latest")
def get_latest_environment_data(device_id: str = Query("device01")):
    doc = environmental_logs.find_one(
        {"device_id": device_id},
        sort=[("timestamp", -1)]
    )

    if not doc:
        return {
            "success": False,
            "message": "No data found"
        }

    return {
        "success": True,
        "data": serialize_doc(doc)
    }


@router.get("/history")
def get_environment_history(
    device_id: str = Query("device01"),
    limit: int = Query(60, ge=1, le=5000)
):
    docs = list(
        environmental_logs.find({"device_id": device_id})
        .sort("timestamp", -1)
        .limit(limit)
    )

    docs = [serialize_doc(doc) for doc in docs]

    return {
        "success": True,
        "count": len(docs),
        "data": docs
    }