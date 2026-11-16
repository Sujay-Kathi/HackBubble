from datetime import datetime, timezone
from fastapi import APIRouter, Depends
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession
from app.api.v1.auth import router as auth_router
from app.api.v1.hackathons import router as hackathons_router
from app.api.v1.profiles import router as profiles_router
from app.api.v1.teams import router as teams_router
from app.core.config import get_settings
from app.database.session import get_db
from app.schemas.common import APIResponse, HealthCheckResponse

settings = get_settings()
api_router = APIRouter()

# Register sub-routers
api_router.include_router(auth_router)
api_router.include_router(profiles_router)
api_router.include_router(hackathons_router)
api_router.include_router(teams_router)


@api_router.get("/health", response_model=APIResponse[HealthCheckResponse], tags=["System"])
async def health_check(db: AsyncSession = Depends(get_db)):
    db_status = "connected"
    try:
        await db.execute(text("SELECT 1"))
    except Exception as e:
        db_status = f"unreachable: {str(e)}"

    return APIResponse(
        success=True,
        data=HealthCheckResponse(
            status="healthy" if "unreachable" not in db_status else "degraded",
            app_name=settings.APP_NAME,
            version="0.1.0",
            environment=settings.APP_ENV,
            database=db_status,
            timestamp=datetime.now(timezone.utc).isoformat(),
        ),
    )
