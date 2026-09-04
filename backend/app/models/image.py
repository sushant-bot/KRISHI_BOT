from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, ForeignKey, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base

if TYPE_CHECKING:
    from app.models.farm import Farm
    from app.models.image import AIResult
    from app.models.zone import Zone


class CropImage(Base):
    __tablename__ = "crop_images"

    id: Mapped[int] = mapped_column(primary_key=True)
    farm_id: Mapped[int] = mapped_column(
        ForeignKey("farms.id", ondelete="CASCADE"), nullable=False, index=True
    )
    zone_id: Mapped[int] = mapped_column(
        ForeignKey("zones.id", ondelete="CASCADE"), nullable=False, index=True
    )
    image_path: Mapped[str] = mapped_column(String(1024), nullable=False)
    timestamp: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    farm: Mapped["Farm"] = relationship()
    zone: Mapped["Zone"] = relationship()
    ai_results: Mapped[list["AIResult"]] = relationship(
        back_populates="image", cascade="all, delete-orphan"
    )


class AIResult(Base):
    __tablename__ = "ai_results"

    id: Mapped[int] = mapped_column(primary_key=True)
    image_id: Mapped[int] = mapped_column(
        ForeignKey("crop_images.id", ondelete="CASCADE"), nullable=False, index=True
    )
    zone_id: Mapped[int] = mapped_column(
        ForeignKey("zones.id", ondelete="CASCADE"), nullable=False, index=True
    )
    crop_health: Mapped[str | None] = mapped_column(String(64))
    disease: Mapped[str | None] = mapped_column(String(128))
    confidence: Mapped[float | None] = mapped_column()
    growth_stage: Mapped[str | None] = mapped_column(String(64))
    provider: Mapped[str] = mapped_column(String(128), nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    image: Mapped["CropImage"] = relationship(back_populates="ai_results")