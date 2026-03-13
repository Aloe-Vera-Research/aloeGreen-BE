from pydantic import BaseModel
from typing import Optional

class PriceData(BaseModel):
    date: str
    productionQuantity: int
    totalCost: float
    farmerPrice: float
    webPrice: float
    # The backend will automatically detect and override this value, but
    # the field exists for compatibility with older clients.
    naturalDisaster: Optional[str] = "none"

    # Optional planting / harvest dates; clients can omit them and they will
    # simply not be stored.
    plantDate: Optional[str] = None
    harvestDate: Optional[str] = None
    predictedPrice: Optional[float] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
