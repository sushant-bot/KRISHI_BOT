from sqlalchemy.orm import Session

from app.models import SensorReading
from app.repositories import sensor as sensor_repository
from app.schemas.sensor import SensorReadingCreate
from app.services.farm import get_zone


def create_reading(session: Session, payload: SensorReadingCreate) -> SensorReading:
    get_zone(session, payload.zone_id)
    reading = SensorReading(**payload.model_dump())
    return sensor_repository.create_reading(session, reading)


def list_readings(session: Session, zone_id: int, limit: int) -> list[SensorReading]:
    get_zone(session, zone_id)
    return sensor_repository.list_readings(session, zone_id, limit)
