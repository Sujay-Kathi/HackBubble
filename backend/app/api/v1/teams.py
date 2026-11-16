import uuid
from typing import Optional
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.api.deps import get_current_user
from app.database.session import get_db
from app.models.user import User
from app.schemas.common import APIResponse, PaginatedResponse
from app.schemas.team import (
    ApplicationResponse,
    ApplicationSubmitRequest,
    FinalizeResultResponse,
    InvitationResponse,
    InvitationResponseRequest,
    ScreeningActionRequest,
    TeamCreateRequest,
    TeamDetailResponse,
    TeamFinalizeRequest,
    TeamRoleCreate,
    TeamRoleResponse,
    TeamRoleUpdate,
    TeamSummaryResponse,
    TeamUpdateRequest,
)
from app.services.team_service import TeamService

router = APIRouter(tags=["Teams"])


@router.post("/teams", response_model=APIResponse[TeamDetailResponse], status_code=status.HTTP_201_CREATED)
async def create_team(
    req: TeamCreateRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    team = await TeamService.create_team(db, current_user.id, req)
    return APIResponse(
        success=True,
        data=TeamDetailResponse.model_validate(team),
        message="Team created successfully",
    )


@router.get("/teams/discover", response_model=PaginatedResponse[TeamSummaryResponse])
async def discover_teams(
    hackathon_id: Optional[uuid.UUID] = Query(None),
    role_name: Optional[str] = Query(None),
    skill: Optional[str] = Query(None),
    beginner_friendly: Optional[bool] = Query(None),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
):
    teams, meta = await TeamService.discover_teams(
        db,
        hackathon_id=hackathon_id,
        role_name=role_name,
        skill=skill,
        beginner_friendly=beginner_friendly,
        page=page,
        page_size=page_size,
    )
    return PaginatedResponse(
        success=True,
        data=[TeamSummaryResponse.model_validate(t) for t in teams],
        pagination=meta,
    )


@router.get("/teams/{team_id}", response_model=APIResponse[TeamDetailResponse])
async def get_team_detail(
    team_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
):
    team = await TeamService.get_team_by_id(db, team_id)
    return APIResponse(
        success=True,
        data=TeamDetailResponse.model_validate(team),
    )


@router.patch("/teams/{team_id}", response_model=APIResponse[TeamDetailResponse])
async def update_team(
    team_id: uuid.UUID,
    req: TeamUpdateRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    team = await TeamService.update_team(db, team_id, current_user.id, req)
    return APIResponse(
        success=True,
        data=TeamDetailResponse.model_validate(team),
        message="Team updated successfully",
    )


@router.post("/teams/{team_id}/publish", response_model=APIResponse[TeamDetailResponse])
async def publish_team(
    team_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    team = await TeamService.publish_team(db, team_id, current_user.id)
    return APIResponse(
        success=True,
        data=TeamDetailResponse.model_validate(team),
        message="Team published successfully",
    )


@router.post("/teams/{team_id}/pause", response_model=APIResponse[TeamDetailResponse])
async def pause_team(
    team_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    team = await TeamService.pause_team(db, team_id, current_user.id)
    return APIResponse(
        success=True,
        data=TeamDetailResponse.model_validate(team),
        message="Recruitment paused",
    )


@router.post("/teams/{team_id}/close", response_model=APIResponse[TeamDetailResponse])
async def close_team(
    team_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    team = await TeamService.close_team(db, team_id, current_user.id)
    return APIResponse(
        success=True,
        data=TeamDetailResponse.model_validate(team),
        message="Recruitment closed",
    )


@router.post("/teams/{team_id}/roles", response_model=APIResponse[TeamRoleResponse], status_code=status.HTTP_201_CREATED)
async def add_role(
    team_id: uuid.UUID,
    req: TeamRoleCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    role = await TeamService.add_role(db, team_id, current_user.id, req)
    return APIResponse(
        success=True,
        data=TeamRoleResponse.model_validate(role),
        message="Role vacancy added successfully",
    )


@router.patch("/teams/{team_id}/roles/{role_id}", response_model=APIResponse[TeamRoleResponse])
async def update_role(
    team_id: uuid.UUID,
    role_id: uuid.UUID,
    req: TeamRoleUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    role = await TeamService.update_role(db, team_id, current_user.id, role_id, req)
    return APIResponse(
        success=True,
        data=TeamRoleResponse.model_validate(role),
        message="Role updated successfully",
    )


@router.delete("/teams/{team_id}/roles/{role_id}", response_model=APIResponse[None])
async def delete_role(
    team_id: uuid.UUID,
    role_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    await TeamService.delete_role(db, team_id, current_user.id, role_id)
    return APIResponse(success=True, data=None, message="Role deleted successfully")


# --- Applications Endpoints ---

@router.post("/teams/{team_id}/applications", response_model=APIResponse[ApplicationResponse], status_code=status.HTTP_201_CREATED)
async def apply_to_team(
    team_id: uuid.UUID,
    req: ApplicationSubmitRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    app = await TeamService.apply_to_team(
        db, team_id=team_id, applicant_id=current_user.id, role_id=req.role_id, message=req.message
    )
    return APIResponse(
        success=True,
        data=ApplicationResponse.model_validate(app),
        message="Application submitted successfully",
    )


@router.get("/applications/me", response_model=APIResponse[list[ApplicationResponse]])
async def get_my_applications(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    apps = await TeamService.get_my_applications(db, current_user.id)
    return APIResponse(
        success=True,
        data=[ApplicationResponse.model_validate(a) for a in apps],
    )


@router.post("/applications/{application_id}/withdraw", response_model=APIResponse[ApplicationResponse])
async def withdraw_application(
    application_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    app = await TeamService.withdraw_application(db, application_id, current_user.id)
    return APIResponse(
        success=True,
        data=ApplicationResponse.model_validate(app),
        message="Application withdrawn",
    )


# --- Screening, Invitations & Finalization ---

@router.post("/teams/{team_id}/screening-actions", response_model=APIResponse[None])
async def record_screening_action(
    team_id: uuid.UUID,
    req: ScreeningActionRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    await TeamService.record_screening_action(
        db,
        team_id=team_id,
        leader_id=current_user.id,
        role_id=req.role_id,
        candidate_id=req.candidate_id,
        action=req.action,
        pass_id=req.pass_id,
    )
    return APIResponse(success=True, data=None, message=f"Recorded action '{req.action}'")


@router.post("/teams/{team_id}/invitations/{invitation_id}/respond", response_model=APIResponse[InvitationResponse])
async def respond_to_invitation(
    team_id: uuid.UUID,
    invitation_id: uuid.UUID,
    req: InvitationResponseRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    inv = await TeamService.respond_to_invitation(
        db, invitation_id=invitation_id, candidate_id=current_user.id, action=req.action
    )
    return APIResponse(
        success=True,
        data=InvitationResponse.model_validate(inv),
        message=f"Invitation {req.action}ed successfully",
    )


@router.post("/teams/{team_id}/finalize", response_model=APIResponse[FinalizeResultResponse])
async def finalize_team(
    team_id: uuid.UUID,
    req: TeamFinalizeRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await TeamService.finalize_team(
        db, team_id=team_id, leader_id=current_user.id, selections=req.selections
    )
    return APIResponse(
        success=True,
        data=result,
        message="Team roster finalized successfully",
    )
