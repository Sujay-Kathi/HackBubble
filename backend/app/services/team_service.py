import uuid
from datetime import datetime, timezone
from typing import Optional
from sqlalchemy import and_, func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from app.core.exceptions import (
    CapacityExceededError,
    ConflictError,
    ForbiddenError,
    NotFoundError,
)
from app.models.hackathon import Hackathon
from app.models.team import (
    ScreeningAction,
    Team,
    TeamApplication,
    TeamInvitation,
    TeamMember,
    TeamPreference,
    TeamRole,
)
from app.models.user import User
from app.schemas.common import PaginationMeta
from app.schemas.team import (
    CandidateFinalizeSelection,
    FinalizeResultResponse,
    TeamCreateRequest,
    TeamRoleCreate,
    TeamUpdateRequest,
)


class TeamService:
    @staticmethod
    async def create_team(
        db: AsyncSession, leader_id: uuid.UUID, req: TeamCreateRequest
    ) -> Team:
        # Check if hackathon exists
        h_stmt = select(Hackathon).where(Hackathon.id == req.hackathon_id)
        if not (await db.execute(h_stmt)).scalar_one_or_none():
            raise NotFoundError(message="Hackathon not found")

        team_id = uuid.uuid4()
        team = Team(
            id=team_id,
            hackathon_id=req.hackathon_id,
            leader_id=leader_id,
            name=req.name,
            description=req.description,
            problem_statement=req.problem_statement,
            project_idea=req.project_idea,
            target_size=req.target_size,
            current_size=1,  # Leader is first member
            visibility=req.visibility,
            status="draft",
        )
        db.add(team)

        # Leader is automatically the first official team member
        leader_member = TeamMember(
            id=uuid.uuid4(),
            team_id=team_id,
            user_id=leader_id,
            role_id=None,
            membership_status="active",
        )
        db.add(leader_member)

        # Add initial roles
        for r in req.roles:
            role = TeamRole(
                id=uuid.uuid4(),
                team_id=team_id,
                role_name=r.role_name,
                description=r.description,
                vacancy_count=r.vacancy_count,
                priority=r.priority,
                mandatory_skills=r.mandatory_skills,
                preferred_skills=r.preferred_skills,
                experience_level=r.experience_level,
            )
            db.add(role)

        # Add preferences
        pref = req.preferences
        if pref:
            preference = TeamPreference(
                id=uuid.uuid4(),
                team_id=team_id,
                time_commitment=pref.time_commitment,
                collaboration_style=pref.collaboration_style,
                meeting_frequency=pref.meeting_frequency,
                communication_preference=pref.communication_preference,
                beginner_friendly=pref.beginner_friendly,
            )
        else:
            preference = TeamPreference(id=uuid.uuid4(), team_id=team_id)
        db.add(preference)

        await db.commit()

        # Reload with relationships
        return await TeamService.get_team_by_id(db, team_id)

    @staticmethod
    async def get_team_by_id(
        db: AsyncSession, team_id: uuid.UUID
    ) -> Team:
        stmt = (
            select(Team)
            .where(Team.id == team_id)
            .options(
                selectinload(Team.roles),
                selectinload(Team.preferences),
                selectinload(Team.members),
            )
        )
        team = (await db.execute(stmt)).scalar_one_or_none()
        if not team:
            raise NotFoundError(message="Team not found")
        return team

    @staticmethod
    async def update_team(
        db: AsyncSession, team_id: uuid.UUID, leader_id: uuid.UUID, req: TeamUpdateRequest
    ) -> Team:
        team = await TeamService.get_team_by_id(db, team_id)
        if team.leader_id != leader_id:
            raise ForbiddenError(message="Only the team leader can modify team settings")

        update_data = req.model_dump(exclude_unset=True)
        for field, val in update_data.items():
            setattr(team, field, val)

        await db.commit()
        await db.refresh(team)
        return team

    @staticmethod
    async def publish_team(db: AsyncSession, team_id: uuid.UUID, leader_id: uuid.UUID) -> Team:
        team = await TeamService.get_team_by_id(db, team_id)
        if team.leader_id != leader_id:
            raise ForbiddenError(message="Only the team leader can publish the team")

        # Verify vacancies exist
        total_vacancies = sum(r.vacancy_count for r in team.roles)
        if total_vacancies == 0 and team.current_size >= team.target_size:
            team.status = "full"
        else:
            team.status = "open"

        await db.commit()
        await db.refresh(team)
        return team

    @staticmethod
    async def pause_team(db: AsyncSession, team_id: uuid.UUID, leader_id: uuid.UUID) -> Team:
        team = await TeamService.get_team_by_id(db, team_id)
        if team.leader_id != leader_id:
            raise ForbiddenError(message="Only the team leader can pause recruitment")

        team.status = "paused"
        await db.commit()
        await db.refresh(team)
        return team

    @staticmethod
    async def close_team(db: AsyncSession, team_id: uuid.UUID, leader_id: uuid.UUID) -> Team:
        team = await TeamService.get_team_by_id(db, team_id)
        if team.leader_id != leader_id:
            raise ForbiddenError(message="Only the team leader can close recruitment")

        team.status = "closed"
        await db.commit()
        await db.refresh(team)
        return team

    @staticmethod
    async def add_role(
        db: AsyncSession, team_id: uuid.UUID, leader_id: uuid.UUID, req: TeamRoleCreate
    ) -> TeamRole:
        team = await TeamService.get_team_by_id(db, team_id)
        if team.leader_id != leader_id:
            raise ForbiddenError(message="Only the team leader can add roles")

        role = TeamRole(
            id=uuid.uuid4(),
            team_id=team_id,
            role_name=req.role_name,
            description=req.description,
            vacancy_count=req.vacancy_count,
            priority=req.priority,
            mandatory_skills=req.mandatory_skills,
            preferred_skills=req.preferred_skills,
            experience_level=req.experience_level,
        )
        db.add(role)
        await db.commit()
        await db.refresh(role)
        return role

    @staticmethod
    async def discover_teams(
        db: AsyncSession,
        hackathon_id: Optional[uuid.UUID] = None,
        role_name: Optional[str] = None,
        skill: Optional[str] = None,
        beginner_friendly: Optional[bool] = None,
        page: int = 1,
        page_size: int = 20,
    ) -> tuple[list[Team], PaginationMeta]:
        stmt = (
            select(Team)
            .where(Team.visibility == "public", Team.status == "open")
            .options(
                selectinload(Team.roles),
                selectinload(Team.preferences),
            )
        )
        conditions = []
        if hackathon_id:
            conditions.append(Team.hackathon_id == hackathon_id)

        if conditions:
            stmt = stmt.where(and_(*conditions))

        # Count total
        count_stmt = select(func.count()).select_from(stmt.subquery())
        total_items = (await db.execute(count_stmt)).scalar() or 0

        offset = (page - 1) * page_size
        stmt = stmt.order_by(Team.created_at.desc()).offset(offset).limit(page_size)
        teams = (await db.execute(stmt)).scalars().all()

        total_pages = (total_items + page_size - 1) // page_size if total_items > 0 else 1
        meta = PaginationMeta(
            page=page,
            page_size=page_size,
            total_items=total_items,
            total_pages=total_pages,
            has_next=page < total_pages,
            has_prev=page > 1,
        )
        return list(teams), meta

    # --- Application Workflow ---

    @staticmethod
    async def apply_to_team(
        db: AsyncSession,
        team_id: uuid.UUID,
        applicant_id: uuid.UUID,
        role_id: uuid.UUID,
        message: Optional[str] = None,
    ) -> TeamApplication:
        team = await TeamService.get_team_by_id(db, team_id)
        if team.status != "open":
            raise ConflictError(message="Team is not currently accepting applications")

        if team.leader_id == applicant_id:
            raise ConflictError(message="Team leader cannot apply to their own team")

        # Check if already a member
        mem_stmt = select(TeamMember).where(
            TeamMember.team_id == team_id,
            TeamMember.user_id == applicant_id,
            TeamMember.membership_status == "active",
        )
        if (await db.execute(mem_stmt)).scalar_one_or_none():
            raise ConflictError(message="You are already an active member of this team")

        # Verify role exists and has vacancies
        role_stmt = select(TeamRole).where(TeamRole.id == role_id, TeamRole.team_id == team_id)
        role = (await db.execute(role_stmt)).scalar_one_or_none()
        if not role or role.vacancy_count <= 0:
            raise ConflictError(message="Selected role is not available or has no vacancies")

        # Check for duplicate active application
        app_stmt = select(TeamApplication).where(
            TeamApplication.team_id == team_id,
            TeamApplication.applicant_id == applicant_id,
            TeamApplication.status.in_(["submitted", "under_review", "shortlisted", "candidate_accepted"]),
        )
        if (await db.execute(app_stmt)).scalar_one_or_none():
            raise ConflictError(message="You already have an active application to this team")

        application = TeamApplication(
            id=uuid.uuid4(),
            team_id=team_id,
            applicant_id=applicant_id,
            role_id=role_id,
            message=message,
            status="submitted",
        )
        db.add(application)
        await db.commit()
        await db.refresh(application)
        return application

    @staticmethod
    async def withdraw_application(
        db: AsyncSession, application_id: uuid.UUID, applicant_id: uuid.UUID
    ) -> TeamApplication:
        stmt = select(TeamApplication).where(
            TeamApplication.id == application_id,
            TeamApplication.applicant_id == applicant_id,
        )
        app = (await db.execute(stmt)).scalar_one_or_none()
        if not app:
            raise NotFoundError(message="Application not found")

        if app.status == "finalized":
            raise ConflictError(message="Cannot withdraw an already finalized application")

        app.status = "withdrawn"
        await db.commit()
        await db.refresh(app)
        return app

    @staticmethod
    async def get_my_applications(
        db: AsyncSession, user_id: uuid.UUID
    ) -> list[TeamApplication]:
        stmt = (
            select(TeamApplication)
            .where(TeamApplication.applicant_id == user_id)
            .order_by(TeamApplication.created_at.desc())
        )
        return list((await db.execute(stmt)).scalars().all())

    # --- Screening & Invitation Workflow ---

    @staticmethod
    async def record_screening_action(
        db: AsyncSession,
        team_id: uuid.UUID,
        leader_id: uuid.UUID,
        role_id: uuid.UUID,
        candidate_id: uuid.UUID,
        action: str,  # shortlist | reject | revisit
        pass_id: int = 1,
    ) -> None:
        team = await TeamService.get_team_by_id(db, team_id)
        if team.leader_id != leader_id:
            raise ForbiddenError(message="Only team leader can screen candidates")

        # Persist action
        act = ScreeningAction(
            id=uuid.uuid4(),
            team_id=team_id,
            role_id=role_id,
            leader_id=leader_id,
            candidate_id=candidate_id,
            action=action,
            pass_id=pass_id,
        )
        db.add(act)

        # If shortlist: create invitation and update application if exists
        if action == "shortlist":
            # Check or create invitation
            inv_stmt = select(TeamInvitation).where(
                TeamInvitation.team_id == team_id,
                TeamInvitation.candidate_id == candidate_id,
                TeamInvitation.role_id == role_id,
            )
            invitation = (await db.execute(inv_stmt)).scalar_one_or_none()
            if not invitation:
                invitation = TeamInvitation(
                    id=uuid.uuid4(),
                    team_id=team_id,
                    candidate_id=candidate_id,
                    role_id=role_id,
                    invited_by=leader_id,
                    status="pending",
                )
                db.add(invitation)

            # Update application if exists
            app_stmt = select(TeamApplication).where(
                TeamApplication.team_id == team_id,
                TeamApplication.applicant_id == candidate_id,
                TeamApplication.role_id == role_id,
            )
            app = (await db.execute(app_stmt)).scalar_one_or_none()
            if app:
                app.status = "shortlisted"

        elif action == "reject":
            # Update application if exists
            app_stmt = select(TeamApplication).where(
                TeamApplication.team_id == team_id,
                TeamApplication.applicant_id == candidate_id,
                TeamApplication.role_id == role_id,
            )
            app = (await db.execute(app_stmt)).scalar_one_or_none()
            if app:
                app.status = "rejected"

        await db.commit()

    @staticmethod
    async def respond_to_invitation(
        db: AsyncSession,
        invitation_id: uuid.UUID,
        candidate_id: uuid.UUID,
        action: str,  # accept | decline
    ) -> TeamInvitation:
        stmt = select(TeamInvitation).where(
            TeamInvitation.id == invitation_id,
            TeamInvitation.candidate_id == candidate_id,
        )
        inv = (await db.execute(stmt)).scalar_one_or_none()
        if not inv:
            raise NotFoundError(message="Invitation not found")

        if inv.status != "pending":
            raise ConflictError(message=f"Invitation is already {inv.status}")

        now = datetime.now(timezone.utc)
        inv.responded_at = now

        # Update application state
        app_stmt = select(TeamApplication).where(
            TeamApplication.team_id == inv.team_id,
            TeamApplication.applicant_id == candidate_id,
            TeamApplication.role_id == inv.role_id,
        )
        app = (await db.execute(app_stmt)).scalar_one_or_none()

        if action == "accept":
            inv.status = "accepted"
            if app:
                app.status = "candidate_accepted"
        elif action == "decline":
            inv.status = "declined"
            if app:
                app.status = "candidate_declined"
        else:
            raise ConflictError(message="Invalid invitation response action")

        await db.commit()
        await db.refresh(inv)
        return inv

    # --- Pessimistic Concurrency-Safe Finalization ---

    @staticmethod
    async def finalize_team(
        db: AsyncSession,
        team_id: uuid.UUID,
        leader_id: uuid.UUID,
        selections: list[CandidateFinalizeSelection],
    ) -> FinalizeResultResponse:
        """Atomically lock team row and commit finalized candidate memberships."""
        # 1. Lock team row with pessimistic lock
        team_stmt = (
            select(Team)
            .where(Team.id == team_id)
            .with_for_update()
        )
        team = (await db.execute(team_stmt)).scalar_one_or_none()
        if not team:
            raise NotFoundError(message="Team not found")

        if team.leader_id != leader_id:
            raise ForbiddenError(message="Only the team leader can finalize members")

        if team.status not in ("open", "paused"):
            raise ConflictError(message=f"Cannot finalize team with status {team.status}")

        # 2. Check team capacity
        num_new_members = len(selections)
        if team.current_size + num_new_members > team.target_size:
            raise CapacityExceededError(
                message=f"Finalizing {num_new_members} candidates exceeds target capacity of {team.target_size}"
            )

        finalized_candidates: list[uuid.UUID] = []
        now = datetime.now(timezone.utc)

        # 3. Process each candidate
        for sel in selections:
            # Check role vacancy
            role_stmt = (
                select(TeamRole)
                .where(TeamRole.id == sel.role_id, TeamRole.team_id == team_id)
                .with_for_update()
            )
            role = (await db.execute(role_stmt)).scalar_one_or_none()
            if not role or role.vacancy_count <= 0:
                raise ConflictError(message=f"Role {sel.role_id} has no available vacancy")

            # Check candidate is not already a member
            mem_stmt = select(TeamMember).where(
                TeamMember.team_id == team_id,
                TeamMember.user_id == sel.candidate_id,
                TeamMember.membership_status == "active",
            )
            if (await db.execute(mem_stmt)).scalar_one_or_none():
                raise ConflictError(message=f"Candidate {sel.candidate_id} is already a member")

            # Create official membership
            member = TeamMember(
                id=uuid.uuid4(),
                team_id=team_id,
                user_id=sel.candidate_id,
                role_id=sel.role_id,
                membership_status="active",
                joined_at=now,
            )
            db.add(member)

            # Decrement vacancy
            role.vacancy_count = max(0, role.vacancy_count - 1)

            # Update application state
            app_stmt = select(TeamApplication).where(
                TeamApplication.team_id == team_id,
                TeamApplication.applicant_id == sel.candidate_id,
            )
            app = (await db.execute(app_stmt)).scalar_one_or_none()
            if app:
                app.status = "finalized"

            # Update invitation state
            inv_stmt = select(TeamInvitation).where(
                TeamInvitation.team_id == team_id,
                TeamInvitation.candidate_id == sel.candidate_id,
            )
            inv = (await db.execute(inv_stmt)).scalar_one_or_none()
            if inv:
                inv.status = "finalized"

            finalized_candidates.append(sel.candidate_id)

        # 4. Increment team current size
        team.current_size += len(finalized_candidates)

        # 5. Check if team is full
        roles_stmt = select(TeamRole).where(TeamRole.team_id == team_id)
        all_roles = (await db.execute(roles_stmt)).scalars().all()
        remaining_vacancies = sum(r.vacancy_count for r in all_roles)

        if team.current_size >= team.target_size or remaining_vacancies == 0:
            team.status = "full"

        # 6. Mark non-selected applicants / invitations as not_selected
        not_selected_cand_ids: list[uuid.UUID] = []
        pending_apps_stmt = select(TeamApplication).where(
            TeamApplication.team_id == team_id,
            TeamApplication.status.in_(["submitted", "under_review", "shortlisted", "candidate_accepted"]),
            TeamApplication.applicant_id.notin_(finalized_candidates),
        )
        pending_apps = (await db.execute(pending_apps_stmt)).scalars().all()
        for p_app in pending_apps:
            p_app.status = "not_selected"
            not_selected_cand_ids.append(p_app.applicant_id)

        await db.commit()

        return FinalizeResultResponse(
            team_id=team.id,
            team_status=team.status,
            current_size=team.current_size,
            target_size=team.target_size,
            finalized_candidates=finalized_candidates,
            rejected_or_not_selected_candidates=not_selected_cand_ids,
            message=f"Successfully finalized {len(finalized_candidates)} candidates",
        )
