from __future__ import annotations

from datetime import datetime, timezone

from fastapi import APIRouter, Depends, Query
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from ..core.security import get_current_user
from ..database import get_db
from ..enums import Role
from ..models import Activity, User
from ..schemas.notification import ActivityOut, NotificationsResponse

router = APIRouter(tags=["notifications"])


@router.get("/notifications", response_model=NotificationsResponse)
def list_notifications(
    limit: int = Query(5, ge=1, le=50),
    before_id: int | None = None,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """Activity feed since the user last cleared. `before_id` pages older items.

    Admins see all activity (oversight). A matchmaker sees only events that involve
    them: their own actions, or a client the admin assigned to them.
    """
    base = select(Activity)
    if user.role != Role.admin:
        base = base.where((Activity.actor_user_id == user.id) | (Activity.target_user_id == user.id))
    if user.notifications_cleared_at is not None:
        base = base.where(Activity.created_at > user.notifications_cleared_at)

    stmt = base.order_by(Activity.id.desc())
    if before_id is not None:
        stmt = stmt.where(Activity.id < before_id)
    rows = list(db.scalars(stmt.limit(limit + 1)))
    has_more = len(rows) > limit
    rows = rows[:limit]

    count_stmt = select(func.count()).select_from(base.subquery())
    unread_count = db.scalar(count_stmt) or 0

    return NotificationsResponse(
        items=[ActivityOut.model_validate(r) for r in rows],
        unread_count=unread_count,
        has_more=has_more,
    )


@router.post("/notifications/clear")
def clear_notifications(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    user.notifications_cleared_at = datetime.now(timezone.utc)
    db.commit()
    return {"ok": True}
