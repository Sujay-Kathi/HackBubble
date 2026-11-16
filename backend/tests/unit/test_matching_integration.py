"""
Phase 6 integration tests: embedding persistence, candidate queue, and explanations.
"""

from __future__ import annotations

import uuid

import pytest
from httpx import AsyncClient
from sqlalchemy import select

from app.models.hackathon import Hackathon
from app.models.resume import CandidateEmbedding
from app.models.team import TeamIntelligence
from app.services.hackathon_service import HackathonService
from scraper.sources.mock import MockHackathonScraper


async def _register(
    client: AsyncClient, email: str, display_name: str
) -> tuple[str, dict[str, str]]:
    resp = await client.post(
        "/api/v1/auth/register",
        json={
            "email": email,
            "password": "password123",
            "display_name": display_name,
        },
    )
    assert resp.status_code == 201, resp.text
    data = resp.json()["data"]
    return data["user_id"], {"Authorization": f"Bearer {data['access_token']}"}


async def _seed_hackathon(test_db) -> str:
    await HackathonService.run_scraper_and_ingest(test_db, MockHackathonScraper())
    result = await test_db.execute(
        select(Hackathon).where(Hackathon.source_event_id == "mock-event-101")
    )
    return str(result.scalar_one().id)


async def _create_open_team(
    client: AsyncClient, headers: dict[str, str], hackathon_id: str
) -> tuple[str, str]:
    resp = await client.post(
        "/api/v1/teams",
        headers=headers,
        json={
            "hackathon_id": hackathon_id,
            "name": "Matching Team",
            "problem_statement": (
                "Build a multi-agent AI coordinator that plans hackathon work"
            ),
            "project_idea": "Autonomous agents coordinating team tasks",
            "target_size": 3,
            "visibility": "public",
            "roles": [
                {
                    "role_name": "Backend Engineer",
                    "vacancy_count": 1,
                    "mandatory_skills": ["Python", "FastAPI"],
                    "experience_level": "intermediate",
                }
            ],
        },
    )
    assert resp.status_code == 201, resp.text
    data = resp.json()["data"]
    await client.post(f"/api/v1/teams/{data['id']}/publish", headers=headers)
    return data["id"], data["roles"][0]["id"]


async def _add_candidate_profile(
    client: AsyncClient,
    headers: dict[str, str],
    skill: str,
    domain: str,
    project_name: str,
) -> None:
    await client.patch(
        "/api/v1/profiles/me",
        headers=headers,
        json={"domains_of_interest": [domain]},
    )
    await client.post(
        "/api/v1/profiles/me/skills",
        headers=headers,
        json={"skill_name": skill, "proficiency": "advanced"},
    )
    await client.post(
        "/api/v1/profiles/me/projects",
        headers=headers,
        json={
            "name": project_name,
            "description": "AI agent orchestration service for hackathon teams",
            "technologies": [skill, "Docker"],
        },
    )


@pytest.mark.asyncio
async def test_team_creation_persists_problem_embedding(
    async_client: AsyncClient, test_db
):
    hackathon_id = await _seed_hackathon(test_db)
    _, headers = await _register(
        async_client, "embedding_leader@example.com", "Embedding Leader"
    )
    team_id, _ = await _create_open_team(async_client, headers, hackathon_id)

    intel = (
        await test_db.execute(
            select(TeamIntelligence).where(
                TeamIntelligence.team_id == uuid.UUID(team_id)
            )
        )
    ).scalar_one()
    assert intel.problem_embedding is not None
    assert len(intel.problem_embedding) == 384
    assert intel.model_version


@pytest.mark.asyncio
async def test_candidate_queue_and_explanation(async_client: AsyncClient, test_db):
    hackathon_id = await _seed_hackathon(test_db)

    leader_id, leader_headers = await _register(
        async_client, "match_leader@example.com", "Match Leader"
    )
    python_id, python_headers = await _register(
        async_client, "python_candidate@example.com", "Python Candidate"
    )
    rust_id, rust_headers = await _register(
        async_client, "rust_candidate@example.com", "Rust Candidate"
    )

    await _add_candidate_profile(
        async_client,
        python_headers,
        skill="Python",
        domain="Artificial Intelligence",
        project_name="Agent Coordinator",
    )
    await _add_candidate_profile(
        async_client,
        rust_headers,
        skill="Rust",
        domain="Blockchain",
        project_name="Ledger Toolkit",
    )

    team_id, role_id = await _create_open_team(
        async_client, leader_headers, hackathon_id
    )

    # Ranked queue: the Python/FastAPI candidate should outrank the Rust candidate
    queue = await async_client.get(
        f"/api/v1/teams/{team_id}/candidates", headers=leader_headers
    )
    assert queue.status_code == 200, queue.text
    payload = queue.json()
    assert payload["team_id"] == team_id
    candidates = payload["candidates"]
    assert len(candidates) == 2
    assert candidates[0]["user_id"] == python_id
    assert candidates[0]["score"] > 0

    top = candidates[0]
    assert "Python" in top["explanation"]["matched_skills"]
    assert len(top["explanation"]["components"]) == 5
    assert top["explanation"]["overall_label"] in {
        "Excellent",
        "Strong",
        "Good",
        "Moderate",
        "Weak",
    }
    assert top["explanation"]["reasons"]

    # Role-scoped queue works
    scoped = await async_client.get(
        f"/api/v1/teams/{team_id}/candidates?role_id={role_id}",
        headers=leader_headers,
    )
    assert scoped.status_code == 200
    assert scoped.json()["role_id"] == role_id

    # Single-candidate explanation endpoint
    detail = await async_client.get(
        f"/api/v1/teams/{team_id}/candidates/{python_id}", headers=leader_headers
    )
    assert detail.status_code == 200, detail.text
    assert detail.json()["user_id"] == python_id
    assert detail.json()["explanation"]["total_score"] == top["score"]

    # Unknown candidate -> 404
    missing = await async_client.get(
        f"/api/v1/teams/{team_id}/candidates/{uuid.uuid4()}", headers=leader_headers
    )
    assert missing.status_code == 404

    # Non-member cannot inspect the candidate pool
    outsider = await async_client.get(
        f"/api/v1/teams/{team_id}/candidates", headers=rust_headers
    )
    assert outsider.status_code == 403


@pytest.mark.asyncio
async def test_profile_skill_edits_refresh_embedding(
    async_client: AsyncClient, test_db
):
    user_id, headers = await _register(
        async_client, "refresh_user@example.com", "Refresh User"
    )

    await async_client.post(
        "/api/v1/profiles/me/skills",
        headers=headers,
        json={"skill_name": "Python", "proficiency": "advanced"},
    )

    def vectors():
        return select(CandidateEmbedding).where(
            CandidateEmbedding.user_id == uuid.UUID(user_id)
        )

    rows = (await test_db.execute(vectors())).scalars().all()
    by_type = {row.embedding_type: row for row in rows}
    assert set(by_type) == {"skills", "projects"}
    first_skill_vector = list(by_type["skills"].vector)

    await async_client.post(
        "/api/v1/profiles/me/skills",
        headers=headers,
        json={"skill_name": "Rust", "proficiency": "intermediate"},
    )
    await test_db.commit()

    rows = (await test_db.execute(vectors())).scalars().all()
    updated = {row.embedding_type: row for row in rows}
    assert list(updated["skills"].vector) != first_skill_vector


@pytest.mark.asyncio
async def test_candidate_queue_empty_for_draft_team(
    async_client: AsyncClient, test_db
):
    hackathon_id = await _seed_hackathon(test_db)
    _, headers = await _register(
        async_client, "draft_leader@example.com", "Draft Leader"
    )
    _, candidate_headers = await _register(
        async_client, "draft_candidate@example.com", "Draft Candidate"
    )
    await _add_candidate_profile(
        async_client,
        candidate_headers,
        skill="Python",
        domain="Artificial Intelligence",
        project_name="Draft Project",
    )

    resp = await async_client.post(
        "/api/v1/teams",
        headers=headers,
        json={
            "hackathon_id": hackathon_id,
            "name": "Draft Team",
            "problem_statement": "Keep this team in draft",
            "target_size": 2,
            "roles": [{"role_name": "Backend", "vacancy_count": 1}],
        },
    )
    team_id = resp.json()["data"]["id"]

    queue = await async_client.get(
        f"/api/v1/teams/{team_id}/candidates", headers=headers
    )
    assert queue.status_code == 200
    assert queue.json()["candidates"] == []
    assert queue.json()["total_scored"] == 0
