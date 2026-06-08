"""Unit tests for the matching engine — pure functions, no DB required."""
from __future__ import annotations

from datetime import date, timedelta
from types import SimpleNamespace

from app.enums import Diet, FamilyType, Frequency, Gender, MaritalStatus, MatchTier, TriState
from app.services.matching import passes_hard_gates, rank_matches, score_candidate, tier_for


def _dob(age: int) -> date:
    return date.today() - timedelta(days=age * 365 + 10)


def make(gender: Gender, **overrides) -> SimpleNamespace:
    base = dict(
        id=overrides.pop("id", 1),
        gender=gender,
        dob=_dob(30),
        city="Pune",
        height_cm=180 if gender == Gender.male else 162,
        income_lpa=20.0,
        languages_known=["English", "Hindi"],
        mother_tongue="Hindi",
        hobbies=["Reading", "Music"],
        religion="Hindu",
        caste="Brahmin",
        want_kids=TriState.yes,
        open_to_relocate=TriState.yes,
        open_to_pets=TriState.maybe,
        diet=Diet.veg,
        smoking=Frequency.no,
        drinking=Frequency.no,
        family_type=FamilyType.nuclear,
        degree="B.Tech",
        marital_status=MaritalStatus.never_married,
    )
    base.update(overrides)
    return SimpleNamespace(**base)


def test_male_prefers_younger_shorter_earns_less_same_kids():
    client = make(Gender.male, dob=_dob(31), height_cm=182, income_lpa=30.0)
    good = make(Gender.female, id=2, dob=_dob(27), height_cm=160, income_lpa=18.0, want_kids=TriState.yes)
    weak = make(Gender.female, id=3, dob=_dob(34), height_cm=171, income_lpa=48.0, want_kids=TriState.no)

    ranked = rank_matches(client, [weak, good], limit=10)
    assert ranked[0].candidate.id == good.id
    assert score_candidate(client, good)[0] > score_candidate(client, weak)[0]


def test_female_rule_set_rewards_compatibility():
    client = make(Gender.female, dob=_dob(29), degree="B.Tech", open_to_relocate=TriState.no, city="Pune")
    compatible = make(
        Gender.male, id=2, dob=_dob(31), degree="B.Tech", city="Pune",
        diet=Diet.veg, family_type=FamilyType.nuclear, want_kids=TriState.yes, open_to_pets=TriState.maybe,
    )
    incompatible = make(
        Gender.male, id=3, dob=_dob(40), degree="B.Com", city="Delhi",
        diet=Diet.non_veg, family_type=FamilyType.joint, want_kids=TriState.no,
        open_to_relocate=TriState.no, smoking=Frequency.yes, drinking=Frequency.yes,
    )
    assert score_candidate(client, compatible)[0] > score_candidate(client, incompatible)[0]


def test_hard_age_window_excludes_far_candidates():
    client = make(Gender.male, dob=_dob(30))
    too_old = make(Gender.female, id=2, dob=_dob(46))
    assert passes_hard_gates(client, too_old) is False
    assert rank_matches(client, [too_old], limit=10) == []


def test_opposite_gender_required():
    client = make(Gender.male)
    same_gender = make(Gender.male, id=2)
    assert passes_hard_gates(client, same_gender) is False


def test_tier_thresholds():
    assert tier_for(80) == MatchTier.high
    assert tier_for(60) == MatchTier.promising
    assert tier_for(40) == MatchTier.possible


def test_reasons_present_and_capped():
    client = make(Gender.male, dob=_dob(31), height_cm=182, income_lpa=30.0, city="Pune")
    candidate = make(Gender.female, id=2, dob=_dob(27), height_cm=160, income_lpa=18.0, city="Pune", want_kids=TriState.yes)
    ranked = rank_matches(client, [candidate], limit=1)
    reasons = ranked[0].reasons
    assert 0 < len(reasons) <= 4
    assert "Both want kids" in reasons
