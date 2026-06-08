from __future__ import annotations

from datetime import date, datetime, timezone

from sqlalchemy import Boolean, Date, DateTime, Enum, Float, ForeignKey, Integer, String, Text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ..database import Base
from ..enums import (
    Diet,
    FamilyType,
    Frequency,
    Gender,
    JourneyStage,
    Manglik,
    MaritalStatus,
    TriState,
)


def _now() -> datetime:
    return datetime.now(timezone.utc)


class Profile(Base):
    """A client of the studio. Matching draws each client's candidates from the
    opposite-gender clients (see ``opposite_pool``)."""

    __tablename__ = "profiles"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)

    first_name: Mapped[str] = mapped_column(String(64), nullable=False)
    last_name: Mapped[str] = mapped_column(String(64), nullable=False)
    gender: Mapped[Gender] = mapped_column(Enum(Gender, name="gender"), nullable=False, index=True)
    dob: Mapped[date] = mapped_column(Date, nullable=False)
    country: Mapped[str] = mapped_column(String(64), nullable=False)
    city: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    height_cm: Mapped[int] = mapped_column(Integer, nullable=False)

    email: Mapped[str] = mapped_column(String(128), nullable=False)
    phone: Mapped[str] = mapped_column(String(32), nullable=False)

    ug_college: Mapped[str] = mapped_column(String(128), nullable=False)
    degree: Mapped[str] = mapped_column(String(64), nullable=False)
    income_lpa: Mapped[float] = mapped_column(Float, nullable=False)
    company: Mapped[str] = mapped_column(String(128), nullable=False)
    designation: Mapped[str] = mapped_column(String(128), nullable=False)

    marital_status: Mapped[MaritalStatus] = mapped_column(Enum(MaritalStatus, name="marital_status"), nullable=False)
    languages_known: Mapped[list[str]] = mapped_column(JSONB, default=list)
    siblings: Mapped[int] = mapped_column(Integer, default=0)

    caste: Mapped[str] = mapped_column(String(64), nullable=False)
    religion: Mapped[str] = mapped_column(String(64), nullable=False)
    mother_tongue: Mapped[str] = mapped_column(String(64), nullable=False)
    manglik: Mapped[Manglik] = mapped_column(Enum(Manglik, name="manglik"), nullable=False)

    want_kids: Mapped[TriState] = mapped_column(Enum(TriState, name="want_kids"), nullable=False)
    open_to_relocate: Mapped[TriState] = mapped_column(Enum(TriState, name="open_to_relocate"), nullable=False)
    open_to_pets: Mapped[TriState] = mapped_column(Enum(TriState, name="open_to_pets"), nullable=False)

    diet: Mapped[Diet] = mapped_column(Enum(Diet, name="diet"), nullable=False)
    smoking: Mapped[Frequency] = mapped_column(Enum(Frequency, name="smoking"), nullable=False)
    drinking: Mapped[Frequency] = mapped_column(Enum(Frequency, name="drinking"), nullable=False)
    family_type: Mapped[FamilyType] = mapped_column(Enum(FamilyType, name="family_type"), nullable=False)

    hobbies: Mapped[list[str]] = mapped_column(JSONB, default=list)
    bio: Mapped[str] = mapped_column(Text, default="")
    photo_url: Mapped[str] = mapped_column(String(512), default="")

    journey_stage: Mapped[JourneyStage | None] = mapped_column(Enum(JourneyStage, name="journey_stage"), nullable=True)
    assigned_matchmaker_id: Mapped[int | None] = mapped_column(ForeignKey("users.id"), nullable=True)

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_now)

    matchmaker = relationship("User", back_populates="clients", foreign_keys=[assigned_matchmaker_id])
    notes = relationship("Note", back_populates="customer", cascade="all, delete-orphan")

    @property
    def verified(self) -> bool:
        """Verification is part of the journey, not a separate flag: a client is verified
        once they move past "New". This makes a verified/stage contradiction impossible."""
        return self.journey_stage is not None and self.journey_stage != JourneyStage.new
