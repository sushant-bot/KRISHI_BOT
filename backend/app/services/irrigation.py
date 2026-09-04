from datetime import UTC, datetime

from sqlalchemy.orm import Session

from app.models import (
    Alert,
    IrrigationAction,
    IrrigationEvent,
    IrrigationStatus,
    PumpStatus,
    WaterFlowReading,
)
from app.repositories import alert as alert_repository
from app.repositories import irrigation as irrigation_repository
from app.schemas.irrigation import FlowFeedback, IrrigationCommand
from app.services.farm import ConflictError, get_zone


def issue_command(session: Session, payload: IrrigationCommand) -> IrrigationEvent:
    zone = get_zone(session, payload.zone_id)
    active_event = irrigation_repository.get_active_event(session, payload.zone_id)

    if payload.action == IrrigationAction.START:
        if active_event is not None:
            raise ConflictError("Irrigation is already active for this zone.")
        return irrigation_repository.create_event(
            session,
            IrrigationEvent(
                zone_id=zone.id,
                command=payload.action,
                target_water_liters=payload.target_water_liters,
                status=IrrigationStatus.ACTIVE,
            ),
        )

    if active_event is None:
        raise ConflictError("No active irrigation event exists for this zone.")
    active_event.command = payload.action
    active_event.status = IrrigationStatus.STOPPED
    active_event.ended_at = datetime.now(UTC)
    session.commit()
    session.refresh(active_event)
    return active_event


def record_flow(session: Session, payload: FlowFeedback) -> WaterFlowReading:
    zone = get_zone(session, payload.zone_id)
    event = irrigation_repository.get_active_event(session, payload.zone_id)
    if event is None:
        raise ConflictError("No active irrigation event exists for this zone.")

    timestamp = payload.timestamp or datetime.now(UTC)
    reading = WaterFlowReading(
        irrigation_event_id=event.id,
        zone_id=zone.id,
        timestamp=timestamp,
        flow_rate=payload.flow_rate,
        water_delivered_liters=payload.water_delivered,
        pump_status=payload.pump_status,
    )
    event.water_delivered_liters = payload.water_delivered

    if payload.pump_status == PumpStatus.ON and payload.flow_rate == 0:
        event.status = IrrigationStatus.FAILED
        event.ended_at = timestamp
        event.fault_message = "Pump is on but water flow is zero."
        alert_repository.create_alert(
            session,
            Alert(
                farm_id=zone.farm_id,
                zone_id=zone.id,
                type="IRRIGATION_FLOW_FAILURE",
                severity="HIGH",
                message=event.fault_message,
            ),
        )
    elif (
        event.target_water_liters is not None
        and payload.water_delivered >= event.target_water_liters
    ):
        event.status = IrrigationStatus.COMPLETED
        event.ended_at = timestamp

    return irrigation_repository.create_flow_reading(session, reading)


def get_status(session: Session, zone_id: int) -> IrrigationEvent | None:
    get_zone(session, zone_id)
    return irrigation_repository.get_active_event(session, zone_id)


def get_history(session: Session, zone_id: int | None, limit: int) -> list[IrrigationEvent]:
    if zone_id is not None:
        get_zone(session, zone_id)
    return irrigation_repository.list_events(session, zone_id, limit)