"""
Human-readable match explanation generator.
Converts score breakdown into actionable match reasons.
"""

from __future__ import annotations

from app.ai.matching.engine import (
    WEIGHT_EXPERIENCE,
    WEIGHT_PREFERENCE,
    WEIGHT_PROJECT_PROBLEM,
    WEIGHT_ROLE_SKILL,
    WEIGHT_SEMANTIC_SKILL,
    CandidateMatch,
    ScoreBreakdown,
)


def explain_match(match: CandidateMatch) -> dict:
    """
    Returns a structured explanation dict for a CandidateMatch.
    """
    b = match.breakdown

    components = {
        "role_skill_match": {
            "score": round(b.role_skill, 3),
            "weight": WEIGHT_ROLE_SKILL,
            "weighted": round(b.role_skill * WEIGHT_ROLE_SKILL, 3),
            "label": _label(b.role_skill),
        },
        "semantic_skill": {
            "score": round(b.semantic_skill, 3),
            "weight": WEIGHT_SEMANTIC_SKILL,
            "weighted": round(b.semantic_skill * WEIGHT_SEMANTIC_SKILL, 3),
            "label": _label(b.semantic_skill),
        },
        "project_problem": {
            "score": round(b.project_problem, 3),
            "weight": WEIGHT_PROJECT_PROBLEM,
            "weighted": round(b.project_problem * WEIGHT_PROJECT_PROBLEM, 3),
            "label": _label(b.project_problem),
        },
        "experience": {
            "score": round(b.experience, 3),
            "weight": WEIGHT_EXPERIENCE,
            "weighted": round(b.experience * WEIGHT_EXPERIENCE, 3),
            "label": _label(b.experience),
        },
        "preference": {
            "score": round(b.preference, 3),
            "weight": WEIGHT_PREFERENCE,
            "weighted": round(b.preference * WEIGHT_PREFERENCE, 3),
            "label": _label(b.preference),
        },
    }

    return {
        "total_score": round(match.score, 4),
        "overall_label": _label(match.score),
        "matched_skills": match.matched_skills,
        "reasons": match.reasons,
        "components": components,
    }


def _label(score: float) -> str:
    if score >= 0.85:
        return "Excellent"
    if score >= 0.70:
        return "Strong"
    if score >= 0.50:
        return "Good"
    if score >= 0.30:
        return "Moderate"
    return "Weak"
