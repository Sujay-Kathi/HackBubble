import uuid
import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession
from app.services.hackathon_service import HackathonService
from scraper.sources.mock import MockHackathonScraper


@pytest.mark.asyncio
async def test_full_team_formation_lifecycle(async_client: AsyncClient, test_db: AsyncSession):
    # 0. Ingest sample hackathon
    scraper = MockHackathonScraper()
    await HackathonService.run_scraper_and_ingest(test_db, scraper)

    h_list = await async_client.get("/api/v1/hackathons")
    hackathon_id = h_list.json()["data"][0]["id"]

    # 1. Register Leader & Candidate
    reg_leader = await async_client.post(
        "/api/v1/auth/register",
        json={"email": "leader@example.com", "password": "password123", "display_name": "Team Leader"},
    )
    leader_token = reg_leader.json()["data"]["access_token"]
    leader_id = reg_leader.json()["data"]["user_id"]
    leader_headers = {"Authorization": f"Bearer {leader_token}"}

    reg_cand = await async_client.post(
        "/api/v1/auth/register",
        json={"email": "candidate@example.com", "password": "password123", "display_name": "Candidate Bob"},
    )
    cand_token = reg_cand.json()["data"]["access_token"]
    cand_id = reg_cand.json()["data"]["user_id"]
    cand_headers = {"Authorization": f"Bearer {cand_token}"}

    # 2. Leader creates team with target_size=2 and 1 Frontend vacancy
    team_resp = await async_client.post(
        "/api/v1/teams",
        headers=leader_headers,
        json={
            "hackathon_id": hackathon_id,
            "name": "Team Alpha",
            "problem_statement": "Revolutionizing hackathon matchmaking with AI agents",
            "target_size": 2,
            "visibility": "public",
            "roles": [
                {
                    "role_name": "Frontend Developer",
                    "vacancy_count": 1,
                    "mandatory_skills": ["Flutter", "Dart"],
                    "preferred_skills": ["State Management"],
                }
            ],
            "preferences": {
                "time_commitment": "high",
                "collaboration_style": "agile",
            },
        },
    )
    assert team_resp.status_code == 201
    team_data = team_resp.json()["data"]
    team_id = team_data["id"]
    role_id = team_data["roles"][0]["id"]
    assert team_data["status"] == "draft"
    assert team_data["current_size"] == 1  # Leader is initial member

    # 3. Leader publishes team
    pub_resp = await async_client.post(f"/api/v1/teams/{team_id}/publish", headers=leader_headers)
    assert pub_resp.status_code == 200
    assert pub_resp.json()["data"]["status"] == "open"

    # 4. Team appears in discovery
    disc_resp = await async_client.get("/api/v1/teams/discover")
    assert disc_resp.status_code == 200
    assert len(disc_resp.json()["data"]) == 1

    # 5. Candidate applies for the role
    app_resp = await async_client.post(
        f"/api/v1/teams/{team_id}/applications",
        headers=cand_headers,
        json={"role_id": role_id, "message": "I have 2 years of Flutter experience!"},
    )
    assert app_resp.status_code == 201
    app_id = app_resp.json()["data"]["id"]
    assert app_resp.json()["data"]["status"] == "submitted"

    # Duplicate application rejected
    dup_app = await async_client.post(
        f"/api/v1/teams/{team_id}/applications",
        headers=cand_headers,
        json={"role_id": role_id, "message": "Applying again"},
    )
    assert dup_app.status_code == 409

    # 6. Leader shortlists candidate
    screen_resp = await async_client.post(
        f"/api/v1/teams/{team_id}/screening-actions",
        headers=leader_headers,
        json={
            "role_id": role_id,
            "candidate_id": cand_id,
            "action": "shortlist",
            "pass_id": 1,
        },
    )
    assert screen_resp.status_code == 200

    # 7. Candidate's application status is now shortlisted
    my_apps = await async_client.get("/api/v1/applications/me", headers=cand_headers)
    assert my_apps.status_code == 200
    assert my_apps.json()["data"][0]["status"] == "shortlisted"

    # 8. Candidate accepts invitation
    # Fetch team to get invitation
    from sqlalchemy import select
    from app.models.team import TeamInvitation
    inv_stmt = select(TeamInvitation).where(TeamInvitation.team_id == uuid.UUID(team_id))
    invitation = (await test_db.execute(inv_stmt)).scalar_one()

    accept_resp = await async_client.post(
        f"/api/v1/teams/{team_id}/invitations/{invitation.id}/respond",
        headers=cand_headers,
        json={"action": "accept"},
    )
    assert accept_resp.status_code == 200
    assert accept_resp.json()["data"]["status"] == "accepted"

    # Candidate is NOT an official member yet!
    team_pre_final = await async_client.get(f"/api/v1/teams/{team_id}")
    assert team_pre_final.json()["data"]["current_size"] == 1

    # 9. Leader finalizes team
    final_resp = await async_client.post(
        f"/api/v1/teams/{team_id}/finalize",
        headers=leader_headers,
        json={
            "selections": [
                {"candidate_id": cand_id, "role_id": role_id}
            ]
        },
    )
    assert final_resp.status_code == 200
    final_data = final_resp.json()["data"]
    assert final_data["team_status"] == "full"
    assert final_data["current_size"] == 2
    assert cand_id in [str(c) for c in final_data["finalized_candidates"]]

    # 10. Official membership is verified
    team_final = await async_client.get(f"/api/v1/teams/{team_id}")
    team_obj = team_final.json()["data"]
    assert team_obj["current_size"] == 2
    assert team_obj["status"] == "full"
    member_user_ids = [m["user_id"] for m in team_obj["members"]]
    assert leader_id in member_user_ids
    assert cand_id in member_user_ids
