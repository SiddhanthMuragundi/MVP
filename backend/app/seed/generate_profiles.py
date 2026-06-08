"""Deterministic generator for dummy client and pool profiles."""
from __future__ import annotations

import random
from datetime import date, datetime, timedelta, timezone

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
from ..models import Profile
from . import data_pools as pool

_email_seq = 0

# Metros that draw migrants from across India; used to model people living away from home.
_METRO_CITIES = ["Delhi", "Mumbai", "Bengaluru", "Pune", "Hyderabad", "Gurugram", "Noida"]

# DiceBear avataaars hair sets, so avatars read clearly as male or female.
_MALE_TOPS = "shortFlat,shortCurly,shortRound,shortWaved,theCaesar,theCaesarAndSidePart,sides,shavedSides,dreads01,frizzle"
_FEMALE_TOPS = "bigHair,bob,bun,curly,curvy,frida,fro,longButNotTooLong,miaWallace,straight01,straight02,straightAndStrand,shaggyMullet"
_MALE_FACIAL = "beardLight,beardMajestic,beardMedium,moustacheFancy,moustacheMagnum"
# Every face smiles (a matrimonial profile, not a random social-media snapshot).
_SMILE = "&mouth=smile,twinkle&eyes=happy,default,wink&eyebrows=default,raisedExcited"


def _avatar_url(rng: random.Random, first: str, gender: Gender) -> str:
    seed = f"{first}{rng.randint(1, 99999)}"
    base = f"https://api.dicebear.com/9.x/avataaars/svg?seed={seed}"
    if gender == Gender.male:
        return f"{base}&top={_MALE_TOPS}&facialHair={_MALE_FACIAL}&facialHairProbability=45{_SMILE}"
    return f"{base}&top={_FEMALE_TOPS}&facialHairProbability=0{_SMILE}"


def _email_for(first: str, last: str) -> str:
    global _email_seq
    _email_seq += 1
    base = f"{first}.{last}" if last else first
    return f"{base}{_email_seq}@example.com".lower()

_CLIENT_STAGES = [
    JourneyStage.new,
    JourneyStage.verified,
    JourneyStage.matching,
    JourneyStage.matches_sent,
    JourneyStage.in_conversation,
    JourneyStage.meeting,
    JourneyStage.on_hold,
]


def _weighted(rng: random.Random, choices: list, weights: list):
    return rng.choices(choices, weights=weights, k=1)[0]


def _dob_for_age(rng: random.Random, age: int) -> date:
    return date.today() - timedelta(days=age * 365 + rng.randint(0, 364))


def _pick_community(rng: random.Random) -> dict:
    weights = [c["weight"] for c in pool.COMMUNITIES]
    return rng.choices(pool.COMMUNITIES, weights=weights, k=1)[0]


def _make_profile(rng: random.Random, gender: Gender, *, matchmaker_id: int | None = None, stage: JourneyStage | None = None) -> Profile:
    # Draw a community first so name, religion, region and language stay coherent.
    comm = _pick_community(rng)
    first = rng.choice(comm["male"] if gender == Gender.male else comm["female"])
    last = rng.choice(comm["last"])
    # Many Tamil/Malayali names go by given name + father's initial, so drop the
    # surname for a share of those profiles.
    if comm.get("optional_surname") and rng.random() < 0.4:
        last = ""
    religion = comm["religion"]
    mother_tongue = rng.choice(comm["tongues"])
    # ~30% have migrated to a metro for work: city decouples from the home region, but
    # mother tongue (and religion/caste) keep their home-state identity intact.
    if rng.random() < 0.3:
        city = rng.choice(_METRO_CITIES)
    else:
        city = rng.choice(comm["cities"])
    caste = rng.choice(comm["castes"]) if comm["castes"] else ""

    # Draw a coherent career so degree, college, employer and role line up.
    career = rng.choice(pool.CAREERS)
    degree = rng.choice(career["degrees"])
    ug_college = rng.choice(career["colleges"])
    company = rng.choice(career["companies"])
    designation = rng.choice(career["designations"])

    age = rng.randint(24, 38)
    height = rng.randint(165, 188) if gender == Gender.male else rng.randint(150, 175)
    income = round(max(4.0, ((age - 22) * 1.6 + rng.uniform(-3, 8)) * career["income_mult"]), 1)

    languages = list({mother_tongue, "English"})
    if "Hindi" not in languages and rng.random() < 0.5:
        languages.append("Hindi")
    hobbies = rng.sample(pool.HOBBIES, rng.randint(2, 4))

    return Profile(
        first_name=first,
        last_name=last,
        gender=gender,
        dob=_dob_for_age(rng, age),
        country="India",
        city=city,
        height_cm=height,
        email=_email_for(first, last),
        phone=f"+91-{rng.randint(7000000000, 9999999999)}",
        ug_college=ug_college,
        degree=degree,
        income_lpa=income,
        company=company,
        designation=designation,
        marital_status=_weighted(rng, list(MaritalStatus), [0.82, 0.1, 0.04, 0.04]),
        languages_known=languages,
        siblings=rng.randint(0, 3),
        caste=caste,
        religion=religion,
        mother_tongue=mother_tongue,
        manglik=_weighted(rng, list(Manglik), [0.2, 0.5, 0.3]),
        want_kids=_weighted(rng, list(TriState), [0.6, 0.15, 0.25]),
        open_to_relocate=_weighted(rng, list(TriState), [0.45, 0.25, 0.3]),
        open_to_pets=_weighted(rng, list(TriState), [0.4, 0.25, 0.35]),
        diet=Diet.jain if religion == "Jain" else _weighted(rng, list(Diet), [0.45, 0.35, 0.1, 0.05, 0.05]),
        smoking=_weighted(rng, list(Frequency), [0.75, 0.18, 0.07]),
        drinking=_weighted(rng, list(Frequency), [0.55, 0.32, 0.13]),
        family_type=_weighted(rng, list(FamilyType), [0.6, 0.4]),
        hobbies=hobbies,
        bio=f"{designation} from {mother_tongue}-speaking family who enjoys {hobbies[0].lower()} and {hobbies[1].lower()}.",
        photo_url=_avatar_url(rng, first, gender),
        journey_stage=stage,
        assigned_matchmaker_id=matchmaker_id,
    )


def generate_all(
    matchmaker_ids: list[int],
    per_gender: int = 150,
    num_unassigned: int = 10,
    seed: int = 42,
) -> list[Profile]:
    """Return the studio's clients (everyone is a client). Deterministic for a given seed.

    Genders are interleaved so each matchmaker gets a mix, and each client also serves as a
    potential opposite-gender match for others. The first ``num_unassigned`` are left
    unassigned and "New" to represent a fresh intake queue for an admin to route.
    """
    global _email_seq
    _email_seq = 0
    rng = random.Random(seed)

    genders: list[Gender] = []
    for _ in range(per_gender):
        genders += [Gender.male, Gender.female]

    clients: list[Profile] = []
    for i, gender in enumerate(genders):
        if i < num_unassigned:
            # Fresh intake: unassigned, new, awaiting verification.
            owner, stage = None, JourneyStage.new
        else:
            stage = _CLIENT_STAGES[i % len(_CLIENT_STAGES)]
            owner = matchmaker_ids[i % len(matchmaker_ids)]
        clients.append(_make_profile(rng, gender, matchmaker_id=owner, stage=stage))

    return clients
