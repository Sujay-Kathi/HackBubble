import pytest
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.database.seed import seed_database, INITIAL_SOURCES
from app.models.hackathon import HackathonSource
from app.models.user import User


@pytest.mark.asyncio
async def test_seed_database_idempotency(test_db: AsyncSession):
    # Mock session factory for test_db
    class MockSessionFactory:
        def __call__(self):
            return self

        async def __aenter__(self):
            return test_db

        async def __aexit__(self, exc_type, exc_val, exc_tb):
            pass

    mock_factory = MockSessionFactory()

    # First run: should seed sources and admin
    report1 = await seed_database(session_factory=mock_factory)
    assert report1["status"] == "success"
    assert report1["sources_seeded"] == len(INITIAL_SOURCES)
    assert report1["admin_seeded"] is True

    # Verify rows in DB
    sources = (await test_db.execute(select(HackathonSource))).scalars().all()
    assert len(sources) == len(INITIAL_SOURCES)

    admin = (await test_db.execute(select(User).where(User.email == "admin@hackbubble.local"))).scalar_one_or_none()
    assert admin is not None
    assert admin.is_admin is True

    # Second run: should be completely idempotent (0 sources added, admin already exists)
    report2 = await seed_database(session_factory=mock_factory)
    assert report2["status"] == "success"
    assert report2["sources_seeded"] == 0
    assert report2["admin_seeded"] is False
