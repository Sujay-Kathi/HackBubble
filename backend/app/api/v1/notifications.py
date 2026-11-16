"""
Notification API endpoints.

GET   /notifications           — list current user's notifications (paginated)
PATCH /notifications/{id}/read — mark a notification as read
PATCH /notifications/read-all  — mark all as read
"""

from __future__ import annotations

import logging
from datetime import datetime, timezone
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user, get_db
from app.models.notification import Notification
from app.models.user import User

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/notifications", tags=["notifications"])


class NotificationOut(BaseModel):
    id: UUID
    type: str
    title: str
    body: str
    entity_type: str
    entity_id: UUID | None = None
    read_at: datetime | None = None
    created_at: datetime

    model_config = {"from_attributes": True}


class NotificationListResponse(BaseModel):
    items: list[NotificationOut]
    total: int
    unread_count: int


@router.get("", response_model=NotificationListResponse)
async def list_notifications(
    unread_only: bool = Query(False),
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """List the current user's notifications, newest first."""
    query = select(Notification).where(Notification.user_id == current_user.id)
    if unread_only:
        query = query.where(Notification.read_at.is_(None))
    query = query.order_by(Notification.created_at.desc())

    # Total and unread counts
    all_res = await db.execute(
        select(Notification).where(Notification.user_id == current_user.id)
    )
    all_notifs = all_res.scalars().all()
    total = len(all_notifs)
    unread_count = sum(1 for n in all_notifs if n.read_at is None)

    # Paginated fetch
    page_res = await db.execute(query.offset(offset).limit(limit))
    items = page_res.scalars().all()

    return NotificationListResponse(
        items=list(items),
        total=total,
        unread_count=unread_count,
    )


@router.patch("/{notification_id}/read", response_model=NotificationOut)
async def mark_notification_read(
    notification_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Mark a single notification as read."""
    result = await db.execute(
        select(Notification).where(
            Notification.id == notification_id,
            Notification.user_id == current_user.id,
        )
    )
    notif = result.scalar_one_or_none()
    if notif is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Notification not found")

    if notif.read_at is None:
        notif.read_at = datetime.now(timezone.utc)
        await db.commit()

    return notif


@router.patch("/read-all", response_model=dict)
async def mark_all_read(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Mark all unread notifications as read."""
    now = datetime.now(timezone.utc)
    await db.execute(
        update(Notification)
        .where(Notification.user_id == current_user.id, Notification.read_at.is_(None))
        .values(read_at=now)
    )
    await db.commit()
    return {"success": True, "message": "All notifications marked as read"}
