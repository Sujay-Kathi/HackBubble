import re
from datetime import datetime, timezone
from typing import Any, Optional
from urllib.parse import urlparse, urlunparse


class HackathonNormalizer:
    @staticmethod
    def clean_text(text: Optional[str]) -> Optional[str]:
        if not text:
            return None
        cleaned = re.sub(r"\s+", " ", text).strip()
        return cleaned if cleaned else None

    @staticmethod
    def canonicalize_url(url: str) -> str:
        """Strip tracking parameters and fragments from URL."""
        if not url:
            return ""
        parsed = urlparse(url.strip())
        # Strip query parameters and fragments for canonical identity
        clean_parsed = parsed._replace(query="", fragment="")
        return urlunparse(clean_parsed).rstrip("/")

    @staticmethod
    def normalize_mode(raw_mode: Optional[str]) -> str:
        if not raw_mode:
            return "unknown"
        m = raw_mode.strip().lower()
        if "online" in m or "virtual" in m or "remote" in m:
            return "online"
        if "hybrid" in m:
            return "hybrid"
        if "offline" in m or "in-person" in m or "on-site" in m:
            return "offline"
        return "unknown"

    @staticmethod
    def parse_datetime(raw_val: Any) -> Optional[datetime]:
        if not raw_val:
            return None
        if isinstance(raw_val, datetime):
            if raw_val.tzinfo is None:
                return raw_val.replace(tzinfo=timezone.utc)
            return raw_val.astimezone(timezone.utc)
        if isinstance(raw_val, (int, float)):
            # Timestamp (seconds or milliseconds)
            ts = raw_val / 1000.0 if raw_val > 1e11 else raw_val
            return datetime.fromtimestamp(ts, tz=timezone.utc)
        if isinstance(raw_val, str):
            # Try ISO 8601
            try:
                dt = datetime.fromisoformat(raw_val.replace("Z", "+00:00"))
                if dt.tzinfo is None:
                    dt = dt.replace(tzinfo=timezone.utc)
                return dt
            except ValueError:
                pass
        return None

    @classmethod
    def compute_status(
        cls,
        registration_deadline: Optional[datetime],
        start_date: Optional[datetime],
        end_date: Optional[datetime],
    ) -> str:
        now = datetime.now(timezone.utc)
        if end_date and now > end_date:
            return "completed"
        if start_date and now >= start_date:
            return "ongoing"
        if registration_deadline:
            if now <= registration_deadline:
                return "registration_open"
            else:
                return "registration_closed"
        if start_date and now < start_date:
            return "upcoming"
        return "upcoming"

    @classmethod
    def normalize_event_dict(cls, raw: dict[str, Any], source_name: str, source_url: str) -> dict[str, Any]:
        reg_deadline = cls.parse_datetime(raw.get("registration_deadline"))
        start_d = cls.parse_datetime(raw.get("start_date"))
        end_d = cls.parse_datetime(raw.get("end_date"))

        computed_status = raw.get("status") or cls.compute_status(reg_deadline, start_d, end_d)
        event_url = cls.canonicalize_url(raw.get("event_url") or "")
        reg_url = raw.get("registration_url") or event_url

        return {
            "title": cls.clean_text(raw.get("title")) or "Untitled Hackathon",
            "organizer": cls.clean_text(raw.get("organizer")),
            "description": cls.clean_text(raw.get("description")),
            "themes": [cls.clean_text(t) for t in raw.get("themes", []) if t],
            "eligibility": cls.clean_text(raw.get("eligibility")),
            "mode": cls.normalize_mode(raw.get("mode")),
            "location": cls.clean_text(raw.get("location")),
            "registration_url": reg_url,
            "event_url": event_url,
            "source_name": source_name,
            "source_url": source_url,
            "source_event_id": str(raw.get("source_event_id")) if raw.get("source_event_id") else None,
            "registration_deadline": reg_deadline,
            "start_date": start_d,
            "end_date": end_d,
            "prize_pool_amount": float(raw["prize_pool_amount"]) if raw.get("prize_pool_amount") is not None else None,
            "prize_pool_currency": raw.get("prize_pool_currency") or "USD",
            "status": computed_status,
            "data_quality_status": "verified" if event_url and raw.get("title") else "needs_review",
            "image_url": raw.get("image_url"),
        }
