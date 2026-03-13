from pydantic import BaseModel
from typing import Dict


class DiseasePredictionResponse(BaseModel):
    disease: str
    confidence: float
    all_scores: Dict[str, float]