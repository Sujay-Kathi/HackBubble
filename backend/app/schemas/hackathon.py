import uuid
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict, Field, HttpUrl


class CanonicalHackathonSchema(BaseModel):
    title: str = Field(min_length=2, max_length=300)
    organizer: Optional[str] = Field(default=None, max_length=200)
    description: Optional[str] = None
    themes: list[str] = Field(default_factory=list)
    eligibility: Optional[str] = None
    mode: str = Field(default="online")  # online, offline, hybrid, unknown
    location: Optional[str] = None
    registration_url: Optional[str] = None
    event_url: str
    source_name: str
    source_url: str
    source_event_id: Optional[str] = None
    registration_deadline: Optional[datetime] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    prize_pool_amount: Optional[float] = None
    prize_pool_currency: Optional[str] = "USD"
    status: str = Field(default="upcoming")
    data_quality_status: str = Field(default="verified")


class HackathonSummaryResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    title: str
    organizer: Optional[str] = None
    themes: list[str] = Field(default_factory=list)
    mode: str
    location: Optional[str] = None
    registration_url: Optional[str] = None
    event_url: str
    source_name: str
    registration_deadline: Optional[datetime] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    prize_pool_amount: Optional[float] = None
    prize_pool_currency: Optional[str] = None
    status: str
    created_at: datetime


class HackathonDetailResponse(HackathonSummaryResponse):
    description: Optional[str] = None
    eligibility: Optional[str] = None
    source_url: str
    last_scraped_at: Optional[datetime] = None
    last_verified_at: Optional[datetime] = None
    data_quality_status: str
    is_bookmarked: bool = False


class SavedHackathonResponse(BaseModel):
    hackathon: HackathonSummaryResponse
    saved_at: datetime


class IngestionReport(BaseModel):
    source_name: str
    events_found: int
    events_created: int
    events_updated: int
    duration_seconds: float
    status: str
    errors: list[str] = Field(default_factory=list)
