from typing import Any
import httpx
from scraper.core.base_scraper import BaseHackathonScraper


class DevfolioScraper(BaseHackathonScraper):
    source_name = "Devfolio"
    source_url = "https://devfolio.co"
    adapter_key = "devfolio"

    def __init__(self, client: httpx.AsyncClient | None = None):
        self._client = client

    async def fetch_events(self) -> list[dict[str, Any]]:
        """Fetch hackathons from Devfolio's open public API / feed."""
        events: list[dict[str, Any]] = []
        url = "https://api.devfolio.co/api/hackathons?filter=open&page=1&limit=20"

        try:
            if self._client:
                resp = await self._client.get(url, timeout=10.0)
            else:
                async with httpx.AsyncClient() as client:
                    resp = await client.get(url, timeout=10.0)

            if resp.status_code == 200:
                data = resp.json()
                items = data.get("result", [])
                for item in items:
                    events.append({
                        "title": item.get("name"),
                        "organizer": item.get("organisation", {}).get("name") if isinstance(item.get("organisation"), dict) else None,
                        "description": item.get("desc"),
                        "themes": item.get("themes", []),
                        "mode": "online" if item.get("is_online") else "offline",
                        "location": item.get("location"),
                        "event_url": f"https://{item.get('slug')}.devfolio.co" if item.get("slug") else item.get("hackathon_setting", {}).get("site"),
                        "registration_url": f"https://{item.get('slug')}.devfolio.co" if item.get("slug") else None,
                        "source_event_id": item.get("slug") or item.get("id"),
                        "start_date": item.get("starts_at"),
                        "end_date": item.get("ends_at"),
                        "prize_pool_amount": None,
                        "prize_pool_currency": "INR",
                    })
        except Exception:
            # Fallback gracefully if external network/endpoint is unavailable
            pass

        return events
