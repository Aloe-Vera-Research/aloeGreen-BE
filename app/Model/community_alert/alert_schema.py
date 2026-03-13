from pydantic import BaseModel
from typing import Optional


class EmailAlertRequest(BaseModel):
    disease: str
    severity: str
    spread_risk: str
    message: str
    latitude: Optional[float] = None
    longitude: Optional[float] = None