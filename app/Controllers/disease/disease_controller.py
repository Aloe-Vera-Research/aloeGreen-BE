from fastapi import APIRouter, UploadFile, File, HTTPException
from PIL import Image
import io
import traceback
from datetime import datetime

from app.Utils.image_preprocess import preprocess_image
from app.MLModels.disease.inference import predict_disease
from app.Model.disease.disease_schema import DiseasePredictionResponse
from app.Utils.db import scan_history_collection

router = APIRouter(prefix="/disease", tags=["Disease Detection"])


@router.post("/detect", response_model=DiseasePredictionResponse)
async def detect_disease(file: UploadFile = File(...)):
    try:
        print("Received file:", file.filename)

        contents = await file.read()
        image = Image.open(io.BytesIO(contents))

        print("Image opened successfully")

        processed_image = preprocess_image(image)
        print("Image preprocessed successfully")

        result = predict_disease(processed_image)
        print("Prediction result:", result)

        # Save scan history to MongoDB
        await scan_history_collection.insert_one({
            "disease": result["disease"],
            "confidence": float(result["confidence"]),
            "created_at": datetime.utcnow(),
        })

        return result

    except Exception as e:
        print("Disease detection error:")
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/history")
async def get_scan_history():
    try:
        history = []
        cursor = scan_history_collection.find().sort("created_at", -1)

        async for item in cursor:
            item["_id"] = str(item["_id"])
            history.append(item)

        return {
            "success": True,
            "data": history
        }

    except Exception as e:
        print("Scan history error:")
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))