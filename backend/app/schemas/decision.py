from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class DecisionResultCreate(BaseModel):
    zone_id: int = Field(gt=0)
    irrigation_priority: str | None = Field(default=None, max_length=32)
    water_stress: str | None = Field(default=None, max_length=32)
    heat_stress: str | None = Field(default=None, max_length=32)
    disease_spread_risk: str | None = Field(default=None, max_length=32)
    yield_risk: str | None = Field(default=None, max_length=32)
    farm_health_score: int | None = Field(default=None, ge=0, le=100)
    advisory: str | None = Field(default=None, max_length=2000)
    provider: str = Field(min_length=1, max_length=128)


class DecisionResultResponse(DecisionResultCreate):
    model_config = ConfigDict(from_attributes=True)

    id: int
    created_at: datetime


class SensorContext(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    timestamp: datetime
    soil_moisture: float
    soil_temperature: float
    light_intensity: float


class AIContext(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    image_id: int
    crop_health: str | None
    disease: str | None
    confidence: float | None
    growth_stage: str | None
    provider: str


class IrrigationContext(BaseModel):
    event_id: int
    status: str
    water_delivered_liters: float


class DecisionContextResponse(BaseModel):
    zone_id: int
    latest_sensor: SensorContext | None
    latest_ai_result: AIContext | None
    active_irrigation: IrrigationContext | None