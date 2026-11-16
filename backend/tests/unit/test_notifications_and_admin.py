"""
Phase 7 tests: notification service, notifications API, admin moderation, ops.
"""

from __future__ import annotations

import os
import uuid

import pytest
from httpx import AsyncClient
from sqlalchemy import select, update

from app.models.hackathon import Hackathon
from app.models.notification import Notification
from app.models.team import TeamInvitation
from app.models.user import User
from app.services import notification_service as svc
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


async def _create_open_team(
    client: AsyncClient,
    headers: dict[str, str],
    hackathon_id: str,
    name: str = "Notification Team",
) -> tuple[str, str]:
    resp = await client.post(
        "/api/v1/teams",
        headers=headers,
        json={
            "hackathon_id": hackathon_id,
            "name": name,
            "problem_statement": "Build an AI agent coordinator for hackathon teams",
            "target_size": 2,
            "visibility": "public",
            "roles": [
                {
                    "role_name": "Backend Engineer",
                    "vacancy_count": 1,
                    "mandatory_skills": ["Python"],
                }
            ],
        },
    )
    assert resp.status_code == 201, resp.text
    data = resp.json()["data"]
    published = await client.post(
        f"/api/v1/teams/{data['id']}/publish", headers=headers
    )
    assert published.status_code == 200, published.text
    return data["id"], data["roles"][0]["id"]


async def _notification_types(client: AsyncClient, headers: dict[str, str]) -> list[str]:
    resp = await client.get("/api/v1/notifications", headers=headers)
    assert resp.status_code == 200, resp.text
    return [item["type"] for item in resp.json()["items"]]


# ── Notification Service Unit Tests ──────────────────────────────────────────


@pytest.mark.asyncio
async def test_create_notification(test_db):
    """create_notification persists a Notification row."""
    user_id = uuid.uuid4()
    notif = await svc.create_notification(
        db=test_db,
        user_id=user_id,
        notif_type=svc.NOTIF_TEAM_FINALIZED,
        title="Team Finalized!",
        body="Your team has been finalized.",
        entity_type="team",
        entity_id=uuid.uuid4(),
    )
    await test_db.commit()

    result = await test_db.execute(
        select(Notification).where(Notification.id == notif.id)
    )
    persisted = result.scalar_one()
    assert persisted.type == svc.NOTIF_TEAM_FINALIZED
    assert persisted.title == "Team Finalized!"
    assert persisted.user_id == user_id


@pytest.mark.asyncio
async def test_notify_application_received(test_db):
    """notify_application_received creates correct notification for team leader."""
    leader_id = uuid.uuid4()

    await svc.notify_application_received(
        db=test_db,
        team_leader_id=leader_id,
        applicant_name="Bob",
        team_name="Team Alpha",
        team_id=uuid.uuid4(),
        application_id=uuid.uuid4(),
    )
    await test_db.commit()

    result = await test_db.execute(
        select(Notification).where(Notification.user_id == leader_id)
    )
    notif = result.scalar_one()
    assert notif.type == svc.NOTIF_APPLICATION_RECEIVED
    assert "Bob" in notif.body
    assert "Team Alpha" in notif.body


@pytest.mark.asyncio
async def test_notify_team_finalized_multiple_members(test_db):
    """notify_team_finalized creates one notification per member."""
    member_ids = [uuid.uuid4(), uuid.uuid4(), uuid.uuid4()]

    await svc.notify_team_finalized(
        db=test_db,
        member_ids=member_ids,
        team_name="Hack Warriors",
        team_id=uuid.uuid4(),
    )
    await test_db.commit()

    for mid in member_ids:
        result = await test_db.execute(
            select(Notification).where(Notification.user_id == mid)
        )
        notif = result.scalar_one()
        assert notif.type == svc.NOTIF_TEAM_FINALIZED
        assert "Hack Warriors" in notif.body


# ── Notifications API Tests ──────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_notification_read_flow(async_client: AsyncClient, test_db):
    user_id, headers = await _register(
        async_client, "notify_api@example.com", "Notify User"
    )

    for index in range(2):
        await svc.create_notification(
            db=test_db,
            user_id=uuid.UUID(user_id),
            notif_type=svc.NOTIF_APPLICATION_RECEIVED,
            title=f"Notice {index}",
            body="Body",
            entity_type="system",
        )
    await test_db.commit()

    listing = await async_client.get("/api/v1/notifications", headers=headers)
    assert listing.status_code == 200
    payload = listing.json()
    assert payload["total"] == 2
    assert payload["unread_count"] == 2

    first_id = payload["items"][0]["id"]
    read_resp = await async_client.patch(
        f"/api/v1/notifications/{first_id}/read", headers=headers
    )
    assert read_resp.status_code == 200
    assert read_resp.json()["read_at"] is not None

    listing = await async_client.get("/api/v1/notifications", headers=headers)
    assert listing.json()["unread_count"] == 1

    read_all = await async_client.patch(
        "/api/v1/notifications/read-all", headers=headers
    )
    assert read_all.status_code == 200

    listing = await async_client.get("/api/v1/notifications", headers=headers)
    assert listing.json()["unread_count"] == 0

    unread = await async_client.get(
        "/api/v1/notifications?unread_only=true", headers=headers
    )
    assert unread.json()["items"] == []


@pytest.mark.asyncio
async def test_team_workflow_emits_notifications(async_client: AsyncClient, test_db):
    await HackathonService.run_scraper_and_ingest(test_db, MockHackathonScraper())
    hackathon_id = str((await test_db.execute(select(Hackathon.id))).scalars().first())

    leader_id, leader_headers = await _register(
        async_client, "workflow_leader@example.com", "Workflow Leader"
    )
    candidate_id, candidate_headers = await _register(
        async_client, "workflow_candidate@example.com", "Workflow Candidate"
    )

    team_id, role_id = await _create_open_team(
        async_client, leader_headers, hackathon_id
    )

    # 1. Application notifies the leader
    apply_resp = await async_client.post(
        f"/api/v1/teams/{team_id}/applications",
        headers=candidate_headers,
        json={"role_id": role_id, "message": "I build FastAPI services."},
    )
    assert apply_resp.status_code == 201, apply_resp.text

    leader_types = await _notification_types(async_client, leader_headers)
    assert svc.NOTIF_APPLICATION_RECEIVED in leader_types

    # 2. Shortlisting notifies the candidate
    screen_resp = await async_client.post(
        f"/api/v1/teams/{team_id}/screening-actions",
        headers=leader_headers,
        json={
            "role_id": role_id,
            "candidate_id": candidate_id,
            "action": "shortlist",
            "pass_id": 1,
        },
    )
    assert screen_resp.status_code == 200, screen_resp.text

    candidate_types = await _notification_types(async_client, candidate_headers)
    assert svc.NOTIF_APPLICATION_SHORTLISTED in candidate_types

    # 3. Accepting the invitation notifies the leader
    invitation = (
        await test_db.execute(
            select(TeamInvitation).where(TeamInvitation.team_id == uuid.UUID(team_id))
        )
    ).scalar_one()

    accept_resp = await async_client.post(
        f"/api/v1/teams/{team_id}/invitations/{invitation.id}/respond",
        headers=candidate_headers,
        json={"action": "accept"},
    )
    assert accept_resp.status_code == 200, accept_resp.text

    leader_types = await _notification_types(async_client, leader_headers)
    assert svc.NOTIF_INVITATION_ACCEPTED in leader_types

    # 4. Finalization notifies every new member
    final_resp = await async_client.post(
        f"/api/v1/teams/{team_id}/finalize",
        headers=leader_headers,
        json={"selections": [{"candidate_id": candidate_id, "role_id": role_id}]},
    )
    assert final_resp.status_code == 200, final_resp.text
    assert str(final_resp.json()["data"]["current_size"]) == "2"

    candidate_types = await _notification_types(async_client, candidate_headers)
    assert svc.NOTIF_TEAM_FINALIZED in candidate_types


@pytest.mark.asyncio
async def test_withdrawal_emits_leader_notification(async_client: AsyncClient, test_db):
    await HackathonService.run_scraper_and_ingest(test_db, MockHackathonScraper())
    hackathon_id = str((await test_db.execute(select(Hackathon.id))).scalars().first())

    _, leader_headers = await _register(
        async_client, "withdraw_leader@example.com", "Withdraw Leader"
    )
    _, candidate_headers = await _register(
        async_client, "withdraw_candidate@example.com", "Withdraw Candidate"
    )

    team_id, role_id = await _create_open_team(
        async_client, leader_headers, hackathon_id, name="Withdraw Team"
    )

    apply_resp = await async_client.post(
        f"/api/v1/teams/{team_id}/applications",
        headers=candidate_headers,
        json={"role_id": role_id},
    )
    application_id = apply_resp.json()["data"]["id"]

    withdraw_resp = await async_client.post(
        f"/api/v1/applications/{application_id}/withdraw",
        headers=candidate_headers,
    )
    assert withdraw_resp.status_code == 200, withdraw_resp.text

    leader_types = await _notification_types(async_client, leader_headers)
    assert svc.NOTIF_APPLICATION_WITHDRAWN in leader_types


@pytest.mark.asyncio
async def test_rejection_emits_candidate_notification(async_client: AsyncClient, test_db):
    await HackathonService.run_scraper_and_ingest(test_db, MockHackathonScraper())
    hackathon_id = str((await test_db.execute(select(Hackathon.id))).scalars().first())

    _, leader_headers = await _register(
        async_client, "reject_leader@example.com", "Reject Leader"
    )
    candidate_id, candidate_headers = await _register(
        async_client, "reject_candidate@example.com", "Reject Candidate"
    )

    team_id, role_id = await _create_open_team(
        async_client, leader_headers, hackathon_id, name="Reject Team"
    )
    await async_client.post(
        f"/api/v1/teams/{team_id}/applications",
        headers=candidate_headers,
        json={"role_id": role_id},
    )

    reject_resp = await async_client.post(
        f"/api/v1/teams/{team_id}/screening-actions",
        headers=leader_headers,
        json={
            "role_id": role_id,
            "candidate_id": candidate_id,
            "action": "reject",
            "pass_id": 1,
        },
    )
    assert reject_resp.status_code == 200, reject_resp.text

    candidate_types = await _notification_types(async_client, candidate_headers)
    assert svc.NOTIF_APPLICATION_REJECTED in candidate_types


@pytest.mark.asyncio
async def test_declined_invitation_emits_leader_notification(
    async_client: AsyncClient, test_db
):
    await HackathonService.run_scraper_and_ingest(test_db, MockHackathonScraper())
    hackathon_id = str((await test_db.execute(select(Hackathon.id))).scalars().first())

    _, leader_headers = await _register(
        async_client, "decline_leader@example.com", "Decline Leader"
    )
    candidate_id, candidate_headers = await _register(
        async_client, "decline_candidate@example.com", "Decline Candidate"
    )

    team_id, role_id = await _create_open_team(
        async_client, leader_headers, hackathon_id, name="Decline Team"
    )
    await async_client.post(
        f"/api/v1/teams/{team_id}/applications",
        headers=candidate_headers,
        json={"role_id": role_id},
    )
    await async_client.post(
        f"/api/v1/teams/{team_id}/screening-actions",
        headers=leader_headers,
        json={
            "role_id": role_id,
            "candidate_id": candidate_id,
            "action": "shortlist",
            "pass_id": 1,
        },
    )

    invitation = (
        await test_db.execute(
            select(TeamInvitation).where(TeamInvitation.team_id == uuid.UUID(team_id))
        )
    ).scalar_one()

    decline_resp = await async_client.post(
        f"/api/v1/teams/{team_id}/invitations/{invitation.id}/respond",
        headers=candidate_headers,
        json={"action": "decline"},
    )
    assert decline_resp.status_code == 200, decline_resp.text

    leader_types = await _notification_types(async_client, leader_headers)
    assert svc.NOTIF_INVITATION_DECLINED in leader_types


# ── Admin API Tests ──────────────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_admin_moderation_flow(async_client: AsyncClient, test_db):
    await HackathonService.run_scraper_and_ingest(test_db, MockHackathonScraper())
    admin_id, headers = await _register(async_client, "admin@example.com", "Admin User")
    _, non_admin_headers = await _register(
        async_client, "non_admin@example.com", "Non Admin"
    )

    # A regular authenticated user is forbidden, not merely unauthenticated
    forbidden = await async_client.get(
        "/api/v1/admin/hackathons", headers=non_admin_headers
    )
    assert forbidden.status_code == 403

    # Promote the account (in production this is a manual/ops action)
    await test_db.execute(
        update(User).where(User.id == uuid.UUID(admin_id)).values(is_admin=True)
    )
    await test_db.commit()

    runs = await async_client.get("/api/v1/admin/scraper/runs", headers=headers)
    assert runs.status_code == 200
    assert runs.json()[0]["total_records"] == 2

    listing = await async_client.get("/api/v1/admin/hackathons", headers=headers)
    assert listing.status_code == 200
    hackathons = listing.json()
    assert len(hackathons) == 2
    assert all(item["is_verified"] is False for item in hackathons)

    target_id = hackathons[0]["id"]
    approve = await async_client.post(
        f"/api/v1/admin/hackathons/{target_id}/moderate",
        headers=headers,
        json={"action": "approve", "reason": "Looks legitimate"},
    )
    assert approve.status_code == 200, approve.text

    unverified = await async_client.get(
        "/api/v1/admin/hackathons?unverified_only=true", headers=headers
    )
    assert len(unverified.json()) == 1

    reject = await async_client.post(
        f"/api/v1/admin/hackathons/{target_id}/moderate",
        headers=headers,
        json={"action": "reject"},
    )
    assert reject.status_code == 200

    unverified = await async_client.get(
        "/api/v1/admin/hackathons?unverified_only=true", headers=headers
    )
    assert len(unverified.json()) == 2

    invalid = await async_client.post(
        f"/api/v1/admin/hackathons/{target_id}/moderate",
        headers=headers,
        json={"action": "delete"},
    )
    assert invalid.status_code == 400


# ── Authorization & Production Readiness ────────────────────────────────────


@pytest.mark.asyncio
async def test_protected_endpoints_require_auth(async_client: AsyncClient):
    team_id = uuid.uuid4()
    user_id = uuid.uuid4()
    requests = [
        ("GET", "/api/v1/notifications"),
        ("PATCH", "/api/v1/notifications/read-all"),
        ("GET", "/api/v1/admin/scraper/runs"),
        ("GET", "/api/v1/admin/hackathons"),
        ("GET", f"/api/v1/teams/{team_id}/candidates"),
        ("GET", f"/api/v1/teams/{team_id}/candidates/{user_id}"),
    ]
    for method, path in requests:
        resp = await async_client.request(method, path)
        assert resp.status_code == 401, f"{method} {path} -> {resp.status_code}"


def test_dockerfile_exists():
    """Dockerfile exists in backend directory."""
    dockerfile = os.path.join(os.path.dirname(__file__), "..", "..", "Dockerfile")
    assert os.path.isfile(os.path.normpath(dockerfile)), "Dockerfile not found"


def test_docker_compose_exists():
    """docker-compose.yml exists in repo root."""
    compose = os.path.join(os.path.dirname(__file__), "..", "..", "..", "docker-compose.yml")
    assert os.path.isfile(os.path.normpath(compose)), "docker-compose.yml not found"
