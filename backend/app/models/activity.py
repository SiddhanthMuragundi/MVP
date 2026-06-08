from __future__ import annotations

from datetime import datetime, timezone

from sqlalchemy import DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from ..database import Base


def _now() -> datetime:
    return datetime.now(timezone.utc)


class Activity(Base):
    """Append-only audit/activity log. Holds no sensitive data (no contact details or
    biodata) — only who did what, described for a human reader.

    ``actor_user_id`` is who performed the action; ``target_user_id`` is the matchmaker
    it concerns (e.g. who a client was assigned to). These drive notification audience.
    """

    __tablename__ = "activity"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    actor_user_id: Mapped[int | None] = mapped_column(ForeignKey("users.id"), nullable=True)
    actor_name: Mapped[str] = mapped_column(String(128), nullable=False)
    target_user_id: Mapped[int | None] = mapped_column(ForeignKey("users.id"), nullable=True)
    target_name: Mapped[str | None] = mapped_column(String(128), nullable=True)
    customer_id: Mapped[int | None] = mapped_column(ForeignKey("profiles.id"), nullable=True)
    action: Mapped[str] = mapped_column(String(64), nullable=False)
    message: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_now, index=True)
