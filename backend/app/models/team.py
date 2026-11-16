import uuid
from datetime import datetime, timezone
from typing import TYPE_CHECKING, Any, Optional
from pgvector.sqlalchemy import Vector
from sqlalchemy import Boolean, DateTime, ForeignKey, Index, Integer, String, Text, UniqueConstraint
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database.base import Base, TimestampMixin, UUIDPrimaryKeyMixin

if TYPE_CHECKING:
    from app.models.hackathon import Hackathon
    from app.models.user import User


class Team(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    __tablename__ = "teams"

    hackathon_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("hackathons.id", ondelete="CASCADE"), index=True, nullable=False
    )
    leader_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="RESTRICT"), index=True, nullable=False
    )
    name: Mapped[str] = mapped_column(String(150), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    problem_statement: Mapped[str] = mapped_column(Text, nullable=False)
    project_idea: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    target_size: Mapped[int] = mapped_column(Integer, default=4, nullable=False)
    current_size: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    visibility: Mapped[str] = mapped_column(String(32), default="public", index=True, nullable=False)  # public, private
    status: Mapped[str] = mapped_column(String(32), default="draft", index=True, nullable=False)  # draft, open, paused, full, closed, cancelled, completed

    # Relationships
    hackathon: Mapped["Hackathon"] = relationship("Hackathon", back_populates="teams")
    leader: Mapped["User"] = relationship("User", back_populates="teams_led", foreign_keys=[leader_id])
    roles: Mapped[list["TeamRole"]] = relationship("TeamRole", back_populates="team", cascade="all, delete-orphan")
    preferences: Mapped[Optional["TeamPreference"]] = relationship(
        "TeamPreference", back_populates="team", uselist=False, cascade="all, delete-orphan"
    )
    intelligence: Mapped[Optional["TeamIntelligence"]] = relationship(
        "TeamIntelligence", back_populates="team", uselist=False, cascade="all, delete-orphan"
    )
    applications: Mapped[list["TeamApplication"]] = relationship(
        "TeamApplication", back_populates="team", cascade="all, delete-orphan"
    )
    invitations: Mapped[list["TeamInvitation"]] = relationship(
        "TeamInvitation", back_populates="team", cascade="all, delete-orphan"
    )
    members: Mapped[list["TeamMember"]] = relationship(
        "TeamMember", back_populates="team", cascade="all, delete-orphan"
    )
    screening_actions: Mapped[list["ScreeningAction"]] = relationship(
        "ScreeningAction", back_populates="team", cascade="all, delete-orphan"
    )


class TeamRole(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    __tablename__ = "team_roles"

    team_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("teams.id", ondelete="CASCADE"), index=True, nullable=False
    )
    role_name: Mapped[str] = mapped_column(String(100), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    vacancy_count: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    priority: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    mandatory_skills: Mapped[list[str]] = mapped_column(JSONB, default=list, nullable=False)
    preferred_skills: Mapped[list[str]] = mapped_column(JSONB, default=list, nullable=False)
    experience_level: Mapped[str] = mapped_column(String(32), default="intermediate", nullable=False)
    role_embedding: Mapped[Optional[list[float]]] = mapped_column(Vector(384), nullable=True)

    team: Mapped["Team"] = relationship("Team", back_populates="roles")
    applications: Mapped[list["TeamApplication"]] = relationship("TeamApplication", back_populates="role")
    invitations: Mapped[list["TeamInvitation"]] = relationship("TeamInvitation", back_populates="role")
    members: Mapped[list["TeamMember"]] = relationship("TeamMember", back_populates="role")
    screening_actions: Mapped[list["ScreeningAction"]] = relationship("ScreeningAction", back_populates="role")


class TeamPreference(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    __tablename__ = "team_preferences"

    team_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("teams.id", ondelete="CASCADE"), unique=True, index=True, nullable=False
    )
    time_commitment: Mapped[str] = mapped_column(String(50), default="flexible", nullable=False)
    collaboration_style: Mapped[str] = mapped_column(String(50), default="asynchronous", nullable=False)
    meeting_frequency: Mapped[str] = mapped_column(String(50), default="daily", nullable=False)
    communication_preference: Mapped[str] = mapped_column(String(50), default="discord", nullable=False)
    beginner_friendly: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    team: Mapped["Team"] = relationship("Team", back_populates="preferences")


class TeamIntelligence(Base, UUIDPrimaryKeyMixin):
    __tablename__ = "team_intelligence"

    team_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("teams.id", ondelete="CASCADE"), unique=True, index=True, nullable=False
    )
    problem_embedding: Mapped[Optional[list[float]]] = mapped_column(Vector(384), nullable=True)
    model_name: Mapped[str] = mapped_column(String(100), default="sentence-transformers/all-MiniLM-L6-v2", nullable=False)
    model_version: Mapped[str] = mapped_column(String(32), default="1.0", nullable=False)
    processed_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False
    )

    team: Mapped["Team"] = relationship("Team", back_populates="intelligence")


class TeamApplication(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    __tablename__ = "team_applications"

    team_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("teams.id", ondelete="CASCADE"), index=True, nullable=False
    )
    applicant_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), index=True, nullable=False
    )
    role_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("team_roles.id", ondelete="CASCADE"), index=True, nullable=False
    )
    message: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    status: Mapped[str] = mapped_column(String(32), default="submitted", index=True, nullable=False)

    team: Mapped["Team"] = relationship("Team", back_populates="applications")
    applicant: Mapped["User"] = relationship("User", back_populates="applications")
    role: Mapped["TeamRole"] = relationship("TeamRole", back_populates="applications")

    __table_args__ = (
        Index("ix_app_team_applicant_status", "team_id", "applicant_id", "status"),
    )


class TeamInvitation(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    __tablename__ = "team_invitations"

    team_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("teams.id", ondelete="CASCADE"), index=True, nullable=False
    )
    candidate_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), index=True, nullable=False
    )
    role_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("team_roles.id", ondelete="CASCADE"), index=True, nullable=False
    )
    invited_by: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="RESTRICT"), nullable=False
    )
    status: Mapped[str] = mapped_column(String(32), default="pending", index=True, nullable=False)
    expires_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    responded_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)

    team: Mapped["Team"] = relationship("Team", back_populates="invitations")
    candidate: Mapped["User"] = relationship("User", back_populates="invitations", foreign_keys=[candidate_id])
    role: Mapped["TeamRole"] = relationship("TeamRole", back_populates="invitations")


class TeamMember(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    __tablename__ = "team_members"

    team_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("teams.id", ondelete="CASCADE"), index=True, nullable=False
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), index=True, nullable=False
    )
    role_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True), ForeignKey("team_roles.id", ondelete="SET NULL"), nullable=True
    )
    membership_status: Mapped[str] = mapped_column(String(32), default="active", index=True, nullable=False)  # active, removed, left
    joined_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False
    )
    left_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)

    team: Mapped["Team"] = relationship("Team", back_populates="members")
    user: Mapped["User"] = relationship("User", back_populates="team_memberships")
    role: Mapped[Optional["TeamRole"]] = relationship("TeamRole", back_populates="members")

    __table_args__ = (
        UniqueConstraint("team_id", "user_id", name="uq_team_user_active_member"),
    )


class ScreeningAction(Base, UUIDPrimaryKeyMixin):
    __tablename__ = "screening_actions"

    team_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("teams.id", ondelete="CASCADE"), index=True, nullable=False
    )
    role_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("team_roles.id", ondelete="CASCADE"), index=True, nullable=False
    )
    leader_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    candidate_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), index=True, nullable=False
    )
    action: Mapped[str] = mapped_column(String(32), nullable=False)  # shortlist, reject, revisit
    pass_id: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False
    )

    team: Mapped["Team"] = relationship("Team", back_populates="screening_actions")
    role: Mapped["TeamRole"] = relationship("TeamRole", back_populates="screening_actions")
    candidate: Mapped["User"] = relationship("User", back_populates="screening_actions_received", foreign_keys=[candidate_id])

    __table_args__ = (
        Index("ix_screening_action_team_cand", "team_id", "candidate_id", "pass_id"),
    )
