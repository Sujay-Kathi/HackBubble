import uuid
from typing import Optional
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.api.deps import get_current_user, get_optional_current_user
from app.database.session import get_db
from app.models.user import User
from app.schemas.common import APIResponse, PaginatedResponse
from app.schemas.hackathon import (
    HackathonDetailResponse,
    HackathonSummaryResponse,
    IngestionReport,
    SavedHackathonResponse,
)
from app.services.hackathon_service import HackathonService
from scraper.sources.devfolio import DevfolioScraper
from scraper.sources.mock import MockHackathonScraper

router = APIRouter(prefix="/hackathons", tags=["Hackathons"])


@router.get("", response_model=PaginatedResponse[HackathonSummaryResponse])
async def list_hackathons(
    query: Optional[str] = Query(None, description="Search by title, organizer, or description"),
    mode: Optional[str] = Query(None, description="online | offline | hybrid | all"),
    status: Optional[str] = Query(None, description="upcoming | registration_open | registration_closed | ongoing | all"),
    theme: Optional[str] = Query(None, description="Filter by theme"),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
):
    hackathons, meta = await HackathonService.list_hackathons(
        db, query=query, mode=mode, status=status, theme=theme, page=page, page_size=page_size
    )

    data = [HackathonSummaryResponse.model_validate(h) for h in hackathons]
    return PaginatedResponse(
        success=True,
        data=data,
        pagination=meta,
    )


@router.get("/saved", response_model=APIResponse[list[SavedHackathonResponse]])
async def get_saved_hackathons(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    saved_items = await HackathonService.get_saved_hackathons(db, current_user.id)
    results = [
        SavedHackathonResponse(
            hackathon=HackathonSummaryResponse.model_validate(h),
            saved_at=saved_at,
        )
        for h, saved_at in saved_items
    ]
    return APIResponse(success=True, data=results)


@router.get("/{hackathon_id}", response_model=APIResponse[HackathonDetailResponse])
async def get_hackathon_detail(
    hackathon_id: uuid.UUID,
    viewer: Optional[User] = Depends(get_optional_current_user),
    db: AsyncSession = Depends(get_db),
):
    viewer_id = viewer.id if viewer else None
    hackathon, is_bookmarked = await HackathonService.get_hackathon_detail(
        db, hackathon_id, viewer_id
    )

    resp = HackathonDetailResponse(
        id=hackathon.id,
        title=hackathon.title,
        organizer=hackathon.organizer,
        description=hackathon.description,
        themes=hackathon.themes or [],
        eligibility=hackathon.eligibility,
        mode=hackathon.mode,
        location=hackathon.location,
        registration_url=hackathon.registration_url,
        event_url=hackathon.event_url,
        source_name=hackathon.source_name,
        source_url=hackathon.source_url,
        registration_deadline=hackathon.registration_deadline,
        start_date=hackathon.start_date,
        end_date=hackathon.end_date,
        prize_pool_amount=hackathon.prize_pool_amount,
        prize_pool_currency=hackathon.prize_pool_currency,
        status=hackathon.status,
        last_scraped_at=hackathon.last_scraped_at,
        last_verified_at=hackathon.last_verified_at,
        data_quality_status=hackathon.data_quality_status,
        created_at=hackathon.created_at,
        is_bookmarked=is_bookmarked,
    )

    return APIResponse(success=True, data=resp)


@router.post("/{hackathon_id}/bookmark", response_model=APIResponse[None], status_code=status.HTTP_200_OK)
async def bookmark_hackathon(
    hackathon_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    await HackathonService.bookmark_hackathon(db, current_user.id, hackathon_id)
    return APIResponse(success=True, data=None, message="Hackathon bookmarked successfully")


@router.delete("/{hackathon_id}/bookmark", response_model=APIResponse[None])
async def remove_bookmark(
    hackathon_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    await HackathonService.remove_bookmark(db, current_user.id, hackathon_id)
    return APIResponse(success=True, data=None, message="Bookmark removed successfully")


@router.post("/admin/scrape-trigger", response_model=APIResponse[IngestionReport])
async def trigger_scraper(
    adapter_key: str = Query(default="mock_adapter", description="mock_adapter | devfolio"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    if adapter_key == "devfolio":
        scraper = DevfolioScraper()
    else:
        scraper = MockHackathonScraper()

    report = await HackathonService.run_scraper_and_ingest(db, scraper)
    return APIResponse(
        success=True,
        data=report,
        message=f"Scraper run finished with status {report.status}",
    )
