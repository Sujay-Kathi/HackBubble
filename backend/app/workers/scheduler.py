"""
Background scheduler loops.

Three independent loops run inside the FastAPI lifespan when
``WORKERS_ENABLED`` is set:

* notification delivery drain
* due-source scraper crawl (respects ``HackathonSource.crawl_interval_hours``)
* embedding backfill for candidates missing vectors

Loops are cancelled cleanly on application shutdown.
"""

from __future__ import annotations

import asyncio
import logging
from datetime import datetime, timedelta, timezone

from sqlalchemy import select

from app.core.config import get_settings
from app.database.session import async_session_factory
from app.models.hackathon import HackathonSource, ScrapeRun
from app.services.delivery_service import dispatch_pending_deliveries
from app.services.embedding_service import backfill_missing_embeddings
from app.services.hackathon_service import HackathonService
from scraper.registry import UnknownAdapterError, get_scraper

logger = logging.getLogger(__name__)
settings = get_settings()

_tasks: list[asyncio.Task] = []
_stop_event: asyncio.Event | None = None


async def _sleep_or_stop(stop: asyncio.Event, seconds: float) -> None:
    try:
        await asyncio.wait_for(stop.wait(), timeout=seconds)
    except asyncio.TimeoutError:
        pass


async def delivery_loop(stop: asyncio.Event) -> None:
    while not stop.is_set():
        try:
            async with async_session_factory() as db:
                counts = await dispatch_pending_deliveries(
                    db, limit=settings.WORKER_BATCH_SIZE
                )
                await db.commit()
                if any(counts.values()):
                    logger.info("Notification deliveries: %s", counts)
        except Exception:  # noqa: BLE001 - workers must survive a bad batch
            logger.exception("Notification delivery loop failed")
        await _sleep_or_stop(stop, settings.WORKER_DISPATCH_INTERVAL_SECONDS)


def _as_utc(value: datetime) -> datetime:
    return value if value.tzinfo else value.replace(tzinfo=timezone.utc)


async def _due_sources(db) -> list[HackathonSource]:
    sources = (
        await db.execute(
            select(HackathonSource).where(HackathonSource.enabled == True)  # noqa: E712
        )
    ).scalars().all()

    now = datetime.now(timezone.utc)
    due: list[HackathonSource] = []
    for source in sources:
        last_started = (
            await db.execute(
                select(ScrapeRun.started_at)
                .where(ScrapeRun.source_id == source.id)
                .order_by(ScrapeRun.started_at.desc())
                .limit(1)
            )
        ).scalar_one_or_none()

        if last_started is None:
            due.append(source)
            continue

        next_due = _as_utc(last_started) + timedelta(
            hours=source.crawl_interval_hours
        )
        if next_due <= now:
            due.append(source)
    return due


async def scraper_loop(stop: asyncio.Event) -> None:
    while not stop.is_set():
        try:
            async with async_session_factory() as db:
                for source in await _due_sources(db):
                    try:
                        scraper = get_scraper(source.adapter_key)
                    except UnknownAdapterError:
                        logger.warning(
                            "No adapter registered for source %s (%s)",
                            source.name,
                            source.adapter_key,
                        )
                        continue
                    report = await HackathonService.run_scraper_and_ingest(
                        db, scraper
                    )
                    logger.info(
                        "Scheduled scrape %s: status=%s found=%d created=%d updated=%d",
                        source.name,
                        report.status,
                        report.events_found,
                        report.events_created,
                        report.events_updated,
                    )
        except Exception:  # noqa: BLE001
            logger.exception("Scraper loop failed")
        await _sleep_or_stop(stop, settings.WORKER_SCRAPE_INTERVAL_SECONDS)


async def embedding_loop(stop: asyncio.Event) -> None:
    while not stop.is_set():
        try:
            async with async_session_factory() as db:
                count = await backfill_missing_embeddings(
                    db, limit=settings.WORKER_BATCH_SIZE
                )
                if count:
                    logger.info("Embedding backfill processed %d candidates", count)
        except Exception:  # noqa: BLE001
            logger.exception("Embedding backfill loop failed")
        await _sleep_or_stop(stop, settings.WORKER_EMBEDDING_BACKFILL_INTERVAL_SECONDS)


def start_workers() -> None:
    """Start scheduler loops on the running event loop."""
    global _stop_event
    if _tasks:
        logger.warning("Workers already running; ignoring start_workers()")
        return

    _stop_event = asyncio.Event()
    _tasks.extend(
        [
            asyncio.create_task(delivery_loop(_stop_event), name="delivery-loop"),
            asyncio.create_task(scraper_loop(_stop_event), name="scraper-loop"),
            asyncio.create_task(embedding_loop(_stop_event), name="embedding-loop"),
        ]
    )
    logger.info("Background workers started (%d loops)", len(_tasks))


async def stop_workers() -> None:
    """Signal and await worker shutdown."""
    global _stop_event
    if _stop_event is not None:
        _stop_event.set()
    for task in _tasks:
        task.cancel()
    if _tasks:
        await asyncio.gather(*_tasks, return_exceptions=True)
        _tasks.clear()
    _stop_event = None
    logger.info("Background workers stopped")
