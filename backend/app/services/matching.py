"""Gender-specific, weighted matching engine.

Pure and deterministic — no database or LLM calls. Each scorer returns a value in
[0, 1]; the final score is the weighted average scaled to 0-100. Human-readable
reasons are derived from the strongest scorers so the matchmaker (and the UI) can see
why a candidate ranked where it did.
"""
from __future__ import annotations

from dataclasses import dataclass

from ..enums import Frequency, Gender, MaritalStatus, MatchTier, TriState, opposite_gender
from ..utils import compute_age
from . import matching_config as cfg


@dataclass
class MatchResult:
    candidate: object
    score: float
    tier: MatchTier
    reasons: list[str]


# --- low-level helpers ------------------------------------------------------

def _clamp(value: float) -> float:
    return max(0.0, min(1.0, value))


def _diet_score(a, b) -> float:
    if a.diet == b.diet:
        return 1.0
    for group in cfg._DIET_GROUPS:
        if a.diet.value in group and b.diet.value in group:
            return 0.7
    return 0.3


def _freq_score(a: Frequency, b: Frequency) -> float:
    if a == b:
        return 1.0
    extremes = {a, b}
    if extremes == {Frequency.no, Frequency.yes}:
        return 0.2
    return 0.6  # one step apart (no/occasionally or occasionally/yes)


def _habit_axis(a: Frequency, b: Frequency) -> float:
    # Smoking/drinking matters most as a dealbreaker: most people tolerate a similar
    # level, but a non-user paired with a regular user is the mismatch people actually
    # care about, so penalise that hardest. Similar levels score high either way.
    if a == b:
        return 1.0
    if {a, b} == {Frequency.no, Frequency.yes}:
        return 0.1  # abstainer vs regular user
    return 0.55  # one step apart (occasional on one side)


def _habits_match(client, cand) -> float:
    return (_habit_axis(client.smoking, cand.smoking) + _habit_axis(client.drinking, cand.drinking)) / 2.0


def _tristate_alignment(a: TriState, b: TriState) -> float:
    if a == b:
        return 1.0
    if TriState.maybe in (a, b):
        return 0.6
    return 0.1  # yes vs no


# --- shared scorers ---------------------------------------------------------

def _city_relocation(client, cand) -> float:
    if client.city == cand.city:
        return 1.0
    if TriState.yes in (client.open_to_relocate, cand.open_to_relocate):
        return 0.6
    if TriState.maybe in (client.open_to_relocate, cand.open_to_relocate):
        return 0.4
    return 0.15


def _mother_tongue_match(client, cand) -> float:
    # Same native language = same home-state / linguistic community: a strong cultural
    # affinity in Indian matchmaking, and exactly what someone who has migrated to a
    # metro looks for. English is near-universal, so it is not kinship on its own.
    if client.mother_tongue and client.mother_tongue == cand.mother_tongue:
        return 1.0
    shared = (set(client.languages_known or []) & set(cand.languages_known or [])) - {"English"}
    return 0.4 if shared else 0.05


def _religion_match(client, cand) -> float:
    # In Indian matchmaking, same religion is the dominant expectation. Different
    # religion is heavily penalised (not excluded — inter-faith does happen, rarely).
    return 1.0 if client.religion == cand.religion else 0.05


def _caste_match(client, cand) -> float:
    if client.religion != cand.religion:
        return 0.0  # caste is moot across religions; the religion penalty already applies
    if not client.caste or not cand.caste:
        return 0.7  # caste not applicable for this community (e.g. Muslim/Christian) — neutral
    return 1.0 if client.caste == cand.caste else 0.25


def _marital_match(client, cand) -> float:
    # Never-married usually prefers never-married (soft, not a hard rule). Someone
    # previously married tends to be more open to either.
    if client.marital_status == cand.marital_status:
        return 1.0
    nm = MaritalStatus.never_married
    if client.marital_status == nm:
        return 0.35  # never-married client, previously-married candidate
    if cand.marital_status == nm:
        return 0.6  # previously-married client, never-married candidate
    return 0.85  # both previously married (e.g. divorced vs widowed)


def _hobbies_overlap(client, cand) -> float:
    client_hobbies = set(client.hobbies or [])
    if not client_hobbies:
        return 0.3
    shared = client_hobbies & set(cand.hobbies or [])
    if not shared:
        return 0.3
    return _clamp(len(shared) / len(client_hobbies))


def _lifestyle(client, cand) -> float:
    # Food/diet habits (smoking and drinking are scored separately via _habits_match).
    return _diet_score(client, cand)


def _family_type_match(client, cand) -> float:
    return 1.0 if client.family_type == cand.family_type else 0.4


# --- male-client scorers (matching women) -----------------------------------

def _age_younger(client, cand) -> float:
    gap = compute_age(client.dob) - compute_age(cand.dob)
    if 2 <= gap <= 6:
        return 1.0
    if 0 <= gap < 2 or 6 < gap <= 10:
        return 0.7
    if gap < 0:
        return 0.2
    return 0.4  # gap > 10


def _income_less_or_equal(client, cand) -> float:
    ratio = cand.income_lpa / max(1.0, client.income_lpa)
    if ratio <= 1.0:
        return 1.0
    if ratio <= 1.25:
        return 0.6
    return 0.25


def _height_shorter(client, cand) -> float:
    diff = client.height_cm - cand.height_cm
    if 5 <= diff <= 20:
        return 1.0
    if 0 <= diff < 5:
        return 0.7
    if diff > 20:
        return 0.8
    return 0.3  # taller than client


def _height_taller(client, cand) -> float:
    # Female client: candidate (man) ideally a bit taller.
    diff = cand.height_cm - client.height_cm
    if 5 <= diff <= 25:
        return 1.0
    if 0 <= diff < 5:
        return 0.7
    if diff > 25:
        return 0.8
    return 0.3  # shorter than client


# --- female-client scorers (matching men) -----------------------------------

def _values_lifestyle(client, cand) -> float:
    return (_lifestyle(client, cand) + _family_type_match(client, cand)) / 2.0


def _profession_education_parity(client, cand) -> float:
    client_tier = cfg.EDUCATION_TIER.get(client.degree, cfg.DEFAULT_EDUCATION_TIER)
    cand_tier = cfg.EDUCATION_TIER.get(cand.degree, cfg.DEFAULT_EDUCATION_TIER)
    diff = abs(client_tier - cand_tier)
    edu_score = {0: 1.0, 1: 0.7}.get(diff, 0.4)
    denom = max(client.income_lpa, cand.income_lpa, 1.0)
    income_parity = 1.0 - min(1.0, abs(client.income_lpa - cand.income_lpa) / denom)
    return (edu_score + income_parity) / 2.0


def _relocation_fit(client, cand) -> float:
    if client.open_to_relocate == TriState.no:
        if client.city == cand.city:
            return 1.0
        if cand.open_to_relocate == TriState.yes:
            return 0.7
        return 0.2
    return 1.0 if client.city == cand.city else 0.8


def _kids_pets_alignment(client, cand) -> float:
    kids = _tristate_alignment(client.want_kids, cand.want_kids)
    pets = _tristate_alignment(client.open_to_pets, cand.open_to_pets)
    return (kids + pets) / 2.0


def _age_respectful_window(client, cand) -> float:
    gap = abs(compute_age(cand.dob) - compute_age(client.dob))
    if gap <= 4:
        return 1.0
    if gap <= 8:
        return 0.7
    return 0.3


_MALE_SCORERS = {
    "religion_match": _religion_match,
    "caste_match": _caste_match,
    "mother_tongue_match": _mother_tongue_match,
    "income_less_or_equal": _income_less_or_equal,
    "city_relocation": _city_relocation,
    "want_kids_alignment": lambda c, x: _tristate_alignment(c.want_kids, x.want_kids),
    "marital_match": _marital_match,
    "habits_match": _habits_match,
    "age_younger": _age_younger,
    "lifestyle": _lifestyle,
    "height_shorter": _height_shorter,
    "hobbies_overlap": _hobbies_overlap,
}

_FEMALE_SCORERS = {
    "religion_match": _religion_match,
    "caste_match": _caste_match,
    "mother_tongue_match": _mother_tongue_match,
    "profession_education_parity": _profession_education_parity,
    "city_relocation": _city_relocation,
    "relocation_fit": _relocation_fit,
    "marital_match": _marital_match,
    "values_lifestyle": _values_lifestyle,
    "habits_match": _habits_match,
    "kids_pets_alignment": _kids_pets_alignment,
    "age_respectful_window": _age_respectful_window,
    "height_taller": _height_taller,
    "hobbies_overlap": _hobbies_overlap,
}


def _rule_set(client) -> tuple[dict, dict]:
    if client.gender == Gender.male:
        return _MALE_SCORERS, cfg.MALE_CLIENT_WEIGHTS
    return _FEMALE_SCORERS, cfg.FEMALE_CLIENT_WEIGHTS


# --- hard gates -------------------------------------------------------------

def passes_hard_gates(client, cand) -> bool:
    if cand.gender != opposite_gender(client.gender):
        return False
    if abs(compute_age(cand.dob) - compute_age(client.dob)) > cfg.HARD_AGE_WINDOW:
        return False
    allowed = cfg.MARITAL_STATUS_ALLOWED.get(client.marital_status.value)
    if allowed is not None and cand.marital_status.value not in allowed:
        return False
    return True


# --- scoring + reasons ------------------------------------------------------

def score_candidate(client, cand) -> tuple[float, dict[str, float], dict[str, float]]:
    scorers, weights = _rule_set(client)
    scores = {name: _clamp(fn(client, cand)) for name, fn in scorers.items()}
    total_weight = sum(weights.values())
    weighted = sum(scores[name] * weights[name] for name in scorers)
    final = round(100.0 * weighted / total_weight, 1) if total_weight else 0.0
    return final, scores, weights


def tier_for(score: float) -> MatchTier:
    if score >= cfg.TIER_THRESHOLDS["high"]:
        return MatchTier.high
    if score >= cfg.TIER_THRESHOLDS["promising"]:
        return MatchTier.promising
    return MatchTier.possible


def _reason_text(name: str, client, cand) -> str | None:
    if name == "want_kids_alignment":
        if client.want_kids == cand.want_kids:
            return {
                TriState.yes: "Both want kids",
                TriState.no: "Both prefer no kids",
                TriState.maybe: "Both open about kids",
            }[client.want_kids]
        return None
    if name == "kids_pets_alignment":
        return "Aligned on kids and pets"
    if name == "city_relocation":
        if client.city == cand.city:
            return f"Same city: {client.city}"
        if TriState.yes in (client.open_to_relocate, cand.open_to_relocate):
            return "Open to relocating"
        return None
    if name == "relocation_fit":
        return "Relocation preferences align"
    if name in ("age_younger", "age_respectful_window"):
        gap = abs(compute_age(cand.dob) - compute_age(client.dob))
        return f"{gap}-year age gap"
    if name == "marital_match":
        if client.marital_status == cand.marital_status:
            if client.marital_status == MaritalStatus.never_married:
                return "Both never married"
            return "Same marital status"
        return None
    if name == "income_less_or_equal":
        return "Comfortable income match"
    if name in ("height_shorter", "height_taller"):
        return "Comfortable height match"
    if name == "habits_match":
        return "Similar take on smoking and drinking"
    if name == "mother_tongue_match":
        if client.mother_tongue and client.mother_tongue == cand.mother_tongue:
            return f"Both speak {client.mother_tongue}"
        shared = (set(client.languages_known or []) & set(cand.languages_known or [])) - {"English"}
        return f"Shares {sorted(shared)[0]}" if shared else None
    if name == "religion_match":
        return f"Same religion: {client.religion}" if client.religion == cand.religion else None
    if name == "caste_match":
        if client.religion == cand.religion and client.caste and client.caste == cand.caste:
            return f"Same community: {client.caste}"
        return None
    if name == "hobbies_overlap":
        shared = set(client.hobbies or []) & set(cand.hobbies or [])
        return f"Common interest: {sorted(shared)[0]}" if shared else None
    if name == "lifestyle":
        return "Similar food and diet preference"
    if name == "values_lifestyle":
        return "Shared values (diet and family)"
    if name == "profession_education_parity":
        return "Similar education and profession"
    return None


def build_reasons(client, cand, scores: dict[str, float], weights: dict[str, float]) -> list[str]:
    contributions = []
    for name, score in scores.items():
        if score >= cfg.REASON_MIN_CONTRIBUTION:
            text = _reason_text(name, client, cand)
            if text:
                contributions.append((score * weights[name], text))
    contributions.sort(key=lambda item: item[0], reverse=True)

    seen, reasons = set(), []
    for _, text in contributions:
        if text not in seen:
            seen.add(text)
            reasons.append(text)
        if len(reasons) == 4:
            break
    return reasons


def rank_matches(client, pool, limit: int = cfg.DEFAULT_MATCH_LIMIT) -> list[MatchResult]:
    results: list[MatchResult] = []
    for cand in pool:
        if not passes_hard_gates(client, cand):
            continue
        score, scores, weights = score_candidate(client, cand)
        results.append(
            MatchResult(
                candidate=cand,
                score=score,
                tier=tier_for(score),
                reasons=build_reasons(client, cand, scores, weights),
            )
        )
    results.sort(key=lambda r: r.score, reverse=True)
    return results[:limit]
