from fastapi import APIRouter, HTTPException
from app.Model.price.prediction_model import PredictionInput
import pickle
import numpy as np
from pathlib import Path

router = APIRouter()

MODEL_PATH = Path(__file__).resolve().parent.parent.parent / "MLModels" / "price" / "aleo_vera_price_prediction.pickle"

with open(MODEL_PATH, "rb") as f:
    model = pickle.load(f)

@router.post("/predict-price")
def predict_price(data: PredictionInput):
    try:
        # One-hot encoding (MATCH TRAINING)
        drought = 1 if data.natural_disaster == "Drought" else 0
        flood = 1 if data.natural_disaster == "Flood" else 0
        no_disaster = 1 if data.natural_disaster == "No disaster" else 0

        features = np.array([[
            data.production_qty_kg,
            data.total_cost_lkr,
            data.web_price_lkr,
            drought,
            flood,
            no_disaster
        ]])

        predicted_price = model.predict(features)[0]

        return {
            "predictedPrice": round(float(predicted_price), 2)
        }

    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail=f"Prediction failed: {str(e)}"
        )
