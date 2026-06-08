from __future__ import annotations

from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from ..core.security import get_current_user
from ..database import get_db
from ..enums import JourneyStage, MatchStatus
from ..models import Profile, User
from ..schemas.match import (
    DraftMatchRequest,
    DraftMatchResponse,
    SendMatchRequest,
    SendMatchResponse,
)
from ..services import llm, mailer
from ..services.activity import client_label, log
from ..services.email_mock import build_match_email
from ._helpers import get_or_create_match, load_client

router = APIRouter(prefix="/matches", tags=["matches"])


@router.post("/draft", response_model=DraftMatchResponse)
def draft_match(payload: DraftMatchRequest, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    """Generate an editable introduction email. Nothing is sent yet."""
    client = load_client(db, user, payload.customer_id)
    candidate = db.get(Profile, payload.candidate_id)
    intro = llm.intro_email(db, client, candidate)
    return DraftMatchResponse(email=build_match_email(client, candidate, intro))


@router.post("/send", response_model=SendMatchResponse)
def send_match(payload: SendMatchRequest, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    client = load_client(db, user, payload.customer_id)
    row = get_or_create_match(db, client, payload.candidate_id)
    candidate = db.get(Profile, payload.candidate_id)

    # Sending is a one-way commit: block an accidental duplicate unless explicitly resending.
    already_sent = row.sent_at is not None
    if already_sent and not payload.resend:
        raise HTTPException(
            status.HTTP_409_CONFLICT,
            "This match has already been sent to the client. Use resend if you mean to send it again.",
        )

    # Use the matchmaker's edited content if provided, otherwise draft fresh.
    if payload.body:
        email = build_match_email(client, candidate, "")
        email.body = payload.body
        if payload.subject:
            email.subject = payload.subject
    else:
        email = build_match_email(client, candidate, llm.intro_email(db, client, candidate))

    row.status = MatchStatus.sent
    row.sent_at = datetime.now(timezone.utc)
    # Sending the first match advances the client's journey to "Matches Sent".
    if client.journey_stage in (JourneyStage.new, JourneyStage.verified, JourneyStage.matching):
        client.journey_stage = JourneyStage.matches_sent
    log(db, user, "match_sent", f"{user.display_name} sent a match to {client_label(client)}", customer_id=client.id)
    db.commit()

    # Deliver the email through SMTP (Mailpit in the demo). Never block the request if
    # the mail server is unreachable.
    mailer.send_email(email.to, email.subject, email.body)

    return SendMatchResponse(email=email)
