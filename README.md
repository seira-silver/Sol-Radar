# Sol Radar

**Detect emerging narratives and early signals within the Solana ecosystem.**

Sol Radar is an automated intelligence tool that continuously scrapes, analyzes, and synthesizes data from across the Solana ecosystem — news outlets, research platforms, community forums, and key opinion leaders on X (Twitter) — to surface emerging narratives, rank them by momentum, and generate actionable product ideas for builders.

> **Live:** [https://sol-radar.xyz](https://sol-radar.xyz)

---

## Table of Contents

- [How It Works](#how-it-works)
- [Data Sources](#data-sources)
- [Pipeline: From Raw Data to Narratives](#pipeline-from-raw-data-to-narratives)
  - [Phase 1 — Scraping](#phase-1--scraping)
  - [Phase 2 — Signal Extraction (Stage 1)](#phase-2--signal-extraction-stage-1)
  - [Phase 3 — Narrative Synthesis (Stage 2)](#phase-3--narrative-synthesis-stage-2)
  - [Velocity Scoring & Ranking](#velocity-scoring--ranking)
- [Architecture](#architecture)
- [Tech Stack](#tech-stack)
- [Getting Started](#getting-started)
  - [Prerequisites](#prerequisites)
  - [Backend Setup](#backend-setup)
  - [Frontend Setup](#frontend-setup)
  - [Running in Production](#running-in-production)
- [Environment Variables](#environment-variables)
- [API Endpoints](#api-endpoints)
- [Scheduler Jobs](#scheduler-jobs)
- [Project Structure](#project-structure)
- [Seira AI Agent](#seira-ai-agent)
- [License](#license)

---

## How It Works

Sol Radar operates a three-stage pipeline that runs on automated schedules:

1. **Scrape** — Collect raw content from 12+ web sources and 50+ verified Solana KOLs on X.
2. **Extract** — An LLM analyzes each piece of content individually and extracts structured **signals** (on-chain activity, developer moves, social momentum, research insights).
3. **Synthesize** — The LLM aggregates all recent signals across sources and synthesizes high-level **narratives**, assigns confidence ratings, and generates **product ideas** (hackathon-ready) for each narrative.

All narratives are scored by a **velocity algorithm** and ranked, so the most fast-moving and well-sourced narratives surface first.

---

## Data Sources

Sol Radar pulls from a diverse set of sources across the Solana ecosystem:

### Ecosystem & News

| Source | URL | Type | Priority |
|--------|-----|------|----------|
| Solana News | https://solana.com/news | Web (deep-linked) | High |
| Solana Homepage | https://solana.com/ | Web | Medium |
| Solana Compass | https://solanacompass.com/ | Web | Medium |
| Helius Blog | https://www.helius.dev/blog | Web (deep-linked) | High |
| Solana Mobile Blog | https://blog.solanamobile.com/ | Web (deep-linked) | High |

### Research & Reports

| Source | URL | Type | Priority |
|--------|-----|------|----------|
| Messari | https://messari.io/ | Web (deep-linked) | High |
| Arkham Research | https://info.arkm.com/research | Web (deep-linked) | Low |
| Electric Capital | https://www.electriccapital.com/ | Web (deep-linked) | Low |
| CoinGecko 2025 Report | coingecko.com/reports/2025 (PDF) | PDF | Low |

### Community & Social

| Source | URL | Type | Priority |
|--------|-----|------|----------|
| Reddit r/solana | https://www.reddit.com/r/solana.json | Reddit JSON | High |
| Reddit Solana Search | https://www.reddit.com/search.json?q=solana | Reddit JSON | Medium |

### X (Twitter) — Verified Solana KOLs

Tweets are fetched via the [ScrapeBadger](https://scrapebadger.com) API from **59 verified Solana key opinion leaders**, including:

- **Core Team:** @solana, @toly, @rajgokal, @solanalabs, @SolanaConf
- **Infrastructure:** @heliuslabs, @Quicknode, @PythNetwork, @switchboardxyz, @GenesysGo
- **DeFi:** @DriftProtocol, @marginfi, @jito_sol, @Lifinity_io, @port_finance, @ApricotFinance, @debridgefinance, @syrupfi
- **Consumer & NFTs:** @phantom, @MagicEden, @tensor_hq, @solflare, @Claynosaurz, @drip_haus, @exchgART, @metaplex
- **Gaming & DePIN:** @staratlas, @AuroryProject, @Hivemapper, @helium, @rendernetwork
- **Mobile:** @solanamobile, @vibhu
- **Analytics:** @birdeye_so, @SolanaFloor, @gmgnai, @bullx_io, @Rugcheckxyz
- **KOLs & Analysts:** @SOLBigBrain, @waleswoosh, @banditxbt, @SolanaLegend, @SolportTom, @Harri_obi

The full list is maintained in [`data/verified_solana_kols.json`](data/verified_solana_kols.json).

---

## Pipeline: From Raw Data to Narratives

### Phase 1 — Scraping

The scraping layer collects raw content and stores it in the `scraped_content` table with `analysis_status = 'pending'`.

**Web Scraper** (`app/scrapers/web_scraper.py`):
- Fetches HTML pages and follows article links up to depth 2 (max 20 links per source) for deep-linked sources.
- Extracts main content using BeautifulSoup with custom handlers for Messari's Next.js-heavy pages.
- Parses Reddit JSON feeds for posts and comments.
- Extracts text from PDF reports (CoinGecko), filtering for Solana-relevant content.
- Deduplicates by SHA-256 content hash — the same article is never stored twice.

**Twitter Scraper** (`app/scrapers/twitter_scraper.py`):
- Fetches latest tweets from each KOL via the ScrapeBadger API.
- Rate-limited to 5 requests/minute (free tier).
- Prefers original tweets over retweets.
- Each tweet is stored as a JSON payload in `scraped_content`.

### Phase 2 — Signal Extraction (Stage 1)

**Signal Extractor** (`app/analyzers/signal_extractor.py`):

Each pending piece of scraped content is analyzed individually by an LLM:

1. The content and its source metadata are formatted into a structured prompt.
2. The LLM extracts zero or more **signals** — discrete observations about ecosystem trends.
3. Each signal is classified by:
   - **Type**: `onchain` | `developer` | `social` | `research` | `mobile` | `other`
   - **Novelty**: `high` | `medium` | `low`
   - **Evidence**: supporting facts from the content
   - **Related Projects**: Solana projects mentioned
   - **Tags**: categorization labels
4. Signals are stored in the `signals` table, linked back to their source content.

The extractor uses a status state machine to prevent double-processing:
```
pending → processing → completed ✅
pending → processing → failed (retryable up to 3 attempts)
pending → skipped (content too short or invalid)
```

### Phase 3 — Narrative Synthesis (Stage 2)

**Narrative Synthesizer** (`app/analyzers/narrative_synthesizer.py`):

All signals from the past 14 days are aggregated and fed to the LLM:

1. Signals are grouped by source name for context.
2. The LLM synthesizes high-level **narratives** — emerging themes supported by multiple signals across sources.
3. For each narrative, the LLM generates:
   - A **title** and **summary**
   - A **confidence** level (`high` | `medium` | `low`) with reasoning
   - **Key evidence** — the strongest supporting data points
   - **Tags** for categorization
   - **3–5 product ideas** — actionable concepts for hackathons or builders, each with a problem statement, proposed solution, why Solana is the right platform, scale potential, and market signals
4. Narratives are upserted (matched by title), with traceability links to the signals that support them.
5. Stale narratives (no supporting signals in 7+ days) are auto-deactivated.

### Velocity Scoring & Ranking

Every active narrative receives a **velocity score** that determines its ranking:

```
velocity_score = (
    min(signal_count, 50)    × 0.4    Signal volume (capped)
  + min(source_diversity, 10) × 0.3    Unique sources (capped)
  + recency_factor            × 0.2    Decays over time
  + novelty_avg               × 0.1    Based on confidence level
)
```

| Factor | Weight | Description |
|--------|--------|-------------|
| Signal Count | 40% | Total signals supporting the narrative, capped at 50 |
| Source Diversity | 30% | Number of distinct sources, capped at 10 |
| Recency | 20% | Decays by `VELOCITY_DECAY_RATE` per day since last signal |
| Novelty | 10% | Average of confidence scores (high=1.0, medium=0.6, low=0.3) |

Narratives are sorted by `velocity_score DESC, created_at DESC` across the dashboard.

---

## Architecture

```
┌──────────────────────────────────────────────────────┐
│                     FRONTEND                         │
│              Next.js 15 + Tailwind CSS               │
│                                                      │
│  ┌──────────┐  ┌──────────┐  ┌────────────────────┐  │
│  │Narratives│  │ Signals  │  │  Hackathon Ideas   │  │
│  │   Tab    │  │   Tab    │  │       Tab          │  │
│  └────┬─────┘  └────┬─────┘  └────────┬───────────┘  │
│       │              │                 │              │
│       └──────────────┼─────────────────┘              │
│                      │  HTTP (paginated)              │
└──────────────────────┼───────────────────────────────┘
                       │
              ┌────────▼────────┐
              │   FastAPI (v1)  │
              │  REST API Layer │
              └────────┬────────┘
                       │
        ┌──────────────┼──────────────┐
        │              │              │
   ┌────▼────┐   ┌─────▼─────┐  ┌────▼────┐
   │ Signals │   │Narratives │  │  Ideas  │
   │   API   │   │    API    │  │   API   │
   └────┬────┘   └─────┬─────┘  └────┬────┘
        │              │              │
        └──────────────┼──────────────┘
                       │
              ┌────────▼────────┐
              │   PostgreSQL    │
              │  (async via     │
              │   asyncpg)      │
              └────────┬────────┘
                       │
        ┌──────────────┼──────────────┐
        │              │              │
   ┌────▼────┐   ┌─────▼─────┐  ┌────▼────┐
   │ Stage 1 │   │  Stage 2  │  │Velocity │
   │ Signal  │   │ Narrative │  │ Scoring │
   │Extractor│   │Synthesizer│  │  Engine  │
   └────┬────┘   └─────┬─────┘  └─────────┘
        │              │
        └──────┬───────┘
               │
        ┌──────▼──────┐
        │  LLM Layer  │
        │  (LiteLLM)  │
        │ xAI / Gemini│
        └──────┬──────┘
               │
        ┌──────▼──────┐
        │  Schedulers  │
        │ (APScheduler)│
        └──────┬──────┘
               │
     ┌─────────┼─────────┐
     │         │         │
┌────▼───┐ ┌──▼───┐ ┌───▼───┐
│  Web   │ │  X   │ │Reddit │
│Scraper │ │Scraper│ │ Feed  │
└────────┘ └──────┘ └───────┘
```

---

## Tech Stack

| Layer | Technology |
|-------|------------|
| Frontend | Next.js 15, React, TypeScript, Tailwind CSS |
| Backend | Python 3.12, FastAPI, SQLAlchemy (async), Pydantic |
| Database | PostgreSQL + asyncpg |
| LLM | LiteLLM → xAI Grok / Google Gemini |
| Scraping | httpx, BeautifulSoup, lxml, pypdf, ScrapeBadger API |
| Scheduling | APScheduler |
| Migrations | Alembic |
| Process Manager | PM2 |

---

## Getting Started

### Prerequisites

- Python 3.12+
- Node.js 18+
- PostgreSQL 14+
- API keys for at least one LLM provider (xAI or Google Gemini)
- (Optional) ScrapeBadger API key for X/Twitter scraping

### Backend Setup

```bash
cd backend

# Create virtual environment and install dependencies
make setup

# Copy and configure environment variables
cp .env.example .env
# Edit .env with your database URL, API keys, etc.

# Run database migrations
make migrate

# Start the development server (http://localhost:8000)
make dev
```

### Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Copy and configure environment variables
cp .env.example .env
# Ensure NEXT_PUBLIC_API_URL points to your backend (default: http://localhost:8000/api/v1)

# Start the development server (http://localhost:3000)
npm run dev
```

### Running in Production

**Backend** (via PM2):

```bash
cd backend
make start       # Start with PM2
make restart     # Restart
make stop        # Stop
make deploy      # Pull + migrate + restart (one command)
```

**Frontend** (via Next.js):

```bash
cd frontend
npm run build
npm start
```

---

## Environment Variables

### Backend (`backend/.env`)

| Variable | Description | Default |
|----------|-------------|---------|
| `DATABASE_URL` | PostgreSQL connection string | `postgresql+asyncpg://postgres:admin@localhost:5432/solana_narrative` |
| `LLM_MODEL` | LLM model identifier | `xai/grok-4-1-fast-non-reasoning` |
| `XAI_API_KEY` | xAI (Grok) API key | — |
| `GEMINI_API_KEY` | Google Gemini API key | — |
| `SCRAPEBADGER_API_KEY` | ScrapeBadger API key (for X scraping) | — |
| `ENVIRONMENT` | `development` or `production` | `development` |
| `LOG_LEVEL` | Logging level | `INFO` |

### Frontend (`frontend/.env`)

| Variable | Description | Default |
|----------|-------------|---------|
| `NEXT_PUBLIC_API_URL` | Backend API base URL | `http://localhost:8000/api/v1` |

---

## API Endpoints

All endpoints are under `/api/v1`.

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/landing` | Bundled stats + narratives (with nested ideas) |
| `GET` | `/signals` | List signals — filterable by type, novelty, source, tags, date range |
| `GET` | `/signals/{id}` | Single signal with source metadata |
| `GET` | `/narratives` | List narratives sorted by velocity score |
| `GET` | `/narratives/hackathons` | Hackathon-tagged narratives |
| `GET` | `/narratives/{id}` | Narrative detail with ideas, sources, and supporting signals |
| `GET` | `/ideas` | List product ideas |
| `GET` | `/hackathons` | Ideas from high-velocity or hackathon narratives |
| `GET` | `/stats` | Dashboard statistics |
| `POST` | `/chat` | Chat with Seira — SSE streaming response |

All list endpoints support `limit` and `offset` query parameters for pagination.

---

## Scheduler Jobs

| Job | Schedule | Pipeline |
|-----|----------|----------|
| **Web Scrape** | Daily at 2 AM UTC | Scrape all web sources → Extract signals → Synthesize narratives |
| **Twitter Scrape** | Every 72 hours | Scrape KOL tweets → Extract signals → Synthesize narratives |
| **Narrative Synthesis** | Every 14 days at 3 AM UTC | Re-synthesize all narratives from aggregated signals |

---

## Project Structure

```
narration/
├── backend/
│   ├── app/
│   │   ├── api/               # FastAPI route handlers
│   │   ├── analyzers/         # LLM-powered signal extraction & narrative synthesis
│   │   ├── models/            # SQLAlchemy ORM models
│   │   ├── schemas/           # Pydantic response schemas
│   │   ├── scrapers/          # Web, Twitter, and Reddit scrapers
│   │   ├── schedulers/        # APScheduler job definitions
│   │   ├── utils/             # Helpers and logger
│   │   ├── config.py          # Pydantic settings
│   │   ├── database.py        # Async SQLAlchemy engine
│   │   └── main.py            # FastAPI app entry point
│   ├── alembic/               # Database migrations
│   ├── data/                  # LLM prompt templates
│   ├── pm2.config.js          # PM2 process manager config
│   ├── Makefile               # Common commands
│   └── requirements.txt       # Python dependencies
├── frontend/
│   ├── app/                   # Next.js app router (pages)
│   ├── components/            # React UI components
│   ├── hooks/                 # Custom React hooks (infinite scroll, etc.)
│   ├── lib/                   # API client, types, constants
│   └── styles/                # Global styles
├── data/
│   └── verified_solana_kols.json  # Tracked X/Twitter KOL handles
└── README.md
```

---

## Seira AI Agent

Sol Radar includes **Seira**, a built-in AI research analyst powered by Grok. Seira has two interaction modes:

### Human-to-AI Chat (UI)

A floating chat interface is available on every page of the dashboard (bottom-right corner). Users can:

- Ask Seira about active narratives, signals, and product ideas
- Paste a URL for Seira to scrape, analyze, and relate to current Solana intelligence
- Generate and validate product ideas with PMF reasoning grounded in real signals
- Get early alpha backed by cross-source evidence from Sol Radar's database

Seira cites specific narrative titles, signal evidence, and confidence levels from the live database in every response. Chat history persists in the browser via localStorage.

### Agent-to-Agent Communication

External AI agents can interact with Sol Radar programmatically via the REST API and the Seira chat endpoint. A machine-readable capability spec is published at:

> **SKILL.md:** [https://sol-radar.vercel.app/SKILL.md](https://sol-radar.vercel.app/SKILL.md)

The SKILL.md documents all available API endpoints, request/response schemas, the SSE streaming chat protocol, data models, and example usage patterns. Agents can use it to:

- Fetch the latest Solana narratives and signals (`GET /api/v1/narratives`, `GET /api/v1/signals`)
- Validate product ideas against current narratives via Seira (`POST /api/v1/chat`)
- Monitor ecosystem health and signal volume (`GET /api/v1/stats`)
- Analyze external URLs in the context of current Solana intelligence

---

## License

This project is for research and educational purposes.
