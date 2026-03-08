from fastapi import APIRouter
from app.Model.fertilizer.request import FertilizerRequest
from app.Controllers.fertilizer.predictor import predict_fertilizer

router = APIRouter(prefix="/api/fertilizer", tags=["Fertilizer"])


@router.post("/predict")
def predict(request: FertilizerRequest):
    result = predict_fertilizer(request.model_dump())
    return {
        "success": True,
        "data": result
    }