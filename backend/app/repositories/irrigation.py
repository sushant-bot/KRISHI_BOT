from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import IrrigationEvent, IrrigationStatus, WaterFlowReading


def create_event(session: Session, event: IrrigationEvent) -> IrrigationEvent:
    session.add(event)
    session.commit()
    session.refresh(event)
    return event


def get_event(session: Session, event_id: int) -> IrrigationEvent | None:
    return session.get(IrrigationEvent, event_id)


def get_active_event(session: Session, zone_id: int) -> IrrigationEvent | None:
    statement = (
        select(IrrigationEvent)
        .where(
            IrrigationEvent.zone_id == zone_id,
            IrrigationEvent.status == IrrigationStatus.ACTIVE,
        )
        .order_by(IrrigationEvent.id.desc())
    )
    return session.scalars(statement).first()


def list_events(session: Session, zone_id: int | None, limit: int) -> list[IrrigationEvent]:
    statement = select(IrrigationEvent).order_by(IrrigationEvent.id.desc()).limit(limit)
    if zone_id is not None:
        statement = statement.where(IrrigationEvent.zone_id == zone_id)
    return list(session.scalars(statement))


def create_flow_reading(session: Session, reading: WaterFlowReading) -> WaterFlowReading:
    session.add(reading)
    session.commit()
    session.refresh(reading)
    return reading