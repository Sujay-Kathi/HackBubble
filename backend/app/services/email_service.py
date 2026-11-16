"""
Email delivery over SMTP.

When SMTP is not configured the send is reported as ``skipped`` instead of
failing, so background workers can drain queues in dev/test environments.
"""

from __future__ import annotations

import asyncio
import logging
import smtplib
from email.message import EmailMessage

from app.core.config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()


def smtp_configured() -> bool:
    return bool(settings.SMTP_HOST)


def _send_sync(to_email: str, subject: str, body: str) -> None:
    message = EmailMessage()
    message["Subject"] = subject
    message["From"] = settings.SMTP_FROM_EMAIL
    message["To"] = to_email
    message.set_content(body)

    with smtplib.SMTP(
        settings.SMTP_HOST,
        settings.SMTP_PORT,
        timeout=settings.SMTP_TIMEOUT_SECONDS,
    ) as server:
        if settings.SMTP_USE_TLS:
            server.starttls()
        if settings.SMTP_USERNAME:
            server.login(settings.SMTP_USERNAME, settings.SMTP_PASSWORD)
        server.send_message(message)


async def send_email(to_email: str, subject: str, body: str) -> str:
    """Send an email, returning ``sent`` or ``skipped``."""
    if not smtp_configured():
        logger.info("SMTP not configured; skipping email to %s", to_email)
        return "skipped"

    await asyncio.to_thread(_send_sync, to_email, subject, body)
    logger.info("Sent email to %s", to_email)
    return "sent"
