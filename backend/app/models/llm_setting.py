from __future__ import annotations

from datetime import datetime

from sqlalchemy import DateTime, Enum, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from ..database import Base
from ..enums import LLMProvider


class LLMSetting(Base):
    """Single active LLM configuration (row id is always 1).

    The API key is stored encrypted (AES-256-GCM) and never returned to clients.
    """

    __tablename__ = "llm_settings"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    provider: Mapped[LLMProvider | None] = mapped_column(Enum(LLMProvider, name="llm_provider"), nullable=True)
    api_key_encrypted: Mapped[str | None] = mapped_column(Text, nullable=True)
    model: Mapped[str | None] = mapped_column(String(128), nullable=True)
    updated_by: Mapped[int | None] = mapped_column(ForeignKey("users.id"), nullable=True)
    updated_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
