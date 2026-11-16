"""
Matching API endpoints.

GET  /teams/{team_id}/candidates           — ranked candidate queue
GET  /teams/{team_id}/candidates/{user_id} — single candidate explanation
"""

from __future__ import annotations

import logging
from uuid import UUID

from fastapi import APIRouter, Depends, Query

from app.api.deps import get_current_user, get_db
from app.schemas.matching import CandidateMatchResponse, CandidateQueueResponse
from app.services.matching_service import get_candidate_match, get_candidate_queue

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/teams", tags=["matching"])


@router.get("/{team_id}/candidates", response_model=CandidateQueueResponse)
async def list_candidates_for_team(
    team_id: UUID,
    role_id: UUID | None = Query(None, description="Filter to a specific open role"),
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    db=Depends(get_db),
    current_user=Depends(get_current_user),
):
    """
    Returns a ranked list of candidates for the given team.
    Team leaders/members only (enforced in the service).
    """
    result = await get_candidate_queue(
        db=db,
        team_id=team_id,
        role_id=role_id,
        viewer_user_id=current_user.id,
        limit=limit,
        offset=offset,
    )
    return result


@router.get("/{team_id}/candidates/{user_id}", response_model=CandidateMatchResponse)
async def get_candidate_for_team(
    team_id: UUID,
    user_id: UUID,
    db=Depends(get_db),
    current_user=Depends(get_current_user),
):
    """
    Returns the score breakdown and evidence-grounded explanation for one candidate.
    Team leaders/members only (enforced in the service).
    """
    result = await get_candidate_match(
        db=db,
        team_id=team_id,
        candidate_user_id=user_id,
        viewer_user_id=current_user.id,
    )
    return result
