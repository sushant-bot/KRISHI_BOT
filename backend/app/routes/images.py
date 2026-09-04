from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.image import CropImageCreate, CropImageResponse
from app.services import image as image_service

router = APIRouter(prefix="/images", tags=["images"])
zone_router = APIRouter(tags=["images"])


@router.post("", response_model=CropImageResponse, status_code=status.HTTP_201_CREATED)
def create_image(payload: CropImageCreate, session: Session = Depends(get_db)):
    return image_service.create_image(session, payload)


@router.get("/{image_id}", response_model=CropImageResponse)
def get_image(image_id: int, session: Session = Depends(get_db)):
    return image_service.get_image(session, image_id)


@router.get("/zone/{zone_id}", response_model=list[CropImageResponse])
def list_images(
    zone_id: int,
    limit: int = Query(default=100, ge=1, le=1000),
    session: Session = Depends(get_db),
):
    return image_service.list_images(session, zone_id, limit)


@zone_router.get("/zones/{zone_id}/images", response_model=list[CropImageResponse])
def list_zone_images(
    zone_id: int,
    limit: int = Query(default=100, ge=1, le=1000),
    session: Session = Depends(get_db),
):
    return image_service.list_images(session, zone_id, limit)