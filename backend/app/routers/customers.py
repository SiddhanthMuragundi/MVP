from __future__ import annotations

from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import or_, select
from sqlalchemy.orm import Session

from .. import reference
from ..core.security import get_current_user, require_admin
from ..database import get_db
from ..enums import Gender, JourneyStage, MaritalStatus, MatchStatus, Role
from ..models import Profile, User
from ..utils import compute_age
from ..schemas.match import MatchOut, OutcomeRequest
from ..schemas.note import NoteOut
from ..schemas.profile import (
    AssignMatchmakerRequest,
    CustomerDetail,
    CustomerListItem,
    FilterOptions,
    ProfileOut,
    StageUpdate,
)
from ..services.activity import client_label, log
from ._helpers import (
    compute_matches,
    get_or_create_match,
    is_matchable,
    least_loaded_matchmaker,
    load_client,
    load_client_readonly,
    serialize_match,
)

router = APIRouter(prefix="/customers", tags=["customers"])


@router.get("", response_model=list[CustomerListItem])
def list_customers(
    search: str | None = None,
    stage: JourneyStage | None = None,
    verified: bool | None = None,
    state: str | None = None,
    city: str | None = None,
    religion: str | None = None,
    language: str | None = None,
    gender: Gender | None = None,
    marital_status: MaritalStatus | None = None,
    age_min: int | None = None,
    age_max: int | None = None,
    mine: bool = False,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    # `mine` narrows the roster to the matchmaker's own clients.
    stmt = select(Profile)
    if mine:
        stmt = stmt.where(Profile.assigned_matchmaker_id == user.id)
    if stage is not None:
        stmt = stmt.where(Profile.journey_stage == stage)
    if verified is not None:
        # verified == (journey is past "New"); pending == "New" or no stage yet.
        if verified:
            stmt = stmt.where(Profile.journey_stage.isnot(None), Profile.journey_stage != JourneyStage.new)
        else:
            stmt = stmt.where(
                or_(Profile.journey_stage.is_(None), Profile.journey_stage == JourneyStage.new)
            )
    if religion:
        stmt = stmt.where(Profile.religion == religion)
    if gender is not None:
        stmt = stmt.where(Profile.gender == gender)
    if marital_status is not None:
        stmt = stmt.where(Profile.marital_status == marital_status)
    if city:
        stmt = stmt.where(Profile.city == city)
    if state:
        stmt = stmt.where(Profile.city.in_(reference.cities_for_state(state)))

    clients = list(db.scalars(stmt))
    if language:
        clients = [c for c in clients if language == c.mother_tongue or language in (c.languages_known or [])]
    if age_min is not None or age_max is not None:
        lo, hi = age_min or 0, age_max or 200
        clients = [c for c in clients if lo <= compute_age(c.dob) <= hi]
    if search:
        term = search.lower()

        def haystack(c: Profile) -> str:
            return " ".join(
                [
                    c.first_name, c.last_name, c.city, reference.state_for(c.city) or "",
                    c.religion, c.caste, c.mother_tongue, c.designation, c.company, c.degree,
                ]
            ).lower()

        clients = [c for c in clients if term in haystack(c)]

    for c in clients:
        c.mine = c.assigned_matchmaker_id == user.id
        c.assigned_matchmaker_name = c.matchmaker.display_name if c.matchmaker else None
        c.state = reference.state_for(c.city)

    items = [CustomerListItem.model_validate(c) for c in clients]
    items.sort(key=lambda x: (not x.mine, x.first_name.lower()))
    return items


@router.get("/filter-options", response_model=FilterOptions)
def filter_options(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    """Distinct roster filter values, computed from the live data (never hardcoded), so a
    new city/state/language/religion appears the moment such a profile exists."""
    clients = list(db.scalars(select(Profile)))

    cities_by_state: dict[str, list[str]] = {}
    for city in {c.city for c in clients if c.city}:
        st = reference.state_for(city)
        if st:
            cities_by_state.setdefault(st, []).append(city)
    for st in cities_by_state:
        cities_by_state[st].sort()

    languages: set[str] = set()
    for c in clients:
        if c.mother_tongue:
            languages.add(c.mother_tongue)
        languages.update(c.languages_known or [])

    return FilterOptions(
        states=sorted(cities_by_state.keys()),
        cities_by_state=cities_by_state,
        cities=sorted({c.city for c in clients if c.city}),
        languages=sorted(languages),
        religions=sorted({c.religion for c in clients if c.religion}),
        marital_statuses=sorted({c.marital_status.value for c in clients}),
    )


@router.get("/{customer_id}", response_model=CustomerDetail)
def get_customer(customer_id: int, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    client = load_client_readonly(db, customer_id)
    base = ProfileOut.model_validate(client).model_dump()
    base.pop("age", None)
    base.pop("mine", None)
    notes = [
        NoteOut(
            id=n.id,
            body=n.body,
            author_name=n.author.display_name if n.author else "",
            created_at=n.created_at,
        )
        for n in sorted(client.notes, key=lambda n: n.created_at, reverse=True)
    ]
    mine = client.assigned_matchmaker_id == user.id
    return CustomerDetail(
        **base,
        notes=notes,
        mine=mine,
        editable=mine,  # only the assigned matchmaker can act; admins are read-only overseers
        assigned_matchmaker_id=client.assigned_matchmaker_id,
        assigned_matchmaker_name=client.matchmaker.display_name if client.matchmaker else None,
    )


@router.patch("/{customer_id}/stage", response_model=ProfileOut)
def update_stage(customer_id: int, payload: StageUpdate, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    client = load_client(db, user, customer_id)
    client.journey_stage = payload.journey_stage
    log(db, user, "stage_changed",
        f"{user.display_name} moved {client_label(client)} to {payload.journey_stage.value.replace('_', ' ')}",
        customer_id=client.id)
    db.commit()
    return ProfileOut.model_validate(client)


@router.patch("/{customer_id}/matchmaker", response_model=ProfileOut)
def assign_matchmaker(customer_id: int, payload: AssignMatchmakerRequest, db: Session = Depends(get_db), admin: User = Depends(require_admin)):
    """Admin assigns/reassigns a client to a matchmaker. With no matchmaker_id, the
    client is auto-assigned to the least-loaded matchmaker."""
    client = load_client_readonly(db, customer_id)
    if payload.matchmaker_id is not None:
        target = db.get(User, payload.matchmaker_id)
        if target is None or target.role != Role.matchmaker:
            raise HTTPException(status.HTTP_400_BAD_REQUEST, "Not a valid matchmaker")
    else:
        target = least_loaded_matchmaker(db)
        if target is None:
            raise HTTPException(status.HTTP_400_BAD_REQUEST, "No matchmakers available")
    client.assigned_matchmaker_id = target.id
    log(db, admin, "client_assigned",
        f"{admin.display_name} assigned new client {client_label(client)} to {target.display_name}",
        customer_id=client.id, target_user_id=target.id, target_name=target.display_name)
    db.commit()
    return ProfileOut.model_validate(client)


@router.post("/{customer_id}/verify", response_model=ProfileOut)
def verify_customer(customer_id: int, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    client = load_client(db, user, customer_id)
    # Verifying = moving past "New". `verified` is derived from this, so they can't disagree.
    if client.journey_stage in (None, JourneyStage.new):
        client.journey_stage = JourneyStage.verified
    log(db, user, "client_verified", f"{user.display_name} verified {client_label(client)}", customer_id=client.id)
    db.commit()
    return ProfileOut.model_validate(client)


@router.get("/{customer_id}/matches", response_model=list[MatchOut])
def customer_matches(
    customer_id: int,
    limit: int = Query(10, ge=1, le=50),
    refresh: bool = False,
    explain: bool = True,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    client = load_client(db, user, customer_id)
    if not is_matchable(client):
        return []  # not verified, or on hold / closed
    rows = compute_matches(db, client, limit, explain, refresh)
    rows.sort(key=lambda r: r.score, reverse=True)
    return [serialize_match(r) for r in rows]


# A match that has gone out to the client (or has an outcome recorded) is past the
# reversible, internal "shortlist" stage.
_SENT_STATES = {
    MatchStatus.sent,
    MatchStatus.accepted,
    MatchStatus.declined,
    MatchStatus.no_response,
    MatchStatus.withdrawn,
}


@router.post("/{customer_id}/matches/{candidate_id}/shortlist", response_model=MatchOut)
def shortlist_match(customer_id: int, candidate_id: int, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    """Shortlisting is an internal, reversible pick. It does not touch the client."""
    client = load_client(db, user, customer_id)
    row = get_or_create_match(db, client, candidate_id)
    if row.status not in _SENT_STATES:  # already sent? leave it alone
        row.status = MatchStatus.shortlisted
        row.assigned_at = datetime.now(timezone.utc)
        db.commit()
    return serialize_match(row)


@router.delete("/{customer_id}/matches/{candidate_id}/shortlist", response_model=MatchOut)
def remove_shortlist(customer_id: int, candidate_id: int, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    client = load_client(db, user, customer_id)
    row = get_or_create_match(db, client, candidate_id)
    if row.status in _SENT_STATES:
        raise HTTPException(status.HTTP_409_CONFLICT, "This match was already sent, so it can't be unshortlisted.")
    row.status = MatchStatus.suggested  # keep the row for history, just reset the status
    row.assigned_at = None
    db.commit()
    return serialize_match(row)


@router.post("/{customer_id}/matches/{candidate_id}/outcome", response_model=MatchOut)
def set_match_outcome(
    customer_id: int,
    candidate_id: int,
    payload: OutcomeRequest,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """Record what happened after a match was sent (interested / not / no response)."""
    client = load_client(db, user, customer_id)
    row = get_or_create_match(db, client, candidate_id)
    if row.status not in _SENT_STATES:
        raise HTTPException(status.HTTP_409_CONFLICT, "Record an outcome only after the match has been sent.")
    row.status = MatchStatus(payload.outcome)
    log(db, user, "match_outcome", f"{user.display_name} updated a match outcome for {client_label(client)}", customer_id=client.id)
    db.commit()
    return serialize_match(row)
