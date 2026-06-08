"""Sends outgoing emails over SMTP. In the demo this targets Mailpit, whose inbox is
viewable in a browser. Failures never propagate to the request."""
from __future__ import annotations

import smtplib
from email.message import EmailMessage

from ..config import settings


def send_email(to: str, subject: str, body: str) -> bool:
    msg = EmailMessage()
    msg["From"] = settings.MAIL_FROM
    msg["To"] = to
    msg["Subject"] = subject
    msg.set_content(body)
    try:
        with smtplib.SMTP(settings.SMTP_HOST, settings.SMTP_PORT, timeout=5) as smtp:
            smtp.send_message(msg)
        return True
    except Exception:
        # Demo SMTP (Mailpit) may be down; don't fail the match send.
        return False
