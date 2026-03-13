from typing import List
from pydantic import BaseModel


class HistoryPoint(BaseModel):
    timestamp: str
    temp_day_c: float
    humidity_pct: float
    rainfall_mm: float


class ForecastRequest(BaseModel):
    history: List[HistoryPoint]
    hours_ahead: int = 24