"""
Phase 8 tests: catalog/team filters, role management, scraper registry,
audit logging, notification delivery, workers, CLI, and rate limiting.
"""

from __future__ import annotations

import uuid

import pymupdf
import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import async_sessionmaker
from starlette.applications import Starlette
from starlette.responses import JSONResponse
from starlette.routing import Route

from app.middleware.rate_limit import RateLimitMiddleware, SlidingWindowLimiter
from app import cli
from app.models.hackathon import Hackathon, HackathonSource
from app.models.notification import AuditLog, NotificationDelivery
from app.models.resume import CandidateEmbedding
from app.models.team import TeamIntelligence, TeamRole
from app.models.user import User
from app.services import delivery_service
from app.services import notification_service as notif
from app.services.embedding_service import backfill_missing_embeddings
from app.services.hackathon_service import HackathonService
from app.workers import scheduler
from scraper.registry import available_adapters, get_scraper
from scraper.sources.mock import MockHackathonScraper


# ── Helpers ─────────────────────────────────────────────────────────────────


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


async def _promote_admin(test_db, user_id: str) -> None:
    await test_db.execute(
        update(User).where(User.id == uuid.UUID(user_id)).values(is_admin=True)
    )
    await test_db.commit()


async def _create_team(
    client: AsyncClient,
    headers: dict[str, str],
    hackathon_id: str,
    *,
    name: str = "Discovery Team",
    role_name: str = "Backend Engineer",
    skills: list[str] | None = None,
    beginner_friendly: bool = True,
    publish: bool = True,
) -> tuple[str, str]:
    payload = {
        "hackathon_id": hackathon_id,
        "name": name,
        "problem_statement": "Build an AI assistant for hackathon team formation",
        "target_size": 3,
        "visibility": "public",
        "roles": [
            {
                "role_name": role_name,
                "vacancy_count": 1,
                "mandatory_skills": skills or ["Python"],
            }
        ],
        "preferences": {
            "beginner_friendly": beginner_friendly,
            "time_commitment": "flexible",
        },
    }
    resp = await client.post("/api/v1/teams", headers=headers, json=payload)
    assert resp.status_code == 201, resp.text
    data = resp.json()["data"]
    if publish:
        published = await client.post(
            f"/api/v1/teams/{data['id']}/publish", headers=headers
        )
        assert published.status_code == 200, published.text
    return data["id"], data["roles"][0]["id"]


# ── Catalog filters ─────────────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_hackathon_theme_filter(async_client: AsyncClient, test_db):
    await _seed_hackathon(test_db)

    all_resp = await async_client.get("/api/v1/hackathons")
    assert all_resp.status_code == 200
    assert all_resp.json()["pagination"]["total_items"] == 2

    resp = await async_client.get("/api/v1/hackathons", params={"theme": "blockchain"})
    assert resp.status_code == 200
    payload = resp.json()
    assert payload["pagination"]["total_items"] == 1
    assert "Web3" in payload["data"][0]["title"]

    empty = await async_client.get(
        "/api/v1/hackathons", params={"theme": "does-not-exist"}
    )
    assert empty.json()["pagination"]["total_items"] == 0
    assert empty.json()["data"] == []


# ── Team discovery filters ─────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_team_discovery_filters(async_client: AsyncClient, test_db):
    hackathon_id = await _seed_hackathon(test_db)
    _, leader_a = await _register(async_client, "disc_a@example.com", "Leader A")
    _, leader_b = await _register(async_client, "disc_b@example.com", "Leader B")
    _, leader_c = await _register(async_client, "disc_c@example.com", "Leader C")

    team_a, _ = await _create_team(
        async_client,
        leader_a,
        hackathon_id,
        name="Team Alpha",
        role_name="Backend Engineer",
        skills=["Python"],
        beginner_friendly=True,
    )
    team_b, _ = await _create_team(
        async_client,
        leader_b,
        hackathon_id,
        name="Team Beta",
        role_name="Frontend Designer",
        skills=["Figma"],
        beginner_friendly=False,
    )
    team_c, _ = await _create_team(
        async_client,
        leader_c,
        hackathon_id,
        name="Team Gamma",
        role_name="Backend Engineer",
        skills=["Rust"],
        beginner_friendly=True,
    )

    async def discover(**params) -> list[str]:
        resp = await async_client.get("/api/v1/teams/discover", params=params)
        assert resp.status_code == 200, resp.text
        return [t["id"] for t in resp.json()["data"]]

    assert set(await discover(role_name="backend")) == {team_a, team_c}
    assert await discover(skill="figma") == [team_b]
    assert await discover(beginner_friendly="false") == [team_b]
    assert await discover(role_name="backend", skill="rust") == [team_c]


# ── Team/role management ───────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_update_team_refreshes_problem_embedding(
    async_client: AsyncClient, test_db
):
    hackathon_id = await _seed_hackathon(test_db)
    _, headers = await _register(async_client, "embed_edit@example.com", "Embed Editor")
    team_id, _ = await _create_team(async_client, headers, hackathon_id)

    def current_vector():
        return select(TeamIntelligence).where(
            TeamIntelligence.team_id == uuid.UUID(team_id)
        )

    before = list((await test_db.execute(current_vector())).scalar_one().problem_embedding)

    update = await async_client.patch(
        f"/api/v1/teams/{team_id}",
        headers=headers,
        json={"problem_statement": "Design blockchain supply-chain attestations"},
    )
    assert update.status_code == 200, update.text

    await test_db.commit()
    after = list((await test_db.execute(current_vector())).scalar_one().problem_embedding)
    assert after != before


@pytest.mark.asyncio
async def test_role_update_delete_and_guards(async_client: AsyncClient, test_db):
    hackathon_id = await _seed_hackathon(test_db)
    _, leader = await _register(async_client, "role_leader@example.com", "Role Leader")
    _, outsider = await _register(async_client, "role_outsider@example.com", "Outsider")
    _, candidate = await _register(async_client, "role_candidate@example.com", "Cand")
    team_id, role_id = await _create_team(async_client, leader, hackathon_id)

    forbidden = await async_client.patch(
        f"/api/v1/teams/{team_id}/roles/{role_id}",
        headers=outsider,
        json={"role_name": "Hijacked"},
    )
    assert forbidden.status_code == 403

    updated = await async_client.patch(
        f"/api/v1/teams/{team_id}/roles/{role_id}",
        headers=leader,
        json={"role_name": "Senior Backend Engineer", "mandatory_skills": ["Go"]},
    )
    assert updated.status_code == 200, updated.text
    assert updated.json()["data"]["role_name"] == "Senior Backend Engineer"
    assert updated.json()["data"]["mandatory_skills"] == ["Go"]

    await test_db.commit()
    role = (
        await test_db.execute(select(TeamRole).where(TeamRole.id == uuid.UUID(role_id)))
    ).scalar_one()
    assert role.role_embedding is not None

    extra = await async_client.post(
        f"/api/v1/teams/{team_id}/roles",
        headers=leader,
        json={"role_name": "Designer", "vacancy_count": 1},
    )
    extra_id = extra.json()["data"]["id"]

    deleted = await async_client.delete(
        f"/api/v1/teams/{team_id}/roles/{extra_id}", headers=leader
    )
    assert deleted.status_code == 200, deleted.text

    # A role with an application cannot be deleted
    await async_client.post(
        f"/api/v1/teams/{team_id}/applications",
        headers=candidate,
        json={"role_id": role_id},
    )
    blocked = await async_client.delete(
        f"/api/v1/teams/{team_id}/roles/{role_id}", headers=leader
    )
    assert blocked.status_code == 409


# ── Scraper registry & admin ops ───────────────────────────────────────────


def test_scraper_registry_resolves_adapters():
    assert {"mock_adapter", "devfolio"} <= set(available_adapters())
    assert get_scraper("mock_adapter").adapter_key == "mock_adapter"

    with pytest.raises(KeyError):
        get_scraper("missing-adapter")


@pytest.mark.asyncio
async def test_admin_scraper_trigger_and_audit(async_client: AsyncClient, test_db):
    admin_id, admin_headers = await _register(
        async_client, "ops_admin@example.com", "Ops Admin"
    )
    _, regular_headers = await _register(
        async_client, "ops_regular@example.com", "Regular"
    )
    await _promote_admin(test_db, admin_id)

    # Regular users are blocked on both trigger paths
    for path in (
        "/api/v1/admin/scraper/trigger",
        "/api/v1/hackathons/admin/scrape-trigger",
    ):
        resp = await async_client.post(path, headers=regular_headers)
        assert resp.status_code == 403

    adapters = await async_client.get(
        "/api/v1/admin/scraper/adapters", headers=admin_headers
    )
    assert adapters.status_code == 200
    assert "mock_adapter" in adapters.json()

    unknown = await async_client.post(
        "/api/v1/admin/scraper/trigger",
        params={"adapter_key": "nope"},
        headers=admin_headers,
    )
    assert unknown.status_code == 400

    triggered = await async_client.post(
        "/api/v1/hackathons/admin/scrape-trigger",
        params={"adapter_key": "mock_adapter"},
        headers=admin_headers,
    )
    assert triggered.status_code == 200, triggered.text
    assert triggered.json()["data"]["events_created"] == 2

    admin_triggered = await async_client.post(
        "/api/v1/admin/scraper/trigger",
        params={"adapter_key": "mock_adapter"},
        headers=admin_headers,
    )
    assert admin_triggered.status_code == 200, admin_triggered.text
    assert admin_triggered.json()["events_updated"] == 2

    runs = await async_client.get("/api/v1/admin/scraper/runs", headers=admin_headers)
    assert runs.status_code == 200
    assert len(runs.json()) == 2
    assert all(run["status"] == "completed" for run in runs.json())

    await test_db.commit()
    audit_rows = (
        await test_db.execute(select(AuditLog).where(AuditLog.action == "scraper.run"))
    ).scalars().all()
    assert len(audit_rows) == 1
    assert audit_rows[0].actor_id == uuid.UUID(admin_id)
    assert audit_rows[0].metadata_json["events_found"] == 2

    logs = await async_client.get(
        "/api/v1/admin/audit-logs",
        params={"action": "scraper.run"},
        headers=admin_headers,
    )
    assert logs.status_code == 200
    assert len(logs.json()) == 1
    assert logs.json()[0]["entity_type"] == "scraper_adapter"

    stats = await async_client.get(
        "/api/v1/admin/notifications/deliveries", headers=admin_headers
    )
    assert stats.status_code == 200
    assert isinstance(stats.json(), dict)


@pytest.mark.asyncio
async def test_moderation_writes_audit_log(async_client: AsyncClient, test_db):
    await _seed_hackathon(test_db)
    admin_id, admin_headers = await _register(
        async_client, "audit_admin@example.com", "Audit Admin"
    )
    await _promote_admin(test_db, admin_id)

    listing = await async_client.get(
        "/api/v1/admin/hackathons", headers=admin_headers
    )
    hackathon_id = listing.json()[0]["id"]

    approve = await async_client.post(
        f"/api/v1/admin/hackathons/{hackathon_id}/moderate",
        headers=admin_headers,
        json={"action": "approve", "reason": "verified source"},
    )
    assert approve.status_code == 200, approve.text

    await test_db.commit()
    entries = (
        await test_db.execute(
            select(AuditLog).where(AuditLog.action == "hackathon.approve")
        )
    ).scalars().all()
    assert len(entries) == 1
    assert entries[0].metadata_json["reason"] == "verified source"


# ── Notification delivery ──────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_notification_queues_email_delivery(async_client: AsyncClient, test_db):
    user_id, _ = await _register(async_client, "queued@example.com", "Queued User")

    created = await notif.create_notification(
        db=test_db,
        user_id=uuid.UUID(user_id),
        notif_type=notif.NOTIF_TEAM_FINALIZED,
        title="Season ready",
        body="Your team is set.",
        entity_type="team",
        entity_id=uuid.uuid4(),
    )
    await test_db.commit()

    rows = (
        await test_db.execute(
            select(NotificationDelivery).where(
                NotificationDelivery.notification_id == created.id
            )
        )
    ).scalars().all()
    assert len(rows) == 1
    assert rows[0].provider == "email"
    assert rows[0].status == "queued"


@pytest.mark.asyncio
async def test_dispatch_pending_deliveries(monkeypatch, async_client: AsyncClient, test_db):
    user_id, _ = await _register(async_client, "dispatch@example.com", "Dispatch User")
    created = await notif.create_notification(
        db=test_db,
        user_id=uuid.UUID(user_id),
        notif_type=notif.NOTIF_TEAM_FINALIZED,
        title="Dispatch me",
        body="Delivery body",
        entity_type="team",
    )
    await test_db.commit()

    sent: list[tuple[str, str]] = []

    async def fake_send(to_email: str, subject: str, body: str) -> str:
        sent.append((to_email, subject))
        return "sent"

    monkeypatch.setattr(delivery_service, "send_email", fake_send)

    counts = await delivery_service.dispatch_pending_deliveries(test_db)
    await test_db.commit()
    assert counts == {"sent": 1, "skipped": 0, "failed": 0}
    assert sent == [("dispatch@example.com", "Dispatch me")]

    delivery = (
        await test_db.execute(
            select(NotificationDelivery).where(
                NotificationDelivery.notification_id == created.id
            )
        )
    ).scalar_one()
    assert delivery.status == "sent"
    assert delivery.attempts == 1
    assert delivery.delivered_at is not None

    # Draining again is a no-op
    assert await delivery_service.dispatch_pending_deliveries(test_db) == {
        "sent": 0,
        "skipped": 0,
        "failed": 0,
    }


@pytest.mark.asyncio
async def test_dispatch_marks_skipped_when_smtp_unconfigured(
    monkeypatch, async_client: AsyncClient, test_db
):
    user_id, _ = await _register(async_client, "skipmail@example.com", "Skip Mail")
    await notif.create_notification(
        db=test_db,
        user_id=uuid.UUID(user_id),
        notif_type=notif.NOTIF_TEAM_FINALIZED,
        title="No SMTP",
        body="Body",
        entity_type="team",
    )
    await test_db.commit()

    async def fake_send(to_email: str, subject: str, body: str) -> str:
        return "skipped"

    monkeypatch.setattr(delivery_service, "send_email", fake_send)
    counts = await delivery_service.dispatch_pending_deliveries(test_db)
    await test_db.commit()
    assert counts["skipped"] == 1


# ── Workers ────────────────────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_due_sources_respects_crawl_interval(test_db):
    await HackathonService.run_scraper_and_ingest(test_db, MockHackathonScraper())
    source = (await test_db.execute(select(HackathonSource))).scalar_one()

    assert await scheduler._due_sources(test_db) == []

    source.crawl_interval_hours = 0
    await test_db.commit()
    due = await scheduler._due_sources(test_db)
    assert [s.id for s in due] == [source.id]

    source.enabled = False
    await test_db.commit()
    assert await scheduler._due_sources(test_db) == []


@pytest.mark.asyncio
async def test_embedding_backfill_restores_missing_vectors(
    async_client: AsyncClient, test_db
):
    user_id, headers = await _register(async_client, "backfill@example.com", "Backfill")
    await async_client.post(
        "/api/v1/profiles/me/skills",
        headers=headers,
        json={"skill_name": "Python", "proficiency": "advanced"},
    )
    await test_db.commit()

    for row in (
        await test_db.execute(
            select(CandidateEmbedding).where(
                CandidateEmbedding.user_id == uuid.UUID(user_id)
            )
        )
    ).scalars().all():
        await test_db.delete(row)
    await test_db.commit()

    processed = await backfill_missing_embeddings(test_db, limit=10)
    assert processed == 1

    rows = (
        await test_db.execute(
            select(CandidateEmbedding).where(
                CandidateEmbedding.user_id == uuid.UUID(user_id)
            )
        )
    ).scalars().all()
    assert {row.embedding_type for row in rows} == {"skills", "projects"}


# ── Resume storage management ─────────────────────────────────────────────


def _make_pdf_bytes() -> bytes:
    doc = pymupdf.open()
    page = doc.new_page()
    page.insert_text(
        (50, 72),
        "Jamie Lee\njamie@example.com\n\nSkills:\nPython, FastAPI, PostgreSQL\n",
    )
    data = doc.tobytes()
    doc.close()
    return data


@pytest.mark.asyncio
async def test_resume_list_download_and_delete(async_client: AsyncClient, test_db):
    _, headers = await _register(async_client, "resume_files@example.com", "Resume Files")
    _, other_headers = await _register(
        async_client, "resume_other@example.com", "Other User"
    )

    pdf_bytes = _make_pdf_bytes()
    upload = await async_client.post(
        "/api/v1/profiles/me/resumes",
        headers=headers,
        files={"file": ("jamie_lee.pdf", pdf_bytes, "application/pdf")},
    )
    assert upload.status_code == 201, upload.text
    resume_id = upload.json()["data"]["id"]

    listing = await async_client.get(
        "/api/v1/profiles/me/resumes", headers=headers
    )
    assert listing.status_code == 200, listing.text
    items = listing.json()["data"]
    assert [item["id"] for item in items] == [resume_id]
    assert items[0]["file_name"] == "jamie_lee.pdf"

    download = await async_client.get(
        f"/api/v1/profiles/me/resumes/{resume_id}/download", headers=headers
    )
    assert download.status_code == 200, download.text
    assert download.content == pdf_bytes
    assert "attachment" in download.headers.get("content-disposition", "")

    # Another user cannot read the private document
    denied = await async_client.get(
        f"/api/v1/profiles/me/resumes/{resume_id}/download", headers=other_headers
    )
    assert denied.status_code == 404

    deleted = await async_client.delete(
        f"/api/v1/profiles/me/resumes/{resume_id}", headers=headers
    )
    assert deleted.status_code == 200, deleted.text

    listing = await async_client.get(
        "/api/v1/profiles/me/resumes", headers=headers
    )
    assert listing.json()["data"] == []

    gone = await async_client.get(
        f"/api/v1/profiles/me/resumes/{resume_id}/download", headers=headers
    )
    assert gone.status_code == 404


# ── CLI ────────────────────────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_cli_promote_and_demote_admin(async_client: AsyncClient, test_db):
    user_id, _ = await _register(async_client, "cli_admin@example.com", "CLI Admin")
    factory = async_sessionmaker(bind=test_db.bind, expire_on_commit=False)

    assert await cli.set_admin("cli_admin@example.com", True, factory) == 0
    user = (
        await test_db.execute(
            select(User)
            .where(User.id == uuid.UUID(user_id))
            .execution_options(populate_existing=True)
        )
    ).scalar_one()
    assert user.is_admin is True

    assert await cli.set_admin("cli_admin@example.com", False, factory) == 0
    await test_db.refresh(user)
    assert user.is_admin is False

    assert await cli.set_admin("ghost@example.com", True, factory) == 1


def test_cli_lists_adapters(capsys):
    assert cli.main(["list-adapters"]) == 0
    output = capsys.readouterr().out
    assert "mock_adapter" in output
    assert "devfolio" in output


# ── Rate limiting ──────────────────────────────────────────────────────────


def test_sliding_window_limiter():
    limiter = SlidingWindowLimiter(max_requests=2, window_seconds=10)
    assert limiter.allow("ip", now=0)
    assert limiter.allow("ip", now=1)
    assert not limiter.allow("ip", now=2)
    assert limiter.allow("other", now=2)
    # Window slides forward
    assert limiter.allow("ip", now=11)


@pytest.mark.asyncio
async def test_rate_limit_middleware_returns_429():
    async def ok(request):
        return JSONResponse({"ok": True})

    test_app = Starlette(routes=[Route("/x", ok)])
    test_app.add_middleware(RateLimitMiddleware, max_requests=2, window_seconds=60)

    transport = ASGITransport(app=test_app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        assert (await client.get("/x")).status_code == 200
        assert (await client.get("/x")).status_code == 200
        limited = await client.get("/x")
        assert limited.status_code == 429
        assert limited.json()["success"] is False
