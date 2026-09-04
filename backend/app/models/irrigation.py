from datetime import datetime
from enum import StrEnum
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, Float, ForeignKey, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base

if TYPE_CHECKING:
    from app.models.zone import Zone


class IrrigationAction(StrEnum):
    START = "START"
    STOP = "STOP"


class IrrigationStatus(StrEnum):
    ACTIVE = "ACTIVE"
    COMPLETED = "COMPLETED"
    STOPPED = "STOPPED"
    FAILED = "FAILED"


class PumpStatus(StrEnum):
    ON = "ON"
    OFF = "OFF"


class IrrigationEvent(Base):
    __tablename__ = "irrigation_events"

    id: Mapped[int] = mapped_column(primary_key=True)
    zone_id: Mapped[int] = mapped_column(
        ForeignKey("zones.id", ondelete="CASCADE"), nullable=False, index=True
    )
    command: Mapped[IrrigationAction] = mapped_column(String(16), nullable=False)
    started_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    ended_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    target_water_liters: Mapped[float | None] = mapped_column(Float)
    water_delivered_liters: Mapped[float] = mapped_column(Float, default=0, nullable=False)
    status: Mapped[IrrigationStatus] = mapped_column(
        String(16), default=IrrigationStatus.ACTIVE, nullable=False, index=True
    )
    fault_message: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    zone: Mapped["Zone"] = relationship()
    flow_readings: Mapped[list["WaterFlowReading"]] = relationship(
        back_populates="irrigation_event", cascade="all, delete-orphan"
    )


class WaterFlowReading(Base):
    __tablename__ = "water_flow_readings"

    id: Mapped[int] = mapped_column(primary_key=True)
    irrigation_event_id: Mapped[int] = mapped_column(
        ForeignKey("irrigation_events.id", ondelete="CASCADE"), nullable=False, index=True
    )
    zone_id: Mapped[int] = mapped_column(
        ForeignKey("zones.id", ondelete="CASCADE"), nullable=False, index=True
    )
    timestamp: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    flow_rate: Mapped[float] = mapped_column(Float, nullable=False)
    water_delivered_liters: Mapped[float] = mapped_column(Float, nullable=False)
    pump_status: Mapped[PumpStatus] = mapped_column(String(8), nullable=False)

    irrigation_event: Mapped["IrrigationEvent"] = relationship(back_populates="flow_readings")