from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, ForeignKey, String, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base

if TYPE_CHECKING:
    from app.models.farm import Farm
    from app.models.sensor_reading import SensorReading


class Zone(Base):
    __tablename__ = "zones"
    __table_args__ = (UniqueConstraint("farm_id", "code", name="uq_zone_farm_code"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    farm_id: Mapped[int] = mapped_column(
        ForeignKey("farms.id", ondelete="CASCADE"), nullable=False, index=True
    )
    code: Mapped[str] = mapped_column(String(32), nullable=False)
    name: Mapped[str] = mapped_column(String(120), nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    farm: Mapped["Farm"] = relationship(back_populates="zones")
    sensor_readings: Mapped[list["SensorReading"]] = relationship(
        back_populates="zone", cascade="all, delete-orphan"
    )
