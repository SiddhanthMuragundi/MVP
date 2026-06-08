from __future__ import annotations

from typing import Literal

from pydantic import BaseModel

from ..enums import MatchStatus, MatchTier
from .profile import ProfileOut


class MatchOut(BaseModel):
    id: int | None = None
    candidate: ProfileOut
    score: float
    tier: MatchTier
    reasons: list[str]
    ai_explanation: str | None = None
    status: MatchStatus = MatchStatus.suggested


class DraftMatchRequest(BaseModel):
    customer_id: int
    candidate_id: int


class SendMatchRequest(BaseModel):
    customer_id: int
    candidate_id: int
    # The matchmaker may edit the drafted email before sending.
    subject: str | None = None
    body: str | None = None
    # Sending is a one-way commit; re-sending the same candidate needs an explicit flag.
    resend: bool = False


class OutcomeRequest(BaseModel):
    outcome: Literal["accepted", "declined", "no_response", "withdrawn"]


class CandidateSummary(BaseModel):
    name: str
    age: int
    city: str
    designation: str
    company: str
    marital_status: str
    photo_url: str


class EmailDraft(BaseModel):
    to: str
    subject: str
    body: str
    candidate_summary: CandidateSummary


class DraftMatchResponse(BaseModel):
    email: EmailDraft


class SendMatchResponse(BaseModel):
    ok: bool = True
    email: EmailDraft
