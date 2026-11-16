"""
Candidate embedding synchronization.

Keeps the persisted skill/project vectors in sync with the user's confirmed
profile content so the matching engine always scores fresh evidence.
"""

from __future__ import annotations

import logging
from collections.abc import Iterable
from uuid import UUID

from sqlalchemy import or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.ai.embeddings.generator import embed_skills, embed_text, get_model_version
from app.ai.embeddings.store import upsert_candidate_embedding
from app.models.resume import CandidateEmbedding
from app.models.user import User, UserProject, UserSkill

logger = logging.getLogger(__name__)


def build_project_text(projects: Iterable[UserProject]) -> str:
    """Flatten project evidence into one embedding input document."""
    return " ".join(
        f"{p.name}. {p.description or ''} {' '.join(p.technologies or [])}"
        for p in projects
    )


async def refresh_candidate_embeddings(
    db: AsyncSession, user_id: UUID
) -> None:
    """Recompute and upsert a candidate's skill and project vectors."""
    skill_names = (
        await db.execute(
            select(UserSkill.skill_name).where(UserSkill.user_id == user_id)
        )
    ).scalars().all()
    projects = (
        await db.execute(
            select(UserProject).where(UserProject.user_id == user_id)
        )
    ).scalars().all()

    await upsert_candidate_embedding(
        db,
        user_id=user_id,
        skill_embedding=embed_skills(list(skill_names)),
        project_embedding=embed_text(build_project_text(projects)),
        model_version=get_model_version(),
    )


async def backfill_missing_embeddings(
    db: AsyncSession, limit: int = 25
) -> int:
    """Recompute embeddings for candidates that have profile data but no vectors."""
    has_skills = select(UserSkill.id).where(UserSkill.user_id == User.id).exists()
    has_projects = select(UserProject.id).where(UserProject.user_id == User.id).exists()
    has_embedding = (
        select(CandidateEmbedding.id)
        .where(CandidateEmbedding.user_id == User.id)
        .exists()
    )

    user_ids = (
        await db.execute(
            select(User.id)
            .where(or_(has_skills, has_projects), ~has_embedding)
            .limit(limit)
        )
    ).scalars().all()

    for user_id in user_ids:
        await refresh_candidate_embeddings(db, user_id)

    await db.commit()
    logger.info("Backfilled embeddings for %d candidates", len(user_ids))
    return len(user_ids)
