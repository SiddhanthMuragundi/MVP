from __future__ import annotations

from datetime import datetime, timezone

from sqlalchemy import DateTime, Enum, Float, ForeignKey, Integer, Text, UniqueConstraint
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ..database import Base
from ..enums import MatchStatus, MatchTier


def _now() -> datetime:
    return datetime.now(timezone.utc)


class Match(Base):
    __tablename__ = "matches"
    __table_args__ = (UniqueConstraint("customer_id", "candidate_id", name="uq_match_pair"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    customer_id: Mapped[int] = mapped_column(ForeignKey("profiles.id"), nullable=False, index=True)
    candidate_id: Mapped[int] = mapped_column(ForeignKey("profiles.id"), nullable=False)

    score: Mapped[float] = mapped_column(Float, nullable=False)
    tier: Mapped[MatchTier] = mapped_column(Enum(MatchTier, name="match_tier"), nullable=False)
    reasons: Mapped[list[str]] = mapped_column(JSONB, default=list)
    ai_explanation: Mapped[str | None] = mapped_column(Text, nullable=True)

    status: Mapped[MatchStatus] = mapped_column(Enum(MatchStatus, name="match_status"), default=MatchStatus.suggested)
    assigned_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    sent_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_now)

    candidate = relationship("Profile", foreign_keys=[candidate_id])
