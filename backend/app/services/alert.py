from sqlalchemy.orm import Session

from app.models import Alert
from app.repositories import alert as alert_repository
from app.services.farm import NotFoundError


def list_alerts(
    session: Session,
    farm_id: int | None,
    zone_id: int | None,
    unread_only: bool,
    limit: int,
) -> list[Alert]:
    return alert_repository.list_alerts(session, farm_id, zone_id, unread_only, limit)


def mark_read(session: Session, alert_id: int) -> Alert:
    alert = alert_repository.get_alert(session, alert_id)
    if alert is None:
        raise NotFoundError("Alert was not found.")
    alert.is_read = True
    session.commit()
    session.refresh(alert)
    return alert