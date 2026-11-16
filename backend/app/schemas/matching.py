"""Pydantic schemas for matching endpoints."""

from __future__ import annotations

from uuid import UUID
from pydantic import BaseModel


class ScoreComponentSchema(BaseModel):
    score: float
    weight: float
    weighted: float
    label: str


class MatchExplanationSchema(BaseModel):
    total_score: float
    overall_label: str
    matched_skills: list[str]
    reasons: list[str]
    components: dict[str, ScoreComponentSchema]


class CandidateMatchResponse(BaseModel):
    user_id: UUID
    display_name: str
    headline: str
    avatar_url: str | None = None
    score: float
    explanation: MatchExplanationSchema

    model_config = {"from_attributes": True}


class CandidateQueueResponse(BaseModel):
    team_id: UUID
    role_id: UUID | None = None
    total_scored: int
    candidates: list[CandidateMatchResponse]
