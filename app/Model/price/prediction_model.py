from pydantic import BaseModel

class PredictionInput(BaseModel):
    production_qty_kg: float
    total_cost_lkr: float
    web_price_lkr: float
    natural_disaster: str  # "Drought" | "Flood" | "No disaster"
