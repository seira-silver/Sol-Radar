"""Backfill product ideas for narratives that have fewer than 3.

Usage (from backend/):
    python3 -m scripts.backfill_ideas            # backfill all under-populated narratives
    python3 -m scripts.backfill_ideas --dry-run   # preview without writing to DB
    python3 -m scripts.backfill_ideas --id 42     # backfill a single narrative by ID
"""

import argparse
import asyncio
import sys
from pathlib import Path

# Ensure the backend package is importable when running as `python3 -m scripts.backfill_ideas`
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.analyzers.idea_backfiller import (
    backfill_narrative,
    run_idea_backfill,
    MIN_IDEAS,
)
from app.database import async_session_factory
from app.models.narrative import Narrative
from app.utils.logger import logger


async def main(dry_run: bool = False, narrative_id: int | None = None) -> None:
    """Find all narratives with < 3 ideas and backfill them."""
    async with async_session_factory() as db:
        if narrative_id is not None:
            result = await db.execute(
                select(Narrative).where(Narrative.id == narrative_id)
            )
            narrative = result.scalar_one_or_none()
            if not narrative:
                logger.error(f"[BACKFILL] Narrative #{narrative_id} not found")
                return
            created = await backfill_narrative(db, narrative, dry_run=dry_run)
            if not dry_run:
                await db.commit()
            logger.info(f"[BACKFILL] Done. Created {created} new idea(s) for narrative #{narrative_id}.")
        else:
            summary = await run_idea_backfill(db, dry_run=dry_run)
            if not dry_run:
                await db.commit()
            logger.info(f"[BACKFILL] Done. {summary}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Backfill ideas for narratives with fewer than 3.")
    parser.add_argument("--dry-run", action="store_true", help="Preview without writing to database")
    parser.add_argument("--id", type=int, default=None, dest="narrative_id", help="Backfill a single narrative by ID")
    args = parser.parse_args()

    asyncio.run(main(dry_run=args.dry_run, narrative_id=args.narrative_id))
