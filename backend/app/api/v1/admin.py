"""
Admin API endpoints.

GET  /admin/scraper/runs       — list recent scraper runs
GET  /admin/scraper/adapters   — list registered scraper adapter keys
POST /admin/scraper/trigger    — run a scraper adapter on demand
GET  /admin/hackathons         — list hackathons with moderation status
POST /admin/hackathons/{id}/moderate — approve or reject a hackathon listing
GET  /admin/audit-logs         — inspect privileged action history
"""

from __future__ import annotations

import logging
from datetime import datetime
from typing import Any
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_db, require_admin
from app.models.hackathon import Hackathon, HackathonSource, ScrapeRun
from app.models.user import User
from app.schemas.hackathon import IngestionReport
from app.services import audit_service
from app.services import delivery_service
from app.services.hackathon_service import HackathonService
from scraper.registry import (
    UnknownAdapterError,
    available_adapters,
    get_scraper,
)

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/admin", tags=["admin"])


class ScraperRunSummary(BaseModel):
    id: UUID
    source_name: str
    adapter_key: str
    status: str
    started_at: datetime
    finished_at: datetime | None = None
    events_found: int
    events_created: int
    events_updated: int
    error_summary: str | None = None


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


class AuditLogOut(BaseModel):
    id: UUID
    actor_id: UUID | None = None
    action: str
    entity_type: str
    entity_id: UUID | None = None
    metadata_json: dict[str, Any]
    ip_address: str | None = None
    created_at: datetime

    model_config = {"from_attributes": True}


@router.get("/scraper/runs", response_model=list[ScraperRunSummary])
async def list_scraper_runs(
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    db: AsyncSession = Depends(get_db),
    _admin: User = Depends(require_admin),
):
    """List recorded scraper runs, newest first."""
    result = await db.execute(
        select(ScrapeRun, HackathonSource.name, HackathonSource.adapter_key)
        .join(HackathonSource, HackathonSource.id == ScrapeRun.source_id)
        .order_by(ScrapeRun.started_at.desc())
        .offset(offset)
        .limit(limit)
    )
    return [
        ScraperRunSummary(
            id=run.id,
            source_name=source_name,
            adapter_key=adapter_key,
            status=run.status,
            started_at=run.started_at,
            finished_at=run.finished_at,
            events_found=run.events_found,
            events_created=run.events_created,
            events_updated=run.events_updated,
            error_summary=run.error_summary,
        )
        for run, source_name, adapter_key in result.all()
    ]


@router.get("/scraper/adapters", response_model=list[str])
async def list_scraper_adapters(_admin: User = Depends(require_admin)):
    """List adapter keys accepted by the manual trigger endpoint."""
    return available_adapters()


@router.post("/scraper/trigger", response_model=IngestionReport)
async def trigger_scraper(
    adapter_key: str = Query(default="mock_adapter"),
    db: AsyncSession = Depends(get_db),
    admin: User = Depends(require_admin),
):
    """Run a registered scraper adapter and ingest its events."""
    try:
        scraper = get_scraper(adapter_key)
    except UnknownAdapterError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=(
                f"Unknown adapter '{adapter_key}'. "
                f"Available: {', '.join(available_adapters())}"
            ),
        )

    report = await HackathonService.run_scraper_and_ingest(db, scraper)
    await audit_service.log_action(
        db,
        actor_id=admin.id,
        action="scraper.run",
        entity_type="scraper_adapter",
        metadata={
            "adapter_key": adapter_key,
            "status": report.status,
            "events_found": report.events_found,
            "events_created": report.events_created,
            "events_updated": report.events_updated,
        },
    )
    await db.commit()
    return report


@router.get("/hackathons", response_model=list[HackathonModerationOut])
async def list_hackathons_for_moderation(
    unverified_only: bool = Query(False),
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    db: AsyncSession = Depends(get_db),
    _admin: User = Depends(require_admin),
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
    admin: User = Depends(require_admin),
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

    await audit_service.log_action(
        db,
        actor_id=admin.id,
        action=f"hackathon.{action.action}",
        entity_type="hackathon",
        entity_id=hackathon.id,
        metadata={"reason": action.reason} if action.reason else {},
    )
    await db.commit()
    logger.info("Admin moderation: %s hackathon_id=%s", action.action, hackathon_id)
    return {"success": True, "message": msg}


@router.get("/notifications/deliveries", response_model=dict[str, int])
async def notification_delivery_stats(
    db: AsyncSession = Depends(get_db),
    _admin: User = Depends(require_admin),
):
    """Delivery queue health by status (queued, sent, skipped, failed)."""
    return await delivery_service.delivery_stats(db)


@router.get("/audit-logs", response_model=list[AuditLogOut])
async def list_audit_logs(
    action: str | None = Query(None),
    entity_type: str | None = Query(None),
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    db: AsyncSession = Depends(get_db),
    _admin: User = Depends(require_admin),
):
    """Inspect privileged action history."""
    entries = await audit_service.list_audit_logs(
        db,
        action=action,
        entity_type=entity_type,
        limit=limit,
        offset=offset,
    )
    return [AuditLogOut.model_validate(entry) for entry in entries]
