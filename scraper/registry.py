"""
Adapter registry for hackathon scrapers.

Sources are referenced by their ``adapter_key`` so new adapters can be added in
one place without touching API or worker code.
"""

from __future__ import annotations

from collections.abc import Callable

from scraper.core.base_scraper import BaseHackathonScraper
from scraper.sources.devfolio import DevfolioScraper
from scraper.sources.mock import MockHackathonScraper

AdapterFactory = Callable[[], BaseHackathonScraper]

_ADAPTERS: dict[str, AdapterFactory] = {
    MockHackathonScraper.adapter_key: MockHackathonScraper,
    DevfolioScraper.adapter_key: DevfolioScraper,
}


class UnknownAdapterError(KeyError):
    """Raised when an adapter key is not registered."""


def register_adapter(adapter_key: str, factory: AdapterFactory) -> None:
    """Register (or replace) an adapter factory under a key."""
    _ADAPTERS[adapter_key] = factory


def available_adapters() -> list[str]:
    return sorted(_ADAPTERS)


def get_scraper(adapter_key: str) -> BaseHackathonScraper:
    try:
        factory = _ADAPTERS[adapter_key]
    except KeyError as exc:
        raise UnknownAdapterError(adapter_key) from exc
    return factory()
