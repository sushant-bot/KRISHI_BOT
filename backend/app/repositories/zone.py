from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import Zone


def create_zone(session: Session, zone: Zone) -> Zone:
    session.add(zone)
    session.commit()
    session.refresh(zone)
    return zone


def list_zones(session: Session, farm_id: int) -> list[Zone]:
    statement = select(Zone).where(Zone.farm_id == farm_id).order_by(Zone.id)
    return list(session.scalars(statement))


def get_zone(session: Session, zone_id: int) -> Zone | None:
    return session.get(Zone, zone_id)
