import uuid
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict, Field


# --- Role Schemas ---

class TeamRoleCreate(BaseModel):
    role_name: str = Field(min_length=2, max_length=100)
    description: Optional[str] = None
    vacancy_count: int = Field(default=1, ge=1, le=20)
    priority: int = Field(default=1, ge=1, le=5)
    mandatory_skills: list[str] = Field(default_factory=list)
    preferred_skills: list[str] = Field(default_factory=list)
    experience_level: str = Field(default="intermediate")


class TeamRoleUpdate(BaseModel):
    role_name: Optional[str] = None
    description: Optional[str] = None
    vacancy_count: Optional[int] = Field(default=None, ge=0)
    priority: Optional[int] = Field(default=None, ge=1, le=5)
    mandatory_skills: Optional[list[str]] = None
    preferred_skills: Optional[list[str]] = None
    experience_level: Optional[str] = None


class TeamRoleResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    team_id: uuid.UUID
    role_name: str
    description: Optional[str] = None
    vacancy_count: int
    priority: int
    mandatory_skills: list[str]
    preferred_skills: list[str]
    experience_level: str
    created_at: datetime


# --- Preference Schemas ---

class TeamPreferenceCreate(BaseModel):
    time_commitment: str = Field(default="flexible")
    collaboration_style: str = Field(default="asynchronous")
    meeting_frequency: str = Field(default="daily")
    communication_preference: str = Field(default="discord")
    beginner_friendly: bool = True


class TeamPreferenceResponse(TeamPreferenceCreate):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    team_id: uuid.UUID


# --- Team Schemas ---

class TeamCreateRequest(BaseModel):
    hackathon_id: uuid.UUID
    name: str = Field(min_length=2, max_length=150)
    description: Optional[str] = None
    problem_statement: str = Field(min_length=10)
    project_idea: Optional[str] = None
    target_size: int = Field(default=4, ge=2, le=20)
    visibility: str = Field(default="public")  # public, private
    roles: list[TeamRoleCreate] = Field(default_factory=list)
    preferences: Optional[TeamPreferenceCreate] = None


class TeamUpdateRequest(BaseModel):
    name: Optional[str] = Field(default=None, min_length=2, max_length=150)
    description: Optional[str] = None
    problem_statement: Optional[str] = Field(default=None, min_length=10)
    project_idea: Optional[str] = None
    target_size: Optional[int] = Field(default=None, ge=2, le=20)
    visibility: Optional[str] = None


class TeamMemberResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    user_id: uuid.UUID
    role_id: Optional[uuid.UUID] = None
    membership_status: str
    joined_at: datetime


class TeamDetailResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    hackathon_id: uuid.UUID
    leader_id: uuid.UUID
    name: str
    description: Optional[str] = None
    problem_statement: str
    project_idea: Optional[str] = None
    target_size: int
    current_size: int
    visibility: str
    status: str
    roles: list[TeamRoleResponse] = Field(default_factory=list)
    preferences: Optional[TeamPreferenceResponse] = None
    members: list[TeamMemberResponse] = Field(default_factory=list)
    created_at: datetime
    updated_at: datetime


class TeamSummaryResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    hackathon_id: uuid.UUID
    leader_id: uuid.UUID
    name: str
    problem_statement: str
    target_size: int
    current_size: int
    visibility: str
    status: str
    roles: list[TeamRoleResponse] = Field(default_factory=list)
    created_at: datetime


# --- Application & Invitation Schemas ---

class ApplicationSubmitRequest(BaseModel):
    role_id: uuid.UUID
    message: Optional[str] = None


class ApplicationResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    team_id: uuid.UUID
    applicant_id: uuid.UUID
    role_id: uuid.UUID
    message: Optional[str] = None
    status: str
    created_at: datetime
    updated_at: datetime


class ScreeningActionRequest(BaseModel):
    role_id: uuid.UUID
    candidate_id: uuid.UUID
    action: str = Field(description="shortlist | reject | revisit")
    pass_id: int = Field(default=1, ge=1)


class InvitationResponseRequest(BaseModel):
    action: str = Field(description="accept | decline")


class InvitationResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    team_id: uuid.UUID
    candidate_id: uuid.UUID
    role_id: uuid.UUID
    invited_by: uuid.UUID
    status: str
    expires_at: Optional[datetime] = None
    responded_at: Optional[datetime] = None
    created_at: datetime


# --- Finalization Schemas ---

class CandidateFinalizeSelection(BaseModel):
    candidate_id: uuid.UUID
    role_id: uuid.UUID


class TeamFinalizeRequest(BaseModel):
    selections: list[CandidateFinalizeSelection] = Field(min_length=1)


class FinalizeResultResponse(BaseModel):
    team_id: uuid.UUID
    team_status: str
    current_size: int
    target_size: int
    finalized_candidates: list[uuid.UUID]
    rejected_or_not_selected_candidates: list[uuid.UUID]
    message: str
