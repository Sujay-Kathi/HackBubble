"""
Admin API endpoints.

GET  /admin/scraper/runs      — list recent scraper run summaries
GET  /admin/hackathons        — list all hackathons with moderation status
POST /admin/hackathons/{id}/moderate — approve or reject a hackathon listing
"""

from __future__ import annotations

import logging
from datetime import datetime
from typing import Any
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user, get_db
from app.core.exceptions import ForbiddenError
from app.models.hackathon import Hackathon, HackathonSource, HackathonSourceRecord
from app.models.user import User

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/admin", tags=["admin"])


def _require_admin(current_user: User = Depends(get_current_user)) -> User:
    """Reject non-administrators from moderation endpoints."""
    if not current_user.is_admin:
        raise ForbiddenError(message="Administrator privileges required")
    return current_user


class ScraperRunSummary(BaseModel):
    source_name: str
    total_records: int
    earliest_scraped: datetime | None
    latest_scraped: datetime | None


class HackathonModerationOut(BaseModel):
    id: UUID
    title: str
    source_name: str
    is_verified: bool
    created_at: datetime

    model_config = {"from_attributes": True}


class ModerationAction(BaseModel):
    action: str  # "approve" or "reject"
    reason: str | None = None


@router.get("/scraper/runs", response_model=list[ScraperRunSummary])
async def list_scraper_runs(
    db: AsyncSession = Depends(get_db),
    _admin: User = Depends(_require_admin),
):
    """
    Returns a summary of ingested records per source (proxy for scraper runs).
    """
    result = await db.execute(
        select(
            HackathonSource.name.label("source_name"),
            func.count(HackathonSourceRecord.id).label("total_records"),
            func.min(HackathonSourceRecord.last_scraped_at).label("earliest_scraped"),
            func.max(HackathonSourceRecord.last_scraped_at).label("latest_scraped"),
        )
        .join(HackathonSource, HackathonSource.id == HackathonSourceRecord.source_id)
        .group_by(HackathonSource.name)
    )
    rows = result.all()
    return [
        ScraperRunSummary(
            source_name=row.source_name,
            total_records=row.total_records,
            earliest_scraped=row.earliest_scraped,
            latest_scraped=row.latest_scraped,
        )
        for row in rows
    ]


@router.get("/hackathons", response_model=list[HackathonModerationOut])
async def list_hackathons_for_moderation(
    unverified_only: bool = Query(False),
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    db: AsyncSession = Depends(get_db),
    _admin: User = Depends(_require_admin),
):
    """List hackathons for admin moderation."""
    query = select(Hackathon)
    if unverified_only:
        query = query.where(Hackathon.is_verified == False)  # noqa: E712
    query = query.order_by(Hackathon.created_at.desc()).offset(offset).limit(limit)
    result = await db.execute(query)
    hackathons = result.scalars().all()
    return [
        HackathonModerationOut(
            id=h.id,
            title=h.title,
            source_name=h.source_name,
            is_verified=h.is_verified,
            created_at=h.created_at,
        )
        for h in hackathons
    ]


@router.post("/hackathons/{hackathon_id}/moderate", response_model=dict)
async def moderate_hackathon(
    hackathon_id: UUID,
    action: ModerationAction,
    db: AsyncSession = Depends(get_db),
    _admin: User = Depends(_require_admin),
):
    """Approve or reject a hackathon listing."""
    if action.action not in ("approve", "reject"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="action must be 'approve' or 'reject'",
        )

    result = await db.execute(select(Hackathon).where(Hackathon.id == hackathon_id))
    hackathon = result.scalar_one_or_none()
    if hackathon is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Hackathon not found")

    if action.action == "approve":
        hackathon.is_verified = True
        hackathon.data_quality_status = "verified"
        msg = f"Hackathon '{hackathon.title}' approved."
    else:
        hackathon.is_verified = False
        hackathon.data_quality_status = "rejected"
        msg = f"Hackathon '{hackathon.title}' rejected."

    await db.commit()
    logger.info("Admin moderation: %s hackathon_id=%s", action.action, hackathon_id)
    return {"success": True, "message": msg}
