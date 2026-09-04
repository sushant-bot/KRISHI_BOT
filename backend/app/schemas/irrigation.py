from datetime import datetime
from enum import StrEnum

from pydantic import BaseModel, ConfigDict, Field


class IrrigationAction(StrEnum):
    START = "START"
    STOP = "STOP"


class PumpStatus(StrEnum):
    ON = "ON"
    OFF = "OFF"


class IrrigationCommand(BaseModel):
    zone_id: int = Field(gt=0)
    action: IrrigationAction
    target_water_liters: float | None = Field(default=None, gt=0)


class FlowFeedback(BaseModel):
    zone_id: int = Field(gt=0)
    timestamp: datetime | None = None
    flow_rate: float = Field(ge=0)
    water_delivered: float = Field(ge=0)
    pump_status: PumpStatus


class IrrigationResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    zone_id: int
    command: str
    started_at: datetime
    ended_at: datetime | None
    target_water_liters: float | None
    water_delivered_liters: float
    status: str
    fault_message: str | None


class FlowResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    irrigation_event_id: int
    zone_id: int
    timestamp: datetime
    flow_rate: float
    water_delivered: float = Field(validation_alias="water_delivered_liters")
    pump_status: str