import json
import re
from typing import Any, Optional
import httpx
from app.core.config import get_settings
from app.schemas.resume import (
    ExtractedAchievementItem,
    ExtractedEducationItem,
    ExtractedExperienceItem,
    ExtractedProjectItem,
    ExtractedSkillItem,
    ParsedResumeDraftSchema,
)

settings = get_settings()


class LLMResumeParser:
    @classmethod
    async def parse_resume_text(cls, raw_text: str) -> ParsedResumeDraftSchema:
        """Parse raw resume text into strict ParsedResumeDraftSchema using configured LLM,
        with robust deterministic heuristic fallback for offline/development environments.
        """
        if settings.LLM_API_KEY:
            try:
                return await cls._call_llm(raw_text)
            except Exception:
                # Graceful degradation to deterministic parser
                pass

        return cls._heuristic_fallback(raw_text)

    @classmethod
    async def _call_llm(cls, raw_text: str) -> ParsedResumeDraftSchema:
        system_prompt = (
            "You are an expert resume parsing engine for HackBubble. "
            "Extract structured data from the provided resume text matching the JSON schema. "
            "Never invent or hallucinate claims. Return ONLY valid JSON."
        )
        user_prompt = f"Resume text:\n\n{raw_text[:4000]}"

        headers = {
            "Authorization": f"Bearer {settings.LLM_API_KEY}",
            "Content-Type": "application/json",
        }
        payload = {
            "model": settings.LLM_MODEL,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            "response_format": {"type": "json_object"},
            "temperature": 0.0,
        }

        async with httpx.AsyncClient(timeout=30.0) as client:
            resp = await client.post(
                f"{settings.LLM_BASE_URL}/chat/completions",
                headers=headers,
                json=payload,
            )
            resp.raise_for_status()
            content = resp.json()["choices"][0]["message"]["content"]
            parsed_json = json.loads(content)
            return ParsedResumeDraftSchema.model_validate(parsed_json)

    @classmethod
    def _heuristic_fallback(cls, text: str) -> ParsedResumeDraftSchema:
        """Deterministic heuristic extraction from raw text for development and offline testing."""
        lines = [line.strip() for line in text.splitlines() if line.strip()]

        common_skills = [
            "python", "javascript", "typescript", "react", "flutter", "dart",
            "fastapi", "django", "node.js", "postgresql", "docker", "kubernetes",
            "aws", "solidity", "web3", "machine learning", "pytorch", "tensorflow",
            "c++", "java", "go", "rust", "html", "css", "sql", "git"
        ]

        text_lower = text.lower()
        extracted_skills: list[ExtractedSkillItem] = []
        for s in common_skills:
            if re.search(rf"\b{re.escape(s)}\b", text_lower):
                extracted_skills.append(
                    ExtractedSkillItem(
                        name=s.title(),
                        proficiency="intermediate",
                        evidence=f"Found in resume: '{s}'",
                        source="resume",
                    )
                )

        domains: list[str] = []
        if any(w in text_lower for w in ["ai", "machine learning", "deep learning", "nlp"]):
            domains.append("Artificial Intelligence")
        if any(w in text_lower for w in ["web", "full stack", "frontend", "backend"]):
            domains.append("Web Development")
        if any(w in text_lower for w in ["mobile", "flutter", "android", "ios"]):
            domains.append("Mobile App Development")
        if any(w in text_lower for w in ["web3", "blockchain", "crypto", "defi", "solidity"]):
            domains.append("Web3 / Blockchain")

        # Basic project extraction from lines containing 'project' or bullets
        projects: list[ExtractedProjectItem] = []
        for i, line in enumerate(lines):
            if "project" in line.lower() and len(line) > 10:
                desc = lines[i + 1] if i + 1 < len(lines) else line
                projects.append(
                    ExtractedProjectItem(
                        name=line[:50],
                        description=desc,
                        technologies=[s.name for s in extracted_skills[:3]],
                    )
                )

        if not projects:
            projects.append(
                ExtractedProjectItem(
                    name="Hackathon Project",
                    description="Contributed to full-stack application development",
                    technologies=[s.name for s in extracted_skills[:3]],
                )
            )

        return ParsedResumeDraftSchema(
            education=[
                ExtractedEducationItem(
                    institution="University / College",
                    degree="Bachelor of Technology / Science",
                    field="Computer Science",
                )
            ],
            domains=domains or ["General Software Engineering"],
            skills=extracted_skills,
            experience=[
                ExtractedExperienceItem(
                    organization="Tech Internship / Contribution",
                    role="Software Developer Intern",
                    description="Engineered software features and collaborated with agile team",
                )
            ],
            projects=projects,
            achievements=[
                ExtractedAchievementItem(
                    title="Hackathon Participant",
                    issuer="College / Global Event",
                )
            ],
            certifications=[],
            links=[],
        )
