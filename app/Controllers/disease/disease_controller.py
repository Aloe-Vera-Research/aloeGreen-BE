from fastapi import APIRouter, UploadFile, File, HTTPException
from PIL import Image
import io
import traceback

from app.Utils.image_preprocess import preprocess_image
from app.MLModels.disease.inference import predict_disease
from app.Model.disease.disease_schema import DiseasePredictionResponse

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

        return result

    except Exception as e:
        print("Disease detection error:")
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))