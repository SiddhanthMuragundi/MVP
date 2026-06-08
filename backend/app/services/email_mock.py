"""Builds the 'Send Match' introduction email. No real email is dispatched."""
from __future__ import annotations

from ..schemas.match import CandidateSummary, EmailDraft
from ..utils import compute_age


def build_match_email(client, candidate, intro_text: str) -> EmailDraft:
    summary = CandidateSummary(
        name=f"{candidate.first_name} {candidate.last_name}",
        age=compute_age(candidate.dob),
        city=candidate.city,
        designation=candidate.designation,
        company=candidate.company,
        marital_status=candidate.marital_status.value,
        photo_url=candidate.photo_url,
    )
    body = (
        f"{intro_text}\n\n"
        "Here are a few details about your suggested match:\n"
        f"- Name: {summary.name}\n"
        f"- Age: {summary.age}\n"
        f"- City: {summary.city}\n"
        f"- Work: {summary.designation} at {summary.company}\n"
        f"- Education: {candidate.degree}, {candidate.ug_college}\n"
        f"- Marital status: {summary.marital_status.replace('_', ' ')}\n\n"
        "Let us know if you'd like an introduction.\n"
        "Warm regards,\nThe Saathiya Team"
    )
    return EmailDraft(
        to=client.email,
        subject=f"A match we think you'll like, {client.first_name}!",
        body=body,
        candidate_summary=summary,
    )
