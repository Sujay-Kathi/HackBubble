import uuid
from datetime import datetime, timezone
from typing import Optional
from sqlalchemy import and_, false, func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from app.ai.embeddings.generator import embed_skills, embed_text, get_model_version
from app.ai.embeddings.store import upsert_team_problem_embedding
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
from app.models.user import User, UserProfile
from app.schemas.common import PaginationMeta
from app.schemas.team import (
    CandidateFinalizeSelection,
    FinalizeResultResponse,
    TeamCreateRequest,
    TeamRoleCreate,
    TeamRoleUpdate,
    TeamUpdateRequest,
)
from app.services import notification_service as notif


class TeamService:
    @staticmethod
    async def _display_name(db: AsyncSession, user_id: uuid.UUID) -> str:
        """Resolve a user's display name for notification copy."""
        stmt = select(UserProfile.display_name).where(UserProfile.user_id == user_id)
        return (await db.execute(stmt)).scalar_one_or_none() or "A candidate"

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
                role_embedding=embed_skills(
                    list(r.mandatory_skills or []) + list(r.preferred_skills or [])
                ),
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

        # Build the team's problem-domain embedding for semantic candidate matching
        problem_text = " ".join(
            part for part in (req.problem_statement, req.project_idea) if part
        )
        await upsert_team_problem_embedding(
            db,
            team_id=team_id,
            problem_embedding=embed_text(problem_text),
            model_version=get_model_version(),
        )
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

        # Keep the semantic problem vector in sync with edited content
        if {"problem_statement", "project_idea"} & update_data.keys():
            problem_text = " ".join(
                part for part in (team.problem_statement, team.project_idea) if part
            )
            await upsert_team_problem_embedding(
                db,
                team_id=team.id,
                problem_embedding=embed_text(problem_text),
                model_version=get_model_version(),
            )
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
            role_embedding=embed_skills(
                list(req.mandatory_skills or []) + list(req.preferred_skills or [])
            ),
        )
        db.add(role)
        await db.commit()
        await db.refresh(role)
        return role

    @staticmethod
    async def update_role(
        db: AsyncSession,
        team_id: uuid.UUID,
        leader_id: uuid.UUID,
        role_id: uuid.UUID,
        req: TeamRoleUpdate,
    ) -> TeamRole:
        team = await TeamService.get_team_by_id(db, team_id)
        if team.leader_id != leader_id:
            raise ForbiddenError(message="Only the team leader can modify roles")

        role = (
            await db.execute(
                select(TeamRole).where(
                    TeamRole.id == role_id, TeamRole.team_id == team_id
                )
            )
        ).scalar_one_or_none()
        if not role:
            raise NotFoundError(message="Team role not found")

        update_data = req.model_dump(exclude_unset=True)
        for field, val in update_data.items():
            setattr(role, field, val)

        if {"mandatory_skills", "preferred_skills"} & update_data.keys():
            role.role_embedding = embed_skills(
                list(role.mandatory_skills or []) + list(role.preferred_skills or [])
            )

        await db.commit()
        await db.refresh(role)
        return role

    @staticmethod
    async def delete_role(
        db: AsyncSession, team_id: uuid.UUID, leader_id: uuid.UUID, role_id: uuid.UUID
    ) -> None:
        team = await TeamService.get_team_by_id(db, team_id)
        if team.leader_id != leader_id:
            raise ForbiddenError(message="Only the team leader can delete roles")

        role = (
            await db.execute(
                select(TeamRole).where(
                    TeamRole.id == role_id, TeamRole.team_id == team_id
                )
            )
        ).scalar_one_or_none()
        if not role:
            raise NotFoundError(message="Team role not found")

        reference_checks = (
            select(TeamApplication.id).where(TeamApplication.role_id == role_id).limit(1),
            select(TeamInvitation.id).where(TeamInvitation.role_id == role_id).limit(1),
            select(TeamMember.id).where(TeamMember.role_id == role_id).limit(1),
            select(ScreeningAction.id).where(ScreeningAction.role_id == role_id).limit(1),
        )
        for stmt in reference_checks:
            if (await db.execute(stmt)).first() is not None:
                raise ConflictError(
                    message=(
                        "Role has related applications, invitations, members, or "
                        "screening history and cannot be deleted"
                    )
                )

        await db.delete(role)
        await db.commit()

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

        if beginner_friendly is not None:
            conditions.append(
                Team.id.in_(
                    select(TeamPreference.team_id).where(
                        TeamPreference.beginner_friendly == beginner_friendly
                    )
                )
            )

        if role_name or skill:
            role_stmt = select(TeamRole)
            if role_name:
                role_stmt = role_stmt.where(
                    func.lower(TeamRole.role_name).like(f"%{role_name.strip().lower()}%")
                )
            matching_roles = (await db.execute(role_stmt)).scalars().all()

            if skill and skill.strip():
                skill_lc = skill.strip().lower()

                def _has_skill(role: TeamRole) -> bool:
                    return any(
                        skill_lc in (s or "").lower()
                        for s in list(role.mandatory_skills or [])
                        + list(role.preferred_skills or [])
                    )

                matching_roles = [r for r in matching_roles if _has_skill(r)]

            team_ids = {r.team_id for r in matching_roles}
            conditions.append(Team.id.in_(team_ids) if team_ids else false())

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
        await db.flush()

        applicant_name = await TeamService._display_name(db, applicant_id)
        await notif.notify_application_received(
            db,
            team_leader_id=team.leader_id,
            applicant_name=applicant_name,
            team_name=team.name,
            team_id=team.id,
            application_id=application.id,
        )

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

        team = (
            await db.execute(select(Team).where(Team.id == app.team_id))
        ).scalar_one()
        applicant_name = await TeamService._display_name(db, applicant_id)
        await notif.notify_application_withdrawn(
            db,
            leader_id=team.leader_id,
            applicant_name=applicant_name,
            team_name=team.name,
            team_id=team.id,
            application_id=app.id,
        )

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

            await notif.notify_application_shortlisted(
                db,
                applicant_id=candidate_id,
                team_name=team.name,
                team_id=team.id,
                application_id=app.id if app else invitation.id,
            )

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
                await notif.notify_application_rejected(
                    db,
                    applicant_id=candidate_id,
                    team_name=team.name,
                    team_id=team.id,
                    application_id=app.id,
                )

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

        team = (
            await db.execute(select(Team).where(Team.id == inv.team_id))
        ).scalar_one()
        candidate_name = await TeamService._display_name(db, candidate_id)
        notify = (
            notif.notify_invitation_accepted
            if action == "accept"
            else notif.notify_invitation_declined
        )
        await notify(
            db,
            leader_id=team.leader_id,
            candidate_name=candidate_name,
            team_name=team.name,
            invitation_id=inv.id,
        )

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

        await notif.notify_team_finalized(
            db,
            member_ids=finalized_candidates,
            team_name=team.name,
            team_id=team.id,
        )

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
