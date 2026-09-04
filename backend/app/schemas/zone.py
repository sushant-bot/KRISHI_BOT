from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class ZoneCreate(BaseModel):
    code: str = Field(min_length=1, max_length=32, pattern=r"^[A-Za-z0-9_-]+$")
    name: str = Field(min_length=1, max_length=120)


class ZoneResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    farm_id: int
    code: str
    name: str
    created_at: datetime
