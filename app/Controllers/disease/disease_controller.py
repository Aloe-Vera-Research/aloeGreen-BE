from fastapi import APIRouter, UploadFile, File, HTTPException
from PIL import Image
import io

from app.Utils.image_preprocess import preprocess_image
from app.MLModels.disease.inference import predict_disease
from app.Model.disease.disease_schema import DiseasePredictionResponse

router = APIRouter(prefix="/api/disease", tags=["Disease Detection"])


@router.post("/detect", response_model=DiseasePredictionResponse)
async def detect_disease(file: UploadFile = File(...)):
    try:
        contents = await file.read()
        image = Image.open(io.BytesIO(contents))

        processed_image = preprocess_image(image)
        result = predict_disease(processed_image)

        return result

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))