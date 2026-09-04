from sqlalchemy.orm import Session

from app.models import Farm, Zone
from app.repositories import alert as alert_repository
from app.repositories import decision as decision_repository
from app.repositories import image as image_repository
from app.repositories import irrigation as irrigation_repository
from app.repositories import sensor as sensor_repository
from app.schemas.decision import AIContext, IrrigationContext, SensorContext
from app.schemas.digital_twin import FarmTwinResponse, ZoneTwinResponse
from app.services.farm import NotFoundError


def build_zone_twin(session: Session, zone: Zone) -> ZoneTwinResponse:
    sensors = sensor_repository.list_readings(session, zone.id, 1)
    images = image_repository.list_images(session, zone.id, 1)
    ai_results = image_repository.list_ai_results(session, zone.id, 1)
    risks = decision_repository.list_results(session, zone.id, 100)
    active_irrigation = irrigation_repository.get_active_event(session, zone.id)
    alerts = alert_repository.list_alerts(session, None, zone.id, False, 100)

    current = SensorContext.model_validate(sensors[0]) if sensors else None
    ai = AIContext.model_validate(ai_results[0]) if ai_results else None
    irrigation = None
    if active_irrigation:
        irrigation = IrrigationContext(
            event_id=active_irrigation.id,
            status=active_irrigation.status,
            water_delivered_liters=active_irrigation.water_delivered_liters,
        )

    return ZoneTwinResponse(
        zone_id=zone.id,
        current=current,
        latest_image=images[0] if images else None,
        ai=ai,
        risks=risks,
        health_score=risks[0] if risks else None,
        irrigation=irrigation,
        alerts=alerts,
    )


def build_farm_twin(session: Session, farm: Farm) -> FarmTwinResponse:
    return FarmTwinResponse(
        farm_id=farm.id,
        zones=[build_zone_twin(session, zone) for zone in farm.zones],
    )


def get_zone_twin(session: Session, zone_id: int) -> ZoneTwinResponse:
    zone = session.get(Zone, zone_id)
    if zone is None:
        raise NotFoundError("Zone was not found.")
    return build_zone_twin(session, zone)