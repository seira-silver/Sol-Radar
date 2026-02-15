"""Tests for Stage 2 narrative synthesis pipeline."""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch


class _ResultAll:
    def __init__(self, rows):
        self._rows = rows

    def all(self):
        return self._rows


class _ResultScalarOneOrNone:
    def __init__(self, obj):
        self._obj = obj

    def scalar_one_or_none(self):
        return self._obj


@pytest.mark.asyncio
async def test_synthesis_retries_when_zero_narratives():
    """
    If there are signals but the first LLM call returns 0 narratives,
    we retry with a stronger constraint and should end up with >=1 narrative.
    """
    from app.analyzers.narrative_synthesizer import run_narrative_synthesis

    # Mock one signal row (Signal, ScrapedContent, DataSource)
    signal = MagicMock()
    signal.id = 123
    signal.signal_title = "New compressed NFT minting pattern"
    signal.description = "Builders are shifting to compressed NFTs for scale."
    signal.signal_type = "developer"
    signal.novelty = "medium"
    signal.evidence = "Multiple KOLs mention cNFT mints and tooling."
    signal.related_projects = ["Bubblegum"]
    signal.tags = ["infrastructure", "developer-tooling"]

    content = MagicMock()
    content.source_url = "https://x.com/someone/status/123"

    ds = MagicMock()
    ds.name = "@someone"
    ds.id = 1
    ds.url = "https://x.com/someone"

    db = MagicMock()
    db.execute = AsyncMock(side_effect=[
        _ResultAll([(signal, content, ds)]),  # initial signals query
        _ResultScalarOneOrNone(None),         # narrative upsert lookup
    ])
    db.add = MagicMock()
    db.flush = AsyncMock()
    db.commit = AsyncMock()

    llm_first = {"narratives": [], "total_narratives_found": 0}
    llm_second = {
        "narratives": [
            {
                "rank": 1,
                "title": "Compressed NFTs become the default primitive",
                "summary": "A shift toward cNFTs is accelerating due to cheaper mints and better tooling.",
                "confidence": "low",
                "confidence_reasoning": "Only one source in this test, but the signal is concrete.",
                "supporting_sources": ["@someone"],
                "key_evidence": ["Multiple KOLs mention cNFT mints and tooling."],
                "tags": ["infrastructure", "developer-tooling"],
                "product_ideas": [
                    {
                        "title": "cNFT Drop Ops",
                        "description": "Ops tooling for launching large cNFT mints with reliability.",
                        "problem": "Teams struggle with large mints and monitoring.",
                        "solution": "Preflight checks + monitoring + retries + dashboards.",
                        "why_solana": "High throughput and cNFT primitives make scale feasible.",
                        "scale_potential": "Every large collection needs reliable mint ops.",
                        "market_signals": "Repeated mentions by builders.",
                        "supporting_signals": ["New compressed NFT minting pattern"],
                    }
                ],
            }
        ],
        "total_narratives_found": 1,
    }

    with patch("app.analyzers.narrative_synthesizer.llm_client.generate_json", new_callable=AsyncMock) as gen:
        gen.side_effect = [llm_first, llm_second]
        with patch("app.analyzers.narrative_synthesizer._deactivate_stale_narratives", new_callable=AsyncMock):
            with patch("app.analyzers.narrative_synthesizer._update_velocity_scores", new_callable=AsyncMock):
                result = await run_narrative_synthesis(db)

    assert gen.await_count == 2
    assert result["narratives_created"] >= 1

