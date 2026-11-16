import uuid
from datetime import datetime, timedelta, timezone
from typing import Any
from scraper.core.base_scraper import BaseHackathonScraper


class MockHackathonScraper(BaseHackathonScraper):
    source_name = "MockPlatform"
    source_url = "https://mockplatform.dev"
    adapter_key = "mock_adapter"

    def __init__(self, sample_events: list[dict[str, Any]] | None = None):
        self._sample_events = sample_events

    async def fetch_events(self) -> list[dict[str, Any]]:
        if self._sample_events is not None:
            return self._sample_events

        now = datetime.now(timezone.utc)
        return [
            {
                "title": "Global AI Innovation Sprint 2026",
                "organizer": "AI Builders Foundation",
                "description": "Build cutting-edge generative AI applications and agent workflows.",
                "themes": ["Artificial Intelligence", "LLMs", "Autonomous Agents"],
                "eligibility": "Open to all developers and students worldwide",
                "mode": "online",
                "event_url": "https://mockplatform.dev/events/ai-sprint-2026?utm_source=twitter",
                "registration_url": "https://mockplatform.dev/events/ai-sprint-2026/register",
                "source_event_id": "mock-event-101",
                "registration_deadline": (now + timedelta(days=14)).isoformat(),
                "start_date": (now + timedelta(days=20)).isoformat(),
                "end_date": (now + timedelta(days=22)).isoformat(),
                "prize_pool_amount": 25000,
                "prize_pool_currency": "USD",
                "status": "registration_open",
            },
            {
                "title": "Bengaluru Web3 & DeFi Hack",
                "organizer": "CryptoIndia Hub",
                "description": "Decentralized finance, smart contract security, and Web3 infrastructure.",
                "themes": ["Web3", "Blockchain", "DeFi"],
                "eligibility": "Students and working professionals",
                "mode": "hybrid",
                "location": "Bengaluru, India",
                "event_url": "https://mockplatform.dev/events/blr-web3-hack",
                "registration_url": "https://mockplatform.dev/events/blr-web3-hack/apply",
                "source_event_id": "mock-event-102",
                "registration_deadline": (now + timedelta(days=7)).isoformat(),
                "start_date": (now + timedelta(days=10)).isoformat(),
                "end_date": (now + timedelta(days=12)).isoformat(),
                "prize_pool_amount": 1000000,
                "prize_pool_currency": "INR",
                "status": "registration_open",
            },
        ]
