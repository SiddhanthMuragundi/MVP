from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, ConfigDict


class ActivityOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    actor_user_id: int | None
    actor_name: str
    target_user_id: int | None
    target_name: str | None
    customer_id: int | None
    action: str
    message: str
    created_at: datetime


class NotificationsResponse(BaseModel):
    items: list[ActivityOut]
    unread_count: int
    has_more: bool
