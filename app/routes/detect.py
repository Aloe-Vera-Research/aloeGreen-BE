from fastapi import APIRouter, File, UploadFile
from PIL import Image
import io

from app.services.inference import predict

router = APIRouter()

@router.post("/detect")
async def detect_disease(file: UploadFile = File(...)):
    image_bytes = await file.read()
    image = Image.open(io.BytesIO(image_bytes))

    result = predict(image)
    return result
          