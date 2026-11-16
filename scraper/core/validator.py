from typing import Any
from urllib.parse import urlparse


class HackathonValidator:
    @staticmethod
    def validate(event: dict[str, Any]) -> tuple[bool, list[str]]:
        errors: list[str] = []

        title = event.get("title")
        if not title or len(title.strip()) < 3:
            errors.append("Title must be at least 3 characters long")

        event_url = event.get("event_url")
        if not event_url:
            errors.append("event_url is required")
        else:
            parsed = urlparse(event_url)
            if parsed.scheme not in ("http", "https"):
                errors.append(f"Invalid URL scheme: {parsed.scheme}")
            if not parsed.netloc:
                errors.append("URL must contain a valid domain")

        start = event.get("start_date")
        end = event.get("end_date")
        if start and end and end < start:
            errors.append("end_date cannot be earlier than start_date")

        return (len(errors) == 0, errors)
