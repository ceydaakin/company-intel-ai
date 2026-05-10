# Architecture

## System structure

```
[ React UI ] ──HTTPS──▶ [ FastAPI ] ──asyncpg──▶ [ Postgres 16 ]
                          │
                          ├── Gemini 2.5 Flash (structured output)
                          ├── /metrics (Prometheus exposition)
                          ▼
                       [ Prometheus ] ◀── Grafana (provisioned dashboard)
```

All services run via Docker Compose: `db`, `api`, `ui`, `prometheus`, `grafana`. Local dev can run api/ui outside Docker against the dockerized Postgres + observability stack.

## Frontend (`ui/`)

Vite + React 18 + TypeScript + Tailwind + shadcn/ui. State: `@tanstack/react-query` for server state, plus a small AuthContext for session. Routing via `react-router-dom`.

Pages: `/login`, `/` (dashboard), `/companies/:id`, `/compare`. A `ProtectedRoute` wrapper checks `/api/auth/me` before rendering the AppShell.

Key components live under `src/components/companies/`: `CreateCompanyModal`, `CompanyTable`, `CompanyFilters`, `ScoreGauge`, `CompetitorGrid`, `InvestmentMemo`, `NotesPanel`, `CompareView`, `BulletList`, `EmptyState`, `StatusPill`.

## Backend (`api/`)

FastAPI with a layered structure:

- `app/api/routes/` — HTTP handlers, thin
- `app/services/` — business logic; `ai/` contains the provider interface and Gemini implementation
- `app/models/` — SQLAlchemy models
- `app/schemas/` — Pydantic DTOs (the same schemas drive Gemini's `response_schema`)
- `app/db/` — async engine, session, and a cross-dialect type module (`GUID`, `JSONB` with SQLite fallback for tests)
- `app/observability/` — custom Prometheus counters and a histogram

Auth is a JWT signed with HS256 and set as an httpOnly cookie. A simple `require_admin` dependency reads the cookie on protected routes.

## Database

```
companies (id, name, hq, website, context, market_tag, summary[],
           investment_thesis[], risks[], why_matters[],
           score_total, score_breakdown, memo_markdown,
           status, error_message, favorite, created_at, updated_at)
competitors (id, company_id, name, summary[], strength_score, position)
notes       (id, company_id, body, created_at)
```

JSONB columns hold the bullet lists and the score breakdown. Indexes on `created_at`, `name`, `market_tag`, `favorite`. Migrations are managed with Alembic.

For tests, a custom `JSONB().with_variant(JSON(), "sqlite")` and `GUID` TypeDecorator let SQLAlchemy's metadata create the same schema on an in-memory SQLite database.

## AI generation flow

1. UI submits `POST /api/companies` with `{name, hq?, website?, context?}`.
2. The handler calls `report_service.create_with_report(...)`:
   1. Inserts a row with `status='generating'`.
   2. Synchronously awaits a single Gemini 2.5 Flash call configured with `response_schema=CompanyReport` (a Pydantic model). The SDK returns a parsed `CompanyReport`.
   3. Persists the 5 competitors, the bullets, the market tag, and the memo. Computes `score_total` server-side from the breakdown.
   4. Sets `status='ready'`, returns the full payload.
3. On any AI exception, the row is left with `status='failed'`, an `error_message`, and the request returns 502 with a clear message. The UI toasts and offers retry.

`POST /api/companies/{id}/regenerate` reuses the same path on an existing row.

## Observability flow

`prometheus-fastapi-instrumentator` exposes default HTTP request metrics on `/metrics`. We register custom counters and a histogram in `app/observability/metrics.py`:

- `companies_created_total`
- `report_regenerations_total`
- `ai_generation_total{result, kind}`
- `ai_generation_duration_seconds` (histogram)
- `pdf_exports_total`
- `errors_total{kind}`

Prometheus is configured to scrape `api:8000/metrics` every 5s. Grafana is provisioned with a Prometheus datasource and a dashboard (`Company Intel — Service`) showing request rate, p95 latency, AI success/failure totals, and AI duration p95.

## Design decisions

- **Synchronous AI call inside the request**: Gemini Flash typically returns under 10s for our prompt size. A background queue would add complexity without user-visible benefit at this scale. The trade-off is owned and documented — a worker would be the obvious next step if latency grows.
- **Pydantic doubling as Gemini schema**: `CompanyReport` is the source of truth for both the API contract and the model's structured output. One schema, no drift.
- **JWT in httpOnly cookie**: protects against XSS token theft, simpler than localStorage + Authorization-header juggling, and survives refresh.
- **`AIProvider` protocol**: lets the test suite use a stub without monkey-patching, and makes swapping Gemini for OpenAI/Anthropic a one-file change.
- **Server-computed `score_total`**: weights live in `app/services/ai/scoring.py` and are documented; the model only produces the breakdown. This keeps the headline number deterministic and auditable.
- **Cross-dialect `GUID` and `JSONB`**: lets the same models drive Postgres in production and SQLite in tests with no migrations gymnastics.

## Differentiating VC feature

The **Deal Attractiveness Score + Investment Memo** ride along on the same Gemini call. The breakdown is part of the structured output schema; the memo is a markdown field. Score weights are explicit (Market 30, Team 25, Traction 20, Moat 15, Fund Fit 10) and shown to the user as 5 bars, so the headline number never feels like a black box. The memo renders via `react-markdown` in the report's "Investment Memo" tab and is included in the PDF export.
