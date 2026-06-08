"""Shared router helpers for loading clients and assembling match results."""
from __future__ import annotations

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from ..enums import JourneyStage, MatchStatus, Role, opposite_gender
from ..models import Match, Profile, User


def list_matchmakers_with_counts(db: Session):
    """Return matchmakers with their current client counts (for assignment UIs)."""
    matchmakers = list(db.scalars(select(User).where(User.role == Role.matchmaker).order_by(User.id)))
    result = []
    for m in matchmakers:
        count = db.query(Profile).filter(Profile.assigned_matchmaker_id == m.id).count()
        result.append((m, count))
    return result


def least_loaded_matchmaker(db: Session) -> User | None:
    pairs = list_matchmakers_with_counts(db)
    if not pairs:
        return None
    return min(pairs, key=lambda pc: pc[1])[0]
from ..schemas.match import MatchOut
from ..schemas.profile import ProfileOut
from ..services import llm
from ..services.matching import build_reasons, rank_matches, score_candidate, tier_for


def load_client_readonly(db: Session, customer_id: int) -> Profile:
    """Any authenticated matchmaker may view any client (read-only)."""
    client = db.get(Profile, customer_id)
    if client is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Customer not found")
    return client


def load_client(db: Session, user: User, customer_id: int) -> Profile:
    """Load a client for an action. Only the assigned matchmaker may act on a client;
    admins are read-only overseers (separation of duties), so they cannot act here."""
    client = load_client_readonly(db, customer_id)
    if client.assigned_matchmaker_id != user.id:
        raise HTTPException(status.HTTP_403_FORBIDDEN, "Only the assigned matchmaker can act on this client")
    return client


# A client is matched only while actively in the journey: verified, and neither
# paused (on hold) nor finished (closed). New/unverified clients verify first.
_INACTIVE_STAGES = {JourneyStage.on_hold, JourneyStage.closed}


def opposite_pool(db: Session, client: Profile) -> list[Profile]:
    """Candidates are drawn from the opposite-gender client base, as long as they are
    verified (past "New") and still available (not on hold or closed). Self is excluded."""
    stmt = select(Profile).where(
        Profile.id != client.id,
        Profile.gender == opposite_gender(client.gender),
        Profile.journey_stage.isnot(None),
        Profile.journey_stage.notin_([JourneyStage.new, *_INACTIVE_STAGES]),
    )
    return list(db.scalars(stmt))


def is_matchable(client: Profile) -> bool:
    return bool(client.verified) and client.journey_stage not in _INACTIVE_STAGES


def serialize_match(row: Match) -> MatchOut:
    return MatchOut(
        id=row.id,
        candidate=ProfileOut.model_validate(row.candidate),
        score=row.score,
        tier=row.tier,
        reasons=row.reasons or [],
        ai_explanation=row.ai_explanation,
        status=row.status,
    )


def result_to_match_out(result) -> MatchOut:
    """Serialize an in-memory MatchResult (not persisted) for chat search replies."""
    return MatchOut(
        id=None,
        candidate=ProfileOut.model_validate(result.candidate),
        score=result.score,
        tier=result.tier,
        reasons=result.reasons,
        ai_explanation=None,
        status=MatchStatus.suggested,
    )


def get_or_create_match(db: Session, client: Profile, candidate_id: int) -> Match:
    row = db.scalar(
        select(Match).where(Match.customer_id == client.id, Match.candidate_id == candidate_id)
    )
    if row is not None:
        return row

    candidate = db.get(Profile, candidate_id)
    if candidate is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Candidate not found")

    score, scores, weights = score_candidate(client, candidate)
    row = Match(
        customer_id=client.id,
        candidate_id=candidate_id,
        score=score,
        tier=tier_for(score),
        reasons=build_reasons(client, candidate, scores, weights),
        status=MatchStatus.suggested,
    )
    db.add(row)
    db.flush()
    return row


def compute_matches(db: Session, client: Profile, limit: int, explain: bool, refresh: bool) -> list[Match]:
    ranked = rank_matches(client, opposite_pool(db, client), limit)
    rows: list[Match] = []
    for result in ranked:
        row = db.scalar(
            select(Match).where(
                Match.customer_id == client.id,
                Match.candidate_id == result.candidate.id,
            )
        )
        if row is None:
            row = Match(customer_id=client.id, candidate_id=result.candidate.id, status=MatchStatus.suggested)
            db.add(row)
        row.score = result.score
        row.tier = result.tier
        row.reasons = result.reasons
        if explain and (refresh or not row.ai_explanation):
            row.ai_explanation = llm.explain_match(
                db, client, result.candidate, result.score, result.tier.value, result.reasons
            )
        rows.append(row)
    db.commit()
    return rows
