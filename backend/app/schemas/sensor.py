from datetime import datetime

from pydantic import BaseModel, Field


class SensorReadingCreate(BaseModel):
    zone_id: int = Field(gt=0)
    timestamp: datetime
    soil_moisture: float = Field(ge=0)
    soil_temperature: float
    light_intensity: float = Field(ge=0)


class SensorReadingResponse(SensorReadingCreate):
    id: int
    created_at: datetime
