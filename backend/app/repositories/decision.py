from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import DecisionResult


def create_result(session: Session, result: DecisionResult) -> DecisionResult:
    session.add(result)
    session.commit()
    session.refresh(result)
    return result


def list_results(session: Session, zone_id: int, limit: int) -> list[DecisionResult]:
    statement = (
        select(DecisionResult)
        .where(DecisionResult.zone_id == zone_id)
        .order_by(DecisionResult.created_at.desc(), DecisionResult.id.desc())
        .limit(limit)
    )
    return list(session.scalars(statement))