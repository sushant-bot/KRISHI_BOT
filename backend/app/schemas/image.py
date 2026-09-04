from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class CropImageCreate(BaseModel):
    farm_id: int = Field(gt=0)
    zone_id: int = Field(gt=0)
    image_path: str = Field(min_length=1, max_length=1024)
    timestamp: datetime | None = None


class CropImageResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    farm_id: int
    zone_id: int
    image_path: str
    timestamp: datetime
    created_at: datetime


class AIResultCreate(BaseModel):
    image_id: int = Field(gt=0)
    crop_health: str | None = Field(default=None, max_length=64)
    disease: str | None = Field(default=None, max_length=128)
    confidence: float | None = Field(default=None, ge=0, le=1)
    growth_stage: str | None = Field(default=None, max_length=64)
    provider: str = Field(min_length=1, max_length=128)


class AIResultResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    image_id: int
    zone_id: int
    crop_health: str | None
    disease: str | None
    confidence: float | None
    growth_stage: str | None
    provider: str
    created_at: datetime