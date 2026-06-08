"""Provider-agnostic AI helper.

The active provider/key/model is resolved from the admin-managed settings row, with
an optional environment fallback. Every AI feature degrades gracefully: if nothing is
configured or a call fails, a deterministic template is returned so the app keeps
working without any API key.
"""
from __future__ import annotations

import json
import re

from sqlalchemy.orm import Session

from ..config import settings
from ..core.crypto import decrypt_key
from ..enums import ChatIntent, LLMProvider
from ..models import LLMSetting
from . import providers


class LLMUnavailable(Exception):
    """Raised when no provider is configured; callers fall back to templates."""


def get_active_llm(db: Session) -> tuple[LLMProvider, str, str] | None:
    row = db.get(LLMSetting, 1)
    if row and row.provider and row.api_key_encrypted and row.model:
        return row.provider, decrypt_key(row.api_key_encrypted), row.model
    if settings.LLM_PROVIDER and settings.LLM_API_KEY and settings.LLM_MODEL:
        return LLMProvider(settings.LLM_PROVIDER), settings.LLM_API_KEY, settings.LLM_MODEL
    return None


def generate(db: Session, prompt: str, system: str | None = None, max_tokens: int = 300, temperature: float = 0.6) -> str:
    active = get_active_llm(db)
    if active is None:
        raise LLMUnavailable()
    provider, key, model = active
    return providers.generate_text(provider, key, model, prompt, system, max_tokens, temperature)


def list_models(provider: LLMProvider, api_key: str) -> list[str]:
    return providers.list_models(provider, api_key)


_TIER_LABEL = {"high": "High Potential Match", "promising": "Promising Match", "possible": "Possible Match"}


def explain_match(db: Session, client, candidate, score: float, tier: str, reasons: list[str]) -> str:
    label = _TIER_LABEL.get(tier, "Match")
    fallback = f"{label}: " + (", ".join(reasons) if reasons else "broadly compatible profiles")
    system = (
        "You are a warm, concise Indian matchmaker assistant. In ONE sentence, explain why "
        "this is a good match, grounded only in the reasons provided. No greetings or preamble. "
        "Do not use em dashes; use commas or full stops."
    )
    prompt = (
        f"Client: {client.first_name}, {candidate_age(client)}, {client.city}.\n"
        f"Candidate: {candidate.first_name}, {candidate_age(candidate)}, {candidate.city}.\n"
        f"Tier: {label}. Score: {score}.\nReasons: {reasons}."
    )
    try:
        return generate(db, prompt, system, max_tokens=80)
    except Exception:
        return fallback


def intro_email(db: Session, client, candidate) -> str:
    fallback = (
        f"Hi {client.first_name}, we'd love to introduce you to {candidate.first_name}, "
        f"a {candidate_age(candidate)}-year-old {candidate.designation} based in {candidate.city}. "
        "We think you two could really hit it off and would be happy to set up an introduction."
    )
    system = (
        "You are a thoughtful Indian matchmaker writing to a client. Write 2-3 warm, tasteful "
        "sentences introducing the suggested match. No subject line, no sign-off. "
        "Do not use em dashes; use commas or full stops."
    )
    prompt = (
        f"Client first name: {client.first_name}.\n"
        f"Candidate: {candidate.first_name}, {candidate_age(candidate)}, {candidate.designation} "
        f"at {candidate.company}, lives in {candidate.city}, studied at {candidate.ug_college}."
    )
    try:
        return generate(db, prompt, system, max_tokens=160)
    except Exception:
        return fallback


def candidate_age(profile) -> int:
    from ..utils import compute_age

    return compute_age(profile.dob)


# --- Chat assistant ---------------------------------------------------------

_CHAT_RULES = (
    "You are the Match Assistant for a TDC matchmaker dashboard. Reply with STRICT JSON only "
    "(no markdown):\n"
    '{"intent": "search|ask|draft", "filters": {"city": str|null, "min_age": int|null, '
    '"max_age": int|null, "want_kids": "yes|no|maybe|null", "open_to_relocate": "yes|no|maybe|null", '
    '"min_income": number|null}, "reply": str}\n'
    "intent 'search' = find/list matches; 'ask' = answer about the client or a listed candidate; "
    "'draft' = write an introduction.\n"
    "GROUNDING RULES (critical):\n"
    "- Use ONLY the facts in CONTEXT below. NEVER invent people, names, numbers, or details.\n"
    "- You may only discuss candidates listed under SUGGESTED CANDIDATES. If the user asks about "
    "anyone not in that list, set reply to say that person is not among the current suggestions.\n"
    "- Resolve pronouns ('he', 'him', 'this one') using the conversation history.\n"
    "- Keep 'reply' factual and concise; put the full answer there.\n"
    "- Do not use em dashes anywhere; use commas, hyphens, or colons."
)


def _profile_brief(p) -> str:
    return (
        f"{p.first_name} {p.last_name} ({candidate_age(p)}, {p.city}); "
        f"{p.designation} at {p.company}; {p.degree} from {p.ug_college}; "
        f"religion {p.religion}, mother tongue {p.mother_tongue}; "
        f"diet {p.diet.value}, wants kids {p.want_kids.value}, open to relocate {p.open_to_relocate.value}; "
        f"income ~{p.income_lpa} LPA, height {p.height_cm}cm, {p.marital_status.value}; "
        f"hobbies {', '.join(p.hobbies or []) or 'n/a'}"
    )


def _build_system(client, notes, candidates) -> str:
    blocks = []
    if client is not None:
        stage = client.journey_stage.value if client.journey_stage else "n/a"
        blocks.append(
            f"ACTIVE CLIENT: {client.first_name} {client.last_name}, {candidate_age(client)}, "
            f"{client.city}, marital status {client.marital_status.value}, journey stage {stage}."
        )
        if notes:
            blocks.append("CLIENT NOTES: " + " | ".join(n.body for n in notes[:5]))
    if candidates:
        listed = "\n".join(f"- {_profile_brief(c)}" for c in candidates)
        blocks.append("SUGGESTED CANDIDATES (the only people you may discuss):\n" + listed)
    context = "\n\n".join(blocks) if blocks else "No client is currently open."
    return _CHAT_RULES + "\n\nCONTEXT:\n" + context


def chat(db: Session, message: str, client=None, notes=None, history=None, candidates=None) -> dict:
    system = _build_system(client, notes, candidates)
    transcript = ""
    if history:
        turns = "\n".join(f"{role}: {content}" for role, content in history[-8:])
        transcript = f"Conversation so far:\n{turns}\n\n"
    prompt = f"{transcript}User's new message: {message}"

    try:
        raw = generate(db, prompt, system, max_tokens=500, temperature=0.2)
        data = json.loads(_extract_json(raw))
        intent = ChatIntent(data.get("intent", "search"))
        return {"intent": intent, "reply": data.get("reply", ""), "filters": data.get("filters") or {}}
    except LLMUnavailable:
        return _keyword_fallback(message)
    except Exception as exc:
        result = _keyword_fallback(message)
        result["error"] = _short_error(exc)
        return result


def _short_error(exc: Exception) -> str:
    import httpx

    if isinstance(exc, httpx.HTTPStatusError):
        try:
            detail = exc.response.json().get("error", {}).get("message")
            if detail:
                return f"AI provider error: {detail}"
        except Exception:
            pass
        return f"AI provider returned {exc.response.status_code}."
    return f"AI call failed: {type(exc).__name__}."


def _extract_json(text: str) -> str:
    start, end = text.find("{"), text.rfind("}")
    return text[start : end + 1] if start != -1 and end != -1 else text


def _keyword_fallback(message: str) -> dict:
    lowered = message.lower()
    if any(w in lowered for w in ("draft", "intro", "email", "write")):
        return {"intent": ChatIntent.draft, "reply": "Drafting an introduction.", "filters": {}}
    if any(w in lowered for w in ("where", "journey", "status", "summary", "summarise", "summarize", "note")):
        return {"intent": ChatIntent.ask, "reply": "Here's what I found.", "filters": {}}

    filters: dict = {}
    age = re.search(r"(under|below|less than)\s+(\d{2})", lowered)
    if age:
        filters["max_age"] = int(age.group(2))
    if "kids" in lowered or "children" in lowered:
        filters["want_kids"] = "no" if ("no kids" in lowered or "without kids" in lowered) else "yes"
    if "relocat" in lowered:
        filters["open_to_relocate"] = "yes"
    return {"intent": ChatIntent.search, "reply": "Here are some matches.", "filters": filters}
