# Company Intel AI

AI-powered company intelligence app for VC analysts. Admin logs in, creates a company profile, and gets back a structured report — summary, 5 competitors with strength scores, market positioning, investment thesis, risks, "why this matters", a deal attractiveness score, and a one-page investment memo.

> Built for the Revo Capital tech intern case (2026-05-08).

## Status

Currently in setup. See [`docs/superpowers/specs/2026-05-08-company-intel-ai-design.md`](docs/superpowers/specs/2026-05-08-company-intel-ai-design.md) for the approved design spec. Implementation plan is next.

## Stack

- **Backend**: Python · FastAPI · SQLAlchemy 2.0 (async) · Alembic · PostgreSQL 16
- **Frontend**: Vite · React · TypeScript · Tailwind · shadcn/ui · React Query
- **AI**: Gemini 2.5 Flash (structured output)
- **Observability**: Prometheus + Grafana via Docker Compose
- **Auth**: JWT in httpOnly cookie (admin / `Revo123456`)

## Differentiating VC feature

Deal Attractiveness Score (0–100, 5-factor breakdown: market, team, moat, traction, fund fit) and an AI-generated one-page Investment Memo, generated alongside the main report.

## Run locally (after implementation)

```bash
docker compose up --build
```

Endpoints will be:
- UI: http://localhost:5173
- API: http://localhost:8000 · Swagger: http://localhost:8000/docs · Metrics: http://localhost:8000/metrics
- Prometheus: http://localhost:9090
- Grafana: http://localhost:3000 (admin / admin)

Full setup, env vars, and verification steps will be filled in once the app is wired up.
