from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.models import Farm, Zone
from app.repositories import farm as farm_repository
from app.repositories import zone as zone_repository
from app.schemas.farm import FarmCreate
from app.schemas.zone import ZoneCreate


class NotFoundError(Exception):
    pass


class ConflictError(Exception):
    pass


def create_farm(session: Session, payload: FarmCreate) -> Farm:
    return farm_repository.create_farm(session, Farm(name=payload.name, location=payload.location))


def list_farms(session: Session) -> list[Farm]:
    return farm_repository.list_farms(session)


def get_farm(session: Session, farm_id: int) -> Farm:
    farm = farm_repository.get_farm(session, farm_id)
    if farm is None:
        raise NotFoundError("Farm was not found.")
    return farm


def create_zone(session: Session, farm_id: int, payload: ZoneCreate) -> Zone:
    get_farm(session, farm_id)
    zone = Zone(farm_id=farm_id, code=payload.code, name=payload.name)
    try:
        return zone_repository.create_zone(session, zone)
    except IntegrityError as exc:
        session.rollback()
        raise ConflictError("A zone with this code already exists in the farm.") from exc


def list_zones(session: Session, farm_id: int) -> list[Zone]:
    get_farm(session, farm_id)
    return zone_repository.list_zones(session, farm_id)


def get_zone(session: Session, zone_id: int) -> Zone:
    zone = zone_repository.get_zone(session, zone_id)
    if zone is None:
        raise NotFoundError("Zone was not found.")
    return zone
