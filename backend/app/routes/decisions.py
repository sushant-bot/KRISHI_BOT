from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.decision import (
    DecisionContextResponse,
    DecisionResultCreate,
    DecisionResultResponse,
)
from app.services import decision as decision_service

router = APIRouter(
    prefix="/decisions", tags=["decisions"]
)
zone_router = APIRouter(tags=["decisions"])


@router.post(
    "/analyze", response_model=DecisionResultResponse, status_code=status.HTTP_201_CREATED
)
def store_external_result(payload: DecisionResultCreate, session: Session = Depends(get_db)):
    return decision_service.create_result(session, payload)


@zone_router.get("/zones/{zone_id}/decision-context", response_model=DecisionContextResponse)
def get_decision_context(zone_id: int, session: Session = Depends(get_db)):
    return decision_service.build_context(session, zone_id)


@zone_router.get("/zones/{zone_id}/risks", response_model=list[DecisionResultResponse])
def list_risks(
    zone_id: int,
    limit: int = Query(default=100, ge=1, le=1000),
    session: Session = Depends(get_db),
):
    return decision_service.list_results(session, zone_id, limit)


@zone_router.get("/zones/{zone_id}/health", response_model=DecisionResultResponse | None)
def get_health(zone_id: int, session: Session = Depends(get_db)):
    results = decision_service.list_results(session, zone_id, 1)
    return results[0] if results else None