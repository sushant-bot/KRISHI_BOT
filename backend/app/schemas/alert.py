from datetime import datetime

from pydantic import BaseModel, ConfigDict


class AlertResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    farm_id: int
    zone_id: int | None
    type: str
    severity: str
    message: str
    is_read: bool
    created_at: datetime