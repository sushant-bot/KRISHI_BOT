from sqlalchemy.orm import Session

from app.models import DecisionResult
from app.repositories import decision as decision_repository
from app.repositories import image as image_repository
from app.repositories import irrigation as irrigation_repository
from app.repositories import sensor as sensor_repository
from app.schemas.decision import (
    AIContext,
    DecisionContextResponse,
    DecisionResultCreate,
    IrrigationContext,
    SensorContext,
)
from app.services.farm import get_zone


def create_result(session: Session, payload: DecisionResultCreate) -> DecisionResult:
    get_zone(session, payload.zone_id)
    return decision_repository.create_result(
        session, DecisionResult(**payload.model_dump())
    )


def list_results(session: Session, zone_id: int, limit: int) -> list[DecisionResult]:
    get_zone(session, zone_id)
    return decision_repository.list_results(session, zone_id, limit)


def build_context(session: Session, zone_id: int) -> DecisionContextResponse:
    get_zone(session, zone_id)
    sensor = sensor_repository.list_readings(session, zone_id, 1)
    ai_results = image_repository.list_ai_results(session, zone_id, 1)
    irrigation = irrigation_repository.get_active_event(session, zone_id)

    latest_sensor = None
    if sensor:
        latest_sensor = SensorContext.model_validate(sensor[0])

    latest_ai_result = None
    if ai_results:
        latest_ai_result = AIContext.model_validate(ai_results[0])

    active_irrigation = None
    if irrigation:
        active_irrigation = IrrigationContext(
            event_id=irrigation.id,
            status=irrigation.status,
            water_delivered_liters=irrigation.water_delivered_liters,
        )

    return DecisionContextResponse(
        zone_id=zone_id,
        latest_sensor=latest_sensor,
        latest_ai_result=latest_ai_result,
        active_irrigation=active_irrigation,
    )