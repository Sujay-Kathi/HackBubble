"""
Hybrid matching engine for HackBubble candidate discovery.

Score breakdown (total 1.0):
  30% role_skill_match   — overlap between required role skills and candidate skills
  25% semantic_skill     — cosine similarity of skill embeddings
  25% project_problem    — cosine similarity of project embedding vs team problem
  10% experience_match   — experience level compatibility
  10% preference_match   — remote/timezone/domain preferences overlap
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from uuid import UUID

from sqlalchemy import and_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.ai.embeddings.generator import cosine_similarity_py, embed_skills, embed_text
from app.models.resume import CandidateEmbedding
from app.models.team import Team, TeamMember, TeamRole
from app.models.user import User, UserProfile

logger = logging.getLogger(__name__)

WEIGHT_ROLE_SKILL = 0.30
WEIGHT_SEMANTIC_SKILL = 0.25
WEIGHT_PROJECT_PROBLEM = 0.25
WEIGHT_EXPERIENCE = 0.10
WEIGHT_PREFERENCE = 0.10


@dataclass
class ScoreBreakdown:
    role_skill: float = 0.0
    semantic_skill: float = 0.0
    project_problem: float = 0.0
    experience: float = 0.0
    preference: float = 0.0

    @property
    def total(self) -> float:
        return (
            self.role_skill * WEIGHT_ROLE_SKILL
            + self.semantic_skill * WEIGHT_SEMANTIC_SKILL
            + self.project_problem * WEIGHT_PROJECT_PROBLEM
            + self.experience * WEIGHT_EXPERIENCE
            + self.preference * WEIGHT_PREFERENCE
        )


@dataclass
class CandidateMatch:
    user_id: UUID
    display_name: str
    headline: str
    avatar_url: str | None
    score: float
    breakdown: ScoreBreakdown
    matched_skills: list[str] = field(default_factory=list)
    reasons: list[str] = field(default_factory=list)


async def find_candidates_for_team(
    db: AsyncSession,
    team: Team,
    role: TeamRole | None = None,
    viewer_user_id: UUID | None = None,
    limit: int = 20,
    offset: int = 0,
    candidate_user_id: UUID | None = None,
) -> list[CandidateMatch]:
    """
    Hard-filter then score all eligible candidates for a team (or specific role).
    Returns ranked list of CandidateMatch objects.
    """
    # ── 1. Hard filters ───────────────────────────────────────────────
    if team.status not in ("open", "paused"):
        return []

    # Fetch current member user IDs to exclude
    member_res = await db.execute(
        select(TeamMember.user_id).where(TeamMember.team_id == team.id)
    )
    member_ids: set[UUID] = {row[0] for row in member_res.fetchall()}
    if viewer_user_id:
        member_ids.add(viewer_user_id)  # exclude self too

    # Required skills for this role (or union of all open roles)
    required_skills: list[str] = []
    target_experience: str | None = None
    if role:
        required_skills = list(role.mandatory_skills or [])
        target_experience = role.experience_level
    else:
        for r in (team.roles or []):
            if getattr(r, "is_open", True):
                required_skills.extend(r.mandatory_skills or [])
        required_skills = list(set(required_skills))

    # Problem statement embedding for the team
    team_problem_embedding: list[float] | None = None
    if hasattr(team, "intelligence") and team.intelligence is not None:
        ti = team.intelligence
        raw_emb = getattr(ti, "problem_embedding", None)
        if raw_emb is not None:
            team_problem_embedding = list(raw_emb)

    if team_problem_embedding is None:
        # Fall back to team's hackathon title as proxy
        fallback_text = ""
        if hasattr(team, "hackathon") and team.hackathon:
            fallback_text = team.hackathon.title or ""
        if fallback_text:
            team_problem_embedding = embed_text(fallback_text)

    # ── 2. Fetch candidate pool (Users with profiles, excluding current members) ──
    conditions = []
    if member_ids:
        conditions.append(User.id.notin_(member_ids))
    if candidate_user_id is not None:
        conditions.append(User.id == candidate_user_id)

    users_stmt = (
        select(User)
        .options(
            selectinload(User.profile),
            selectinload(User.skills),
            selectinload(User.projects),
        )
    )
    if conditions:
        users_stmt = users_stmt.where(*conditions)

    users: list[User] = [
        u for u in (await db.execute(users_stmt)).scalars().all()
        if u.profile is not None and u.skills
    ]

    if not users:
        return []

    # Pre-load persisted embeddings (created on resume confirmation)
    emb_res = await db.execute(
        select(CandidateEmbedding).where(
            CandidateEmbedding.user_id.in_([u.id for u in users])
        )
    )
    embeddings: dict[UUID, dict[str, list[float]]] = {}
    for row in emb_res.scalars().all():
        embeddings.setdefault(row.user_id, {})[row.embedding_type] = list(row.vector)

    # Pre-compute the semantic anchor once (role vector preferred, else skill union)
    required_skills_embedding = embed_skills(required_skills) if required_skills else None
    role_embedding: list[float] | None = None
    if role is not None and role.role_embedding is not None:
        role_embedding = list(role.role_embedding)
    semantic_anchor = role_embedding or required_skills_embedding

    # ── 3. Score each candidate ───────────────────────────────────────
    matches: list[CandidateMatch] = []
    for user in users:
        breakdown = ScoreBreakdown()
        profile = user.profile
        candidate_skill_names: list[str] = [s.skill_name for s in user.skills]
        matched_skills: list[str] = []

        # Role-skill overlap
        if required_skills and candidate_skill_names:
            req_set = {s.lower() for s in required_skills}
            cand_set = {s.lower() for s in candidate_skill_names}
            overlap = req_set & cand_set
            matched_skills = [s for s in candidate_skill_names if s.lower() in overlap]
            breakdown.role_skill = min(len(overlap) / max(len(req_set), 1), 1.0)

        # Semantic skill similarity (prefer persisted resume-derived vector)
        user_embs = embeddings.get(user.id, {})
        stored_skill = user_embs.get("skills")
        stored_project = user_embs.get("projects")
        cand_skill_emb = (
            stored_skill if stored_skill is not None
            else embed_skills(candidate_skill_names)
        )
        if semantic_anchor:
            breakdown.semantic_skill = max(
                0.0, cosine_similarity_py(semantic_anchor, cand_skill_emb)
            )

        # Project ↔ Problem embedding similarity
        if team_problem_embedding:
            cand_proj_emb = (
                stored_project if stored_project is not None else cand_skill_emb
            )
            breakdown.project_problem = max(
                0.0, cosine_similarity_py(team_problem_embedding, cand_proj_emb)
            )

        # Experience match (use proficiency from first skill as proxy)
        if target_experience and user.skills:
            proficiency = user.skills[0].proficiency if user.skills else "intermediate"
            breakdown.experience = _experience_score(proficiency, target_experience)
        else:
            breakdown.experience = 0.5

        # Preference match
        breakdown.preference = _preference_score(profile, team)

        total = breakdown.total
        reasons = _build_reasons(breakdown, matched_skills)

        display_name = profile.display_name if profile else "Unknown"
        bio = profile.bio or "" if profile else ""

        matches.append(
            CandidateMatch(
                user_id=user.id,
                display_name=display_name,
                headline=bio[:100],
                avatar_url=None,
                score=round(total, 4),
                breakdown=breakdown,
                matched_skills=matched_skills,
                reasons=reasons,
            )
        )

    # ── 4. Sort descending by score ───────────────────────────────────
    matches.sort(key=lambda m: m.score, reverse=True)
    return matches[offset: offset + limit]


# ── Helpers ───────────────────────────────────────────────────────────────────

_EXP_ORDER = ["beginner", "junior", "intermediate", "mid", "senior", "lead", "principal"]


def _experience_score(candidate_level: str, required_level: str) -> float:
    """Score 1.0 for exact match, decays by distance in seniority ladder."""
    try:
        ci = _EXP_ORDER.index(candidate_level.lower())
        ri = _EXP_ORDER.index(required_level.lower())
        distance = abs(ci - ri)
        return max(0.0, 1.0 - distance * 0.25)
    except ValueError:
        return 0.5


def _preference_score(profile: UserProfile | None, team: Team) -> float:
    """Domain-interest overlap with the hackathon's themes.

    Neutral 0.5 when no signal is available; the remaining 0.5 is scaled by
    how much of the hackathon's domain set the candidate is interested in.
    """
    if profile is None:
        return 0.5

    hackathon = getattr(team, "hackathon", None)
    themes = {t.lower() for t in (getattr(hackathon, "themes", None) or [])}
    domains = {d.lower() for d in (profile.domains_of_interest or [])}
    if not themes or not domains:
        return 0.5

    overlap = len(themes & domains) / len(themes)
    return round(0.5 + 0.5 * overlap, 4)


def _build_reasons(
    breakdown: ScoreBreakdown,
    matched_skills: list[str],
) -> list[str]:
    reasons: list[str] = []
    if matched_skills:
        skills_str = ", ".join(matched_skills[:3])
        reasons.append(f"Matches required skills: {skills_str}")
    if breakdown.semantic_skill > 0.7:
        reasons.append("Strong semantic skill alignment")
    if breakdown.project_problem > 0.6:
        reasons.append("Project background aligns with team's problem domain")
    if breakdown.experience >= 0.75:
        reasons.append("Experience level is a strong fit")
    if not reasons:
        reasons.append("General profile match")
    return reasons
