from pydantic import BaseModel

from app.schemas.alert import AlertResponse
from app.schemas.decision import AIContext, DecisionResultResponse, IrrigationContext, SensorContext
from app.schemas.image import CropImageResponse


class ZoneTwinResponse(BaseModel):
    zone_id: int
    current: SensorContext | None
    latest_image: CropImageResponse | None
    ai: AIContext | None
    risks: list[DecisionResultResponse]
    health_score: DecisionResultResponse | None
    irrigation: IrrigationContext | None
    alerts: list[AlertResponse]


class FarmTwinResponse(BaseModel):
    farm_id: int
    zones: list[ZoneTwinResponse]