from __future__ import annotations

from datetime import date, datetime

from pydantic import BaseModel, ConfigDict, computed_field

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
from ..utils import compute_age
from .note import NoteOut


class FilterOptions(BaseModel):
    """Distinct roster values, derived live from the data so filters never go stale."""

    states: list[str]
    cities_by_state: dict[str, list[str]]
    cities: list[str]
    languages: list[str]
    religions: list[str]
    marital_statuses: list[str]


class CustomerListItem(BaseModel):
    """Compact row for the dashboard customer list."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    first_name: str
    last_name: str
    dob: date
    city: str
    state: str | None = None
    marital_status: MaritalStatus
    journey_stage: JourneyStage | None
    verified: bool
    photo_url: str
    assigned_matchmaker_id: int | None = None
    assigned_matchmaker_name: str | None = None
    mine: bool = False

    @computed_field
    @property
    def age(self) -> int:
        return compute_age(self.dob)


class ProfileOut(BaseModel):
    """Full biodata for the detail view and match cards."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    first_name: str
    last_name: str
    gender: Gender
    dob: date
    country: str
    city: str
    height_cm: int
    email: str
    phone: str
    ug_college: str
    degree: str
    income_lpa: float
    company: str
    designation: str
    marital_status: MaritalStatus
    languages_known: list[str]
    siblings: int
    caste: str
    religion: str
    mother_tongue: str
    manglik: Manglik
    want_kids: TriState
    open_to_relocate: TriState
    open_to_pets: TriState
    diet: Diet
    smoking: Frequency
    drinking: Frequency
    family_type: FamilyType
    hobbies: list[str]
    bio: str
    photo_url: str
    verified: bool
    journey_stage: JourneyStage | None

    @computed_field
    @property
    def age(self) -> int:
        return compute_age(self.dob)


class CustomerDetail(ProfileOut):
    notes: list[NoteOut] = []
    mine: bool = False
    editable: bool = False  # the assigned matchmaker OR an admin
    assigned_matchmaker_id: int | None = None
    assigned_matchmaker_name: str | None = None


class StageUpdate(BaseModel):
    journey_stage: JourneyStage


class MatchmakerOut(BaseModel):
    id: int
    display_name: str
    client_count: int


class AssignMatchmakerRequest(BaseModel):
    # None -> auto-assign to the least-loaded matchmaker.
    matchmaker_id: int | None = None
