from fastapi import APIRouter
from app.Model.fertilizer.request import FertilizerRequest
from app.Controllers.fertilizer.predictor import predict_fertilizer

# Define API router with a common prefix and tag grouping for fertilizer-related endpoints
router = APIRouter(prefix="/api/fertilizer", tags=["Fertilizer"])


@router.post("/predict")
def predict(request: FertilizerRequest):
    # Convert validated request object into a dictionary format suitable for the prediction pipeline
    result = predict_fertilizer(request.model_dump())
    
    # Standardized API response structure including status and prediction output
    return {
        "success": True,
        "data": result
    }