from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import Alert


def create_alert(session: Session, alert: Alert) -> Alert:
    session.add(alert)
    session.flush()
    return alert


def list_alerts(
    session: Session,
    farm_id: int | None,
    zone_id: int | None,
    unread_only: bool,
    limit: int,
) -> list[Alert]:
    statement = select(Alert).order_by(Alert.created_at.desc(), Alert.id.desc()).limit(limit)
    if farm_id is not None:
        statement = statement.where(Alert.farm_id == farm_id)
    if zone_id is not None:
        statement = statement.where(Alert.zone_id == zone_id)
    if unread_only:
        statement = statement.where(Alert.is_read.is_(False))
    return list(session.scalars(statement))


def get_alert(session: Session, alert_id: int) -> Alert | None:
    return session.get(Alert, alert_id)