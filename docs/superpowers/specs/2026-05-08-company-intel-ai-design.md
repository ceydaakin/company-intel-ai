# Design Spec — Company Intel AI

**Date:** 2026-05-08
**Status:** Approved
**Source:** Revo Capital Tech Intern Case Study (PDF, 2026-05-08)

---

## 1. Objective

Build a lightweight, well-structured full-stack web application where an admin user logs in, creates company profiles, and views AI-generated company intelligence reports (summary, 5 competitors, market positioning, investment thesis, risks, "why this matters"), with comparison, notes, PDF export, history with search/filter/favorites, and a differentiating VC feature: **Deal Attractiveness Score + AI Investment Memo**.

The application must feel like a real internal VC tool, not a technical demo.

## 2. Decisions Locked

| Area | Decision | Rationale |
|---|---|---|
| Folder | `~/GitHub/company-intel-ai` | Product-named, sibling to other Sentez projects |
| AI provider | Gemini 2.5 Flash | Native structured output, fast, cheap, hinted in spec |
| Frontend | Vite + React + TypeScript + Tailwind + shadcn/ui | Polished UI with minimum custom CSS work |
| Backend | Python + FastAPI + SQLAlchemy 2.0 (async) + Alembic | Required by spec |
| Database | PostgreSQL 16 | Spec preference |
| Auth | JWT in httpOnly cookie (admin / Revo123456 hardcoded) | Demo-grade, but survives refresh and avoids XSS token theft |
| Observability | prometheus-fastapi-instrumentator + custom counters; Grafana with provisioned datasource + starter dashboard | Spec requirement |
| Dev mode | Hybrid: Postgres + Prometheus + Grafana in Docker; api/ui run locally during dev. Full `docker compose up --build` brings everything up for eval. | Fast iteration, still meets eval expectation |
| Extra VC feature | **Deal Attractiveness Score (0–100, 5-factor breakdown) + AI Investment Memo (one-page)** | Two artifacts, high VC value, visually impactful |

## 3. Project Structure

```
company-intel-ai/
├── api/
│   ├── app/
│   │   ├── main.py                       # FastAPI entry, middleware, router mount
│   │   ├── core/
│   │   │   ├── config.py                 # pydantic-settings (env vars)
│   │   │   ├── security.py               # JWT encode/decode, cookie helpers
│   │   │   └── logging.py                # structured logging setup
│   │   ├── db/
│   │   │   ├── session.py                # async engine + session
│   │   │   └── base.py                   # declarative base
│   │   ├── models/
│   │   │   ├── company.py                # Company (incl. score fields, status)
│   │   │   ├── competitor.py             # Competitor (FK -> Company)
│   │   │   └── note.py                   # Note (FK -> Company)
│   │   ├── schemas/
│   │   │   ├── company.py
│   │   │   ├── report.py                 # Pydantic schemas — also fed to Gemini structured output
│   │   │   ├── compare.py
│   │   │   └── auth.py
│   │   ├── services/
│   │   │   ├── ai/
│   │   │   │   ├── provider.py           # AIProvider protocol (swap-in interface)
│   │   │   │   ├── gemini_client.py      # Gemini 2.5 Flash impl
│   │   │   │   ├── report_generator.py   # company report
│   │   │   │   ├── scoring.py            # deal attractiveness score
│   │   │   │   └── memo.py               # investment memo
│   │   │   └── pdf.py                    # WeasyPrint export
│   │   ├── api/
│   │   │   └── routes/
│   │   │       ├── auth.py               # POST /login, POST /logout, GET /me
│   │   │       ├── companies.py          # CRUD + favorite + regenerate
│   │   │       ├── reports.py            # GET report, regenerate, export PDF
│   │   │       ├── compare.py            # POST /compare {a_id, b_id}
│   │   │       ├── notes.py              # POST/DELETE notes
│   │   │       └── meta.py               # /healthz
│   │   └── observability/
│   │       └── metrics.py                # custom Prometheus counters + histograms
│   ├── alembic/                          # migrations
│   ├── tests/
│   ├── pyproject.toml
│   ├── Dockerfile
│   └── .env.example
├── ui/
│   ├── src/
│   │   ├── main.tsx
│   │   ├── App.tsx                       # router
│   │   ├── lib/
│   │   │   ├── api.ts                    # axios client + typed endpoints
│   │   │   ├── auth.tsx                  # AuthContext + ProtectedRoute
│   │   │   └── types.ts                  # shared response types
│   │   ├── components/
│   │   │   ├── ui/                       # shadcn primitives (button, dialog, input, …)
│   │   │   ├── layout/
│   │   │   │   ├── AppShell.tsx
│   │   │   │   └── TopBar.tsx
│   │   │   └── companies/
│   │   │       ├── CreateCompanyModal.tsx
│   │   │       ├── CompanyTable.tsx
│   │   │       ├── CompanyFilters.tsx
│   │   │       ├── EmptyState.tsx
│   │   │       ├── ReportView.tsx
│   │   │       ├── CompetitorGrid.tsx
│   │   │       ├── ScoreGauge.tsx
│   │   │       ├── InvestmentMemo.tsx
│   │   │       ├── NotesPanel.tsx
│   │   │       └── CompareView.tsx
│   │   ├── pages/
│   │   │   ├── Login.tsx
│   │   │   ├── Dashboard.tsx             # main page (history + create)
│   │   │   ├── CompanyDetail.tsx
│   │   │   └── Compare.tsx
│   │   └── styles/index.css
│   ├── index.html
│   ├── vite.config.ts
│   ├── tailwind.config.ts
│   ├── package.json
│   ├── Dockerfile
│   └── .env.example
├── docker-compose.yml
├── prometheus.yml
├── grafana-provisioning/
│   ├── datasources/datasource.yml
│   └── dashboards/{dashboard.yml, company-intel.json}
├── README.md
├── ARCHITECTURE.md
└── docs/superpowers/specs/               # this spec lives here
```

## 4. Database Schema

```sql
-- companies
id              UUID PK
name            TEXT NOT NULL
hq              TEXT
website         TEXT
context         TEXT                       -- optional user-provided context
market_tag      TEXT                       -- AI-generated market positioning
summary         JSONB                      -- 4-5 bullets
investment_thesis JSONB                    -- bullets
risks           JSONB                      -- bullets
why_matters     JSONB                      -- bullets
score_total     INT                        -- 0..100
score_breakdown JSONB                      -- {market, team, moat, traction, fund_fit}
memo_markdown   TEXT                       -- one-page investment memo
status          TEXT                       -- 'generating' | 'ready' | 'failed'
error_message   TEXT
favorite        BOOLEAN DEFAULT false
created_at      TIMESTAMPTZ DEFAULT now()
updated_at      TIMESTAMPTZ

-- competitors
id              UUID PK
company_id      UUID FK -> companies.id ON DELETE CASCADE
name            TEXT NOT NULL
summary         JSONB                      -- 4-5 bullets
strength_score  INT                        -- 0..100
position        INT                        -- 1..5

-- notes
id              UUID PK
company_id      UUID FK -> companies.id ON DELETE CASCADE
body            TEXT NOT NULL
created_at      TIMESTAMPTZ DEFAULT now()
```

Indexes: `companies(created_at DESC)`, `companies(name)`, `companies(market_tag)`, `companies(favorite)`.

## 5. AI Generation Flow

1. UI submits `POST /api/companies {name, hq, website, context?}` and shows an in-modal loading state.
2. Backend inserts row with `status='generating'` (so a partial record exists if anything crashes mid-call), then **synchronously awaits** the AI call within the same request.
3. AI call via `report_generator.generate(payload)`:
   - Single Gemini 2.5 Flash call with `response_schema` matching the Pydantic `CompanyReport` schema (summary, competitors[5], market_tag, thesis, risks, why_matters, score_breakdown, memo_markdown).
   - `score_total` computed server-side from `score_breakdown` weights, not asked from the model — keeps it deterministic.
4. On success: persist competitors, update company row (`status='ready'`, all AI fields), increment `ai_generation_total{result="success"}`, record `ai_generation_duration_seconds`. Endpoint returns the full report payload (201).
5. On failure: `status='failed'`, `error_message=...`, increment `ai_generation_total{result="failure"}`. Endpoint returns 502 with a clear message; UI toasts and offers retry. The failed row remains visible in the history with a "Retry" badge.
6. **Regenerate** endpoint reuses step 3+ on an existing row.
7. The synchronous model is fine because Gemini 2.5 Flash typically responds in under 10s for this prompt size; if latency becomes a problem we can move to a background worker later (out of scope for v1).

The same provider interface is used for the **investment memo** if we ever split it; for v1 it returns from the same Gemini call to save tokens.

## 6. API Surface

| Method | Path | Purpose |
|---|---|---|
| POST | `/api/auth/login` | admin/Revo123456 → sets httpOnly JWT cookie |
| POST | `/api/auth/logout` | clear cookie |
| GET  | `/api/auth/me` | current user (for guard) |
| GET  | `/api/companies` | list w/ `?q=&market_tag=&favorite=&sort=` |
| POST | `/api/companies` | create + generate report |
| GET  | `/api/companies/{id}` | full report payload |
| PATCH| `/api/companies/{id}` | toggle favorite, edit hq/website/context |
| DELETE | `/api/companies/{id}` | delete |
| POST | `/api/companies/{id}/regenerate` | re-run AI |
| GET  | `/api/companies/{id}/export.pdf` | PDF of the report |
| POST | `/api/companies/{id}/notes` | add note |
| DELETE | `/api/companies/{id}/notes/{note_id}` | delete note |
| POST | `/api/compare` | `{a_id, b_id}` → side-by-side payload |
| GET  | `/metrics` | Prometheus exposition |
| GET  | `/healthz` | liveness |
| GET  | `/docs` | Swagger (FastAPI default) |

## 7. Frontend Flows

- **Login** → redirect to `/`
- **Dashboard** (`/`):
  - Title + product description
  - "Create Company" primary button → modal
  - Filters bar: search input (name/website), market_tag dropdown, favorites toggle, sort
  - Company table/grid with name, market tag chip, HQ, website, created date, star toggle, "View" → `/companies/:id`
  - Empty state when none, skeleton rows while loading, error banner on fetch fail
- **Create modal** → on submit shows in-modal loading state with progress copy ("Researching… analyzing competitors… scoring…"), closes on success and navigates to detail
- **Company detail** (`/companies/:id`):
  - Header: name, HQ, website link, created date, market_tag chip, favorite star
  - Score gauge (circular, 0–100) + 5-factor breakdown bars
  - Tabs or sections: Summary · Competitors (5 cards w/ strength bars) · Investment Thesis · Risks · Why It Matters · Investment Memo (rendered markdown) · Notes
  - Actions: Regenerate (with confirm), Export PDF, Delete
- **Compare** (`/compare?a=…&b=…`): two-column side-by-side of summary, market_tag, score, thesis, risks, competitors list, why_matters

## 8. Observability

**Custom metrics** (in addition to default HTTP from `prometheus-fastapi-instrumentator`):
- `ai_generation_total{result, kind}` — counter (`kind` = `report` | `regenerate`)
- `ai_generation_duration_seconds` — histogram
- `companies_created_total` — counter
- `report_regenerations_total` — counter
- `pdf_exports_total` — counter
- `errors_total{kind}` — counter

**Prometheus** scrapes `api:8000/metrics` every 5s.
**Grafana** ships with provisioned Prometheus datasource and a `company-intel.json` dashboard showing: request rate, p50/p95 latency, AI success/failure ratio, AI duration p95, companies created over time.

## 9. Error Handling

- Backend: a single exception handler maps known errors to clean JSON `{detail, code}`. AI failures are isolated — they never leave a company in `generating` for longer than the request; on timeout/exception the row goes to `failed` with the message.
- Frontend: every mutation uses React Query with `onError` toasts; every screen has explicit empty / loading / error states; AI failure on detail screen shows a "Retry" CTA that calls `regenerate`.
- Validation: Pydantic on the way in, zod-equivalent (or just TS types + form-level checks) on the way out — website must be a valid URL, name required.

## 10. Testing Strategy

Pragmatic for a one-week case, not a 80% formal coverage target:

- **Backend**: pytest + httpx AsyncClient
  - Auth: login success/fail, protected route without cookie
  - Companies CRUD + favorite toggle + filter/search
  - AI service: stubbed Gemini client returning a canned `CompanyReport` — verifies persistence flow, score computation, status transitions, failure path
  - Compare endpoint
  - `/metrics` reachable + a custom counter increments after a request
- **Frontend**: Vitest + React Testing Library on critical components (CreateCompanyModal validation, Dashboard filtering, ReportView render with fixture)
- **Manual smoke**: full flow `docker compose up --build` → login → create company → regenerate → compare → export PDF → check Prometheus + Grafana.

## 11. Environment Variables

`api/.env.example`:
```
DATABASE_URL=postgresql+asyncpg://postgres:postgres@localhost:5432/company_intel
JWT_SECRET=change-me
JWT_EXPIRES_MINUTES=720
ADMIN_USERNAME=admin
ADMIN_PASSWORD=Revo123456
AI_PROVIDER=gemini
AI_API_KEY=
AI_MODEL=gemini-2.5-flash
CORS_ORIGINS=http://localhost:5173
```

`ui/.env.example`:
```
VITE_API_BASE_URL=http://localhost:8000
```

## 12. Docker Compose Services

- `db` — postgres:16, volume, healthcheck
- `api` — built from `api/Dockerfile`, depends on `db` healthy, runs alembic upgrade then uvicorn
- `ui` — built from `ui/Dockerfile`, served via nginx (or Vite preview), depends on `api`
- `prometheus` — official image, mounts `prometheus.yml`
- `grafana` — official image, mounts `grafana-provisioning/`, default admin/admin

Ports: api `8000`, ui `5173`, db `5432`, prometheus `9090`, grafana `3000`.

## 13. Out of Scope

- Real user accounts / RBAC / sign-up
- Web search / live scraping for company facts (Gemini answers from training data + provided context)
- Background job queue (single-request synchronous AI call is sufficient at this scale)
- Multi-tenant data isolation
- i18n
- Rate limiting beyond a basic in-process limiter on `/api/companies` (POST)

## 14. Risks & Open Items

- **Gemini structured output**: if the SDK version we end up using doesn't support full nested schemas reliably, fall back to JSON-mode + Pydantic `model_validate_json` with one repair retry.
- **PDF export**: WeasyPrint requires system deps in Docker — Dockerfile must install them. If it bloats the image badly, swap to ReportLab.
- **Score determinism**: weights for the 5 factors should be documented in `scoring.py` and the breakdown shown to the user so the score never feels like a black box.

---

**Approved by user on 2026-05-08. Next step: implementation plan via writing-plans skill, then folder scaffold.**
