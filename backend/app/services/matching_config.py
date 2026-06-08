"""Tunable weights and thresholds for the matching engine.

Everything that shapes ranking lives here, so the algorithm can be re-tuned without
touching the scoring code.
"""
from __future__ import annotations

# Candidates outside this absolute age gap from the client are dropped before scoring.
HARD_AGE_WINDOW = 12

# Reserved hook: map of acceptable marital-status pairs. Empty means "allow all".
MARITAL_STATUS_ALLOWED: dict[str, set[str]] = {}

# Religion and caste dominate Indian matchmaking, so they carry the most weight. A
# different religion/caste is heavily penalised by the scorers, pushing such matches far
# down the ranking (not excluded — inter-faith/inter-caste does happen, just rarely).
#
# Priority order for Indian matchmaking:
#   1. Religion + caste  (dominant; food habits ride along via lifestyle, e.g. Jain=veg)
#   2. Mother tongue / home-state + economics/salary  (significant second tier)
#   3. Region (current city) + marital-status fit + age difference  (meaningful, soft)
#   4. Everything else (kids, lifestyle, profession, hobbies)
#
# Mother tongue is a proxy for the home state / linguistic community: people who have
# migrated to a metro still look for someone who speaks their language, so it carries
# more weight than the current city.
#
# Scorer weights for a male client (matching against women).
MALE_CLIENT_WEIGHTS = {
    "religion_match": 26,
    "caste_match": 15,
    "mother_tongue_match": 8,    # same native language ~ home state / community
    "income_less_or_equal": 9,   # economics / salary
    "city_relocation": 7,        # current city / relocation
    "want_kids_alignment": 9,
    "marital_match": 7,          # never-married tends to prefer never-married (soft)
    "habits_match": 6,           # smoking / drinking compatibility
    "age_younger": 6,            # age difference
    "lifestyle": 3,              # diet / food habits
    "height_shorter": 2,
    "hobbies_overlap": 2,
}

# Scorer weights for a female client (matching against men). Economics shows up via
# profession/education parity (which blends education tier and income parity).
FEMALE_CLIENT_WEIGHTS = {
    "religion_match": 26,
    "caste_match": 15,
    "mother_tongue_match": 7,           # same native language ~ home state / community
    "profession_education_parity": 10,  # economics / salary + education
    "city_relocation": 5,               # current city
    "relocation_fit": 5,                # relocation
    "marital_match": 7,                 # never-married tends to prefer never-married (soft)
    "habits_match": 6,                  # smoking / drinking compatibility
    "values_lifestyle": 6,              # diet (food habits) and family type
    "kids_pets_alignment": 6,
    "age_respectful_window": 3,         # age difference
    "height_taller": 2,
    "hobbies_overlap": 2,
}

TIER_THRESHOLDS = {"high": 75.0, "promising": 55.0}

# A scorer contributes a reason only if its 0..1 score is at least this high.
REASON_MIN_CONTRIBUTION = 0.6

DEFAULT_MATCH_LIMIT = 10

# Rough education tiers used by the profession/education parity scorer.
EDUCATION_TIER = {
    "PhD": 4, "MD": 4, "MBBS": 4,
    "MBA": 3, "MS": 3, "M.Tech": 3, "M.E.": 3, "CA": 3, "MCA": 3,
    "B.Tech": 2, "B.E.": 2, "BDS": 2, "B.Arch": 2,
    "B.Com": 1, "B.Sc": 1, "BA": 1, "BBA": 1,
}
DEFAULT_EDUCATION_TIER = 2

# Diet groups that are considered compatible even when not identical.
_DIET_GROUPS = [{"veg", "jain", "vegan"}, {"non_veg", "eggetarian"}]
