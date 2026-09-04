from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.sensor import SensorReadingCreate, SensorReadingResponse
from app.services import sensor as sensor_service

router = APIRouter(prefix="/sensors", tags=["sensors"])


@router.post("/readings", response_model=SensorReadingResponse, status_code=201)
def create_reading(payload: SensorReadingCreate, session: Session = Depends(get_db)):
    return sensor_service.create_reading(session, payload)