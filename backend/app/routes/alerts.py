from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.alert import AlertResponse
from app.services import alert as alert_service

router = APIRouter(prefix="/alerts", tags=["alerts"])


@router.get("", response_model=list[AlertResponse])
def list_alerts(
    farm_id: int | None = Query(default=None, gt=0),
    zone_id: int | None = Query(default=None, gt=0),
    unread_only: bool = False,
    limit: int = Query(default=100, ge=1, le=1000),
    session: Session = Depends(get_db),
):
    return alert_service.list_alerts(session, farm_id, zone_id, unread_only, limit)


@router.patch("/{alert_id}/read", response_model=AlertResponse)
def mark_alert_read(alert_id: int, session: Session = Depends(get_db)):
    return alert_service.mark_read(session, alert_id)