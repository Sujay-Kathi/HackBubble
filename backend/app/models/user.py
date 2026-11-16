import uuid
from datetime import date, datetime
from typing import TYPE_CHECKING, Any, Optional
from sqlalchemy import Boolean, Date, DateTime, ForeignKey, Index, String, Text
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database.base import Base, TimestampMixin, UUIDPrimaryKeyMixin

if TYPE_CHECKING:
    from app.models.hackathon import SavedHackathon
    from app.models.notification import AuditLog, Notification
    from app.models.resume import CandidateEmbedding, CandidateIntelligence, UserResume
    from app.models.team import ScreeningAction, Team, TeamApplication, TeamInvitation, TeamMember


class User(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    __tablename__ = "users"

    email: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)
    auth_subject: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)
    hashed_password: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    account_status: Mapped[str] = mapped_column(String(32), default="active", nullable=False)
    is_admin: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    # Relationships
    profile: Mapped[Optional["UserProfile"]] = relationship(
        "UserProfile", back_populates="user", uselist=False, cascade="all, delete-orphan"
    )
    skills: Mapped[list["UserSkill"]] = relationship(
        "UserSkill", back_populates="user", cascade="all, delete-orphan"
    )
    projects: Mapped[list["UserProject"]] = relationship(
        "UserProject", back_populates="user", cascade="all, delete-orphan"
    )
    experience: Mapped[list["UserExperience"]] = relationship(
        "UserExperience", back_populates="user", cascade="all, delete-orphan"
    )
    achievements: Mapped[list["UserAchievement"]] = relationship(
        "UserAchievement", back_populates="user", cascade="all, delete-orphan"
    )
    resumes: Mapped[list["UserResume"]] = relationship(
        "UserResume", back_populates="user", cascade="all, delete-orphan"
    )
    candidate_intelligence: Mapped[Optional["CandidateIntelligence"]] = relationship(
        "CandidateIntelligence", back_populates="user", uselist=False, cascade="all, delete-orphan"
    )
    candidate_embeddings: Mapped[list["CandidateEmbedding"]] = relationship(
        "CandidateEmbedding", back_populates="user", cascade="all, delete-orphan"
    )
    saved_hackathons: Mapped[list["SavedHackathon"]] = relationship(
        "SavedHackathon", back_populates="user", cascade="all, delete-orphan"
    )
    teams_led: Mapped[list["Team"]] = relationship(
        "Team", back_populates="leader", foreign_keys="Team.leader_id"
    )
    applications: Mapped[list["TeamApplication"]] = relationship(
        "TeamApplication", back_populates="applicant", cascade="all, delete-orphan"
    )
    invitations: Mapped[list["TeamInvitation"]] = relationship(
        "TeamInvitation", back_populates="candidate", foreign_keys="TeamInvitation.candidate_id", cascade="all, delete-orphan"
    )
    team_memberships: Mapped[list["TeamMember"]] = relationship(
        "TeamMember", back_populates="user", cascade="all, delete-orphan"
    )
    screening_actions_received: Mapped[list["ScreeningAction"]] = relationship(
        "ScreeningAction", back_populates="candidate", foreign_keys="ScreeningAction.candidate_id"
    )
    notifications: Mapped[list["Notification"]] = relationship(
        "Notification", back_populates="user", cascade="all, delete-orphan"
    )
    audit_logs: Mapped[list["AuditLog"]] = relationship(
        "AuditLog", back_populates="actor"
    )


class UserProfile(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    __tablename__ = "user_profiles"

    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), unique=True, index=True, nullable=False
    )
    display_name: Mapped[str] = mapped_column(String(100), nullable=False)
    bio: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    education_summary: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    location: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    domains_of_interest: Mapped[list[str]] = mapped_column(JSONB, default=list, nullable=False)
    roles_of_interest: Mapped[list[str]] = mapped_column(JSONB, default=list, nullable=False)
    profile_visibility: Mapped[str] = mapped_column(String(32), default="public", nullable=False)
    resume_sharing: Mapped[str] = mapped_column(String(32), default="leaders_only", nullable=False)

    user: Mapped["User"] = relationship("User", back_populates="profile")


class UserSkill(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    __tablename__ = "user_skills"

    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), index=True, nullable=False
    )
    skill_name: Mapped[str] = mapped_column(String(100), nullable=False)
    normalized_skill: Mapped[str] = mapped_column(String(100), index=True, nullable=False)
    proficiency: Mapped[str] = mapped_column(String(32), default="intermediate", nullable=False)
    evidence_source: Mapped[str] = mapped_column(String(32), default="self_reported", nullable=False)
    evidence_text: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    verified_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)

    user: Mapped["User"] = relationship("User", back_populates="skills")


class UserProject(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    __tablename__ = "user_projects"

    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), index=True, nullable=False
    )
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    technologies: Mapped[list[str]] = mapped_column(JSONB, default=list, nullable=False)
    contribution: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    outcome: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    project_url: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    visibility: Mapped[str] = mapped_column(String(32), default="public", nullable=False)

    user: Mapped["User"] = relationship("User", back_populates="projects")


class UserExperience(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    __tablename__ = "user_experience"

    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), index=True, nullable=False
    )
    organization: Mapped[str] = mapped_column(String(200), nullable=False)
    role: Mapped[str] = mapped_column(String(150), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    start_date: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    end_date: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    is_current: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    evidence_source: Mapped[str] = mapped_column(String(32), default="self_reported", nullable=False)

    user: Mapped["User"] = relationship("User", back_populates="experience")


class UserAchievement(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    __tablename__ = "user_achievements"

    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), index=True, nullable=False
    )
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    issuer: Mapped[Optional[str]] = mapped_column(String(150), nullable=True)
    date: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    evidence_url: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    verification_status: Mapped[str] = mapped_column(String(32), default="unverified", nullable=False)

    user: Mapped["User"] = relationship("User", back_populates="achievements")
