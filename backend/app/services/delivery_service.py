"""
Notification delivery queue.

In-app notifications are always persisted; an email delivery row is queued for
each one and drained by the background worker (or on demand by admins).
"""

from __future__ import annotations

import logging
from datetime import datetime, timezone
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.notification import Notification, NotificationDelivery
from app.models.user import User
from app.services.email_service import send_email

logger = logging.getLogger(__name__)


async def queue_email_delivery(
    db: AsyncSession, notification: Notification
) -> NotificationDelivery:
    """Queue an email delivery for a persisted notification."""
    delivery = NotificationDelivery(
        notification_id=notification.id,
        provider="email",
        status="queued",
    )
    db.add(delivery)
    await db.flush()
    return delivery


async def dispatch_pending_deliveries(
    db: AsyncSession, limit: int = 50
) -> dict[str, int]:
    """
    Attempt every queued delivery once.

    Returns counts per outcome. Callers own the transaction boundary.
    """
    result = await db.execute(
        select(NotificationDelivery, Notification, User.email)
        .join(Notification, Notification.id == NotificationDelivery.notification_id)
        .join(User, User.id == Notification.user_id)
        .where(NotificationDelivery.status == "queued")
        .order_by(NotificationDelivery.id)
        .limit(limit)
    )

    counts = {"sent": 0, "skipped": 0, "failed": 0}

    for delivery, notification, email in result.all():
        delivery.attempts += 1
        try:
            outcome = await send_email(email, notification.title, notification.body)
        except Exception as exc:  # noqa: BLE001 - a failed send must not stop the batch
            delivery.status = "failed"
            delivery.last_error = str(exc)[:500]
            counts["failed"] += 1
            logger.warning(
                "Email delivery failed for notification %s: %s",
                notification.id,
                exc,
            )
            continue

        if outcome == "sent":
            delivery.status = "sent"
            delivery.delivered_at = datetime.now(timezone.utc)
            counts["sent"] += 1
        else:
            delivery.status = "skipped"
            counts["skipped"] += 1

    await db.flush()
    return counts


async def delivery_stats(
    db: AsyncSession, notification_ids: list[UUID] | None = None
) -> dict[str, int]:
    """Return queued/sent/failed/skipped counts for diagnostics."""
    from sqlalchemy import func

    stmt = select(NotificationDelivery.status, func.count()).group_by(
        NotificationDelivery.status
    )
    if notification_ids:
        stmt = stmt.where(NotificationDelivery.notification_id.in_(notification_ids))
    rows = (await db.execute(stmt)).all()
    return {status: count for status, count in rows}
