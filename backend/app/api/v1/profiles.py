import uuid
from typing import Optional
from fastapi import APIRouter, Depends, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from app.api.deps import get_current_user, get_optional_current_user
from app.core.exceptions import ForbiddenError, NotFoundError
from app.database.session import get_db
from app.models.user import (
    User,
    UserAchievement,
    UserExperience,
    UserProfile,
    UserProject,
    UserSkill,
)
from app.schemas.common import APIResponse
from app.schemas.user import (
    UserAchievementCreate,
    UserAchievementResponse,
    UserExperienceCreate,
    UserExperienceResponse,
    UserExperienceUpdate,
    UserProfileResponse,
    UserProfileUpdate,
    UserProjectCreate,
    UserProjectResponse,
    UserProjectUpdate,
    UserSkillCreate,
    UserSkillResponse,
    UserSkillUpdate,
)
from app.services.embedding_service import refresh_candidate_embeddings

router = APIRouter(prefix="/profiles", tags=["User Profiles"])


def _build_profile_response(user: User) -> UserProfileResponse:
    profile = user.profile
    if not profile:
        raise NotFoundError(message="User profile does not exist. Please bootstrap your profile.")

    return UserProfileResponse(
        id=profile.id,
        user_id=profile.user_id,
        display_name=profile.display_name,
        bio=profile.bio,
        education_summary=profile.education_summary,
        location=profile.location,
        domains_of_interest=profile.domains_of_interest or [],
        roles_of_interest=profile.roles_of_interest or [],
        profile_visibility=profile.profile_visibility,
        resume_sharing=profile.resume_sharing,
        skills=[UserSkillResponse.model_validate(s) for s in (user.skills or [])],
        projects=[UserProjectResponse.model_validate(p) for p in (user.projects or [])],
        experience=[UserExperienceResponse.model_validate(e) for e in (user.experience or [])],
        achievements=[UserAchievementResponse.model_validate(a) for a in (user.achievements or [])],
        created_at=profile.created_at,
        updated_at=profile.updated_at,
    )


@router.get("/me", response_model=APIResponse[UserProfileResponse])
async def get_my_profile(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    stmt = (
        select(User)
        .where(User.id == current_user.id)
        .execution_options(populate_existing=True)
        .options(
            selectinload(User.profile),
            selectinload(User.skills),
            selectinload(User.projects),
            selectinload(User.experience),
            selectinload(User.achievements),
        )
    )
    user = (await db.execute(stmt)).scalar_one()
    return APIResponse(
        success=True,
        data=_build_profile_response(user),
    )


@router.patch("/me", response_model=APIResponse[UserProfileResponse])
async def update_my_profile(
    req: UserProfileUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    profile = current_user.profile
    if not profile:
        raise NotFoundError(message="User profile does not exist")

    update_data = req.model_dump(exclude_unset=True)
    for field, val in update_data.items():
        setattr(profile, field, val)

    await db.commit()
    await db.refresh(profile)

    return APIResponse(
        success=True,
        data=_build_profile_response(current_user),
        message="Profile updated successfully",
    )


# --- Skills Management ---

@router.post("/me/skills", response_model=APIResponse[UserSkillResponse], status_code=status.HTTP_201_CREATED)
async def add_skill(
    req: UserSkillCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    normalized = req.skill_name.strip().lower()
    skill = UserSkill(
        id=uuid.uuid4(),
        user_id=current_user.id,
        skill_name=req.skill_name.strip(),
        normalized_skill=normalized,
        proficiency=req.proficiency,
        evidence_source=req.evidence_source,
        evidence_text=req.evidence_text,
    )
    db.add(skill)
    await db.commit()
    await db.refresh(skill)

    await refresh_candidate_embeddings(db, current_user.id)
    await db.commit()

    return APIResponse(
        success=True,
        data=UserSkillResponse.model_validate(skill),
        message="Skill added successfully",
    )


@router.patch("/me/skills/{skill_id}", response_model=APIResponse[UserSkillResponse])
async def update_skill(
    skill_id: uuid.UUID,
    req: UserSkillUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    stmt = select(UserSkill).where(UserSkill.id == skill_id, UserSkill.user_id == current_user.id)
    skill = (await db.execute(stmt)).scalar_one_or_none()
    if not skill:
        raise NotFoundError(message="Skill not found")

    if req.proficiency is not None:
        skill.proficiency = req.proficiency
    if req.evidence_text is not None:
        skill.evidence_text = req.evidence_text

    await db.commit()
    await db.refresh(skill)

    return APIResponse(
        success=True,
        data=UserSkillResponse.model_validate(skill),
        message="Skill updated successfully",
    )


@router.delete("/me/skills/{skill_id}", response_model=APIResponse[None])
async def delete_skill(
    skill_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    stmt = select(UserSkill).where(UserSkill.id == skill_id, UserSkill.user_id == current_user.id)
    skill = (await db.execute(stmt)).scalar_one_or_none()
    if not skill:
        raise NotFoundError(message="Skill not found")

    await db.delete(skill)
    await db.commit()

    await refresh_candidate_embeddings(db, current_user.id)
    await db.commit()

    return APIResponse(success=True, data=None, message="Skill removed successfully")


# --- Projects Management ---

@router.post("/me/projects", response_model=APIResponse[UserProjectResponse], status_code=status.HTTP_201_CREATED)
async def add_project(
    req: UserProjectCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    project = UserProject(
        id=uuid.uuid4(),
        user_id=current_user.id,
        name=req.name,
        description=req.description,
        technologies=req.technologies,
        contribution=req.contribution,
        outcome=req.outcome,
        project_url=req.project_url,
        visibility=req.visibility,
    )
    db.add(project)
    await db.commit()
    await db.refresh(project)

    await refresh_candidate_embeddings(db, current_user.id)
    await db.commit()

    return APIResponse(
        success=True,
        data=UserProjectResponse.model_validate(project),
        message="Project added successfully",
    )


@router.patch("/me/projects/{project_id}", response_model=APIResponse[UserProjectResponse])
async def update_project(
    project_id: uuid.UUID,
    req: UserProjectUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    stmt = select(UserProject).where(UserProject.id == project_id, UserProject.user_id == current_user.id)
    project = (await db.execute(stmt)).scalar_one_or_none()
    if not project:
        raise NotFoundError(message="Project not found")

    update_data = req.model_dump(exclude_unset=True)
    for field, val in update_data.items():
        setattr(project, field, val)

    await db.commit()
    await db.refresh(project)

    await refresh_candidate_embeddings(db, current_user.id)
    await db.commit()

    return APIResponse(
        success=True,
        data=UserProjectResponse.model_validate(project),
        message="Project updated successfully",
    )


@router.delete("/me/projects/{project_id}", response_model=APIResponse[None])
async def delete_project(
    project_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    stmt = select(UserProject).where(UserProject.id == project_id, UserProject.user_id == current_user.id)
    project = (await db.execute(stmt)).scalar_one_or_none()
    if not project:
        raise NotFoundError(message="Project not found")

    await db.delete(project)
    await db.commit()

    await refresh_candidate_embeddings(db, current_user.id)
    await db.commit()

    return APIResponse(success=True, data=None, message="Project removed successfully")


# --- Experience Management ---

@router.post("/me/experience", response_model=APIResponse[UserExperienceResponse], status_code=status.HTTP_201_CREATED)
async def add_experience(
    req: UserExperienceCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    exp = UserExperience(
        id=uuid.uuid4(),
        user_id=current_user.id,
        organization=req.organization,
        role=req.role,
        description=req.description,
        start_date=req.start_date,
        end_date=req.end_date,
        is_current=req.is_current,
        evidence_source=req.evidence_source,
    )
    db.add(exp)
    await db.commit()
    await db.refresh(exp)

    return APIResponse(
        success=True,
        data=UserExperienceResponse.model_validate(exp),
        message="Experience added successfully",
    )


@router.delete("/me/experience/{experience_id}", response_model=APIResponse[None])
async def delete_experience(
    experience_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    stmt = select(UserExperience).where(UserExperience.id == experience_id, UserExperience.user_id == current_user.id)
    exp = (await db.execute(stmt)).scalar_one_or_none()
    if not exp:
        raise NotFoundError(message="Experience record not found")

    await db.delete(exp)
    await db.commit()

    return APIResponse(success=True, data=None, message="Experience removed successfully")


# --- Achievements Management ---

@router.post("/me/achievements", response_model=APIResponse[UserAchievementResponse], status_code=status.HTTP_201_CREATED)
async def add_achievement(
    req: UserAchievementCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    ach = UserAchievement(
        id=uuid.uuid4(),
        user_id=current_user.id,
        title=req.title,
        issuer=req.issuer,
        date=req.date,
        evidence_url=req.evidence_url,
        verification_status="unverified",
    )
    db.add(ach)
    await db.commit()
    await db.refresh(ach)

    return APIResponse(
        success=True,
        data=UserAchievementResponse.model_validate(ach),
        message="Achievement added successfully",
    )


@router.delete("/me/achievements/{achievement_id}", response_model=APIResponse[None])
async def delete_achievement(
    achievement_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    stmt = select(UserAchievement).where(UserAchievement.id == achievement_id, UserAchievement.user_id == current_user.id)
    ach = (await db.execute(stmt)).scalar_one_or_none()
    if not ach:
        raise NotFoundError(message="Achievement record not found")

    await db.delete(ach)
    await db.commit()

    return APIResponse(success=True, data=None, message="Achievement removed successfully")


# --- Public / Other User Profile View ---

@router.get("/{user_id}", response_model=APIResponse[UserProfileResponse])
async def get_user_profile(
    user_id: uuid.UUID,
    viewer: Optional[User] = Depends(get_optional_current_user),
    db: AsyncSession = Depends(get_db),
):
    stmt = (
        select(User)
        .where(User.id == user_id)
        .options(
            selectinload(User.profile),
            selectinload(User.skills),
            selectinload(User.projects),
            selectinload(User.experience),
            selectinload(User.achievements),
        )
    )
    target_user = (await db.execute(stmt)).scalar_one_or_none()
    if not target_user or not target_user.profile:
        raise NotFoundError(message="User profile not found")

    # Enforce profile visibility rules
    is_self = viewer and viewer.id == target_user.id
    if not is_self:
        if target_user.profile.profile_visibility == "private":
            raise ForbiddenError(message="This profile is private")
        if target_user.profile.profile_visibility == "registered_only" and not viewer:
            raise ForbiddenError(message="Sign in required to view this profile")

    # Filter private projects if viewer is not self
    visible_projects = [
        p for p in target_user.projects if is_self or p.visibility == "public"
    ]
    resp = _build_profile_response(target_user)
    resp.projects = [UserProjectResponse.model_validate(p) for p in visible_projects]

    return APIResponse(success=True, data=resp)
