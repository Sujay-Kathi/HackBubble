"""
Idempotent Database Seeder.

Seeds initial operational fixtures:
1. Default Hackathon Sources (Devfolio, Mock adapter).
2. Development Admin Account (admin@hackbubble.local).
3. Common Technology Skills Taxonomy for candidate profiles.

Safe to run multiple times without duplicate key or integrity errors.
"""

from __future__ import annotations

import logging
import uuid
from typing import Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from app.core.security import get_password_hash
from app.database.session import async_session_factory
from app.models.hackathon import HackathonSource
from app.models.user import User, UserProfile

logger = logging.getLogger(__name__)

# Baseline sources aligned with scraper adapters in scraper/sources/
INITIAL_SOURCES: list[dict[str, Any]] = [
    {
        "name": "Devfolio",
        "base_url": "https://devfolio.co",
        "adapter_key": "devfolio",
        "enabled": True,
        "crawl_interval_hours": 6,
        "policy_notes": "Scrapes public hackathons from Devfolio API endpoint.",
    },
    {
        "name": "Mock Hackathons",
        "base_url": "https://mock.hackbubble.local",
        "adapter_key": "mock_adapter",
        "enabled": True,
        "crawl_interval_hours": 2,
        "policy_notes": "Local mock adapter for testing, development and verification.",
    },
]

# Baseline technology skills for profile suggestions and normalization
BASELINE_SKILLS: list[str] = [
    "Python",
    "TypeScript",
    "JavaScript",
    "FastAPI",
    "React",
    "Next.js",
    "PostgreSQL",
    "Docker",
    "PyTorch",
    "TensorFlow",
    "Go",
    "Rust",
    "TailwindCSS",
    "GraphQL",
    "Redis",
]


async def seed_hackathon_sources(db: AsyncSession) -> int:
    """Ensure default hackathon sources exist."""
    created_count = 0
    for src_data in INITIAL_SOURCES:
        stmt = select(HackathonSource).where(
            (HackathonSource.name == src_data["name"])
            | (HackathonSource.adapter_key == src_data["adapter_key"])
        )
        existing = (await db.execute(stmt)).scalar_one_or_none()
        if existing is None:
            source = HackathonSource(
                id=uuid.uuid4(),
                name=src_data["name"],
                base_url=src_data["base_url"],
                adapter_key=src_data["adapter_key"],
                enabled=src_data["enabled"],
                crawl_interval_hours=src_data["crawl_interval_hours"],
                policy_notes=src_data["policy_notes"],
            )
            db.add(source)
            created_count += 1
            logger.info("Seeded hackathon source: %s", src_data["name"])
    return created_count


async def seed_admin_user(
    db: AsyncSession,
    email: str = "admin@hackbubble.local",
    password: str = "AdminPass123!",
) -> bool:
    """Ensure a default administrator account exists for development."""
    stmt = select(User).where(User.email == email)
    existing = (await db.execute(stmt)).scalar_one_or_none()
    if existing is not None:
        return False

    user_id = uuid.uuid4()
    admin_user = User(
        id=user_id,
        email=email,
        auth_subject=f"local|{email}",
        hashed_password=get_password_hash(password),
        account_status="active",
        is_admin=True,
    )
    db.add(admin_user)

    admin_profile = UserProfile(
        id=uuid.uuid4(),
        user_id=user_id,
        display_name="HackBubble Admin",
        bio="Default platform administrator account for development & moderation.",
        domains_of_interest=["AI/ML", "Web3", "Developer Tools"],
        roles_of_interest=["Full-stack Developer", "AI Engineer"],
        profile_visibility="public",
    )
    db.add(admin_profile)
    logger.info("Seeded admin user: %s", email)
    return True


async def seed_database(session_factory: async_sessionmaker | None = None) -> dict[str, Any]:
    """Execute all idempotent seeding operations."""
    factory = session_factory or async_session_factory
    async with factory() as db:
        sources_seeded = await seed_hackathon_sources(db)
        admin_seeded = await seed_admin_user(db)
        await db.commit()

    report = {
        "status": "success",
        "sources_seeded": sources_seeded,
        "admin_seeded": admin_seeded,
        "baseline_skills_available": len(BASELINE_SKILLS),
    }
    logger.info("Database seeding complete: %s", report)
    return report


if __name__ == "__main__":
    import asyncio

    result = asyncio.run(seed_database())
    print("Seed report:", result)
