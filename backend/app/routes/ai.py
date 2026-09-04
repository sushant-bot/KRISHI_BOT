from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.image import AIResultCreate, AIResultResponse
from app.services import image as image_service

router = APIRouter(prefix="/ai", tags=["ai"])
zone_router = APIRouter(tags=["ai"])


@router.post("/analyze", response_model=AIResultResponse, status_code=status.HTTP_201_CREATED)
def store_external_result(payload: AIResultCreate, session: Session = Depends(get_db)):
    return image_service.create_ai_result(session, payload)


@router.get("/zones/{zone_id}/results", response_model=list[AIResultResponse])
def list_results(
    zone_id: int,
    limit: int = Query(default=100, ge=1, le=1000),
    session: Session = Depends(get_db),
):
    return image_service.list_ai_results(session, zone_id, limit)


@zone_router.get("/zones/{zone_id}/ai-results", response_model=list[AIResultResponse])
def list_zone_results(
    zone_id: int,
    limit: int = Query(default=100, ge=1, le=1000),
    session: Session = Depends(get_db),
):
    return image_service.list_ai_results(session, zone_id, limit)