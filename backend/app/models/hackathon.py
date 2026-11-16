import uuid
from datetime import datetime, timezone
from typing import TYPE_CHECKING, Any, Optional
from sqlalchemy import Boolean, DateTime, ForeignKey, Index, Numeric, String, Text, UniqueConstraint
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database.base import Base, TimestampMixin, UUIDPrimaryKeyMixin

if TYPE_CHECKING:
    from app.models.team import Team
    from app.models.user import User


class HackathonSource(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    __tablename__ = "hackathon_sources"

    name: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    base_url: Mapped[str] = mapped_column(String(500), nullable=False)
    adapter_key: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    enabled: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    crawl_interval_hours: Mapped[int] = mapped_column(default=6, nullable=False)
    policy_notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Relationships
    scrape_runs: Mapped[list["ScrapeRun"]] = relationship("ScrapeRun", back_populates="source", cascade="all, delete-orphan")
    source_records: Mapped[list["HackathonSourceRecord"]] = relationship("HackathonSourceRecord", back_populates="source", cascade="all, delete-orphan")


class ScrapeRun(Base, UUIDPrimaryKeyMixin):
    __tablename__ = "scrape_runs"

    source_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("hackathon_sources.id", ondelete="CASCADE"), index=True, nullable=False
    )
    started_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)
    finished_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    status: Mapped[str] = mapped_column(String(32), default="running", nullable=False)  # running, completed, failed
    events_found: Mapped[int] = mapped_column(default=0, nullable=False)
    events_created: Mapped[int] = mapped_column(default=0, nullable=False)
    events_updated: Mapped[int] = mapped_column(default=0, nullable=False)
    error_summary: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    source: Mapped["HackathonSource"] = relationship("HackathonSource", back_populates="scrape_runs")


class Hackathon(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    __tablename__ = "hackathons"

    title: Mapped[str] = mapped_column(String(300), index=True, nullable=False)
    organizer: Mapped[Optional[str]] = mapped_column(String(200), index=True, nullable=True)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    themes: Mapped[list[str]] = mapped_column(JSONB, default=list, nullable=False)
    eligibility: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    mode: Mapped[str] = mapped_column(String(32), default="online", nullable=False)  # online, offline, hybrid, unknown
    location: Mapped[Optional[str]] = mapped_column(String(200), nullable=True)
    registration_url: Mapped[Optional[str]] = mapped_column(String(1000), nullable=True)
    event_url: Mapped[str] = mapped_column(String(1000), index=True, nullable=False)
    source_name: Mapped[str] = mapped_column(String(100), index=True, nullable=False)
    source_url: Mapped[str] = mapped_column(String(1000), nullable=False)
    source_event_id: Mapped[Optional[str]] = mapped_column(String(200), index=True, nullable=True)
    registration_deadline: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), index=True, nullable=True)
    start_date: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), index=True, nullable=True)
    end_date: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), index=True, nullable=True)
    prize_pool_amount: Mapped[Optional[float]] = mapped_column(Numeric(12, 2), nullable=True)
    prize_pool_currency: Mapped[Optional[str]] = mapped_column(String(10), nullable=True)
    status: Mapped[str] = mapped_column(String(32), default="upcoming", index=True, nullable=False)
    last_scraped_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    last_verified_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    data_quality_status: Mapped[str] = mapped_column(String(32), default="verified", nullable=False)

    # Relationships
    source_records: Mapped[list["HackathonSourceRecord"]] = relationship(
        "HackathonSourceRecord", back_populates="hackathon", cascade="all, delete-orphan"
    )
    saved_by_users: Mapped[list["SavedHackathon"]] = relationship(
        "SavedHackathon", back_populates="hackathon", cascade="all, delete-orphan"
    )
    teams: Mapped[list["Team"]] = relationship(
        "Team", back_populates="hackathon", cascade="all, delete-orphan"
    )


class HackathonSourceRecord(Base, UUIDPrimaryKeyMixin):
    __tablename__ = "hackathon_source_records"

    hackathon_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("hackathons.id", ondelete="CASCADE"), index=True, nullable=False
    )
    source_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("hackathon_sources.id", ondelete="CASCADE"), index=True, nullable=False
    )
    source_event_id: Mapped[Optional[str]] = mapped_column(String(200), index=True, nullable=True)
    source_url: Mapped[str] = mapped_column(String(1000), nullable=False)
    raw_payload: Mapped[dict[str, Any]] = mapped_column(JSONB, default=dict, nullable=False)
    last_scraped_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False
    )

    hackathon: Mapped["Hackathon"] = relationship("Hackathon", back_populates="source_records")
    source: Mapped["HackathonSource"] = relationship("HackathonSource", back_populates="source_records")


class SavedHackathon(Base):
    __tablename__ = "saved_hackathons"

    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), primary_key=True, nullable=False
    )
    hackathon_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("hackathons.id", ondelete="CASCADE"), primary_key=True, nullable=False
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False
    )

    user: Mapped["User"] = relationship("User", back_populates="saved_hackathons")
    hackathon: Mapped["Hackathon"] = relationship("Hackathon", back_populates="saved_by_users")

    __table_args__ = (
        UniqueConstraint("user_id", "hackathon_id", name="uq_saved_hackathon_user"),
    )
