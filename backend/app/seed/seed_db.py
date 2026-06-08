"""Idempotent database seeding: matchmaker users plus client and pool profiles."""
from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.orm import Session

from ..config import settings
from ..core.security import hash_password
from ..enums import Role
from ..models import Profile, User
from .generate_profiles import generate_all


def seed_if_empty(db: Session) -> None:
    if db.scalar(select(User).limit(1)) is not None:
        return

    admin = User(
        username=settings.ADMIN_USERNAME,
        password_hash=hash_password(settings.ADMIN_PASSWORD),
        display_name="Admin",
        role=Role.admin,
    )
    matchmaker = User(
        username=settings.MATCHMAKER_USERNAME,
        password_hash=hash_password(settings.MATCHMAKER_PASSWORD),
        display_name=settings.MATCHMAKER_USERNAME.title(),
        role=Role.matchmaker,
    )
    matchmaker2 = User(
        username=settings.MATCHMAKER2_USERNAME,
        password_hash=hash_password(settings.MATCHMAKER2_PASSWORD),
        display_name=settings.MATCHMAKER2_USERNAME.title(),
        role=Role.matchmaker,
    )
    db.add_all([admin, matchmaker, matchmaker2])
    db.flush()  # assign user ids

    clients = generate_all(matchmaker_ids=[matchmaker.id, matchmaker2.id])
    db.add_all(clients)
    db.commit()
