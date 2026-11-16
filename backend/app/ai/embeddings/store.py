"""
Embedding persistence layer.
Upserts and retrieves CandidateEmbedding and TeamIntelligence vectors.
"""

from __future__ import annotations

import logging
from uuid import UUID

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.resume import CandidateEmbedding
from app.models.team import TeamIntelligence

logger = logging.getLogger(__name__)


async def _upsert_embedding_row(
    db: AsyncSession,
    user_id: UUID,
    embedding_type: str,
    vector: list[float],
    model_version: str,
) -> CandidateEmbedding:
    result = await db.execute(
        select(CandidateEmbedding).where(
            CandidateEmbedding.user_id == user_id,
            CandidateEmbedding.embedding_type == embedding_type,
        )
    )
    row = result.scalar_one_or_none()

    if row is None:
        row = CandidateEmbedding(
            user_id=user_id,
            embedding_type=embedding_type,
            vector=vector,
            model_version=model_version,
        )
        db.add(row)
    else:
        row.vector = vector  # type: ignore[assignment]
        row.model_version = model_version  # type: ignore[assignment]
        row.source_revision += 1

    return row


async def upsert_candidate_embedding(
    db: AsyncSession,
    user_id: UUID,
    skill_embedding: list[float],
    project_embedding: list[float],
    model_version: str,
) -> list[CandidateEmbedding]:
    """
    Insert or update a candidate's skill and project embedding rows.
    """
    rows = [
        await _upsert_embedding_row(
            db, user_id, "skills", skill_embedding, model_version
        ),
        await _upsert_embedding_row(
            db, user_id, "projects", project_embedding, model_version
        ),
    ]
    await db.flush()
    logger.info("Upserted CandidateEmbedding rows for user %s", user_id)
    return rows


async def get_candidate_embedding(
    db: AsyncSession, user_id: UUID, embedding_type: str = "skills"
) -> CandidateEmbedding | None:
    result = await db.execute(
        select(CandidateEmbedding).where(
            CandidateEmbedding.user_id == user_id,
            CandidateEmbedding.embedding_type == embedding_type,
        )
    )
    return result.scalar_one_or_none()


async def upsert_team_problem_embedding(
    db: AsyncSession,
    team_id: UUID,
    problem_embedding: list[float],
    model_version: str,
) -> None:
    """
    Update (or create) a TeamIntelligence row's problem_embedding.
    """
    result = await db.execute(
        select(TeamIntelligence).where(TeamIntelligence.team_id == team_id)
    )
    ti = result.scalar_one_or_none()
    if ti is None:
        ti = TeamIntelligence(
            team_id=team_id,
            problem_embedding=problem_embedding,
            model_version=model_version,
        )
        db.add(ti)
    else:
        ti.problem_embedding = problem_embedding  # type: ignore[assignment]
        ti.model_version = model_version  # type: ignore[assignment]
    await db.flush()
    logger.info("Upserted TeamIntelligence.problem_embedding for team %s", team_id)
