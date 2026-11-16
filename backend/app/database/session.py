from collections.abc import AsyncGenerator

from sqlalchemy import text
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from app.core.config import get_settings

settings = get_settings()

# ── Build connect_args for asyncpg ────────────────────────────────────────
# When connecting through a transaction pooler (Supabase Supavisor / PgBouncer
# on port 6543), asyncpg prepared-statement caching must be disabled or the
# connection will raise "prepared statement … already exists".
# We detect a pooler by the presence of "pgbouncer" in the URL or port 6543.
_url = settings.DATABASE_URL
_is_pooler = ":6543" in _url or "pgbouncer" in _url.lower()
_connect_args: dict = {"statement_cache_size": 0} if _is_pooler else {}

# ── Async engine ──────────────────────────────────────────────────────────
engine = create_async_engine(
    _url,
    echo=settings.DB_ECHO,
    future=True,
    # Recycle connections after 30 min to avoid stale TCP connections
    pool_recycle=1800,
    # Ping the connection before handing it to a request; drops dead sockets
    pool_pre_ping=True,
    connect_args=_connect_args,
)

async_session_factory = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """FastAPI dependency: yields a managed async database session."""
    async with async_session_factory() as session:
        try:
            yield session
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


async def check_db_connection() -> dict:
    """
    Lightweight database health probe.

    Returns a dict with keys:
      - ``ok`` (bool): True if the database responded.
      - ``pgvector`` (bool): True if the vector extension is installed.
      - ``error`` (str | None): Error message when ``ok`` is False.

    Safe to call from the /health endpoint or a startup hook.
    """
    result = {"ok": False, "pgvector": False, "error": None}
    try:
        async with async_session_factory() as db:
            await db.execute(text("SELECT 1"))
            result["ok"] = True
            # Confirm pgvector extension is present
            row = await db.execute(
                text(
                    "SELECT 1 FROM pg_extension WHERE extname = 'vector' LIMIT 1"
                )
            )
            result["pgvector"] = row.scalar_one_or_none() == 1
    except Exception as exc:  # noqa: BLE001
        result["error"] = str(exc)
    return result
