# Company Intel AI

AI-powered company intelligence app for VC analysts. Admin logs in, creates a company profile, and gets an AI-generated report (summary, 5 competitors with strength scores, market positioning, investment thesis, risks, "why this matters") plus a **Deal Attractiveness Score (0–100)** and a one-page **AI Investment Memo**.

Built for the Revo Capital tech intern case.

## What's inside

- **Frontend**: React + Vite + TypeScript + Tailwind + shadcn/ui — http://localhost:5173
- **Backend**: FastAPI + SQLAlchemy 2.0 (async) + Alembic — http://localhost:8000 · Swagger: http://localhost:8000/docs · Metrics: http://localhost:8000/metrics
- **Database**: PostgreSQL 16
- **AI**: Gemini 2.5 Flash (structured output)
- **Observability**: Prometheus (http://localhost:9090) + Grafana (http://localhost:3000, admin/admin)

## Differentiating VC feature

**Deal Attractiveness Score** — a 0–100 score broken down across 5 weighted factors (Market 30%, Team 25%, Traction 20%, Moat 15%, Fund Fit 10%) plus an **AI-generated one-page Investment Memo** (Markdown, sectioned: Overview, Why Now, Thesis, Risks, Recommendation). Both are produced in the same Gemini call as the rest of the report; the score total is computed deterministically server-side from the model's per-factor breakdown.

## Run locally with Docker Compose

```bash
cp api/.env.example api/.env
# put your real Gemini key in api/.env (AI_API_KEY=...)
docker compose up --build
```

Then:
- UI: http://localhost:5173 — log in with `admin` / `Revo123456`
- Swagger: http://localhost:8000/docs
- Metrics: http://localhost:8000/metrics
- Prometheus: http://localhost:9090 — Status → Targets shows `company-intel-api` UP
- Grafana: http://localhost:3000 — admin/admin — dashboard "Company Intel — Service" is preloaded with Prometheus as the default datasource

## Run locally without Docker (hybrid dev)

Recommended for fast iteration.

```bash
# 1) Postgres + Prometheus + Grafana from compose
docker compose up -d db prometheus grafana

# 2) backend
cd api
python3.13 -m venv .venv && source .venv/bin/activate
pip install -e ".[dev]"
cp .env.example .env  # set AI_API_KEY
alembic upgrade head
uvicorn app.main:app --reload --port 8000

# 3) frontend (new terminal)
cd ui && cp .env.example .env
npm install && npm run dev
```

> **macOS note for PDF export**: WeasyPrint needs `pango`, `cairo`, `gdk-pixbuf` installed via Homebrew. Then export `DYLD_FALLBACK_LIBRARY_PATH=/opt/homebrew/lib` before starting the API or running tests. The Docker image installs these libs directly so `docker compose up --build` works without this step. See `api/README.md` for details.

## Environment variables

`api/.env`:

| Name | Purpose |
|---|---|
| `DATABASE_URL` | Postgres connection (asyncpg driver) |
| `JWT_SECRET` | Signing key for the session JWT |
| `JWT_EXPIRES_MINUTES` | Cookie/JWT TTL (default 720) |
| `ADMIN_USERNAME` / `ADMIN_PASSWORD` | Hardcoded admin creds (defaults match the spec) |
| `AI_PROVIDER` | `gemini` (default) or `stub` (tests) |
| `AI_API_KEY` | Provider key |
| `AI_MODEL` | Default `gemini-2.5-flash` |
| `CORS_ORIGINS` | Comma-separated allowlist (default `http://localhost:5173`) |

`ui/.env`:

| Name | Purpose |
|---|---|
| `VITE_API_BASE_URL` | Backend base URL (default `http://localhost:8000`) |

## Verify observability

1. After login, create a company. Wait for the report.
2. http://localhost:8000/metrics — `companies_created_total` should be `>= 1`, `ai_generation_total{result="success",kind="report"}` `>= 1`.
3. http://localhost:9090/targets — `company-intel-api` is `UP`.
4. http://localhost:3000 — open the **Company Intel — Service** dashboard. The AI panels reflect the activity.

## Tests

```bash
# backend
cd api && DYLD_FALLBACK_LIBRARY_PATH=/opt/homebrew/lib pytest -v
# frontend
cd ui && npm test
```

Backend: 27 tests covering auth, CRUD, AI service, scoring, metrics, PDF, compare, notes.
Frontend: 5 tests on critical components (`StatusPill`, `ScoreGauge`).

## Project structure

```
company-intel-ai/
├── api/                    # FastAPI service (alembic, models, services, routes, tests)
├── ui/                     # Vite + React frontend
├── docker-compose.yml      # db, api, ui, prometheus, grafana
├── prometheus.yml
├── grafana-provisioning/
└── docs/                   # design spec + plan
```

See [`ARCHITECTURE.md`](./ARCHITECTURE.md) for system design and trade-offs.
