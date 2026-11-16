"""
Audit logging for privileged and state-changing operations.
"""

from __future__ import annotations

import logging
from typing import Any
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.notification import AuditLog

logger = logging.getLogger(__name__)


async def log_action(
    db: AsyncSession,
    *,
    actor_id: UUID | None,
    action: str,
    entity_type: str,
    entity_id: UUID | None = None,
    metadata: dict[str, Any] | None = None,
    ip_address: str | None = None,
) -> AuditLog:
    """Stage an audit record. The caller is responsible for committing."""
    entry = AuditLog(
        actor_id=actor_id,
        action=action,
        entity_type=entity_type,
        entity_id=entity_id,
        metadata_json=metadata or {},
        ip_address=ip_address,
    )
    db.add(entry)
    await db.flush()
    logger.info(
        "Audit action=%s entity=%s:%s actor=%s",
        action,
        entity_type,
        entity_id,
        actor_id,
    )
    return entry


async def list_audit_logs(
    db: AsyncSession,
    *,
    action: str | None = None,
    entity_type: str | None = None,
    limit: int = 50,
    offset: int = 0,
) -> list[AuditLog]:
    stmt = select(AuditLog)
    if action:
        stmt = stmt.where(AuditLog.action == action)
    if entity_type:
        stmt = stmt.where(AuditLog.entity_type == entity_type)
    stmt = stmt.order_by(AuditLog.created_at.desc()).offset(offset).limit(limit)
    return list((await db.execute(stmt)).scalars().all())
