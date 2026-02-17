# Solana Narrative Detection Backend

Detects emerging narratives and early signals within the Solana ecosystem. Scrapes web sources and Twitter KOLs, analyzes content with Gemini LLM to surface trends, and generates actionable product ideas for founders, investors, and ecosystem teams.

## Architecture

```
Scheduled Jobs          Scrapers              LLM Pipeline           Database
+-----------+      +---------------+      +------------------+      +----------+
| Daily Web |----->| Web Scraper   |----->| Stage 1: Signal  |----->| Signals  |
| Cron      |      | (10 sources)  |      | Extraction       |      +----------+
+-----------+      +---------------+      +------------------+            |
                                                                          v
+-----------+      +---------------+      +------------------+      +----------+
| 4h Twitter|----->| Twitter KOL   |----->| Stage 2: Synth.  |----->|Narratives|
| Cron      |      | (60 KOLs)    |      | + Idea Gen       |      +----------+
+-----------+      +---------------+      +------------------+            |
                                                                          v
                                          REST API <-----------------| Ideas  |
                                          /narratives, /ideas        +--------+
                                          /hackathons, /stats
```

## Quick Start

### Prerequisites

- Python 3.12+
- PostgreSQL 15+
- API keys: Gemini (free tier), ScrapeBatcher

### Setup

```bash
cd backend

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip3 install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env with your API keys and database URL
```

### Database Setup

```bash
# Create the database
createdb solana_narrative

# Run migrations
alembic upgrade head
```

### Run the Server

```bash
uvicorn app.main:app --reload --port 8000
```

The API will be available at `http://localhost:8000`. Interactive docs at `http://localhost:8000/docs`.

## API Endpoints

### Narratives

| Method | Path | Description |
|--------|------|-------------|
| GET | `/api/v1/narratives` | List narratives (filterable) |
| GET | `/api/v1/narratives/{id}` | Get narrative with ideas |

Query params for list: `is_active`, `min_confidence`, `tags`, `limit`, `offset`

### Ideas

| Method | Path | Description |
|--------|------|-------------|
| GET | `/api/v1/ideas` | List all ideas |

Query params: `narrative_id`, `tags`, `limit`, `offset`

### Hackathons

| Method | Path | Description |
|--------|------|-------------|
| GET | `/api/v1/hackathons` | Ideas for hackathon builders |

Returns ideas from active, high-velocity narratives or those tagged "hackathon".

### Stats

| Method | Path | Description |
|--------|------|-------------|
| GET | `/api/v1/stats` | Dashboard statistics |

Returns: active narratives count, total ideas, velocity scores, active builders, scrape times.

### Manual Triggers (Development)

| Method | Path | Description |
|--------|------|-------------|
| POST | `/api/v1/trigger/web-scrape` | Trigger web scrape cycle |
| POST | `/api/v1/trigger/twitter-scrape` | Trigger Twitter scrape cycle |
| POST | `/api/v1/trigger/synthesis` | Trigger narrative synthesis |
| POST | `/api/v1/trigger/coingecko-scrape` | Trigger CoinGecko trending scrape cycle |
| POST | `/api/v1/trigger/dune-scrape` | Trigger Dune on-chain trending scrape cycle |
| POST | `/api/v1/trigger/github-scrape` | Trigger GitHub Solana repos scrape cycle |

### Health

| Method | Path | Description |
|--------|------|-------------|
| GET | `/health` | Health check |

## Scheduled Jobs

| Job | Schedule | Description |
|-----|----------|-------------|
| Web Scraper | Every 3 hours | Scrapes Solana ecosystem web sources + deep links |
| Twitter Scraper | Every 24 hours | Fetches latest tweets from 59+ Solana KOLs |
| Narrative Synthesis | Daily 3:00 UTC | Synthesizes signals into narratives + ideas |
| Idea Backfill | Hourly | Tops up narratives with &lt; 3 ideas |
| CoinGecko Trending | Every 1 hour | Fetches trending coins from CoinGecko API and stores market signals |
| Dune On-chain Trending | Every 3 hours | Executes Dune queries for on-chain program/wallet activity spikes |
| GitHub Solana Repos | Every 6 hours | Fetches recently updated Solana repos from GitHub API |

## Data Sources

### Web Sources (10)
- Solana News, Helius Blog, Solana Mobile Blog (high priority, deep links)
- Reddit r/solana, Reddit Solana Search (JSON feeds)
- Solana Homepage, Solana Compass (medium priority)
- Arkham Research, Electric Capital (low priority, deep links)
- CoinGecko 2025 Annual Report (PDF extraction)

### On-chain & Market APIs
- **CoinGecko (API):** Trending coins endpoint for market momentum around Solana-related assets.
- **Dune Analytics (API):** Configurable queries for Solana program and wallet activity spikes.
- **GitHub (API):** Solana-related repositories updated recently across Rust/TypeScript/JS/Python.

### Twitter KOLs (60)
Verified Solana KOLs including @toly, @rajgokal, @heliuslabs, @phantom, @MagicEden, etc.
Full list in `data/verified_solana_kols.json`.

## LLM Pipeline

Uses Gemini 2.0 Flash (free tier) via LiteLLM with dual rate limiting:
- 15 requests/minute
- 1500 requests/day

### Stage 1: Signal Extraction
Each piece of scraped content is analyzed individually. The LLM extracts structured signals: title, description, signal type, novelty rating, evidence, related projects, and tags.

### Stage 2: Narrative Synthesis
All signals from the past 14 days are aggregated and sent to the LLM. It identifies cross-source narratives and generates 3-5 product ideas per narrative with problem/solution descriptions, Solana-specific justification, and market signals.

## Velocity Score

Narratives are scored for momentum:

```
velocity = signal_count * 0.4 + source_diversity * 0.3 + recency * 0.2 + novelty * 0.1
```

- Decays 10% per day without new signals
- Narratives inactive after 7 days without signals

## Project Structure

```
backend/
├── app/
│   ├── main.py              # FastAPI entry point
│   ├── config.py             # Settings from .env
│   ├── database.py           # SQLAlchemy async engine
│   ├── models/               # ORM models (6 tables)
│   ├── schemas/              # Pydantic response schemas
│   ├── api/                  # REST endpoints
│   ├── scrapers/             # Web + Twitter scrapers
│   ├── analyzers/            # LLM client, signal extractor, synthesizer
│   ├── schedulers/           # APScheduler cron jobs
│   └── utils/                # Logger, helpers
├── alembic/                  # Database migrations
├── tests/                    # Unit + integration tests
├── requirements.txt
└── .env
```

## Testing

```bash
source venv/bin/activate
pytest tests/ -v
```

## Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `DATABASE_URL` | PostgreSQL connection string | required |
| `SCRAPEBADGER_API_KEY` | ScrapeBatcher API key | required |
| `GEMINI_API_KEY` | Google Gemini API key | required |
| `ENVIRONMENT` | development / production | development |
| `LOG_LEVEL` | Logging level | INFO |
