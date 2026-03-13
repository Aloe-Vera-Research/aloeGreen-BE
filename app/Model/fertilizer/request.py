from pydantic import BaseModel


class FertilizerRequest(BaseModel):
    Soil_pH: float
    N: int
    P: int
    K: int
    Soil_Moisture: float
    Soil_Type: str
    Plant_Age_Category: str
    Application_Timing: str
    Additional_Advice: str