from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Farm
from app.schemas.digital_twin import FarmTwinResponse, ZoneTwinResponse
from app.services import digital_twin as digital_twin_service

router = APIRouter(
    prefix="/digital-twin", tags=["digital-twin"]
)


@router.get("", response_model=list[FarmTwinResponse])
def get_farm_twins(session: Session = Depends(get_db)):
    farms = list(session.query(Farm).order_by(Farm.id))
    return [digital_twin_service.build_farm_twin(session, farm) for farm in farms]


@router.get("/zones", response_model=list[ZoneTwinResponse])
def get_zone_twins(session: Session = Depends(get_db)):
    farms = list(session.query(Farm).order_by(Farm.id))
    return [
        digital_twin_service.build_zone_twin(session, zone)
        for farm in farms
        for zone in farm.zones
    ]


@router.get("/zones/{zone_id}", response_model=ZoneTwinResponse)
def get_zone_twin(zone_id: int, session: Session = Depends(get_db)):
    return digital_twin_service.get_zone_twin(session, zone_id)