from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.sensor import SensorReadingCreate, SensorReadingResponse
from app.schemas.zone import ZoneResponse
from app.services import farm as farm_service
from app.services import sensor as sensor_service

router = APIRouter(prefix="/zones", tags=["zones"])


@router.get("/{zone_id}", response_model=ZoneResponse)
def get_zone(zone_id: int, session: Session = Depends(get_db)):
    return farm_service.get_zone(session, zone_id)


@router.get("/{zone_id}/readings", response_model=list[SensorReadingResponse])
def list_readings(
    zone_id: int,
    limit: int = Query(default=100, ge=1, le=1000),
    session: Session = Depends(get_db),
):
    return sensor_service.list_readings(session, zone_id, limit)


@router.post("/readings", response_model=SensorReadingResponse, status_code=201)
def create_reading(payload: SensorReadingCreate, session: Session = Depends(get_db)):
    return sensor_service.create_reading(session, payload)
