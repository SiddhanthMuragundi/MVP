from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel

from ..enums import LLMProvider


class LLMSettingOut(BaseModel):
    provider: LLMProvider | None
    model: str | None
    configured: bool
    masked_key: str | None
    updated_at: datetime | None


class LLMSettingUpdate(BaseModel):
    provider: LLMProvider
    # Omit/null to keep the existing stored key; provide to replace it.
    api_key: str | None = None
    model: str | None = None


class ModelListOut(BaseModel):
    models: list[str]
