from abc import ABC, abstractmethod
from typing import Any
from scraper.core.normalizer import HackathonNormalizer
from scraper.core.validator import HackathonValidator


class BaseHackathonScraper(ABC):
    source_name: str
    source_url: str
    adapter_key: str

    @abstractmethod
    async def fetch_events(self) -> list[dict[str, Any]]:
        """Fetch raw event listings from the source."""
        pass

    async def extract_event_details(self, event_stub: dict[str, Any]) -> dict[str, Any]:
        """Optionally fetch deeper details for an event stub."""
        return event_stub

    def normalize(self, raw_data: dict[str, Any]) -> dict[str, Any]:
        """Normalize raw scraped payload to canonical schema."""
        return HackathonNormalizer.normalize_event_dict(
            raw_data,
            source_name=self.source_name,
            source_url=self.source_url,
        )

    def validate(self, normalized_data: dict[str, Any]) -> tuple[bool, list[str]]:
        """Validate canonical record."""
        return HackathonValidator.validate(normalized_data)

    async def run(self) -> list[dict[str, Any]]:
        """Complete scraping pipeline: fetch -> extract -> normalize -> validate."""
        raw_events = await self.fetch_events()
        valid_events: list[dict[str, Any]] = []

        for raw in raw_events:
            detailed = await self.extract_event_details(raw)
            norm = self.normalize(detailed)
            is_valid, _ = self.validate(norm)
            if is_valid:
                valid_events.append(norm)

        return valid_events
