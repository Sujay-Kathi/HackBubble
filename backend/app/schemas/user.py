import uuid
from datetime import date, datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict, EmailStr, Field


# --- Auth Schemas ---

class UserRegisterRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=6, max_length=100)
    display_name: str = Field(min_length=2, max_length=100)


class UserLoginRequest(BaseModel):
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user_id: uuid.UUID
    email: str


class ProfileBootstrapRequest(BaseModel):
    display_name: str = Field(min_length=2, max_length=100)
    bio: Optional[str] = None
    location: Optional[str] = None
    domains_of_interest: list[str] = Field(default_factory=list)
    roles_of_interest: list[str] = Field(default_factory=list)


# --- Skill Schemas ---

class UserSkillBase(BaseModel):
    skill_name: str = Field(min_length=1, max_length=100)
    proficiency: str = Field(default="intermediate")
    evidence_source: str = Field(default="self_reported")
    evidence_text: Optional[str] = None


class UserSkillCreate(UserSkillBase):
    pass


class UserSkillUpdate(BaseModel):
    proficiency: Optional[str] = None
    evidence_text: Optional[str] = None


class UserSkillResponse(UserSkillBase):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    normalized_skill: str
    verified_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime


# --- Project Schemas ---

class UserProjectBase(BaseModel):
    name: str = Field(min_length=1, max_length=200)
    description: str
    technologies: list[str] = Field(default_factory=list)
    contribution: Optional[str] = None
    outcome: Optional[str] = None
    project_url: Optional[str] = None
    visibility: str = Field(default="public")


class UserProjectCreate(UserProjectBase):
    pass


class UserProjectUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    technologies: Optional[list[str]] = None
    contribution: Optional[str] = None
    outcome: Optional[str] = None
    project_url: Optional[str] = None
    visibility: Optional[str] = None


class UserProjectResponse(UserProjectBase):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    created_at: datetime
    updated_at: datetime


# --- Experience Schemas ---

class UserExperienceBase(BaseModel):
    organization: str = Field(min_length=1, max_length=200)
    role: str = Field(min_length=1, max_length=150)
    description: Optional[str] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    is_current: bool = False
    evidence_source: str = Field(default="self_reported")


class UserExperienceCreate(UserExperienceBase):
    pass


class UserExperienceUpdate(BaseModel):
    organization: Optional[str] = None
    role: Optional[str] = None
    description: Optional[str] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    is_current: Optional[bool] = None


class UserExperienceResponse(UserExperienceBase):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    created_at: datetime
    updated_at: datetime


# --- Achievement Schemas ---

class UserAchievementBase(BaseModel):
    title: str = Field(min_length=1, max_length=200)
    issuer: Optional[str] = None
    date: Optional[date] = None
    evidence_url: Optional[str] = None


class UserAchievementCreate(UserAchievementBase):
    pass


class UserAchievementResponse(UserAchievementBase):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    verification_status: str
    created_at: datetime
    updated_at: datetime


# --- Profile Schemas ---

class UserProfileUpdate(BaseModel):
    display_name: Optional[str] = Field(default=None, min_length=2, max_length=100)
    bio: Optional[str] = None
    education_summary: Optional[str] = None
    location: Optional[str] = None
    domains_of_interest: Optional[list[str]] = None
    roles_of_interest: Optional[list[str]] = None
    profile_visibility: Optional[str] = None
    resume_sharing: Optional[str] = None


class UserProfileResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    user_id: uuid.UUID
    display_name: str
    bio: Optional[str] = None
    education_summary: Optional[str] = None
    location: Optional[str] = None
    domains_of_interest: list[str] = Field(default_factory=list)
    roles_of_interest: list[str] = Field(default_factory=list)
    profile_visibility: str
    resume_sharing: str
    skills: list[UserSkillResponse] = Field(default_factory=list)
    projects: list[UserProjectResponse] = Field(default_factory=list)
    experience: list[UserExperienceResponse] = Field(default_factory=list)
    achievements: list[UserAchievementResponse] = Field(default_factory=list)
    created_at: datetime
    updated_at: datetime
