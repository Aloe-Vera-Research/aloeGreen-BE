from fastapi import APIRouter
from app.Utils.db import data_collection

router = APIRouter()

@router.get("/dashboard")
async def dashboard():
    """
    Return high‑level summary plus a slice of raw records sorted by
    creation time. The client can use `recordsList` for charts or
    period filtering without needing a separate "data" call.
    """
    # fetch up to 1000 documents (most recent first)
    docs = await data_collection.find().sort("createdAt", -1).to_list(1000)

    total_production = sum(d["productionQuantity"] for d in docs)
    avg_farmer_price = round(
        sum(d["farmerPrice"] for d in docs) / len(docs) if docs else 0,
        2,
    )

    # pick only the fields that the frontend cares about
    records_list = [
        {
            "date": d.get("date"),
            "productionQuantity": d.get("productionQuantity"),
            "farmerPrice": d.get("farmerPrice"),
            "webPrice": d.get("webPrice"),
            "totalCost": d.get("totalCost"),
        }
        for d in docs
    ]

    return {
        "totalProduction": total_production,
        "averageFarmerPrice": avg_farmer_price,
        "records": len(docs),
        "recordsList": records_list,
    }
