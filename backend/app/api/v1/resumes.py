import uuid
from typing import Optional
from fastapi import APIRouter, Depends, File, Response, UploadFile, status
from fastapi.responses import FileResponse
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.api.deps import get_current_user
from app.core.exceptions import AppException, NotFoundError
from app.database.session import get_db
from app.models.resume import UserResume
from app.models.user import User
from app.schemas.common import APIResponse
from app.schemas.resume import (
    CandidateIntelligenceResponse,
    ParsedResumeDraftSchema,
    ResumeConfirmRequest,
    ResumeStatusResponse,
    ResumeSummaryResponse,
    ResumeUploadResponse,
)
from app.services.resume_service import ResumeService
from app.services.storage_service import get_storage_provider

router = APIRouter(prefix="/profiles/me/resumes", tags=["Resumes & Candidate Intelligence"])


@router.post("", response_model=APIResponse[ResumeUploadResponse], status_code=status.HTTP_201_CREATED)
async def upload_resume(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    if not file.filename or not file.filename.lower().endswith(".pdf"):
        raise AppException(message="Only PDF documents are supported for resume processing")

    file_bytes = await file.read()
    if len(file_bytes) > 10 * 1024 * 1024:  # 10 MB limit
        raise AppException(message="Resume file size exceeds maximum permitted limit (10 MB)")

    resume = await ResumeService.upload_resume(
        db, user_id=current_user.id, file_name=file.filename, file_bytes=file_bytes
    )

    return APIResponse(
        success=True,
        data=ResumeUploadResponse.model_validate(resume),
        message="Resume uploaded successfully",
    )


@router.get("", response_model=APIResponse[list[ResumeSummaryResponse]])
async def list_resumes(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    resumes = await ResumeService.list_resumes(db, current_user.id)
    return APIResponse(
        success=True,
        data=[ResumeSummaryResponse.model_validate(r) for r in resumes],
    )


@router.get("/{resume_id}/download")
async def download_resume(
    resume_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    resume = await ResumeService.get_resume_file(db, resume_id, current_user.id)
    storage = get_storage_provider()
    local_path = storage.get_local_path(resume.storage_key)
    if local_path is not None:
        return FileResponse(
            path=str(local_path),
            media_type=resume.mime_type,
            filename=resume.file_name,
        )

    file_bytes = await storage.get_file_bytes(resume.storage_key)
    return Response(
        content=file_bytes,
        media_type=resume.mime_type,
        headers={"Content-Disposition": f'attachment; filename="{resume.file_name}"'},
    )


@router.delete("/{resume_id}", response_model=APIResponse[None])
async def delete_resume(
    resume_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    await ResumeService.delete_resume(db, resume_id, current_user.id)
    return APIResponse(success=True, data=None, message="Resume deleted successfully")


@router.post("/{resume_id}/process", response_model=APIResponse[ResumeStatusResponse])
async def trigger_resume_processing(
    resume_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    resume = await ResumeService.process_resume(
        db, resume_id=resume_id, user_id=current_user.id
    )
    return APIResponse(
        success=True,
        data=ResumeStatusResponse.model_validate(resume),
        message=f"Resume processing state: {resume.processing_status}",
    )


@router.get("/{resume_id}/status", response_model=APIResponse[ResumeStatusResponse])
async def get_resume_status(
    resume_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    stmt = select(UserResume).where(
        UserResume.id == resume_id, UserResume.user_id == current_user.id
    )
    resume = (await db.execute(stmt)).scalar_one_or_none()
    if not resume:
        raise NotFoundError(message="Resume not found")

    return APIResponse(
        success=True,
        data=ResumeStatusResponse.model_validate(resume),
    )


@router.get("/{resume_id}/draft", response_model=APIResponse[Optional[ParsedResumeDraftSchema]])
async def get_parsed_draft(
    resume_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    stmt = select(UserResume).where(
        UserResume.id == resume_id, UserResume.user_id == current_user.id
    )
    resume = (await db.execute(stmt)).scalar_one_or_none()
    if not resume:
        raise NotFoundError(message="Resume not found")

    draft_obj = (
        ParsedResumeDraftSchema.model_validate(resume.parsed_draft)
        if resume.parsed_draft
        else None
    )

    return APIResponse(success=True, data=draft_obj)


@router.post("/{resume_id}/confirm", response_model=APIResponse[CandidateIntelligenceResponse])
async def confirm_resume_draft(
    resume_id: uuid.UUID,
    req: ResumeConfirmRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    intel = await ResumeService.confirm_resume_draft(
        db, resume_id=resume_id, user_id=current_user.id, confirmed_draft=req.draft
    )
    return APIResponse(
        success=True,
        data=CandidateIntelligenceResponse.model_validate(intel),
        message="Resume draft confirmed and profile verified successfully",
    )


@router.get("/intelligence", response_model=APIResponse[Optional[CandidateIntelligenceResponse]])
async def get_candidate_intelligence(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    intel = await ResumeService.get_candidate_intelligence(db, current_user.id)
    return APIResponse(
        success=True,
        data=CandidateIntelligenceResponse.model_validate(intel) if intel else None,
    )
