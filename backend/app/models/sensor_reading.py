from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, Float, ForeignKey, Index, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base

if TYPE_CHECKING:
    from app.models.zone import Zone


class SensorReading(Base):
    __tablename__ = "sensor_readings"
    __table_args__ = (Index("ix_sensor_readings_zone_timestamp", "zone_id", "timestamp"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    zone_id: Mapped[int] = mapped_column(
        ForeignKey("zones.id", ondelete="CASCADE"), nullable=False, index=True
    )
    timestamp: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    soil_moisture: Mapped[float] = mapped_column(Float, nullable=False)
    soil_temperature: Mapped[float] = mapped_column(Float, nullable=False)
    light_intensity: Mapped[float] = mapped_column(Float, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    zone: Mapped["Zone"] = relationship(back_populates="sensor_readings")
