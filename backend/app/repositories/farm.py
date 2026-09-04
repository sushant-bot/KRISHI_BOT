from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import Farm


def create_farm(session: Session, farm: Farm) -> Farm:
    session.add(farm)
    session.commit()
    session.refresh(farm)
    return farm


def list_farms(session: Session) -> list[Farm]:
    return list(session.scalars(select(Farm).order_by(Farm.id)))


def get_farm(session: Session, farm_id: int) -> Farm | None:
    return session.get(Farm, farm_id)
