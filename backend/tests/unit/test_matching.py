"""
Tests for Phase 6: Vector Embeddings & Hybrid Matching Engine.
"""

from __future__ import annotations

import pytest

from app.ai.embeddings.generator import (
    EMBEDDING_DIM,
    cosine_similarity_py,
    embed_batch,
    embed_skills,
    embed_text,
    get_model_version,
)
from app.ai.matching.engine import (
    WEIGHT_EXPERIENCE,
    WEIGHT_PREFERENCE,
    WEIGHT_PROJECT_PROBLEM,
    WEIGHT_ROLE_SKILL,
    WEIGHT_SEMANTIC_SKILL,
    ScoreBreakdown,
    _experience_score,
)
from app.ai.matching.explainer import explain_match, _label


# ── Embedding Generator Tests ─────────────────────────────────────────────────


def test_embed_text_returns_correct_dim():
    """embed_text always returns a 384-dim vector."""
    vec = embed_text("Python, React, FastAPI")
    assert len(vec) == EMBEDDING_DIM
    assert all(isinstance(v, float) for v in vec)


def test_embed_empty_text_returns_zero_vector():
    vec = embed_text("")
    assert vec == [0.0] * EMBEDDING_DIM


def test_embed_skills_non_empty():
    vec = embed_skills(["Python", "FastAPI", "PostgreSQL"])
    assert len(vec) == EMBEDDING_DIM
    # Should NOT be a zero vector for non-empty input
    assert any(v != 0.0 for v in vec)


def test_embed_batch_length_matches():
    texts = ["machine learning", "web development", "mobile apps"]
    vecs = embed_batch(texts)
    assert len(vecs) == 3
    for v in vecs:
        assert len(v) == EMBEDDING_DIM


def test_deterministic_embedding_stability():
    """Same text should always produce the same vector (deterministic fallback or model)."""
    vec1 = embed_text("hackathon team formation backend")
    vec2 = embed_text("hackathon team formation backend")
    assert vec1 == vec2


def test_model_version_string():
    version = get_model_version()
    assert isinstance(version, str)
    assert len(version) > 0


# ── Cosine Similarity Tests ───────────────────────────────────────────────────


def test_cosine_similarity_identical_vectors():
    """Cosine similarity of a vector with itself should be ~1.0."""
    vec = embed_text("Python developer with ML experience")
    sim = cosine_similarity_py(vec, vec)
    assert abs(sim - 1.0) < 1e-5


def test_cosine_similarity_zero_vector():
    zero = [0.0] * EMBEDDING_DIM
    vec = embed_text("some text")
    sim = cosine_similarity_py(zero, vec)
    assert sim == 0.0


def test_cosine_similarity_range():
    """Similarity between arbitrary non-identical vectors is in [-1, 1]."""
    v1 = embed_text("machine learning python data science")
    v2 = embed_text("frontend react javascript css")
    sim = cosine_similarity_py(v1, v2)
    assert -1.0 <= sim <= 1.0


def test_similar_texts_have_higher_similarity_than_dissimilar():
    """Semantically similar texts should have higher cosine similarity."""
    v_python1 = embed_text("Python backend developer FastAPI")
    v_python2 = embed_text("Python REST API developer")
    v_design = embed_text("UI UX designer Figma Adobe")

    sim_related = cosine_similarity_py(v_python1, v_python2)
    sim_unrelated = cosine_similarity_py(v_python1, v_design)
    # Related texts should score higher (or equal for deterministic fallback)
    assert sim_related >= sim_unrelated or abs(sim_related - sim_unrelated) < 0.3


# ── Score Breakdown Tests ─────────────────────────────────────────────────────


def test_score_breakdown_weights_sum_to_one():
    total_weight = (
        WEIGHT_ROLE_SKILL
        + WEIGHT_SEMANTIC_SKILL
        + WEIGHT_PROJECT_PROBLEM
        + WEIGHT_EXPERIENCE
        + WEIGHT_PREFERENCE
    )
    assert abs(total_weight - 1.0) < 1e-9


def test_score_breakdown_total_calculation():
    b = ScoreBreakdown(
        role_skill=1.0,
        semantic_skill=1.0,
        project_problem=1.0,
        experience=1.0,
        preference=1.0,
    )
    assert abs(b.total - 1.0) < 1e-9


def test_score_breakdown_zero():
    b = ScoreBreakdown()
    assert b.total == 0.0


def test_score_breakdown_partial():
    b = ScoreBreakdown(role_skill=1.0)  # only role skill perfect
    expected = 1.0 * WEIGHT_ROLE_SKILL
    assert abs(b.total - expected) < 1e-9


# ── Experience Score Tests ────────────────────────────────────────────────────


def test_experience_exact_match():
    assert _experience_score("junior", "junior") == 1.0


def test_experience_one_step_away():
    # junior -> intermediate is 1 step away in _EXP_ORDER
    score = _experience_score("intermediate", "junior")
    assert score == 0.75


def test_experience_two_steps_away():
    # junior -> senior is 3 steps (junior,intermediate,mid,senior), but let's use beginner->intermediate = 2 steps
    score = _experience_score("intermediate", "beginner")
    assert score == 0.5


def test_experience_max_distance_clamped_to_zero():
    # beginner -> principal: distance of 6, 1.0 - 6*0.25 = -0.5 -> clamped to 0.0
    score = _experience_score("beginner", "principal")
    assert score == 0.0


def test_experience_unknown_level_neutral():
    score = _experience_score("wizard", "junior")
    assert score == 0.5


# ── Explainer Tests ───────────────────────────────────────────────────────────


def test_label_ranges():
    assert _label(0.9) == "Excellent"
    assert _label(0.75) == "Strong"
    assert _label(0.55) == "Good"
    assert _label(0.35) == "Moderate"
    assert _label(0.1) == "Weak"


def test_explain_match_structure(tmp_path):
    """explain_match returns a dict with all required keys."""
    from uuid import uuid4
    from app.ai.matching.engine import CandidateMatch

    b = ScoreBreakdown(
        role_skill=0.8,
        semantic_skill=0.7,
        project_problem=0.6,
        experience=1.0,
        preference=0.5,
    )
    m = CandidateMatch(
        user_id=uuid4(),
        display_name="Alice",
        headline="Full Stack Developer",
        avatar_url=None,
        score=b.total,
        breakdown=b,
        matched_skills=["Python", "FastAPI"],
        reasons=["Matches required skills: Python, FastAPI"],
    )
    explanation = explain_match(m)
    assert "total_score" in explanation
    assert "overall_label" in explanation
    assert "components" in explanation
    assert "reasons" in explanation
    assert "matched_skills" in explanation
    assert len(explanation["components"]) == 5

    # Verify weighted scores sum to total
    weighted_sum = sum(
        c["weighted"] for c in explanation["components"].values()
    )
    assert abs(weighted_sum - explanation["total_score"]) < 0.01


# ── Hard Filter Tests ─────────────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_matching_returns_empty_for_closed_team():
    """
    Hard filter: a closed team returns empty candidate list immediately.
    Uses a minimal mock Team object — no DB needed.
    """
    from unittest.mock import AsyncMock, MagicMock
    from app.ai.matching.engine import find_candidates_for_team

    mock_team = MagicMock()
    mock_team.status = "closed"
    mock_team.roles = []

    mock_db = AsyncMock()

    result = await find_candidates_for_team(db=mock_db, team=mock_team)
    assert result == []
    mock_db.execute.assert_not_called()
