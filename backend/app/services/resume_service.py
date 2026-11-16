import hashlib
import logging
import os
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from app.ai.resume_parser.extractor import ResumeTextExtractor
from app.ai.resume_parser.llm_parser import LLMResumeParser
from app.ai.resume_parser.ocr_fallback import OCRFallbackRunner
from app.ai.summaries.grounded_summarizer import GroundedSummarizer
from app.core.config import get_settings
from app.core.exceptions import ConflictError, NotFoundError
from app.models.resume import CandidateIntelligence, UserResume
from app.models.user import (
    User,
    UserAchievement,
    UserExperience,
    UserProject,
    UserSkill,
)
from app.schemas.resume import ParsedResumeDraftSchema
from app.services.embedding_service import refresh_candidate_embeddings

settings = get_settings()
logger = logging.getLogger(__name__)


class ResumeService:
    @staticmethod
    def _get_storage_path(user_id: uuid.UUID, file_hash: str) -> Path:
        base_dir = Path(settings.LOCAL_STORAGE_DIR) / str(user_id)
        base_dir.mkdir(parents=True, exist_ok=True)
        return base_dir / f"{file_hash}.pdf"

    @classmethod
    async def upload_resume(        cls, db: AsyncSession, user_id: uuid.UUID, file_name: str, file_bytes: bytes
    ) -> UserResume:
        file_hash = hashlib.sha256(file_bytes).hexdigest()
        file_size = len(file_bytes)

        # Save to private storage
        storage_path = cls._get_storage_path(user_id, file_hash)
        with open(storage_path, "wb") as f:
            f.write(file_bytes)

        resume = UserResume(
            id=uuid.uuid4(),
            user_id=user_id,
            storage_key=str(storage_path),
            file_name=file_name,
            file_hash=file_hash,
            file_size_bytes=file_size,
            processing_status="uploaded",
            parser_version="1.0",
        )
        db.add(resume)
        await db.commit()
        await db.refresh(resume)
        return resume

    @staticmethod
    async def list_resumes(
        db: AsyncSession, user_id: uuid.UUID
    ) -> list[UserResume]:
        stmt = (
            select(UserResume)
            .where(
                UserResume.user_id == user_id,
                UserResume.deleted_at.is_(None),
            )
            .order_by(UserResume.created_at.desc())
        )
        return list((await db.execute(stmt)).scalars().all())

    @staticmethod
    async def get_resume_file(
        db: AsyncSession, resume_id: uuid.UUID, user_id: uuid.UUID
    ) -> UserResume:
        stmt = select(UserResume).where(
            UserResume.id == resume_id,
            UserResume.user_id == user_id,
            UserResume.deleted_at.is_(None),
        )
        resume = (await db.execute(stmt)).scalar_one_or_none()
        if not resume:
            raise NotFoundError(message="Resume document not found")

        if not Path(resume.storage_key).is_file():
            raise NotFoundError(message="Resume file is no longer available")
        return resume

    @staticmethod
    async def delete_resume(
        db: AsyncSession, resume_id: uuid.UUID, user_id: uuid.UUID
    ) -> None:
        stmt = select(UserResume).where(
            UserResume.id == resume_id,
            UserResume.user_id == user_id,
            UserResume.deleted_at.is_(None),
        )
        resume = (await db.execute(stmt)).scalar_one_or_none()
        if not resume:
            raise NotFoundError(message="Resume document not found")

        resume.deleted_at = datetime.now(timezone.utc)
        await db.commit()

        # File content is deduplicated by hash; only unlink when no live row uses it
        still_referenced = (
            await db.execute(
                select(UserResume.id)
                .where(
                    UserResume.storage_key == resume.storage_key,
                    UserResume.deleted_at.is_(None),
                )
                .limit(1)
            )
        ).scalar_one_or_none()
        if still_referenced is None:
            path = Path(resume.storage_key)
            if path.is_file():
                try:
                    path.unlink()
                except OSError:
                    logger.warning("Could not remove resume file %s", path)

    @classmethod
    async def process_resume(
        cls, db: AsyncSession, resume_id: uuid.UUID, user_id: uuid.UUID
    ) -> UserResume:
        stmt = select(UserResume).where(
            UserResume.id == resume_id, UserResume.user_id == user_id
        )
        resume = (await db.execute(stmt)).scalar_one_or_none()
        if not resume:
            raise NotFoundError(message="Resume document not found")

        resume.processing_status = "extracting"
        await db.commit()

        try:
            # 1. Read file bytes
            with open(resume.storage_key, "rb") as f:
                file_bytes = f.read()

            # 2. Extract text with PyMuPDF
            raw_text, needs_ocr = ResumeTextExtractor.extract_text_from_bytes(file_bytes)
            if needs_ocr:
                resume.processing_status = "ocr_processing"
                resume.ocr_used = True
                await db.commit()
                ocr_text = OCRFallbackRunner.run_ocr(file_bytes)
                raw_text = f"{raw_text}\n{ocr_text}".strip()

            resume.raw_text = raw_text

            # 3. LLM structured extraction
            resume.processing_status = "structuring"
            await db.commit()

            draft = await LLMResumeParser.parse_resume_text(raw_text)
            resume.parsed_draft = draft.model_dump()
            resume.processing_status = "awaiting_verification"
            await db.commit()
            await db.refresh(resume)
            return resume

        except Exception as e:
            resume.processing_status = "failed_retryable"
            resume.error_message = str(e)
            await db.commit()
            await db.refresh(resume)
            return resume

    @classmethod
    async def confirm_resume_draft(
        cls,
        db: AsyncSession,
        resume_id: uuid.UUID,
        user_id: uuid.UUID,
        confirmed_draft: ParsedResumeDraftSchema,
    ) -> CandidateIntelligence:
        # 1. Verify resume
        stmt = select(UserResume).where(
            UserResume.id == resume_id, UserResume.user_id == user_id
        )
        resume = (await db.execute(stmt)).scalar_one_or_none()
        if not resume:
            raise NotFoundError(message="Resume document not found")

        now = datetime.now(timezone.utc)

        # 2. Add confirmed skills to profile
        for s in confirmed_draft.skills:
            normalized = s.name.strip().lower()
            # Check if skill already exists
            existing_skill = (
                await db.execute(
                    select(UserSkill).where(
                        UserSkill.user_id == user_id,
                        UserSkill.normalized_skill == normalized,
                    )
                )
            ).scalar_one_or_none()

            if not existing_skill:
                new_skill = UserSkill(
                    id=uuid.uuid4(),
                    user_id=user_id,
                    skill_name=s.name.strip(),
                    normalized_skill=normalized,
                    proficiency=s.proficiency,
                    evidence_source="user_confirmed",
                    evidence_text=s.evidence,
                    verified_at=now,
                )
                db.add(new_skill)

        # 3. Add confirmed projects
        for p in confirmed_draft.projects:
            project = UserProject(
                id=uuid.uuid4(),
                user_id=user_id,
                name=p.name,
                description=p.description,
                technologies=p.technologies,
                contribution=p.contribution,
                outcome=p.outcome,
                visibility="public",
            )
            db.add(project)

        # 4. Add confirmed experience
        for e in confirmed_draft.experience:
            exp = UserExperience(
                id=uuid.uuid4(),
                user_id=user_id,
                organization=e.organization or "Organization",
                role=e.role or "Engineer",
                description=e.description,
                evidence_source="user_confirmed",
            )
            db.add(exp)

        # 5. Add achievements
        for a in confirmed_draft.achievements:
            ach = UserAchievement(
                id=uuid.uuid4(),
                user_id=user_id,
                title=a.title,
                issuer=a.issuer,
                verification_status="verified",
            )
            db.add(ach)

        # Mark resume completed
        resume.processing_status = "completed"
        await db.commit()

        # 6. Generate grounded candidate summary
        user_stmt = (
            select(User)
            .where(User.id == user_id)
            .options(
                selectinload(User.profile),
                selectinload(User.skills),
                selectinload(User.projects),
            )
        )
        user = (await db.execute(user_stmt)).scalar_one()
        summary_text = GroundedSummarizer.generate_candidate_summary(user)

        # Upsert CandidateIntelligence
        intel_stmt = select(CandidateIntelligence).where(
            CandidateIntelligence.user_id == user_id
        )
        intel = (await db.execute(intel_stmt)).scalar_one_or_none()

        if intel:
            intel.profile_summary = summary_text
            intel.source_revision += 1
            intel.generated_at = now
        else:
            intel = CandidateIntelligence(
                id=uuid.uuid4(),
                user_id=user_id,
                profile_summary=summary_text,
                summary_version="1.0",
                model_name=settings.LLM_MODEL,
                source_revision=1,
                generated_at=now,
            )
            db.add(intel)

        # 7. Build semantic vectors for matching (skill + project embeddings)
        await refresh_candidate_embeddings(db, user_id)

        await db.commit()
        await db.refresh(intel)
        return intel

    @staticmethod
    async def get_candidate_intelligence(
        db: AsyncSession, user_id: uuid.UUID
    ) -> Optional[CandidateIntelligence]:
        stmt = select(CandidateIntelligence).where(
            CandidateIntelligence.user_id == user_id
        )
        return (await db.execute(stmt)).scalar_one_or_none()
