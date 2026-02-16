# Sol Radar — Agent-to-Agent Interface

Sol Radar is a **Solana ecosystem narrative intelligence platform**. It detects
emerging narratives and early signals by scraping onchain/offchain data sources,
extracting signals with LLMs, and synthesizing them into actionable narratives
with product ideas.

This document describes how external agents can interact with Sol Radar
programmatically.

---

## Base URL

All endpoints are prefixed with:

```
https://static.53.190.27.37.clients.your-server.de/sol-radar/api/v1
```

---

## Available Endpoints

### GET /api/v1/narratives

List detected Solana ecosystem narratives.

**Query Parameters:**
| Param | Type | Description |
|-------|------|-------------|
| `is_active` | bool | Filter by active status (default: `true`) |
| `min_confidence` | string | Minimum confidence: `low`, `medium`, `high` |
| `tags` | string | Comma-separated tag filter (e.g. `defi,infrastructure`) |
| `limit` | int | Page size (default: 10, max: 50) |
| `offset` | int | Pagination offset |

**Response:** `{ narratives: [...], total, limit, offset }`

Each narrative includes: `id`, `title`, `summary`, `confidence`,
`confidence_reasoning`, `velocity_score`, `tags`, `key_evidence`,
`supporting_source_names`, `idea_count`, `ideas` (nested), `is_active`,
`created_at`, `last_detected_at`.

---

### GET /api/v1/signals

List raw signals extracted from scraped sources.

**Query Parameters:**
| Param | Type | Description |
|-------|------|-------------|
| `search` | string | Full-text search in signal titles/descriptions |
| `source_type` | string | Filter: `web`, `twitter` |
| `signal_type` | string | Filter: `onchain`, `developer`, `social`, `research`, `mobile`, `other` |
| `novelty` | string | Filter: `high`, `medium`, `low` |
| `tags` | string | Comma-separated tag filter |
| `limit` | int | Page size (default: 20, max: 100) |
| `offset` | int | Pagination offset |

**Response:** `{ signals: [...], total, limit, offset }`

Each signal includes: `id`, `signal_title`, `description`, `signal_type`,
`novelty`, `evidence`, `related_projects`, `tags`, `content_url`,
`data_source_name`, `data_source_type`, `created_at`.

---

### GET /api/v1/ideas

List product ideas generated from narratives.

**Query Parameters:**
| Param | Type | Description |
|-------|------|-------------|
| `narrative_id` | int | Filter ideas by parent narrative |
| `tags` | string | Comma-separated tag filter |
| `limit` | int | Page size (default: 20) |
| `offset` | int | Pagination offset |

**Response:** `{ ideas: [...], total, limit, offset }`

Each idea includes: `id`, `narrative_id`, `title`, `description`, `problem`,
`solution`, `why_solana`, `scale_potential`, `market_signals`,
`supporting_signals`, `created_at`.

---

### GET /api/v1/stats

Dashboard statistics snapshot.

**Response:**

```json
{
  "active_narratives_count": 12,
  "total_narratives_count": 45,
  "total_ideas_count": 87,
  "avg_velocity_score": 3.2,
  "active_builders": 156,
  "sources_scraped_count": 18,
  "total_signals_count": 342,
  "last_web_scrape_time": "2026-02-16T02:00:00Z",
  "last_twitter_scrape_time": "2026-02-15T14:00:00Z",
  "next_synthesis_time": "2026-02-17T03:00:00Z"
}
```

---

### POST /api/v1/chat

Interact with **Seira**, Sol Radar's AI research analyst.

**Request Body:**

```json
{
  "messages": [
    {
      "role": "user",
      "content": "What are the strongest Solana narratives right now?"
    }
  ],
  "url": "https://example.com/article"
}
```

- `messages`: Conversation history (role: `user` | `assistant`)
- `url` (optional): A URL for Seira to scrape and analyze in context

**Response:** Server-Sent Events (SSE) stream.

Each event is a line: `data: {"content": "token text"}`

Stream ends with: `data: [DONE]`

**Agent usage pattern:**

```python
import httpx

resp = httpx.post(
    f"{BASE_URL}/api/v1/chat",
    json={
        "messages": [{"role": "user", "content": "What DePIN signals are emerging?"}],
    },
    headers={"Accept": "text/event-stream"},
)

full_response = ""
for line in resp.iter_lines():
    if line.startswith("data: ") and line != "data: [DONE]":
        import json
        chunk = json.loads(line[6:])
        full_response += chunk.get("content", "")
```

---

## Data Model Summary

### Narrative

A directional shift in the Solana ecosystem backed by cross-source signals.
Has: title, summary, confidence (high/medium/low), velocity score, tags,
key evidence, and 3-5 actionable product ideas.

### Signal

A raw observation extracted from a single source (blog, tweet, onchain data).
Has: title, description, type, novelty level, evidence quote, related projects,
tags, and source attribution.

### Idea

A concrete, actionable product concept linked to a narrative. Has: title,
description, problem statement, solution, why Solana is the right platform,
scale potential analysis, and market signal evidence.

---

## Use Cases for Agents

1. **Get latest Solana alpha**: `GET /narratives?is_active=true` to see what
   narratives Sol Radar has detected, sorted by velocity score.

2. **Validate a product idea**: `POST /chat` with a description of your idea.
   Seira will evaluate it against current narratives and cite relevant signals.

3. **Find signals for a topic**: `GET /signals?search=depin&novelty=high` to
   find high-novelty signals matching a keyword.

4. **Generate ideas for a narrative**: `POST /chat` asking Seira to brainstorm
   product ideas for a specific narrative or trend.

5. **Analyze external content**: `POST /chat` with a `url` field. Seira will
   scrape the page and analyze it in the context of current Solana intelligence.

6. **Monitor ecosystem health**: `GET /stats` for a snapshot of activity levels,
   narrative counts, signal volume, and scrape freshness.
