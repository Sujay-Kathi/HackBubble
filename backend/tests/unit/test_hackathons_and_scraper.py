from datetime import datetime, timedelta, timezone
import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession
from app.services.hackathon_service import HackathonService
from scraper.core.normalizer import HackathonNormalizer
from scraper.core.validator import HackathonValidator
from scraper.sources.mock import MockHackathonScraper


def test_hackathon_normalizer():
    # URL Canonicalization
    url = "https://example.com/hackathons/ai-sprint?utm_source=twitter&ref=newsletter#overview"
    assert HackathonNormalizer.canonicalize_url(url) == "https://example.com/hackathons/ai-sprint"

    # Mode normalization
    assert HackathonNormalizer.normalize_mode("Virtual / Remote") == "online"
    assert HackathonNormalizer.normalize_mode("In-Person On-Site") == "offline"
    assert HackathonNormalizer.normalize_mode("Hybrid Event") == "hybrid"
    assert HackathonNormalizer.normalize_mode(None) == "unknown"

    # Status computation
    now = datetime.now(timezone.utc)
    future_deadline = now + timedelta(days=5)
    future_start = now + timedelta(days=10)
    future_end = now + timedelta(days=12)
    assert HackathonNormalizer.compute_status(future_deadline, future_start, future_end) == "registration_open"

    past_end = now - timedelta(days=1)
    assert HackathonNormalizer.compute_status(None, None, past_end) == "completed"


def test_hackathon_validator():
    valid_event = {
        "title": "HackBubble Winter 2026",
        "event_url": "https://hackbubble.dev/event",
        "start_date": datetime.now(timezone.utc),
        "end_date": datetime.now(timezone.utc) + timedelta(days=2),
    }
    is_valid, errors = HackathonValidator.validate(valid_event)
    assert is_valid is True
    assert len(errors) == 0

    # Invalid title and invalid date order
    bad_event = {
        "title": "X",
        "event_url": "invalid-url",
        "start_date": datetime.now(timezone.utc),
        "end_date": datetime.now(timezone.utc) - timedelta(days=2),
    }
    is_valid, errors = HackathonValidator.validate(bad_event)
    assert is_valid is False
    assert len(errors) >= 2


@pytest.mark.asyncio
async def test_scraper_ingestion_and_deduplication(test_db: AsyncSession):
    scraper = MockHackathonScraper()
    # 1. First ingestion run: creates 2 hackathons
    report1 = await HackathonService.run_scraper_and_ingest(test_db, scraper)
    assert report1.status == "completed"
    assert report1.events_found == 2
    assert report1.events_created == 2
    assert report1.events_updated == 0

    # 2. Second ingestion run: deduplication should detect existing events and update them
    report2 = await HackathonService.run_scraper_and_ingest(test_db, scraper)
    assert report2.status == "completed"
    assert report2.events_found == 2
    assert report2.events_created == 0
    assert report2.events_updated == 2


@pytest.mark.asyncio
async def test_hackathon_catalog_and_bookmarking(async_client: AsyncClient, test_db: AsyncSession):
    # Ingest sample hackathons
    scraper = MockHackathonScraper()
    await HackathonService.run_scraper_and_ingest(test_db, scraper)

    # Register a test user
    reg = await async_client.post(
        "/api/v1/auth/register",
        json={"email": "hacker@example.com", "password": "password123", "display_name": "Hack Enthusiast"},
    )
    token = reg.json()["data"]["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # 1. List hackathons
    list_resp = await async_client.get("/api/v1/hackathons")
    assert list_resp.status_code == 200
    items = list_resp.json()["data"]
    assert len(items) == 2

    # 2. Filter hackathons by query
    search_resp = await async_client.get("/api/v1/hackathons?query=Web3")
    assert search_resp.status_code == 200
    search_items = search_resp.json()["data"]
    assert len(search_items) == 1
    assert "Web3" in search_items[0]["title"]

    # 3. Get detail view with source attribution
    target_id = items[0]["id"]
    detail_resp = await async_client.get(f"/api/v1/hackathons/{target_id}", headers=headers)
    assert detail_resp.status_code == 200
    detail = detail_resp.json()["data"]
    assert detail["source_name"] == "MockPlatform"
    assert detail["is_bookmarked"] is False

    # 4. Bookmark hackathon
    bm_resp = await async_client.post(f"/api/v1/hackathons/{target_id}/bookmark", headers=headers)
    assert bm_resp.status_code == 200

    # 5. Verify in saved list
    saved_resp = await async_client.get("/api/v1/hackathons/saved", headers=headers)
    assert saved_resp.status_code == 200
    saved_list = saved_resp.json()["data"]
    assert len(saved_list) == 1
    assert saved_list[0]["hackathon"]["id"] == target_id

    # 6. Verify detail now shows is_bookmarked == True
    detail_resp2 = await async_client.get(f"/api/v1/hackathons/{target_id}", headers=headers)
    assert detail_resp2.json()["data"]["is_bookmarked"] is True

    # 7. Remove bookmark
    del_bm = await async_client.delete(f"/api/v1/hackathons/{target_id}/bookmark", headers=headers)
    assert del_bm.status_code == 200

    # 8. Verify cleared from saved list
    saved_resp2 = await async_client.get("/api/v1/hackathons/saved", headers=headers)
    assert len(saved_resp2.json()["data"]) == 0
