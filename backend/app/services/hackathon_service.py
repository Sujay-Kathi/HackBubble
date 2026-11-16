import time
import uuid
from datetime import datetime, timezone
from typing import Any, Optional
from sqlalchemy import and_, func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.exceptions import ConflictError, NotFoundError
from app.models.hackathon import (
    Hackathon,
    HackathonSource,
    HackathonSourceRecord,
    SavedHackathon,
    ScrapeRun,
)
from app.schemas.common import PaginationMeta
from app.schemas.hackathon import IngestionReport
from scraper.core.base_scraper import BaseHackathonScraper


class HackathonService:
    @staticmethod
    async def get_or_create_source(
        db: AsyncSession, name: str, base_url: str, adapter_key: str
    ) -> HackathonSource:
        stmt = select(HackathonSource).where(HackathonSource.adapter_key == adapter_key)
        source = (await db.execute(stmt)).scalar_one_or_none()
        if not source:
            source = HackathonSource(
                id=uuid.uuid4(),
                name=name,
                base_url=base_url,
                adapter_key=adapter_key,
                enabled=True,
                crawl_interval_hours=6,
            )
            db.add(source)
            await db.commit()
            await db.refresh(source)
        return source

    @classmethod
    async def run_scraper_and_ingest(
        cls, db: AsyncSession, scraper: BaseHackathonScraper
    ) -> IngestionReport:
        start_time = time.time()
        source = await cls.get_or_create_source(
            db, scraper.source_name, scraper.source_url, scraper.adapter_key
        )

        scrape_run = ScrapeRun(
            id=uuid.uuid4(),
            source_id=source.id,
            started_at=datetime.now(timezone.utc),
            status="running",
        )
        db.add(scrape_run)
        await db.commit()

        events_found = 0
        events_created = 0
        events_updated = 0
        errors: list[str] = []

        try:
            valid_events = await scraper.run()
            events_found = len(valid_events)

            for event_data in valid_events:
                existing_hackathon = await cls.find_existing_hackathon(db, event_data)

                if existing_hackathon:
                    # Update fields
                    existing_hackathon.title = event_data["title"]
                    if event_data.get("organizer"):
                        existing_hackathon.organizer = event_data["organizer"]
                    if event_data.get("description"):
                        existing_hackathon.description = event_data["description"]
                    if event_data.get("themes"):
                        existing_hackathon.themes = event_data["themes"]
                    existing_hackathon.mode = event_data["mode"]
                    if event_data.get("location"):
                        existing_hackathon.location = event_data["location"]
                    if event_data.get("registration_url"):
                        existing_hackathon.registration_url = event_data["registration_url"]
                    if event_data.get("registration_deadline"):
                        existing_hackathon.registration_deadline = event_data["registration_deadline"]
                    if event_data.get("prize_pool_amount") is not None:
                        existing_hackathon.prize_pool_amount = event_data["prize_pool_amount"]
                    existing_hackathon.status = event_data["status"]
                    existing_hackathon.last_scraped_at = datetime.now(timezone.utc)
                    existing_hackathon.last_verified_at = datetime.now(timezone.utc)
                    events_updated += 1
                else:
                    # Create new Hackathon
                    new_id = uuid.uuid4()
                    now = datetime.now(timezone.utc)
                    new_hackathon = Hackathon(
                        id=new_id,
                        title=event_data["title"],
                        organizer=event_data.get("organizer"),
                        description=event_data.get("description"),
                        themes=event_data.get("themes", []),
                        eligibility=event_data.get("eligibility"),
                        mode=event_data["mode"],
                        location=event_data.get("location"),
                        registration_url=event_data.get("registration_url"),
                        event_url=event_data["event_url"],
                        source_name=event_data["source_name"],
                        source_url=event_data["source_url"],
                        source_event_id=event_data.get("source_event_id"),
                        registration_deadline=event_data.get("registration_deadline"),
                        start_date=event_data.get("start_date"),
                        end_date=event_data.get("end_date"),
                        prize_pool_amount=event_data.get("prize_pool_amount"),
                        prize_pool_currency=event_data.get("prize_pool_currency"),
                        status=event_data["status"],
                        last_scraped_at=now,
                        last_verified_at=now,
                        data_quality_status=event_data["data_quality_status"],
                    )
                    db.add(new_hackathon)

                    raw_serializable = {
                        k: (v.isoformat() if isinstance(v, datetime) else v)
                        for k, v in event_data.items()
                    }
                    source_record = HackathonSourceRecord(
                        id=uuid.uuid4(),
                        hackathon_id=new_id,
                        source_id=source.id,
                        source_event_id=event_data.get("source_event_id"),
                        source_url=event_data["source_url"],
                        raw_payload=raw_serializable,
                        last_scraped_at=now,
                    )
                    db.add(source_record)
                    events_created += 1

            await db.commit()

            scrape_run.status = "completed"
            scrape_run.finished_at = datetime.now(timezone.utc)
            scrape_run.events_found = events_found
            scrape_run.events_created = events_created
            scrape_run.events_updated = events_updated
            await db.commit()

        except Exception as e:
            await db.rollback()
            errors.append(str(e))
            scrape_run.status = "failed"
            scrape_run.finished_at = datetime.now(timezone.utc)
            scrape_run.error_summary = str(e)
            await db.commit()

        duration = time.time() - start_time
        return IngestionReport(
            source_name=scraper.source_name,
            events_found=events_found,
            events_created=events_created,
            events_updated=events_updated,
            duration_seconds=round(duration, 2),
            status=scrape_run.status,
            errors=errors,
        )

    @staticmethod
    async def find_existing_hackathon(
        db: AsyncSession, event_data: dict[str, Any]
    ) -> Optional[Hackathon]:
        # 1. Match by source_name and source_event_id
        src_id = event_data.get("source_event_id")
        src_name = event_data.get("source_name")
        if src_id and src_name:
            stmt = select(Hackathon).where(
                Hackathon.source_name == src_name,
                Hackathon.source_event_id == src_id,
            )
            res = (await db.execute(stmt)).scalar_one_or_none()
            if res:
                return res

        # 2. Match by canonical event_url
        event_url = event_data.get("event_url")
        if event_url:
            stmt = select(Hackathon).where(Hackathon.event_url == event_url)
            res = (await db.execute(stmt)).scalar_one_or_none()
            if res:
                return res

        # 3. Fuzzy match: same title and organizer
        title = event_data.get("title")
        organizer = event_data.get("organizer")
        if title and organizer:
            stmt = select(Hackathon).where(
                func.lower(Hackathon.title) == title.lower(),
                func.lower(Hackathon.organizer) == organizer.lower(),
            )
            res = (await db.execute(stmt)).scalar_one_or_none()
            if res:
                return res

        return None

    @staticmethod
    async def list_hackathons(
        db: AsyncSession,
        query: Optional[str] = None,
        mode: Optional[str] = None,
        status: Optional[str] = None,
        theme: Optional[str] = None,
        page: int = 1,
        page_size: int = 20,
    ) -> tuple[list[Hackathon], PaginationMeta]:
        stmt = select(Hackathon)
        conditions = []

        if query:
            q_like = f"%{query.strip().lower()}%"
            conditions.append(
                or_(
                    func.lower(Hackathon.title).like(q_like),
                    func.lower(Hackathon.organizer).like(q_like),
                    func.lower(Hackathon.description).like(q_like),
                )
            )

        if mode and mode != "all":
            conditions.append(Hackathon.mode == mode)

        if status and status != "all":
            conditions.append(Hackathon.status == status)

        if conditions:
            stmt = stmt.where(and_(*conditions))

        # Total count query
        count_stmt = select(func.count()).select_from(stmt.subquery())
        total_items = (await db.execute(count_stmt)).scalar() or 0

        # Pagination & sorting
        offset = (page - 1) * page_size
        stmt = stmt.order_by(Hackathon.registration_deadline.asc().nulls_last(), Hackathon.created_at.desc())
        stmt = stmt.offset(offset).limit(page_size)

        hackathons = (await db.execute(stmt)).scalars().all()
        total_pages = (total_items + page_size - 1) // page_size if total_items > 0 else 1

        meta = PaginationMeta(
            page=page,
            page_size=page_size,
            total_items=total_items,
            total_pages=total_pages,
            has_next=page < total_pages,
            has_prev=page > 1,
        )

        return list(hackathons), meta

    @staticmethod
    async def get_hackathon_detail(
        db: AsyncSession, hackathon_id: uuid.UUID, user_id: Optional[uuid.UUID] = None
    ) -> tuple[Hackathon, bool]:
        stmt = select(Hackathon).where(Hackathon.id == hackathon_id)
        hackathon = (await db.execute(stmt)).scalar_one_or_none()
        if not hackathon:
            raise NotFoundError(message="Hackathon not found")

        is_bookmarked = False
        if user_id:
            bm_stmt = select(SavedHackathon).where(
                SavedHackathon.user_id == user_id,
                SavedHackathon.hackathon_id == hackathon_id,
            )
            is_bookmarked = (await db.execute(bm_stmt)).scalar_one_or_none() is not None

        return hackathon, is_bookmarked

    @staticmethod
    async def bookmark_hackathon(
        db: AsyncSession, user_id: uuid.UUID, hackathon_id: uuid.UUID
    ) -> None:
        # Check if hackathon exists
        h_stmt = select(Hackathon).where(Hackathon.id == hackathon_id)
        if not (await db.execute(h_stmt)).scalar_one_or_none():
            raise NotFoundError(message="Hackathon not found")

        # Check existing bookmark
        bm_stmt = select(SavedHackathon).where(
            SavedHackathon.user_id == user_id,
            SavedHackathon.hackathon_id == hackathon_id,
        )
        if (await db.execute(bm_stmt)).scalar_one_or_none():
            return  # Already bookmarked, idempotent

        bookmark = SavedHackathon(
            user_id=user_id,
            hackathon_id=hackathon_id,
        )
        db.add(bookmark)
        await db.commit()

    @staticmethod
    async def remove_bookmark(
        db: AsyncSession, user_id: uuid.UUID, hackathon_id: uuid.UUID
    ) -> None:
        bm_stmt = select(SavedHackathon).where(
            SavedHackathon.user_id == user_id,
            SavedHackathon.hackathon_id == hackathon_id,
        )
        bookmark = (await db.execute(bm_stmt)).scalar_one_or_none()
        if bookmark:
            await db.delete(bookmark)
            await db.commit()

    @staticmethod
    async def get_saved_hackathons(
        db: AsyncSession, user_id: uuid.UUID
    ) -> list[tuple[Hackathon, datetime]]:
        stmt = (
            select(Hackathon, SavedHackathon.created_at)
            .join(SavedHackathon, SavedHackathon.hackathon_id == Hackathon.id)
            .where(SavedHackathon.user_id == user_id)
            .order_by(SavedHackathon.created_at.desc())
        )
        rows = (await db.execute(stmt)).all()
        return [(h, saved_at) for h, saved_at in rows]
