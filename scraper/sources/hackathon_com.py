"""Scraper adapter for hackathon.com listing pages."""

from __future__ import annotations

import re
from datetime import datetime, timezone
from typing import Any
from urllib.parse import urljoin

import httpx
import lxml.html as H

from scraper.core.base_scraper import BaseHackathonScraper

MONTHS = {
    "jan": 1, "feb": 2, "mar": 3, "apr": 4, "may": 5, "jun": 6,
    "jul": 7, "aug": 8, "sep": 9, "oct": 10, "nov": 11, "dec": 12,
}

LISTING_URL = "https://www.hackathon.com/theme/ai/2026"


def _parse_date(text: str) -> datetime | None:
    m = re.search(r"(\d{1,2})\s+(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)", text, re.I)
    if not m:
        return None
    day = int(m.group(1))
    month = MONTHS[m.group(2).lower()[:3]]
    year = 2026
    try:
        return datetime(year, month, day, tzinfo=timezone.utc)
    except ValueError:
        return None


class HackathonComScraper(BaseHackathonScraper):
    source_name = "Hackathon.com"
    source_url = "https://www.hackathon.com"
    adapter_key = "hackathon_com"

    def __init__(self, client: httpx.AsyncClient | None = None, limit: int = 10):
        self._client = client
        self.limit = limit

    async def _get(self, url: str) -> str:
        if self._client:
            resp = await self._client.get(url, timeout=20.0, follow_redirects=True)
        else:
            async with httpx.AsyncClient() as c:
                resp = await c.get(url, timeout=20.0, follow_redirects=True)
        resp.raise_for_status()
        return resp.text

    async def fetch_events(self) -> list[dict[str, Any]]:
        html = await self._get(LISTING_URL)
        doc = H.fromstring(html)
        links = []
        seen = set()
        for a in doc.xpath("//a"):
            href = a.get("href") or ""
            if href.startswith("/event/"):
                full = urljoin(self.source_url, href)
                if full not in seen:
                    seen.add(full)
                    links.append(full)
        links = links[: self.limit]

        raw_events: list[dict[str, Any]] = []
        for link in links:
            try:
                detail_html = await self._get(link)
            except Exception:
                continue
            d = H.fromstring(detail_html)

            title = None
            h1 = d.xpath("//h1")
            if h1:
                title = h1[0].text_content().strip()
            if not title:
                t = d.xpath("//title/text()")
                title = t[0].split("|")[0].strip() if t else None

            og_img = d.xpath("//meta[@property='og:image']/@content")
            image_url = og_img[0] if og_img else None

            themes = []
            for a in d.xpath("//a[starts-with(@href,'/theme/')]"):
                txt = (a.text or "").strip()
                if txt and txt not in themes:
                    themes.append(txt)

            page_text = " ".join(t.strip() for t in d.xpath("//text()") if t.strip())
            mode = "unknown"
            if "Hybrid" in page_text:
                mode = "hybrid"
            elif "Online" in page_text:
                mode = "online"
            elif "In-person" in page_text or "In person" in page_text:
                mode = "offline"

            location = None
            # location often appears after city/country; grab first "City, Country" like token
            loc_match = re.search(r"([A-Z][a-zA-Z\s]+,\s*[A-Z][a-zA-Z\s]+)", page_text)
            if loc_match:
                location = loc_match.group(1).strip()

            prize = None
            prize_match = re.search(r"\$\s?([\d,]+)", page_text)
            if prize_match:
                prize = prize_match.group(1).replace(",", "")

            # dates: find "DD Mon" occurrences
            date_matches = re.findall(r"(\d{1,2})\s+(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)", page_text, re.I)
            start_date = None
            end_date = None
            if date_matches:
                start_date = _parse_date(f"{date_matches[0][0]} {date_matches[0][1]}")
                if len(date_matches) > 1:
                    end_date = _parse_date(f"{date_matches[1][0]} {date_matches[1][1]}")

            # description: meta description or first long paragraph
            desc_meta = d.xpath("//meta[@name='description']/@content")
            description = desc_meta[0] if desc_meta else None
            if not description:
                paras = [p.text_content().strip() for p in d.xpath("//p") if len(p.text_content().strip()) > 80]
                if paras:
                    description = paras[0]

            organizer = None
            org_match = re.search(r"by\s+([A-Z][A-Za-z\s]+?)(?:\s{2,}|$)", page_text)
            # fallback: leave None

            raw_events.append({
                "title": title,
                "organizer": organizer,
                "description": description,
                "themes": themes[:6],
                "eligibility": None,
                "mode": mode,
                "location": location,
                "registration_url": link,
                "event_url": link,
                "source_event_id": link.rsplit("/", 1)[-1],
                "registration_deadline": start_date,
                "start_date": start_date,
                "end_date": end_date,
                "prize_pool_amount": float(prize) if prize else None,
                "prize_pool_currency": "USD",
                "status": "upcoming",
                "image_url": image_url,
            })

        return raw_events
