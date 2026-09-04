from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.farm import FarmCreate, FarmResponse
from app.schemas.zone import ZoneCreate, ZoneResponse
from app.services import farm as farm_service

router = APIRouter(prefix="/farms", tags=["farms"])


@router.post("", response_model=FarmResponse, status_code=status.HTTP_201_CREATED)
def create_farm(payload: FarmCreate, session: Session = Depends(get_db)):
    return farm_service.create_farm(session, payload)


@router.get("", response_model=list[FarmResponse])
def list_farms(session: Session = Depends(get_db)):
    return farm_service.list_farms(session)


@router.get("/{farm_id}", response_model=FarmResponse)
def get_farm(farm_id: int, session: Session = Depends(get_db)):
    return farm_service.get_farm(session, farm_id)


@router.post("/{farm_id}/zones", response_model=ZoneResponse, status_code=status.HTTP_201_CREATED)
def create_zone(farm_id: int, payload: ZoneCreate, session: Session = Depends(get_db)):
    return farm_service.create_zone(session, farm_id, payload)


@router.get("/{farm_id}/zones", response_model=list[ZoneResponse])
def list_zones(farm_id: int, session: Session = Depends(get_db)):
    return farm_service.list_zones(session, farm_id)
