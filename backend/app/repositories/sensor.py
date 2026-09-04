from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import SensorReading


def create_reading(session: Session, reading: SensorReading) -> SensorReading:
    session.add(reading)
    session.commit()
    session.refresh(reading)
    return reading


def list_readings(session: Session, zone_id: int, limit: int) -> list[SensorReading]:
    statement = (
        select(SensorReading)
        .where(SensorReading.zone_id == zone_id)
        .order_by(SensorReading.timestamp.desc(), SensorReading.id.desc())
        .limit(limit)
    )
    return list(session.scalars(statement))
