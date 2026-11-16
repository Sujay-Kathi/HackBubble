"""
Operational CLI.

Usage (from ``backend/``)::

    python -m app.cli promote-admin --email you@example.com
    python -m app.cli demote-admin --email you@example.com
    python -m app.cli run-scraper --adapter mock_adapter
    python -m app.cli list-adapters
"""

from __future__ import annotations

import argparse
import asyncio
import os
import sys

# Ensure repository root is on sys.path for the scraper package
_repo_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
if _repo_root not in sys.path:
    sys.path.insert(0, _repo_root)

from sqlalchemy import select
from sqlalchemy.ext.asyncio import async_sessionmaker

from app.database.session import async_session_factory
from app.models.user import User


async def set_admin(
    email: str,
    is_admin: bool,
    session_factory: async_sessionmaker | None = None,
) -> int:
    """Grant or revoke admin on an existing account."""
    factory = session_factory or async_session_factory
    async with factory() as db:
        user = (
            await db.execute(select(User).where(User.email == email))
        ).scalar_one_or_none()
        if user is None:
            print(f"No user found with email {email}")
            return 1
        user.is_admin = is_admin
        await db.commit()

    verb = "granted to" if is_admin else "revoked from"
    print(f"Admin access {verb} {email}")
    return 0


async def run_scraper(
    adapter_key: str,
    session_factory: async_sessionmaker | None = None,
) -> int:
    """Run a scraper adapter once and print the ingestion report."""
    from app.services.hackathon_service import HackathonService
    from scraper.registry import UnknownAdapterError, available_adapters, get_scraper

    try:
        scraper = get_scraper(adapter_key)
    except UnknownAdapterError:
        print(
            f"Unknown adapter '{adapter_key}'. "
            f"Available: {', '.join(available_adapters())}"
        )
        return 1

    factory = session_factory or async_session_factory
    async with factory() as db:
        report = await HackathonService.run_scraper_and_ingest(db, scraper)

    print(report.model_dump_json(indent=2))
    return 0 if report.status == "completed" else 1


def main(argv: list[str] | None = None) -> int:
    from scraper.registry import available_adapters

    parser = argparse.ArgumentParser(prog="python -m app.cli")
    subparsers = parser.add_subparsers(dest="command", required=True)

    promote = subparsers.add_parser("promote-admin", help="Grant admin access")
    promote.add_argument("--email", required=True)

    demote = subparsers.add_parser("demote-admin", help="Revoke admin access")
    demote.add_argument("--email", required=True)

    scrape = subparsers.add_parser("run-scraper", help="Run one scraper adapter")
    scrape.add_argument("--adapter", default="mock_adapter")

    subparsers.add_parser("list-adapters", help="List registered adapter keys")
    subparsers.add_parser("seed", help="Seed database with baseline sources and fixtures")

    args = parser.parse_args(argv)

    if args.command == "seed":
        from app.database.seed import seed_database
        report = asyncio.run(seed_database())
        print(f"Database seeded successfully: {report}")
        return 0
    if args.command == "list-adapters":
        print("\n".join(available_adapters()))
        return 0
    if args.command == "promote-admin":
        return asyncio.run(set_admin(args.email, True))
    if args.command == "demote-admin":
        return asyncio.run(set_admin(args.email, False))
    return asyncio.run(run_scraper(args.adapter))


if __name__ == "__main__":
    raise SystemExit(main())
