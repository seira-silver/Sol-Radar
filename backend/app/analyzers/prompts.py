"""Prompt loading utilities.

We keep prompt templates in the repo-level `data/` directory so they can be
edited without touching application code.
"""

from __future__ import annotations

from functools import lru_cache
from pathlib import Path

from app.utils.logger import logger


_PROJECT_ROOT = Path(__file__).resolve().parents[3]  # .../narration
_DATA_DIR = _PROJECT_ROOT / "data"

_SOURCE_ANALYSIS_PATH = _DATA_DIR / "1_SOURCE_ANALYSIS_PROMPT.txt"
_NARRATIVE_SYNTHESIS_PATH = _DATA_DIR / "2_NARRATIVE_SYNTHESIS_PROMPT.txt"
_IDEA_BACKFILL_PATH = _DATA_DIR / "3_IDEA_BACKFILL_PROMPT.txt"


@lru_cache(maxsize=8)
def _read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except FileNotFoundError:
        logger.error(f"Prompt file not found: {path}")
        return ""
    except Exception as e:
        logger.error(f"Failed reading prompt file {path}: {e}")
        return ""


def get_source_analysis_prompt() -> str:
    """Stage 1 prompt template."""
    text = _read_text(_SOURCE_ANALYSIS_PATH).strip()
    if text:
        return text
    # Minimal fallback (should not happen in normal operation)
    return (
        "Return ONLY valid JSON.\n\n"
        "Source name: {source_name}\n"
        "Source type: {source_type}\n"
        "URL: {source_url}\n"
        "Scraped on: {scrape_date}\n\n"
        "{raw_content}\n"
    )


def get_narrative_synthesis_prompt() -> str:
    """Stage 2 prompt template."""
    text = _read_text(_NARRATIVE_SYNTHESIS_PATH).strip()
    if text:
        return text
    # Minimal fallback (should not happen in normal operation)
    return (
        "Return ONLY valid JSON.\n\n"
        "Signals ({total_sources} sources) {start_date} to {end_date}:\n"
        "{all_signal_reports}\n"
    )


def get_idea_backfill_prompt() -> str:
    """Idea backfill prompt template — used to top-up narratives with < 3 ideas."""
    text = _read_text(_IDEA_BACKFILL_PATH).strip()
    if text:
        return text
    # Minimal fallback
    return (
        "Return ONLY valid JSON.\n\n"
        "Narrative: {narrative_title}\n"
        "Summary: {narrative_summary}\n"
        "Generate {ideas_needed} new product ideas. Do not duplicate: {existing_ideas}\n"
    )

