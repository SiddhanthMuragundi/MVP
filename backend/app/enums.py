"""Domain enumerations shared by models, schemas, and the matching engine."""
from __future__ import annotations

import enum


class Gender(str, enum.Enum):
    male = "male"
    female = "female"


class Role(str, enum.Enum):
    admin = "admin"
    matchmaker = "matchmaker"


class JourneyStage(str, enum.Enum):
    new = "new"
    verified = "verified"
    matching = "matching"
    matches_sent = "matches_sent"
    in_conversation = "in_conversation"
    meeting = "meeting"
    on_hold = "on_hold"
    closed = "closed"


class MaritalStatus(str, enum.Enum):
    never_married = "never_married"
    divorced = "divorced"
    widowed = "widowed"
    separated = "separated"


class TriState(str, enum.Enum):
    yes = "yes"
    no = "no"
    maybe = "maybe"


class Manglik(str, enum.Enum):
    yes = "yes"
    no = "no"
    dont_know = "dont_know"


class Diet(str, enum.Enum):
    veg = "veg"
    non_veg = "non_veg"
    eggetarian = "eggetarian"
    vegan = "vegan"
    jain = "jain"


class Frequency(str, enum.Enum):
    no = "no"
    occasionally = "occasionally"
    yes = "yes"


class FamilyType(str, enum.Enum):
    nuclear = "nuclear"
    joint = "joint"


class MatchTier(str, enum.Enum):
    high = "high"
    promising = "promising"
    possible = "possible"


class MatchStatus(str, enum.Enum):
    suggested = "suggested"      # ranked by the engine, not acted on
    shortlisted = "shortlisted"  # matchmaker picked it (internal, reversible)
    sent = "sent"                # shared with the client (outward, one-way)
    accepted = "accepted"        # client interested
    declined = "declined"        # client not interested
    no_response = "no_response"  # sent, no reply
    withdrawn = "withdrawn"      # sent in error, retracted


class LLMProvider(str, enum.Enum):
    openai = "openai"
    anthropic = "anthropic"
    gemini = "gemini"


class ChatIntent(str, enum.Enum):
    search = "search"
    ask = "ask"
    draft = "draft"
    unknown = "unknown"


def opposite_gender(gender: Gender) -> Gender:
    return Gender.female if gender == Gender.male else Gender.male
