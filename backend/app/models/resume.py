import uuid
from datetime import datetime, timezone
from typing import TYPE_CHECKING, Any, Optional
from pgvector.sqlalchemy import Vector
from sqlalchemy import Boolean, DateTime, ForeignKey, Index, Integer, String, Text
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database.base import Base, TimestampMixin, UUIDPrimaryKeyMixin

if TYPE_CHECKING:
    from app.models.user import User


class UserResume(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    __tablename__ = "user_resumes"

    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), index=True, nullable=False
    )
    storage_key: Mapped[str] = mapped_column(String(500), nullable=False)
    file_name: Mapped[str] = mapped_column(String(255), nullable=False)
    file_hash: Mapped[str] = mapped_column(String(64), index=True, nullable=False)
    mime_type: Mapped[str] = mapped_column(String(100), default="application/pdf", nullable=False)
    file_size_bytes: Mapped[int] = mapped_column(Integer, nullable=False)
    processing_status: Mapped[str] = mapped_column(
        String(32), default="uploaded", index=True, nullable=False
    )
    parser_version: Mapped[str] = mapped_column(String(32), default="1.0", nullable=False)
    ocr_used: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    raw_text: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    parsed_draft: Mapped[Optional[dict[str, Any]]] = mapped_column(JSONB, nullable=True)
    error_message: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    deleted_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)

    user: Mapped["User"] = relationship("User", back_populates="resumes")


class CandidateIntelligence(Base, UUIDPrimaryKeyMixin):
    __tablename__ = "candidate_intelligence"

    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), unique=True, index=True, nullable=False
    )
    profile_summary: Mapped[str] = mapped_column(Text, nullable=False)
    summary_version: Mapped[str] = mapped_column(String(32), default="1.0", nullable=False)
    model_name: Mapped[str] = mapped_column(String(100), default="gpt-4o-mini", nullable=False)
    source_revision: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    generated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False
    )

    user: Mapped["User"] = relationship("User", back_populates="candidate_intelligence")


class CandidateEmbedding(Base, UUIDPrimaryKeyMixin):
    __tablename__ = "candidate_embeddings"

    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), index=True, nullable=False
    )
    embedding_type: Mapped[str] = mapped_column(
        String(32), index=True, nullable=False
    )  # skills, projects, profile
    vector: Mapped[list[float]] = mapped_column(Vector(384), nullable=False)
    model_name: Mapped[str] = mapped_column(String(100), default="sentence-transformers/all-MiniLM-L6-v2", nullable=False)
    model_version: Mapped[str] = mapped_column(String(32), default="1.0", nullable=False)
    source_revision: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False
    )

    user: Mapped["User"] = relationship("User", back_populates="candidate_embeddings")

    __table_args__ = (
        Index("ix_cand_embed_user_type_ver", "user_id", "embedding_type", "model_version"),
    )
