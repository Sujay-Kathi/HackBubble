"""
Matching service — orchestrates hard filters, scoring, ranking, and access control.
"""

from __future__ import annotations

import logging
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.ai.matching.engine import CandidateMatch, find_candidates_for_team
from app.ai.matching.explainer import explain_match
from app.core.exceptions import ForbiddenError, NotFoundError
from app.models.team import Team, TeamRole

logger = logging.getLogger(__name__)

_TEAM_MATCH_LOADS = (
    selectinload(Team.roles),
    selectinload(Team.members),
    selectinload(Team.preferences),
    selectinload(Team.intelligence),
    selectinload(Team.hackathon),
)


async def _load_team(db: AsyncSession, team_id: UUID) -> Team:
    result = await db.execute(
        select(Team).where(Team.id == team_id).options(*_TEAM_MATCH_LOADS)
    )
    team = result.scalar_one_or_none()
    if team is None:
        raise NotFoundError("Team", str(team_id))
    return team


def _ensure_can_view_candidates(team: Team, viewer_user_id: UUID | None) -> None:
    """Candidate queues expose profile-derived evidence, so restrict to the team."""
    if viewer_user_id is None:
        return
    if team.leader_id == viewer_user_id:
        return
    if any(
        m.user_id == viewer_user_id and m.membership_status == "active"
        for m in team.members
    ):
        return
    raise ForbiddenError(
        message="Only team leaders and members can view candidate matches"
    )


def _serialize_match(match: CandidateMatch) -> dict:
    return {
        "user_id": str(match.user_id),
        "display_name": match.display_name,
        "headline": match.headline,
        "avatar_url": match.avatar_url,
        "score": match.score,
        "explanation": explain_match(match),
    }


async def get_candidate_queue(
    db: AsyncSession,
    team_id: UUID,
    role_id: UUID | None = None,
    viewer_user_id: UUID | None = None,
    limit: int = 20,
    offset: int = 0,
) -> dict:
    """
    Returns a ranked candidate queue for a team (optionally filtered by role).
    """
    team = await _load_team(db, team_id)
    _ensure_can_view_candidates(team, viewer_user_id)

    role: TeamRole | None = None
    if role_id:
        role_res = await db.execute(
            select(TeamRole).where(
                TeamRole.id == role_id, TeamRole.team_id == team_id
            )
        )
        role = role_res.scalar_one_or_none()
        if role is None:
            raise NotFoundError("TeamRole", str(role_id))

    matches: list[CandidateMatch] = await find_candidates_for_team(
        db=db,
        team=team,
        role=role,
        viewer_user_id=viewer_user_id,
        limit=limit,
        offset=offset,
    )

    candidates = [_serialize_match(m) for m in matches]

    return {
        "team_id": str(team_id),
        "role_id": str(role_id) if role_id else None,
        "total_scored": len(candidates),
        "candidates": candidates,
    }


async def get_candidate_match(
    db: AsyncSession,
    team_id: UUID,
    candidate_user_id: UUID,
    viewer_user_id: UUID | None = None,
) -> dict:
    """
    Returns a single candidate's score and full explanation for a team.
    """
    team = await _load_team(db, team_id)
    _ensure_can_view_candidates(team, viewer_user_id)

    matches = await find_candidates_for_team(
        db=db,
        team=team,
        viewer_user_id=viewer_user_id,
        limit=1,
        offset=0,
        candidate_user_id=candidate_user_id,
    )
    if not matches:
        raise NotFoundError("Candidate", str(candidate_user_id))
    return _serialize_match(matches[0])
