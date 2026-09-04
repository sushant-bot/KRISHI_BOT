from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Integer, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class DecisionResult(Base):
    __tablename__ = "decision_results"

    id: Mapped[int] = mapped_column(primary_key=True)
    zone_id: Mapped[int] = mapped_column(
        ForeignKey("zones.id", ondelete="CASCADE"), nullable=False, index=True
    )
    irrigation_priority: Mapped[str | None] = mapped_column(String(32))
    water_stress: Mapped[str | None] = mapped_column(String(32))
    heat_stress: Mapped[str | None] = mapped_column(String(32))
    disease_spread_risk: Mapped[str | None] = mapped_column(String(32))
    yield_risk: Mapped[str | None] = mapped_column(String(32))
    farm_health_score: Mapped[int | None] = mapped_column(Integer)
    advisory: Mapped[str | None] = mapped_column(Text)
    provider: Mapped[str] = mapped_column(String(128), nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )