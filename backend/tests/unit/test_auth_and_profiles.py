import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_user_registration_and_login(async_client: AsyncClient):
    # Register user
    reg_resp = await async_client.post(
        "/api/v1/auth/register",
        json={
            "email": "alice@example.com",
            "password": "strongpassword123",
            "display_name": "Alice Developer",
        },
    )
    assert reg_resp.status_code == 201
    reg_data = reg_resp.json()
    assert reg_data["success"] is True
    token = reg_data["data"]["access_token"]
    assert token is not None

    # Duplicate registration fails
    dup_resp = await async_client.post(
        "/api/v1/auth/register",
        json={
            "email": "alice@example.com",
            "password": "strongpassword123",
            "display_name": "Alice Duplicate",
        },
    )
    assert dup_resp.status_code == 409

    # Login with valid credentials
    login_resp = await async_client.post(
        "/api/v1/auth/login",
        json={
            "email": "alice@example.com",
            "password": "strongpassword123",
        },
    )
    assert login_resp.status_code == 200
    assert login_resp.json()["data"]["email"] == "alice@example.com"

    # Login with invalid credentials
    bad_login = await async_client.post(
        "/api/v1/auth/login",
        json={
            "email": "alice@example.com",
            "password": "wrongpassword",
        },
    )
    assert bad_login.status_code == 401


@pytest.mark.asyncio
async def test_profile_management_crud(async_client: AsyncClient):
    # 1. Register Alice
    reg = await async_client.post(
        "/api/v1/auth/register",
        json={
            "email": "alice_profile@example.com",
            "password": "securepassword",
            "display_name": "Alice P",
        },
    )
    token = reg.json()["data"]["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # 2. Get profile
    me_resp = await async_client.get("/api/v1/profiles/me", headers=headers)
    assert me_resp.status_code == 200
    assert me_resp.json()["data"]["display_name"] == "Alice P"

    # 3. Update profile
    patch_resp = await async_client.patch(
        "/api/v1/profiles/me",
        headers=headers,
        json={
            "bio": "Full-stack engineer passionate about hackathons",
            "location": "Bengaluru, India",
            "domains_of_interest": ["AI", "Web3", "Mobile"],
            "roles_of_interest": ["Backend Engineer", "Team Lead"],
        },
    )
    assert patch_resp.status_code == 200
    assert patch_resp.json()["data"]["bio"] == "Full-stack engineer passionate about hackathons"
    assert "AI" in patch_resp.json()["data"]["domains_of_interest"]

    # 4. Add skill
    skill_resp = await async_client.post(
        "/api/v1/profiles/me/skills",
        headers=headers,
        json={
            "skill_name": "Python",
            "proficiency": "advanced",
            "evidence_source": "self_reported",
            "evidence_text": "3 years building FastAPI backends",
        },
    )
    assert skill_resp.status_code == 201
    skill_id = skill_resp.json()["data"]["id"]
    assert skill_resp.json()["data"]["normalized_skill"] == "python"

    # 5. Update skill
    patch_skill = await async_client.patch(
        f"/api/v1/profiles/me/skills/{skill_id}",
        headers=headers,
        json={"proficiency": "expert"},
    )
    assert patch_skill.status_code == 200
    assert patch_skill.json()["data"]["proficiency"] == "expert"

    # 6. Add project
    project_resp = await async_client.post(
        "/api/v1/profiles/me/projects",
        headers=headers,
        json={
            "name": "HackBubble Platform",
            "description": "Hackathon discovery and matchmaking service",
            "technologies": ["FastAPI", "PostgreSQL", "pgvector"],
            "visibility": "public",
        },
    )
    assert project_resp.status_code == 201
    project_id = project_resp.json()["data"]["id"]

    # 7. Add experience
    exp_resp = await async_client.post(
        "/api/v1/profiles/me/experience",
        headers=headers,
        json={
            "organization": "Open Source Initiative",
            "role": "Backend Contributor",
            "description": "Core contributor to open source frameworks",
            "is_current": True,
        },
    )
    assert exp_resp.status_code == 201
    exp_id = exp_resp.json()["data"]["id"]

    # 8. Add achievement
    ach_resp = await async_client.post(
        "/api/v1/profiles/me/achievements",
        headers=headers,
        json={
            "title": "First Place Hackathon Winner",
            "issuer": "Global AI Challenge",
        },
    )
    assert ach_resp.status_code == 201
    ach_id = ach_resp.json()["data"]["id"]

    # 9. Verify full profile has all sections
    full_profile = await async_client.get("/api/v1/profiles/me", headers=headers)
    p_data = full_profile.json()["data"]
    assert len(p_data["skills"]) == 1
    assert len(p_data["projects"]) == 1
    assert len(p_data["experience"]) == 1
    assert len(p_data["achievements"]) == 1

    # 10. Delete skill, project, experience, achievement
    del_s = await async_client.delete(f"/api/v1/profiles/me/skills/{skill_id}", headers=headers)
    assert del_s.status_code == 200
    del_p = await async_client.delete(f"/api/v1/profiles/me/projects/{project_id}", headers=headers)
    assert del_p.status_code == 200
    del_e = await async_client.delete(f"/api/v1/profiles/me/experience/{exp_id}", headers=headers)
    assert del_e.status_code == 200
    del_a = await async_client.delete(f"/api/v1/profiles/me/achievements/{ach_id}", headers=headers)
    assert del_a.status_code == 200

    # Verify cleared
    empty_profile = await async_client.get("/api/v1/profiles/me", headers=headers)
    assert len(empty_profile.json()["data"]["skills"]) == 0


@pytest.mark.asyncio
async def test_profile_privacy_rules(async_client: AsyncClient):
    # Register User A (private profile)
    reg_a = await async_client.post(
        "/api/v1/auth/register",
        json={"email": "private_user@example.com", "password": "password123", "display_name": "Private User"},
    )
    user_a_id = reg_a.json()["data"]["user_id"]
    token_a = reg_a.json()["data"]["access_token"]

    # Set profile to private
    await async_client.patch(
        "/api/v1/profiles/me",
        headers={"Authorization": f"Bearer {token_a}"},
        json={"profile_visibility": "private"},
    )

    # Register User B (viewer)
    reg_b = await async_client.post(
        "/api/v1/auth/register",
        json={"email": "viewer_b@example.com", "password": "password123", "display_name": "Viewer B"},
    )
    token_b = reg_b.json()["data"]["access_token"]

    # User B viewing User A's private profile receives 403 Forbidden
    forbidden_resp = await async_client.get(
        f"/api/v1/profiles/{user_a_id}",
        headers={"Authorization": f"Bearer {token_b}"},
    )
    assert forbidden_resp.status_code == 403

    # User A viewing own profile through public endpoint succeeds
    self_resp = await async_client.get(
        f"/api/v1/profiles/{user_a_id}",
        headers={"Authorization": f"Bearer {token_a}"},
    )
    assert self_resp.status_code == 200
    assert self_resp.json()["data"]["display_name"] == "Private User"
