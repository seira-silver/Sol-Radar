"""Seira AI chat endpoint — SSE streaming responses powered by Grok."""

import json
import os
from typing import AsyncGenerator

import httpx
from bs4 import BeautifulSoup
from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse
from litellm import acompletion
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.analyzers.prompts import get_seira_agent_prompt
from app.config import get_settings
from app.database import get_db
from app.models.narrative import Narrative
from app.models.signal import Signal
from app.schemas.chat import ChatRequest
from app.utils.logger import logger

router = APIRouter(prefix="/chat", tags=["chat"])

settings = get_settings()

_MAX_URL_CHARS = 8000
_MAX_CONTEXT_NARRATIVES = 10
_MAX_CONTEXT_SIGNALS = 20


async def _scrape_url(url: str) -> str | None:
    """Fetch a URL and extract readable text. Returns None on failure."""
    try:
        async with httpx.AsyncClient(
            timeout=httpx.Timeout(20.0, connect=10.0),
            headers={"User-Agent": "SolRadar-Seira/1.0 (research assistant)"},
            follow_redirects=True,
        ) as client:
            resp = await client.get(url)
            resp.raise_for_status()

        soup = BeautifulSoup(resp.text, "html.parser")
        for tag in soup(["script", "style", "nav", "footer", "header", "aside"]):
            tag.decompose()

        text = soup.get_text(separator="\n", strip=True)
        return text[:_MAX_URL_CHARS] if text else None
    except Exception as e:
        logger.warning(f"[SEIRA] Failed to scrape URL {url}: {e}")
        return None


async def _build_context(db: AsyncSession) -> str:
    """Build a compact context block from current Sol Radar intelligence."""
    sections: list[str] = []

    # Active narratives (top by velocity)
    narr_result = await db.execute(
        select(Narrative)
        .where(Narrative.is_active == True)  # noqa: E712
        .order_by(Narrative.velocity_score.desc())
        .limit(_MAX_CONTEXT_NARRATIVES)
    )
    narratives = narr_result.scalars().all()

    if narratives:
        narr_lines = ["### Active Narratives\n"]
        for n in narratives:
            evidence_summary = ""
            if n.key_evidence:
                ev_items = []
                for ev in n.key_evidence[:3]:
                    if isinstance(ev, dict):
                        ev_text = ev.get("evidence", "")[:120]
                        ev_src = ev.get("source_name", "")
                        if ev_text:
                            ev_items.append(f'  - [{ev_src}] "{ev_text}"')
                if ev_items:
                    evidence_summary = "\n".join(ev_items)

            ideas_summary = ""
            if n.ideas:
                idea_titles = [f"  - {idea.title}" for idea in n.ideas[:5]]
                ideas_summary = "\n".join(idea_titles)

            entry = (
                f"**{n.title}** (confidence: {n.confidence}, velocity: {n.velocity_score})\n"
                f"  Summary: {n.summary[:200]}\n"
                f"  Tags: {', '.join(n.tags or [])}\n"
                f"  Sources: {', '.join(n.supporting_source_names or [])}"
            )
            if evidence_summary:
                entry += f"\n  Evidence:\n{evidence_summary}"
            if ideas_summary:
                entry += f"\n  Product Ideas:\n{ideas_summary}"
            narr_lines.append(entry)
        sections.append("\n\n".join(narr_lines))

    # Recent signals
    sig_result = await db.execute(
        select(Signal)
        .order_by(Signal.created_at.desc())
        .limit(_MAX_CONTEXT_SIGNALS)
    )
    signals = sig_result.scalars().all()

    if signals:
        sig_lines = ["### Recent Signals\n"]
        for s in signals:
            entry = (
                f"- **{s.signal_title}** ({s.signal_type}, novelty: {s.novelty})\n"
                f"  {s.description[:150]}\n"
                f"  Tags: {', '.join(s.tags or [])} | Projects: {', '.join(s.related_projects or [])}"
            )
            sig_lines.append(entry)
        sections.append("\n".join(sig_lines))

    if not sections:
        return "(No narratives or signals currently in the database.)"

    return "\n\n---\n\n".join(sections)


async def _stream_chat(
    messages: list[dict], model: str, api_key: str
) -> AsyncGenerator[str, None]:
    """Stream LLM response as SSE data lines."""
    try:
        if model.startswith("xai/") and api_key:
            os.environ["XAI_API_KEY"] = api_key

        response = await acompletion(
            model=model,
            messages=messages,
            api_key=api_key or None,
            temperature=0.6,
            max_tokens=4096,
            stream=True,
        )

        async for chunk in response:
            delta = chunk.choices[0].delta
            content = getattr(delta, "content", None)
            if content:
                yield f"data: {json.dumps({'content': content})}\n\n"

    except Exception as e:
        logger.error(f"[SEIRA] Streaming error: {e}")
        yield f"data: {json.dumps({'error': str(e)})}\n\n"

    yield "data: [DONE]\n\n"


@router.post("")
async def chat(request: ChatRequest, db: AsyncSession = Depends(get_db)):
    """Chat with Seira — Sol Radar's AI research analyst. Returns SSE stream."""

    # Build context from DB
    context = await _build_context(db)

    # If user shared a URL, scrape and append
    url_context = ""
    if request.url:
        logger.info(f"[SEIRA] Scraping user-provided URL: {request.url}")
        scraped = await _scrape_url(request.url)
        if scraped:
            url_context = (
                f"\n\n---\n\n### User Shared URL: {request.url}\n\n"
                f"Content (truncated to {_MAX_URL_CHARS} chars):\n{scraped}"
            )
        else:
            url_context = (
                f"\n\n---\n\n### User Shared URL: {request.url}\n\n"
                "(Failed to fetch or extract content from this URL. "
                "Let the user know and work with what you have.)"
            )

    full_context = context + url_context

    # Build system prompt
    system_prompt_template = get_seira_agent_prompt()
    system_prompt = system_prompt_template.replace("{context}", full_context)

    # Build messages for LLM
    llm_messages = [{"role": "system", "content": system_prompt}]
    for msg in request.messages:
        llm_messages.append({"role": msg.role, "content": msg.content})

    # Resolve model and API key
    model = settings.LLM_MODEL
    s = get_settings()
    if model.startswith("xai/"):
        api_key = (s.XAI_API_KEY or s.GROK_API_KEY or "").strip()
    else:
        api_key = (s.GEMINI_API_KEY or "").strip()

    return StreamingResponse(
        _stream_chat(llm_messages, model, api_key),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )
