from __future__ import annotations

import difflib
import re

from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.orm import Session

from ..core.security import get_current_user
from ..database import get_db
from ..enums import ChatIntent
from ..models import Match, Profile, User
from ..schemas.chat import ChatRequest, ChatResponse
from ..services import llm
from ..services.matching import rank_matches
from ..utils import compute_age
from ._helpers import compute_matches, is_matchable, load_client, opposite_pool, result_to_match_out

router = APIRouter(tags=["chat"])


@router.post("/chat", response_model=ChatResponse)
def chat(payload: ChatRequest, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    client = load_client(db, user, payload.client_id) if payload.client_id else None
    notes = list(client.notes) if client else None
    ai_used = llm.get_active_llm(db) is not None
    history = [(t.role, t.content) for t in payload.history]

    # Ground the assistant in this client's actual ranked matches — the only people it
    # may discuss. This stops it inventing names or picking an unrelated pool profile.
    ranked = rank_matches(client, opposite_pool(db, client), limit=50) if client else []
    candidates = [r.candidate for r in ranked[:8]]
    referenced = _resolve_candidate(candidates, payload.message)

    result = llm.chat(db, payload.message, client, notes, history, candidates)
    intent: ChatIntent = result["intent"]
    ai_error = result.get("error")
    ai_ok = ai_used and not ai_error  # configured AND the call actually succeeded

    # A question about a listed candidate is an "ask", even if the fallback guessed search.
    if referenced is not None and intent == ChatIntent.search and not ai_ok:
        intent = ChatIntent.ask

    if intent == ChatIntent.search:
        if client is None:
            return ChatResponse(reply="Open a client first, then ask me to find matches.", intent=intent, ai_used=ai_used, ai_error=ai_error)
        if not is_matchable(client):
            return ChatResponse(
                reply=f"{client.first_name} isn't in active matchmaking yet. Verify the profile first, and make sure it isn't on hold or closed.",
                intent=intent, ai_used=ai_used, ai_error=ai_error,
            )
        filters = result.get("filters") or {}
        filtered = _apply_filters(ranked, filters)[:5]
        reply = result["reply"] if (ai_ok and result.get("reply")) else _search_reply(client, filters, len(filtered))
        return ChatResponse(reply=reply, intent=intent, matches=[result_to_match_out(r) for r in filtered], ai_used=ai_used, ai_error=ai_error)

    if intent == ChatIntent.ask:
        return ChatResponse(reply=_answer_ask(client, notes, referenced, result, ai_ok), intent=intent, ai_used=ai_used, ai_error=ai_error)

    if intent == ChatIntent.draft:
        return ChatResponse(reply=_draft_intro(db, client), intent=intent, ai_used=ai_used, ai_error=ai_error)

    return ChatResponse(
        reply=result.get("reply") or "I can find matches, summarise a client, or draft an intro.",
        intent=intent,
        ai_used=ai_used,
        ai_error=ai_error,
    )


def _search_reply(client: Profile, filters: dict, count: int) -> str:
    """Deterministic, query-aware reply for the no-AI keyword fallback."""
    parts = []
    if filters.get("city"):
        parts.append(f"in {filters['city']}")
    if filters.get("max_age"):
        parts.append(f"up to {filters['max_age']}")
    if filters.get("min_age"):
        parts.append(f"from {filters['min_age']}")
    if filters.get("want_kids"):
        parts.append("who want kids" if filters["want_kids"] == "yes" else "not wanting kids")
    if filters.get("open_to_relocate") == "yes":
        parts.append("open to relocating")
    if filters.get("min_income"):
        parts.append(f"earning ≥ ₹{filters['min_income']} LPA")
    criteria = (" " + ", ".join(parts)) if parts else ""
    if count == 0:
        return f"No candidates matched{criteria}. Try relaxing the criteria."
    noun = "match" if count == 1 else "matches"
    return f"Found {count} {noun} for {client.first_name}{criteria}, ranked by compatibility."


def _apply_filters(results, filters: dict):
    out = []
    for r in results:
        c = r.candidate
        if filters.get("city") and filters["city"].lower() not in c.city.lower():
            continue
        age = compute_age(c.dob)
        if filters.get("min_age") and age < filters["min_age"]:
            continue
        if filters.get("max_age") and age > filters["max_age"]:
            continue
        if filters.get("want_kids") and c.want_kids.value != filters["want_kids"]:
            continue
        if filters.get("open_to_relocate") and c.open_to_relocate.value != filters["open_to_relocate"]:
            continue
        if filters.get("min_income") and c.income_lpa < filters["min_income"]:
            continue
        out.append(r)
    return out


def _resolve_candidate(candidates: list[Profile], message: str) -> Profile | None:
    """Resolve a candidate the user named — but only among the suggested candidates,
    tolerating small typos (e.g. 'Hrash' -> 'Harsh'). Avoids picking unrelated pool
    profiles that merely share a first name."""
    if not candidates:
        return None
    by_first = {c.first_name.lower(): c for c in candidates}
    words = [w.lower() for w in re.findall(r"[A-Za-z]{3,}", message)]
    for w in words:
        if w in by_first:
            return by_first[w]
    for w in words:
        close = difflib.get_close_matches(w, by_first.keys(), n=1, cutoff=0.85)
        if close:
            return by_first[close[0]]
    return None


def _candidate_summary(p: Profile) -> str:
    return (
        f"{p.first_name} {p.last_name} ({compute_age(p.dob)}, {p.city}). "
        f"{p.designation} at {p.company}; {p.degree} from {p.ug_college}. "
        f"Religion {p.religion}, speaks {p.mother_tongue}. Diet {p.diet.value}, "
        f"wants kids: {p.want_kids.value}, open to relocate: {p.open_to_relocate.value}. "
        f"Income ~₹{p.income_lpa} LPA, height {p.height_cm} cm."
    )


def _answer_ask(client: Profile | None, notes, candidate: Profile | None, result: dict, ai_ok: bool) -> str:
    if ai_ok and result.get("reply"):
        return result["reply"]
    if candidate is not None:
        return _candidate_summary(candidate)
    if client is None:
        return "Tell me which client you mean. Open their profile and ask again."
    recent = sorted(notes, key=lambda n: n.created_at, reverse=True) if notes else []
    note_text = "; ".join(n.body for n in recent[:3]) if recent else "no notes recorded yet"
    stage = client.journey_stage.value if client.journey_stage else "n/a"
    return f"{client.first_name} {client.last_name} is at stage '{stage}'. Recent notes: {note_text}."


def _draft_intro(db: Session, client: Profile | None) -> str:
    if client is None:
        return "Open a client and I'll draft an intro for their top match."
    top = db.scalar(
        select(Match).where(Match.customer_id == client.id).order_by(Match.score.desc())
    )
    if top is None:
        rows = compute_matches(db, client, limit=1, explain=False, refresh=False)
        top = rows[0] if rows else None
    if top is None:
        return "There aren't any suitable matches to introduce yet."
    candidate = db.get(Profile, top.candidate_id)
    return llm.intro_email(db, client, candidate)
