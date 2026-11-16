import io
import uuid

import pymupdf
import pytest
from httpx import AsyncClient
from app.ai.resume_parser.extractor import ResumeTextExtractor
from app.ai.resume_parser.llm_parser import LLMResumeParser
from app.ai.summaries.grounded_summarizer import GroundedSummarizer


def _create_sample_pdf_bytes() -> bytes:
    doc = pymupdf.open()
    page = doc.new_page()
    page.insert_text(
        (50, 72),
        "Alex Rivera\n"
        "alex.rivera@example.com\n\n"
        "Summary:\n"
        "Experienced full-stack engineer building AI-driven web and mobile applications.\n\n"
        "Technical Skills:\n"
        "Python, FastAPI, TypeScript, React, Docker, PostgreSQL\n\n"
        "Projects:\n"
        "Project: Autonomous Agent Coordinator\n"
        "Engineered multi-agent orchestration service using Python and FastAPI.\n\n"
        "Experience:\n"
        "Senior Developer at Tech Labs (2023 - Present)\n"
        "Architected scalable backend microservices and databases.\n"
    )
    pdf_bytes = doc.tobytes()
    doc.close()
    return pdf_bytes


def test_resume_text_extraction():
    pdf_bytes = _create_sample_pdf_bytes()
    text, needs_ocr = ResumeTextExtractor.extract_text_from_bytes(pdf_bytes)
    assert "Alex Rivera" in text
    assert "Python, FastAPI" in text
    assert needs_ocr is False


@pytest.mark.asyncio
async def test_llm_structured_extraction():
    raw_text = (
        "Alex Rivera\n"
        "Skills: Python, TypeScript, Docker, Flutter, PostgreSQL\n"
        "Project: Hackathon Matching Engine using FastAPI\n"
    )
    draft = await LLMResumeParser.parse_resume_text(raw_text)
    skill_names = [s.name.lower() for s in draft.skills]
    assert "python" in skill_names
    assert "docker" in skill_names
    assert "flutter" in skill_names
    assert len(draft.projects) >= 1


@pytest.mark.asyncio
async def test_resume_upload_process_and_confirm_flow(async_client: AsyncClient, test_db):
    # 1. Register candidate
    reg = await async_client.post(
        "/api/v1/auth/register",
        json={"email": "resume_user@example.com", "password": "password123", "display_name": "Alex Rivera"},
    )
    user_id = reg.json()["data"]["user_id"]
    token = reg.json()["data"]["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # 2. Upload PDF resume
    pdf_bytes = _create_sample_pdf_bytes()
    files = {"file": ("alex_resume.pdf", io.BytesIO(pdf_bytes), "application/pdf")}
    upload_resp = await async_client.post(
        "/api/v1/profiles/me/resumes",
        headers=headers,
        files=files,
    )
    assert upload_resp.status_code == 201
    resume_id = upload_resp.json()["data"]["id"]
    assert upload_resp.json()["data"]["processing_status"] == "uploaded"

    # 3. Process resume
    proc_resp = await async_client.post(
        f"/api/v1/profiles/me/resumes/{resume_id}/process",
        headers=headers,
    )
    assert proc_resp.status_code == 200
    assert proc_resp.json()["data"]["processing_status"] == "awaiting_verification"

    # 4. Fetch parsed draft for review
    draft_resp = await async_client.get(
        f"/api/v1/profiles/me/resumes/{resume_id}/draft",
        headers=headers,
    )
    assert draft_resp.status_code == 200
    draft = draft_resp.json()["data"]
    assert len(draft["skills"]) > 0

    # 5. User confirms draft
    confirm_resp = await async_client.post(
        f"/api/v1/profiles/me/resumes/{resume_id}/confirm",
        headers=headers,
        json={"draft": draft},
    )
    assert confirm_resp.status_code == 200
    intel = confirm_resp.json()["data"]
    assert "[AI-Generated Summary]" in intel["profile_summary"]
    assert "Alex Rivera" in intel["profile_summary"]

    # 6. Verify user's verified profile now contains the confirmed skills
    profile_resp = await async_client.get("/api/v1/profiles/me", headers=headers)
    profile_skills = [s["skill_name"].lower() for s in profile_resp.json()["data"]["skills"]]
    assert "python" in profile_skills

    # 7. Verify intelligence endpoint
    intel_resp = await async_client.get("/api/v1/profiles/me/resumes/intelligence", headers=headers)
    assert intel_resp.status_code == 200
    assert intel_resp.json()["data"]["profile_summary"] == intel["profile_summary"]

    # 8. Confirmation persisted the semantic vectors used by the matching engine
    from sqlalchemy import select
    from app.models.resume import CandidateEmbedding

    embedding_rows = (
        await test_db.execute(
            select(CandidateEmbedding).where(
                CandidateEmbedding.user_id == uuid.UUID(user_id)
            )
        )
    ).scalars().all()
    by_type = {row.embedding_type: row for row in embedding_rows}
    assert set(by_type) == {"skills", "projects"}
    assert len(by_type["skills"].vector) == 384
    assert len(by_type["projects"].vector) == 384
    assert by_type["skills"].model_version
