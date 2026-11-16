import uuid
from datetime import datetime
from typing import Any, Optional
from pydantic import BaseModel, ConfigDict, Field


class ExtractedEducationItem(BaseModel):
    institution: Optional[str] = None
    degree: Optional[str] = None
    field: Optional[str] = None
    start_date: Optional[str] = None
    end_date: Optional[str] = None


class ExtractedSkillItem(BaseModel):
    name: str
    proficiency: str = Field(default="intermediate")
    evidence: Optional[str] = None
    source: str = Field(default="resume")


class ExtractedExperienceItem(BaseModel):
    organization: Optional[str] = None
    role: Optional[str] = None
    description: str
    start_date: Optional[str] = None
    end_date: Optional[str] = None


class ExtractedProjectItem(BaseModel):
    name: str
    description: str
    technologies: list[str] = Field(default_factory=list)
    contribution: Optional[str] = None
    outcome: Optional[str] = None


class ExtractedAchievementItem(BaseModel):
    title: str
    issuer: Optional[str] = None
    date: Optional[str] = None
    evidence: Optional[str] = None


class ParsedResumeDraftSchema(BaseModel):
    education: list[ExtractedEducationItem] = Field(default_factory=list)
    domains: list[str] = Field(default_factory=list)
    skills: list[ExtractedSkillItem] = Field(default_factory=list)
    experience: list[ExtractedExperienceItem] = Field(default_factory=list)
    projects: list[ExtractedProjectItem] = Field(default_factory=list)
    achievements: list[ExtractedAchievementItem] = Field(default_factory=list)
    certifications: list[str] = Field(default_factory=list)
    links: list[str] = Field(default_factory=list)


class ResumeUploadResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    file_name: str
    file_size_bytes: int
    processing_status: str
    created_at: datetime


class ResumeStatusResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    processing_status: str
    parser_version: str
    ocr_used: bool
    error_message: Optional[str] = None
    created_at: datetime
    updated_at: datetime


class ResumeSummaryResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    file_name: str
    mime_type: str
    file_size_bytes: int
    processing_status: str
    ocr_used: bool
    created_at: datetime


class ResumeConfirmRequest(BaseModel):
    draft: ParsedResumeDraftSchema


class CandidateIntelligenceResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    user_id: uuid.UUID
    profile_summary: str
    summary_version: str
    model_name: str
    source_revision: int
    generated_at: datetime
