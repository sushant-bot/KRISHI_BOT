from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.irrigation import (
    FlowFeedback,
    FlowResponse,
    IrrigationCommand,
    IrrigationResponse,
)
from app.services import irrigation as irrigation_service

router = APIRouter(
    prefix="/irrigation", tags=["irrigation"]
)


@router.post(
    "/command", response_model=IrrigationResponse, status_code=status.HTTP_201_CREATED
)
def issue_command(payload: IrrigationCommand, session: Session = Depends(get_db)):
    return irrigation_service.issue_command(session, payload)


@router.get("/status", response_model=IrrigationResponse | None)
def get_status(zone_id: int = Query(gt=0), session: Session = Depends(get_db)):
    return irrigation_service.get_status(session, zone_id)


@router.get("/history", response_model=list[IrrigationResponse])
def get_history(
    zone_id: int | None = Query(default=None, gt=0),
    limit: int = Query(default=100, ge=1, le=1000),
    session: Session = Depends(get_db),
):
    return irrigation_service.get_history(session, zone_id, limit)


@router.post("/flow", response_model=FlowResponse, status_code=status.HTTP_201_CREATED)
def record_flow(payload: FlowFeedback, session: Session = Depends(get_db)):
    return irrigation_service.record_flow(session, payload)