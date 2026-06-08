"""Audit/activity logging. Records only non-sensitive, human-readable events."""
from __future__ import annotations

from sqlalchemy.orm import Session

from ..models import Activity, Profile, User


def client_label(client: Profile) -> str:
    """A minimal, non-sensitive label: first name + last initial (no contact/biodata)."""
    last_initial = f" {client.last_name[0]}." if client.last_name else ""
    return f"{client.first_name}{last_initial}"


def log(
    db: Session,
    actor: User,
    action: str,
    message: str,
    customer_id: int | None = None,
    target_user_id: int | None = None,
    target_name: str | None = None,
) -> None:
    """Append an activity row. The caller's commit persists it (same transaction).

    ``customer_id`` links the event to a client so clicking the notification opens
    them. ``target_user_id`` defaults to the actor; pass an explicit one for
    cross-user events like assignment.
    """
    db.add(
        Activity(
            actor_user_id=actor.id,
            actor_name=actor.display_name,
            target_user_id=target_user_id if target_user_id is not None else actor.id,
            target_name=target_name,
            customer_id=customer_id,
            action=action,
            message=message,
        )
    )
