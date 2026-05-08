# Company Intel AI Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a full-stack VC tool where an admin logs in, creates a company, and gets back an AI-generated report (summary, 5 competitors, market positioning, investment thesis, risks, "why this matters"), plus a Deal Attractiveness Score and one-page Investment Memo. Includes search/filter/favorites/notes/comparison/PDF export, Postgres persistence, and Prometheus + Grafana observability via Docker Compose.

**Architecture:** FastAPI backend (async SQLAlchemy 2.0 + Alembic + Postgres) calls Gemini 2.5 Flash with a Pydantic-derived `response_schema` to produce a structured report in one call. React + Vite + Tailwind + shadcn/ui frontend talks to the API via a typed axios client. JWT in httpOnly cookie for auth. Prometheus scrapes `/metrics`; Grafana provisioned with a starter dashboard. Hybrid local dev (Postgres/Prometheus/Grafana in Docker, api/ui local) but `docker compose up --build` brings everything up.

**Tech Stack:**
- Backend: Python 3.12, FastAPI, SQLAlchemy 2.0 (async), Alembic, asyncpg, pydantic-settings, prometheus-fastapi-instrumentator, weasyprint, google-genai
- Frontend: Node 20, Vite 5, React 18, TypeScript, Tailwind 3, shadcn/ui, react-router 6, @tanstack/react-query, axios, sonner (toasts)
- DB: PostgreSQL 16
- Infra: Docker Compose, Prometheus, Grafana
- Tests: pytest + httpx AsyncClient (backend), Vitest + React Testing Library (frontend)

**Spec reference:** [`docs/superpowers/specs/2026-05-08-company-intel-ai-design.md`](../specs/2026-05-08-company-intel-ai-design.md)

**Cadence note:** every task ends with a commit. Push after each phase boundary or whenever convenient. Conventional commits: `feat:`, `fix:`, `chore:`, `test:`, `docs:`, `refactor:`.

---

## Phase 0 — Top-level skeleton

### Task 0.1: Create top-level folders and placeholder files

**Files:**
- Create: `api/.gitkeep`, `ui/.gitkeep`
- Create: `docker-compose.yml` (skeleton)
- Create: `prometheus.yml` (skeleton)
- Create: `grafana-provisioning/datasources/.gitkeep`, `grafana-provisioning/dashboards/.gitkeep`
- Create: `ARCHITECTURE.md` (placeholder, filled in Phase 9)

- [ ] **Step 1: Create folders**

```bash
mkdir -p api ui grafana-provisioning/datasources grafana-provisioning/dashboards
touch api/.gitkeep ui/.gitkeep grafana-provisioning/datasources/.gitkeep grafana-provisioning/dashboards/.gitkeep
```

- [ ] **Step 2: Create skeleton `docker-compose.yml`**

```yaml
# docker-compose.yml — services filled in across Phases 1, 5, and 7
services:
  db:
    image: postgres:16
    environment:
      POSTGRES_USER: postgres
      POSTGRES_PASSWORD: postgres
      POSTGRES_DB: company_intel
    ports: ["5432:5432"]
    volumes: ["postgres-data:/var/lib/postgresql/data"]
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U postgres"]
      interval: 5s
      timeout: 3s
      retries: 10

volumes:
  postgres-data:
```

- [ ] **Step 3: Create skeleton `prometheus.yml`**

```yaml
global:
  scrape_interval: 5s
scrape_configs:
  - job_name: company-intel-api
    static_configs:
      - targets: ["api:8000"]
```

- [ ] **Step 4: Create placeholder `ARCHITECTURE.md`**

```markdown
# Architecture

> Filled in Phase 9 once the implementation is complete. See the design spec at `docs/superpowers/specs/2026-05-08-company-intel-ai-design.md` for the planned shape.
```

- [ ] **Step 5: Commit**

```bash
git add api ui grafana-provisioning docker-compose.yml prometheus.yml ARCHITECTURE.md
git commit -m "chore: top-level project skeleton"
```

---

## Phase 1 — Backend foundation

### Task 1.1: Bootstrap FastAPI project with pyproject and uv

**Files:**
- Create: `api/pyproject.toml`, `api/README.md`, `api/.python-version`
- Create: `api/app/__init__.py`, `api/app/main.py`
- Create: `api/tests/__init__.py`, `api/tests/test_health.py`

- [ ] **Step 1: Write `api/pyproject.toml`**

```toml
[project]
name = "company-intel-api"
version = "0.1.0"
requires-python = ">=3.12"
dependencies = [
  "fastapi>=0.115",
  "uvicorn[standard]>=0.32",
  "pydantic>=2.9",
  "pydantic-settings>=2.6",
  "sqlalchemy[asyncio]>=2.0.36",
  "asyncpg>=0.30",
  "alembic>=1.14",
  "python-jose[cryptography]>=3.3",
  "passlib[bcrypt]>=1.7.4",
  "prometheus-fastapi-instrumentator>=7.0",
  "weasyprint>=63",
  "google-genai>=0.3",
  "httpx>=0.27",
]

[project.optional-dependencies]
dev = [
  "pytest>=8.3",
  "pytest-asyncio>=0.24",
  "pytest-cov>=6.0",
  "ruff>=0.7",
  "mypy>=1.13",
]

[tool.pytest.ini_options]
asyncio_mode = "auto"
testpaths = ["tests"]

[tool.ruff]
line-length = 100
target-version = "py312"
[tool.ruff.lint]
select = ["E", "F", "I", "B", "UP"]
```

- [ ] **Step 2: Write `api/.python-version`**

```
3.12
```

- [ ] **Step 3: Write `api/app/main.py` — minimal app with `/healthz` and `/docs`**

```python
from fastapi import FastAPI

app = FastAPI(title="Company Intel API", version="0.1.0")

@app.get("/healthz")
def healthz() -> dict[str, str]:
    return {"status": "ok"}
```

- [ ] **Step 4: Write the failing test `api/tests/test_health.py`**

```python
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_healthz_returns_ok():
    r = client.get("/healthz")
    assert r.status_code == 200
    assert r.json() == {"status": "ok"}

def test_swagger_docs_available():
    r = client.get("/docs")
    assert r.status_code == 200
```

- [ ] **Step 5: Install deps and run tests**

```bash
cd api
python -m venv .venv && source .venv/bin/activate
pip install -e ".[dev]"
pytest -v
```

Expected: 2 passed.

- [ ] **Step 6: Write `api/README.md`**

```markdown
# api

FastAPI backend for Company Intel AI.

## Local dev

```bash
python -m venv .venv && source .venv/bin/activate
pip install -e ".[dev]"
uvicorn app.main:app --reload --port 8000
```

Swagger: http://localhost:8000/docs · Metrics: http://localhost:8000/metrics
```

- [ ] **Step 7: Commit**

```bash
git add api/
git commit -m "feat(api): bootstrap FastAPI app with healthz and pytest"
```

### Task 1.2: Settings + CORS + structured config

**Files:**
- Create: `api/app/core/__init__.py`, `api/app/core/config.py`
- Create: `api/.env.example`
- Modify: `api/app/main.py`
- Create: `api/tests/test_config.py`

- [ ] **Step 1: Write `api/.env.example`**

```
DATABASE_URL=postgresql+asyncpg://postgres:postgres@localhost:5432/company_intel
JWT_SECRET=change-me-in-prod
JWT_EXPIRES_MINUTES=720
ADMIN_USERNAME=admin
ADMIN_PASSWORD=Revo123456
AI_PROVIDER=gemini
AI_API_KEY=
AI_MODEL=gemini-2.5-flash
CORS_ORIGINS=http://localhost:5173
LOG_LEVEL=INFO
```

- [ ] **Step 2: Write `api/app/core/config.py`**

```python
from functools import lru_cache
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    database_url: str
    jwt_secret: str = "change-me-in-prod"
    jwt_expires_minutes: int = 720
    admin_username: str = "admin"
    admin_password: str = "Revo123456"
    ai_provider: str = "gemini"
    ai_api_key: str = ""
    ai_model: str = "gemini-2.5-flash"
    cors_origins: str = "http://localhost:5173"
    log_level: str = "INFO"

    @property
    def cors_origins_list(self) -> list[str]:
        return [o.strip() for o in self.cors_origins.split(",") if o.strip()]

@lru_cache
def get_settings() -> Settings:
    return Settings()
```

- [ ] **Step 3: Wire CORS in `api/app/main.py`**

```python
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import get_settings

settings = get_settings()
app = FastAPI(title="Company Intel API", version="0.1.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/healthz")
def healthz() -> dict[str, str]:
    return {"status": "ok"}
```

- [ ] **Step 4: Test (`api/tests/test_config.py`)**

```python
import os
from app.core.config import Settings

def test_cors_list_parses_csv(monkeypatch):
    monkeypatch.setenv("DATABASE_URL", "postgresql+asyncpg://x")
    monkeypatch.setenv("CORS_ORIGINS", "http://a, http://b ,http://c")
    s = Settings()
    assert s.cors_origins_list == ["http://a", "http://b", "http://c"]
```

- [ ] **Step 5: Run tests, expect pass; commit**

```bash
pytest -v
git add api/
git commit -m "feat(api): settings + CORS"
```

### Task 1.3: SQLAlchemy async setup + Alembic

**Files:**
- Create: `api/app/db/__init__.py`, `api/app/db/base.py`, `api/app/db/session.py`
- Create: `api/alembic.ini`, `api/alembic/env.py`, `api/alembic/script.py.mako`, `api/alembic/versions/.gitkeep`

- [ ] **Step 1: `api/app/db/base.py`**

```python
from sqlalchemy.orm import DeclarativeBase

class Base(DeclarativeBase):
    pass
```

- [ ] **Step 2: `api/app/db/session.py`**

```python
from collections.abc import AsyncIterator
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from app.core.config import get_settings

settings = get_settings()
engine = create_async_engine(settings.database_url, pool_pre_ping=True)
SessionLocal = async_sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)

async def get_db() -> AsyncIterator[AsyncSession]:
    async with SessionLocal() as session:
        yield session
```

- [ ] **Step 3: Initialize Alembic**

```bash
cd api
alembic init -t async alembic
```

This generates `alembic.ini`, `alembic/env.py`, `alembic/script.py.mako`, and `alembic/versions/`.

- [ ] **Step 4: Edit `api/alembic/env.py` to use settings + import Base**

Replace the `target_metadata` line and the URL config with:

```python
from app.core.config import get_settings
from app.db.base import Base
import app.models  # noqa: F401  (registers models)

config.set_main_option("sqlalchemy.url", get_settings().database_url)
target_metadata = Base.metadata
```

- [ ] **Step 5: Create empty `api/app/models/__init__.py`** (will hold model imports later)

```python
# imports added in Task 1.4
```

- [ ] **Step 6: Commit**

```bash
git add api/
git commit -m "feat(api): SQLAlchemy async + Alembic scaffolding"
```

### Task 1.4: Company / Competitor / Note models + first migration

**Files:**
- Create: `api/app/models/company.py`, `api/app/models/competitor.py`, `api/app/models/note.py`
- Modify: `api/app/models/__init__.py`
- Create: `api/alembic/versions/<hash>_initial.py` (auto-generated)

- [ ] **Step 1: `api/app/models/company.py`**

```python
import uuid
from datetime import datetime
from sqlalchemy import Boolean, DateTime, Integer, String, Text, func
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base import Base

class Company(Base):
    __tablename__ = "companies"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(String(200), nullable=False, index=True)
    hq: Mapped[str | None] = mapped_column(String(200))
    website: Mapped[str | None] = mapped_column(String(500))
    context: Mapped[str | None] = mapped_column(Text)

    market_tag: Mapped[str | None] = mapped_column(String(100), index=True)
    summary: Mapped[list | None] = mapped_column(JSONB)
    investment_thesis: Mapped[list | None] = mapped_column(JSONB)
    risks: Mapped[list | None] = mapped_column(JSONB)
    why_matters: Mapped[list | None] = mapped_column(JSONB)
    score_total: Mapped[int | None] = mapped_column(Integer)
    score_breakdown: Mapped[dict | None] = mapped_column(JSONB)
    memo_markdown: Mapped[str | None] = mapped_column(Text)

    status: Mapped[str] = mapped_column(String(20), default="generating", nullable=False)
    error_message: Mapped[str | None] = mapped_column(Text)
    favorite: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False, index=True)

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), index=True)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    competitors: Mapped[list["Competitor"]] = relationship(back_populates="company", cascade="all, delete-orphan", order_by="Competitor.position")
    notes: Mapped[list["Note"]] = relationship(back_populates="company", cascade="all, delete-orphan", order_by="Note.created_at.desc()")
```

- [ ] **Step 2: `api/app/models/competitor.py`**

```python
import uuid
from sqlalchemy import ForeignKey, Integer, String
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base import Base

class Competitor(Base):
    __tablename__ = "competitors"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    company_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("companies.id", ondelete="CASCADE"), nullable=False, index=True)
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    summary: Mapped[list | None] = mapped_column(JSONB)
    strength_score: Mapped[int] = mapped_column(Integer, nullable=False)
    position: Mapped[int] = mapped_column(Integer, nullable=False)

    company: Mapped["Company"] = relationship(back_populates="competitors")
```

- [ ] **Step 3: `api/app/models/note.py`**

```python
import uuid
from datetime import datetime
from sqlalchemy import DateTime, ForeignKey, Text, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base import Base

class Note(Base):
    __tablename__ = "notes"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    company_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("companies.id", ondelete="CASCADE"), nullable=False, index=True)
    body: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    company: Mapped["Company"] = relationship(back_populates="notes")
```

- [ ] **Step 4: `api/app/models/__init__.py`**

```python
from app.models.company import Company
from app.models.competitor import Competitor
from app.models.note import Note

__all__ = ["Company", "Competitor", "Note"]
```

- [ ] **Step 5: Bring up Postgres and generate the migration**

```bash
docker compose up -d db
cd api
export $(cat .env | xargs)  # or copy .env.example to .env first
alembic revision --autogenerate -m "initial schema"
alembic upgrade head
```

Verify the file in `api/alembic/versions/` creates `companies`, `competitors`, `notes` tables.

- [ ] **Step 6: Commit**

```bash
git add api/
git commit -m "feat(api): company/competitor/note models + initial migration"
```

---

## Phase 2 — Auth (JWT in httpOnly cookie)

### Task 2.1: JWT helpers + tests

**Files:**
- Create: `api/app/core/security.py`
- Create: `api/tests/test_security.py`

- [ ] **Step 1: Write the failing test (`api/tests/test_security.py`)**

```python
import pytest
from datetime import timedelta
from app.core.security import create_access_token, decode_token, TokenError

def test_round_trip_token():
    token = create_access_token(subject="admin", expires=timedelta(minutes=5))
    payload = decode_token(token)
    assert payload["sub"] == "admin"

def test_decode_rejects_garbage():
    with pytest.raises(TokenError):
        decode_token("not-a-real-token")
```

- [ ] **Step 2: Run, expect ImportError**

```bash
pytest tests/test_security.py -v
```

- [ ] **Step 3: Implement `api/app/core/security.py`**

```python
from datetime import datetime, timedelta, timezone
from jose import JWTError, jwt
from app.core.config import get_settings

ALGORITHM = "HS256"

class TokenError(Exception):
    pass

def create_access_token(subject: str, expires: timedelta | None = None) -> str:
    s = get_settings()
    expire = datetime.now(timezone.utc) + (expires or timedelta(minutes=s.jwt_expires_minutes))
    return jwt.encode({"sub": subject, "exp": expire}, s.jwt_secret, algorithm=ALGORITHM)

def decode_token(token: str) -> dict:
    try:
        return jwt.decode(token, get_settings().jwt_secret, algorithms=[ALGORITHM])
    except JWTError as e:
        raise TokenError(str(e)) from e
```

- [ ] **Step 4: Run tests, expect pass; commit**

```bash
pytest tests/test_security.py -v
git add api/
git commit -m "feat(api): JWT helpers"
```

### Task 2.2: Auth dependency + login/logout/me endpoints

**Files:**
- Create: `api/app/api/__init__.py`, `api/app/api/routes/__init__.py`
- Create: `api/app/api/deps.py`
- Create: `api/app/api/routes/auth.py`
- Create: `api/app/schemas/__init__.py`, `api/app/schemas/auth.py`
- Modify: `api/app/main.py`
- Create: `api/tests/test_auth.py`

- [ ] **Step 1: `api/app/schemas/auth.py`**

```python
from pydantic import BaseModel

class LoginRequest(BaseModel):
    username: str
    password: str

class MeResponse(BaseModel):
    username: str
```

- [ ] **Step 2: `api/app/api/deps.py`**

```python
from fastapi import Cookie, HTTPException, status
from app.core.security import TokenError, decode_token

COOKIE_NAME = "cia_session"

def require_admin(cia_session: str | None = Cookie(default=None, alias=COOKIE_NAME)) -> str:
    if not cia_session:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "not authenticated")
    try:
        payload = decode_token(cia_session)
    except TokenError as e:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "invalid token") from e
    return payload["sub"]
```

- [ ] **Step 3: `api/app/api/routes/auth.py`**

```python
from fastapi import APIRouter, Depends, HTTPException, Response, status
from app.api.deps import COOKIE_NAME, require_admin
from app.core.config import get_settings
from app.core.security import create_access_token
from app.schemas.auth import LoginRequest, MeResponse

router = APIRouter(prefix="/api/auth", tags=["auth"])

@router.post("/login", status_code=status.HTTP_204_NO_CONTENT)
def login(payload: LoginRequest, response: Response) -> Response:
    s = get_settings()
    if payload.username != s.admin_username or payload.password != s.admin_password:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "invalid credentials")
    token = create_access_token(subject=payload.username)
    response.set_cookie(
        key=COOKIE_NAME,
        value=token,
        httponly=True,
        samesite="lax",
        secure=False,  # set True behind HTTPS
        max_age=s.jwt_expires_minutes * 60,
        path="/",
    )
    response.status_code = status.HTTP_204_NO_CONTENT
    return response

@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
def logout(response: Response) -> Response:
    response.delete_cookie(COOKIE_NAME, path="/")
    response.status_code = status.HTTP_204_NO_CONTENT
    return response

@router.get("/me", response_model=MeResponse)
def me(username: str = Depends(require_admin)) -> MeResponse:
    return MeResponse(username=username)
```

- [ ] **Step 4: Wire router in `api/app/main.py`**

```python
from app.api.routes import auth as auth_routes
app.include_router(auth_routes.router)
```

- [ ] **Step 5: Tests `api/tests/test_auth.py`**

```python
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_login_success_sets_cookie():
    r = client.post("/api/auth/login", json={"username": "admin", "password": "Revo123456"})
    assert r.status_code == 204
    assert "cia_session" in r.cookies

def test_login_failure():
    r = client.post("/api/auth/login", json={"username": "admin", "password": "wrong"})
    assert r.status_code == 401

def test_me_requires_cookie():
    r = client.get("/api/auth/me")
    assert r.status_code == 401

def test_me_with_cookie():
    login = client.post("/api/auth/login", json={"username": "admin", "password": "Revo123456"})
    me = client.get("/api/auth/me", cookies=login.cookies)
    assert me.status_code == 200
    assert me.json() == {"username": "admin"}

def test_logout_clears_cookie():
    login = client.post("/api/auth/login", json={"username": "admin", "password": "Revo123456"})
    out = client.post("/api/auth/logout", cookies=login.cookies)
    assert out.status_code == 204
```

- [ ] **Step 6: Run tests, expect pass; commit**

```bash
pytest -v
git add api/
git commit -m "feat(api): admin auth via JWT cookie (login/logout/me)"
```

---

## Phase 3 — Companies CRUD (no AI yet)

### Task 3.1: Pydantic schemas

**Files:**
- Create: `api/app/schemas/report.py`, `api/app/schemas/company.py`

- [ ] **Step 1: `api/app/schemas/report.py` — these double as the Gemini structured-output schema**

```python
from pydantic import BaseModel, Field

class CompetitorOut(BaseModel):
    name: str
    summary: list[str] = Field(min_length=3, max_length=6)
    strength_score: int = Field(ge=0, le=100)

class ScoreBreakdown(BaseModel):
    market: int = Field(ge=0, le=100)
    team: int = Field(ge=0, le=100)
    moat: int = Field(ge=0, le=100)
    traction: int = Field(ge=0, le=100)
    fund_fit: int = Field(ge=0, le=100)

class CompanyReport(BaseModel):
    """The full AI-generated payload."""
    summary: list[str] = Field(min_length=3, max_length=6)
    market_tag: str
    competitors: list[CompetitorOut] = Field(min_length=5, max_length=5)
    investment_thesis: list[str] = Field(min_length=3, max_length=6)
    risks: list[str] = Field(min_length=3, max_length=6)
    why_matters: list[str] = Field(min_length=3, max_length=6)
    score_breakdown: ScoreBreakdown
    memo_markdown: str
```

- [ ] **Step 2: `api/app/schemas/company.py`**

```python
import uuid
from datetime import datetime
from pydantic import BaseModel, ConfigDict, Field, HttpUrl
from app.schemas.report import CompetitorOut, ScoreBreakdown

class CompanyCreate(BaseModel):
    name: str = Field(min_length=1, max_length=200)
    hq: str | None = None
    website: HttpUrl | None = None
    context: str | None = None

class CompanyPatch(BaseModel):
    hq: str | None = None
    website: HttpUrl | None = None
    context: str | None = None
    favorite: bool | None = None

class NoteOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: uuid.UUID
    body: str
    created_at: datetime

class CompetitorRow(CompetitorOut):
    model_config = ConfigDict(from_attributes=True)

class CompanyListItem(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: uuid.UUID
    name: str
    hq: str | None
    website: str | None
    market_tag: str | None
    score_total: int | None
    favorite: bool
    status: str
    created_at: datetime

class CompanyDetail(CompanyListItem):
    context: str | None
    summary: list[str] | None
    investment_thesis: list[str] | None
    risks: list[str] | None
    why_matters: list[str] | None
    score_breakdown: ScoreBreakdown | None
    memo_markdown: str | None
    error_message: str | None
    competitors: list[CompetitorRow]
    notes: list[NoteOut]
```

- [ ] **Step 3: Commit**

```bash
git add api/app/schemas
git commit -m "feat(api): pydantic schemas for company report"
```

### Task 3.2: Company list/get/delete + favorite toggle (no AI)

**Files:**
- Create: `api/app/api/routes/companies.py`
- Create: `api/app/services/__init__.py`, `api/app/services/company_repo.py`
- Modify: `api/app/main.py`
- Create: `api/tests/conftest.py`, `api/tests/test_companies_crud.py`

- [ ] **Step 1: `api/app/services/company_repo.py`** — encapsulates DB queries, makes route bodies short

```python
import uuid
from sqlalchemy import select, func, or_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from app.models.company import Company

async def list_companies(
    db: AsyncSession,
    q: str | None = None,
    market_tag: str | None = None,
    favorite: bool | None = None,
    sort: str = "created_desc",
) -> list[Company]:
    stmt = select(Company)
    if q:
        like = f"%{q.lower()}%"
        stmt = stmt.where(or_(func.lower(Company.name).like(like), func.lower(Company.website).like(like)))
    if market_tag:
        stmt = stmt.where(Company.market_tag == market_tag)
    if favorite is not None:
        stmt = stmt.where(Company.favorite == favorite)
    stmt = stmt.order_by(
        Company.created_at.desc() if sort == "created_desc" else Company.created_at.asc()
    )
    return list((await db.scalars(stmt)).all())

async def get_company(db: AsyncSession, company_id: uuid.UUID) -> Company | None:
    stmt = select(Company).where(Company.id == company_id).options(
        selectinload(Company.competitors), selectinload(Company.notes)
    )
    return (await db.scalars(stmt)).one_or_none()

async def delete_company(db: AsyncSession, company: Company) -> None:
    await db.delete(company)
    await db.commit()
```

- [ ] **Step 2: `api/app/api/routes/companies.py`** (no POST yet — that lands in Phase 4)

```python
import uuid
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.api.deps import require_admin
from app.db.session import get_db
from app.models.company import Company
from app.schemas.company import CompanyDetail, CompanyListItem, CompanyPatch
from app.services import company_repo

router = APIRouter(prefix="/api/companies", tags=["companies"], dependencies=[Depends(require_admin)])

@router.get("", response_model=list[CompanyListItem])
async def list_endpoint(
    q: str | None = Query(default=None),
    market_tag: str | None = Query(default=None),
    favorite: bool | None = Query(default=None),
    sort: str = Query(default="created_desc"),
    db: AsyncSession = Depends(get_db),
):
    return await company_repo.list_companies(db, q=q, market_tag=market_tag, favorite=favorite, sort=sort)

@router.get("/{company_id}", response_model=CompanyDetail)
async def get_endpoint(company_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    company = await company_repo.get_company(db, company_id)
    if not company:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "company not found")
    return company

@router.patch("/{company_id}", response_model=CompanyDetail)
async def patch_endpoint(company_id: uuid.UUID, payload: CompanyPatch, db: AsyncSession = Depends(get_db)):
    company = await company_repo.get_company(db, company_id)
    if not company:
        raise HTTPException(status.HTTP_404_NOT_FOUND)
    data = payload.model_dump(exclude_unset=True)
    for k, v in data.items():
        setattr(company, k, str(v) if k == "website" and v is not None else v)
    await db.commit()
    await db.refresh(company)
    return company

@router.delete("/{company_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_endpoint(company_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    company = await company_repo.get_company(db, company_id)
    if not company:
        raise HTTPException(status.HTTP_404_NOT_FOUND)
    await company_repo.delete_company(db, company)
```

- [ ] **Step 3: Wire router in `main.py`**

```python
from app.api.routes import companies as companies_routes
app.include_router(companies_routes.router)
```

- [ ] **Step 4: `api/tests/conftest.py`** — async test client + DB override using SQLite for speed

```python
import pytest_asyncio
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from app.db.base import Base
from app.db.session import get_db
from app.main import app
import app.models  # noqa: F401

TEST_DB_URL = "sqlite+aiosqlite:///:memory:"

@pytest_asyncio.fixture
async def db_engine():
    engine = create_async_engine(TEST_DB_URL)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield engine
    await engine.dispose()

@pytest_asyncio.fixture
async def db_session(db_engine) -> AsyncSession:
    async with async_sessionmaker(db_engine, expire_on_commit=False)() as s:
        yield s

@pytest_asyncio.fixture
async def client(db_session):
    async def _override():
        yield db_session
    app.dependency_overrides[get_db] = _override
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        # log in once
        await ac.post("/api/auth/login", json={"username": "admin", "password": "Revo123456"})
        yield ac
    app.dependency_overrides.clear()
```

Add `aiosqlite` to dev dependencies in `pyproject.toml`:
```toml
dev = [
  ...,
  "aiosqlite>=0.20",
]
```
Then `pip install -e ".[dev]"`.

> Note on JSONB on SQLite: SQLAlchemy maps `JSONB` columns through to JSON on SQLite for testing. If a model fails to create on SQLite, swap the import in `models/*.py` to `from sqlalchemy import JSON` and use `JSON` instead — but `postgresql.JSONB` falls back to JSON on SQLite via SQLAlchemy's dialect handling in 2.0.

- [ ] **Step 5: `api/tests/test_companies_crud.py`**

```python
import pytest

@pytest.mark.asyncio
async def test_list_empty(client):
    r = await client.get("/api/companies")
    assert r.status_code == 200
    assert r.json() == []

@pytest.mark.asyncio
async def test_list_requires_auth(client):
    # drop the login cookie
    client.cookies.clear()
    r = await client.get("/api/companies")
    assert r.status_code == 401

@pytest.mark.asyncio
async def test_404_on_missing(client):
    import uuid
    r = await client.get(f"/api/companies/{uuid.uuid4()}")
    assert r.status_code == 404
```

- [ ] **Step 6: Run, commit**

```bash
pytest -v
git add api/
git commit -m "feat(api): list/get/patch/delete companies + repo + test fixtures"
```

---

## Phase 4 — AI integration (the heart of the product)

### Task 4.1: AI provider protocol + Gemini client + stub for tests

**Files:**
- Create: `api/app/services/ai/__init__.py`, `api/app/services/ai/provider.py`, `api/app/services/ai/gemini_client.py`, `api/app/services/ai/stub_client.py`
- Create: `api/tests/test_ai_stub.py`

- [ ] **Step 1: `api/app/services/ai/provider.py`**

```python
from typing import Protocol
from app.schemas.company import CompanyCreate
from app.schemas.report import CompanyReport

class AIProvider(Protocol):
    async def generate_report(self, payload: CompanyCreate) -> CompanyReport: ...
```

- [ ] **Step 2: `api/app/services/ai/gemini_client.py`**

```python
from google import genai
from google.genai import types
from app.core.config import get_settings
from app.schemas.company import CompanyCreate
from app.schemas.report import CompanyReport

PROMPT = """You are an analyst at a top-tier venture capital firm.
Produce a structured intelligence report for the company below.

Company: {name}
HQ: {hq}
Website: {website}
Context from analyst: {context}

Constraints:
- Each bullet list (summary, investment_thesis, risks, why_matters) must contain 4 to 5 short bullets, each one sentence.
- Provide exactly 5 competitors with their own 4-5 bullet summaries and a strength_score 0-100.
- market_tag is a single short label like "Enterprise SaaS", "Fintech Infrastructure", "AI Tooling".
- score_breakdown is a 0-100 score for each of: market, team, moat, traction, fund_fit.
- memo_markdown is a one-page (~250-400 word) investment memo in Markdown with sections: Overview, Why Now, Thesis, Risks, Recommendation.
"""

class GeminiClient:
    def __init__(self) -> None:
        s = get_settings()
        if not s.ai_api_key:
            raise RuntimeError("AI_API_KEY is not set")
        self._client = genai.Client(api_key=s.ai_api_key)
        self._model = s.ai_model

    async def generate_report(self, payload: CompanyCreate) -> CompanyReport:
        prompt = PROMPT.format(
            name=payload.name,
            hq=payload.hq or "unknown",
            website=str(payload.website) if payload.website else "unknown",
            context=payload.context or "(none)",
        )
        result = await self._client.aio.models.generate_content(
            model=self._model,
            contents=prompt,
            config=types.GenerateContentConfig(
                response_mime_type="application/json",
                response_schema=CompanyReport,
                temperature=0.4,
            ),
        )
        # SDK returns a parsed pydantic instance when response_schema is a Pydantic model
        if isinstance(result.parsed, CompanyReport):
            return result.parsed
        # Fallback: validate raw JSON
        return CompanyReport.model_validate_json(result.text)
```

- [ ] **Step 3: `api/app/services/ai/stub_client.py`** — used in tests

```python
from app.schemas.company import CompanyCreate
from app.schemas.report import CompanyReport, CompetitorOut, ScoreBreakdown

class StubClient:
    def __init__(self, fail: bool = False) -> None:
        self.fail = fail

    async def generate_report(self, payload: CompanyCreate) -> CompanyReport:
        if self.fail:
            raise RuntimeError("AI provider unavailable")
        return CompanyReport(
            summary=[f"{payload.name} is a stubbed company.", "Bullet 2.", "Bullet 3.", "Bullet 4."],
            market_tag="AI Tooling",
            competitors=[
                CompetitorOut(name=f"Comp{i}", summary=["a", "b", "c", "d"], strength_score=60 + i)
                for i in range(5)
            ],
            investment_thesis=["t1", "t2", "t3", "t4"],
            risks=["r1", "r2", "r3", "r4"],
            why_matters=["w1", "w2", "w3", "w4"],
            score_breakdown=ScoreBreakdown(market=70, team=70, moat=70, traction=70, fund_fit=70),
            memo_markdown="# Memo\n\nStubbed memo body.",
        )
```

- [ ] **Step 4: Provider factory in `api/app/services/ai/__init__.py`**

```python
from app.core.config import get_settings
from app.services.ai.provider import AIProvider

def get_ai_provider() -> AIProvider:
    s = get_settings()
    if s.ai_provider == "stub":
        from app.services.ai.stub_client import StubClient
        return StubClient()
    if s.ai_provider == "gemini":
        from app.services.ai.gemini_client import GeminiClient
        return GeminiClient()
    raise RuntimeError(f"unknown AI_PROVIDER={s.ai_provider}")
```

- [ ] **Step 5: Test (`api/tests/test_ai_stub.py`)**

```python
import pytest
from app.schemas.company import CompanyCreate
from app.services.ai.stub_client import StubClient

@pytest.mark.asyncio
async def test_stub_generates_full_report():
    r = await StubClient().generate_report(CompanyCreate(name="Acme"))
    assert len(r.competitors) == 5
    assert r.market_tag
    assert r.score_breakdown.market >= 0
```

- [ ] **Step 6: Run, commit**

```bash
pytest -v
git add api/
git commit -m "feat(api): AIProvider protocol + Gemini client + test stub"
```

### Task 4.2: Score weighting + report generation service

**Files:**
- Create: `api/app/services/ai/scoring.py`
- Create: `api/app/services/report_service.py`
- Create: `api/tests/test_scoring.py`, `api/tests/test_report_service.py`

- [ ] **Step 1: Test the scoring (`api/tests/test_scoring.py`)**

```python
from app.schemas.report import ScoreBreakdown
from app.services.ai.scoring import compute_score_total

def test_perfect_breakdown_is_100():
    assert compute_score_total(ScoreBreakdown(market=100, team=100, moat=100, traction=100, fund_fit=100)) == 100

def test_zero_breakdown_is_0():
    assert compute_score_total(ScoreBreakdown(market=0, team=0, moat=0, traction=0, fund_fit=0)) == 0

def test_weighted_blend_respects_market_weight():
    # market is weighted 0.30; with market=100 and rest=0, score >= 30
    s = ScoreBreakdown(market=100, team=0, moat=0, traction=0, fund_fit=0)
    assert compute_score_total(s) == 30
```

- [ ] **Step 2: Implement (`api/app/services/ai/scoring.py`)**

```python
from app.schemas.report import ScoreBreakdown

WEIGHTS = {"market": 0.30, "team": 0.25, "moat": 0.15, "traction": 0.20, "fund_fit": 0.10}
assert sum(WEIGHTS.values()) == 1.0

def compute_score_total(breakdown: ScoreBreakdown) -> int:
    total = (
        breakdown.market * WEIGHTS["market"]
        + breakdown.team * WEIGHTS["team"]
        + breakdown.moat * WEIGHTS["moat"]
        + breakdown.traction * WEIGHTS["traction"]
        + breakdown.fund_fit * WEIGHTS["fund_fit"]
    )
    return int(round(total))
```

- [ ] **Step 3: Report service (`api/app/services/report_service.py`)**

```python
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.company import Company
from app.models.competitor import Competitor
from app.schemas.company import CompanyCreate
from app.services.ai.provider import AIProvider
from app.services.ai.scoring import compute_score_total

async def create_with_report(db: AsyncSession, payload: CompanyCreate, ai: AIProvider) -> Company:
    company = Company(
        name=payload.name,
        hq=payload.hq,
        website=str(payload.website) if payload.website else None,
        context=payload.context,
        status="generating",
    )
    db.add(company)
    await db.commit()
    await db.refresh(company)
    try:
        report = await ai.generate_report(payload)
    except Exception as e:
        company.status = "failed"
        company.error_message = str(e)[:500]
        await db.commit()
        raise
    _apply_report(company, report)
    db.add_all(_build_competitors(company.id, report))
    company.status = "ready"
    company.error_message = None
    await db.commit()
    await db.refresh(company)
    return company

async def regenerate_report(db: AsyncSession, company: Company, ai: AIProvider) -> Company:
    company.status = "generating"
    await db.commit()
    # wipe old competitors
    for c in list(company.competitors):
        await db.delete(c)
    await db.commit()
    payload = CompanyCreate(
        name=company.name,
        hq=company.hq,
        website=company.website,
        context=company.context,
    )
    try:
        report = await ai.generate_report(payload)
    except Exception as e:
        company.status = "failed"
        company.error_message = str(e)[:500]
        await db.commit()
        raise
    _apply_report(company, report)
    db.add_all(_build_competitors(company.id, report))
    company.status = "ready"
    company.error_message = None
    await db.commit()
    await db.refresh(company)
    return company

def _apply_report(company: Company, report) -> None:
    company.summary = report.summary
    company.market_tag = report.market_tag
    company.investment_thesis = report.investment_thesis
    company.risks = report.risks
    company.why_matters = report.why_matters
    company.score_breakdown = report.score_breakdown.model_dump()
    company.score_total = compute_score_total(report.score_breakdown)
    company.memo_markdown = report.memo_markdown

def _build_competitors(company_id, report):
    from app.models.competitor import Competitor
    return [
        Competitor(
            company_id=company_id,
            name=c.name,
            summary=c.summary,
            strength_score=c.strength_score,
            position=i + 1,
        )
        for i, c in enumerate(report.competitors)
    ]
```

- [ ] **Step 4: Service test (`api/tests/test_report_service.py`)**

```python
import pytest
from app.schemas.company import CompanyCreate
from app.services.ai.stub_client import StubClient
from app.services.report_service import create_with_report

@pytest.mark.asyncio
async def test_create_with_report_persists_competitors_and_score(db_session):
    ai = StubClient()
    company = await create_with_report(db_session, CompanyCreate(name="Acme"), ai)
    assert company.status == "ready"
    assert company.score_total > 0
    assert len(company.competitors) == 5

@pytest.mark.asyncio
async def test_create_with_report_failure_sets_status_failed(db_session):
    ai = StubClient(fail=True)
    with pytest.raises(RuntimeError):
        await create_with_report(db_session, CompanyCreate(name="Acme"), ai)
    # row should still exist with status=failed
    from sqlalchemy import select
    from app.models.company import Company
    rows = (await db_session.scalars(select(Company))).all()
    assert len(rows) == 1
    assert rows[0].status == "failed"
```

- [ ] **Step 5: Run, commit**

```bash
pytest -v
git add api/
git commit -m "feat(api): report service with AI integration + scoring"
```

### Task 4.3: Wire POST /companies + regenerate endpoint

**Files:**
- Modify: `api/app/api/routes/companies.py`
- Modify: `api/app/api/deps.py` (add AI dependency)
- Create: `api/tests/test_companies_create.py`

- [ ] **Step 1: Add AI dependency in `deps.py`**

```python
from app.services.ai import get_ai_provider
from app.services.ai.provider import AIProvider

def get_ai() -> AIProvider:
    return get_ai_provider()
```

- [ ] **Step 2: Append to `companies.py`**

```python
from app.api.deps import get_ai
from app.schemas.company import CompanyCreate
from app.services import report_service
from app.services.ai.provider import AIProvider
from fastapi import HTTPException

@router.post("", response_model=CompanyDetail, status_code=status.HTTP_201_CREATED)
async def create_endpoint(
    payload: CompanyCreate,
    db: AsyncSession = Depends(get_db),
    ai: AIProvider = Depends(get_ai),
):
    try:
        company = await report_service.create_with_report(db, payload, ai)
    except Exception as e:
        raise HTTPException(status.HTTP_502_BAD_GATEWAY, f"AI generation failed: {e}") from e
    # eagerly load relationships for response
    return await company_repo.get_company(db, company.id)

@router.post("/{company_id}/regenerate", response_model=CompanyDetail)
async def regenerate_endpoint(
    company_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    ai: AIProvider = Depends(get_ai),
):
    company = await company_repo.get_company(db, company_id)
    if not company:
        raise HTTPException(status.HTTP_404_NOT_FOUND)
    try:
        await report_service.regenerate_report(db, company, ai)
    except Exception as e:
        raise HTTPException(status.HTTP_502_BAD_GATEWAY, f"AI generation failed: {e}") from e
    return await company_repo.get_company(db, company_id)
```

- [ ] **Step 3: Override AI in tests via `conftest.py`** — append:

```python
from app.api.deps import get_ai
from app.services.ai.stub_client import StubClient

@pytest_asyncio.fixture
async def client(db_session):
    async def _db_override():
        yield db_session
    def _ai_override():
        return StubClient()
    app.dependency_overrides[get_db] = _db_override
    app.dependency_overrides[get_ai] = _ai_override
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        await ac.post("/api/auth/login", json={"username": "admin", "password": "Revo123456"})
        yield ac
    app.dependency_overrides.clear()
```

(Replace the previous `client` fixture body with this version.)

- [ ] **Step 4: Tests (`api/tests/test_companies_create.py`)**

```python
import pytest

@pytest.mark.asyncio
async def test_create_company_returns_full_report(client):
    r = await client.post("/api/companies", json={"name": "Acme"})
    assert r.status_code == 201
    body = r.json()
    assert body["name"] == "Acme"
    assert body["status"] == "ready"
    assert len(body["competitors"]) == 5
    assert body["score_total"] > 0

@pytest.mark.asyncio
async def test_list_after_create(client):
    await client.post("/api/companies", json={"name": "Acme"})
    r = await client.get("/api/companies")
    assert r.status_code == 200
    assert len(r.json()) == 1

@pytest.mark.asyncio
async def test_regenerate(client):
    create = await client.post("/api/companies", json={"name": "Acme"})
    cid = create.json()["id"]
    r = await client.post(f"/api/companies/{cid}/regenerate")
    assert r.status_code == 200
    assert r.json()["status"] == "ready"
```

- [ ] **Step 5: Run, commit**

```bash
pytest -v
git add api/
git commit -m "feat(api): POST /companies + regenerate with AI integration"
```

### Task 4.4: Notes endpoints

**Files:**
- Create: `api/app/api/routes/notes.py`
- Modify: `api/app/main.py`
- Create: `api/tests/test_notes.py`

- [ ] **Step 1: `api/app/schemas/company.py` — add `NoteCreate`** (append)

```python
class NoteCreate(BaseModel):
    body: str = Field(min_length=1, max_length=2000)
```

- [ ] **Step 2: `api/app/api/routes/notes.py`**

```python
import uuid
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.api.deps import require_admin
from app.db.session import get_db
from app.models.note import Note
from app.schemas.company import NoteCreate, NoteOut
from app.services import company_repo

router = APIRouter(prefix="/api/companies/{company_id}/notes", tags=["notes"], dependencies=[Depends(require_admin)])

@router.post("", response_model=NoteOut, status_code=status.HTTP_201_CREATED)
async def create_note(company_id: uuid.UUID, payload: NoteCreate, db: AsyncSession = Depends(get_db)):
    company = await company_repo.get_company(db, company_id)
    if not company:
        raise HTTPException(status.HTTP_404_NOT_FOUND)
    note = Note(company_id=company_id, body=payload.body)
    db.add(note)
    await db.commit()
    await db.refresh(note)
    return note

@router.delete("/{note_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_note(company_id: uuid.UUID, note_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    from sqlalchemy import select
    note = (await db.scalars(select(Note).where(Note.id == note_id, Note.company_id == company_id))).one_or_none()
    if not note:
        raise HTTPException(status.HTTP_404_NOT_FOUND)
    await db.delete(note)
    await db.commit()
```

- [ ] **Step 3: Wire router; test (`api/tests/test_notes.py`)**

```python
import pytest

@pytest.mark.asyncio
async def test_add_and_delete_note(client):
    cid = (await client.post("/api/companies", json={"name": "Acme"})).json()["id"]
    n = await client.post(f"/api/companies/{cid}/notes", json={"body": "interesting team"})
    assert n.status_code == 201
    note_id = n.json()["id"]
    detail = (await client.get(f"/api/companies/{cid}")).json()
    assert any(x["id"] == note_id for x in detail["notes"])
    d = await client.delete(f"/api/companies/{cid}/notes/{note_id}")
    assert d.status_code == 204
```

- [ ] **Step 4: Run, commit**

```bash
pytest -v
git add api/
git commit -m "feat(api): notes CRUD"
```

### Task 4.5: Compare endpoint

**Files:**
- Create: `api/app/api/routes/compare.py`
- Create: `api/app/schemas/compare.py`
- Modify: `api/app/main.py`
- Create: `api/tests/test_compare.py`

- [ ] **Step 1: `api/app/schemas/compare.py`**

```python
import uuid
from pydantic import BaseModel
from app.schemas.company import CompanyDetail

class CompareRequest(BaseModel):
    a_id: uuid.UUID
    b_id: uuid.UUID

class CompareResponse(BaseModel):
    a: CompanyDetail
    b: CompanyDetail
```

- [ ] **Step 2: `api/app/api/routes/compare.py`**

```python
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.api.deps import require_admin
from app.db.session import get_db
from app.schemas.compare import CompareRequest, CompareResponse
from app.services import company_repo

router = APIRouter(prefix="/api/compare", tags=["compare"], dependencies=[Depends(require_admin)])

@router.post("", response_model=CompareResponse)
async def compare(payload: CompareRequest, db: AsyncSession = Depends(get_db)):
    a = await company_repo.get_company(db, payload.a_id)
    b = await company_repo.get_company(db, payload.b_id)
    if not a or not b:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "one or both companies not found")
    return CompareResponse(a=a, b=b)
```

- [ ] **Step 3: Test (`api/tests/test_compare.py`)**

```python
import pytest

@pytest.mark.asyncio
async def test_compare_two_companies(client):
    a_id = (await client.post("/api/companies", json={"name": "Acme"})).json()["id"]
    b_id = (await client.post("/api/companies", json={"name": "Globex"})).json()["id"]
    r = await client.post("/api/compare", json={"a_id": a_id, "b_id": b_id})
    assert r.status_code == 200
    body = r.json()
    assert body["a"]["name"] == "Acme"
    assert body["b"]["name"] == "Globex"
```

- [ ] **Step 4: Run, commit**

```bash
pytest -v
git add api/
git commit -m "feat(api): compare endpoint"
```

---

## Phase 5 — Observability

### Task 5.1: Custom Prometheus metrics + instrumentator

**Files:**
- Create: `api/app/observability/__init__.py`, `api/app/observability/metrics.py`
- Modify: `api/app/main.py`
- Modify: `api/app/services/report_service.py` (record metrics)
- Modify: `api/app/api/routes/companies.py` (record metrics)
- Create: `api/tests/test_metrics.py`

- [ ] **Step 1: `api/app/observability/metrics.py`**

```python
from prometheus_client import Counter, Histogram

ai_generation_total = Counter(
    "ai_generation_total", "AI report generations", ["result", "kind"]
)
ai_generation_duration = Histogram(
    "ai_generation_duration_seconds", "AI generation latency"
)
companies_created_total = Counter("companies_created_total", "Total companies created")
report_regenerations_total = Counter("report_regenerations_total", "Total report regenerations")
pdf_exports_total = Counter("pdf_exports_total", "Total PDF exports")
errors_total = Counter("errors_total", "Backend errors", ["kind"])
```

- [ ] **Step 2: Wire instrumentator in `main.py`**

```python
from prometheus_fastapi_instrumentator import Instrumentator
Instrumentator().instrument(app).expose(app, endpoint="/metrics", include_in_schema=False)
```

- [ ] **Step 3: Record metrics in `report_service.py`**

Wrap the AI call in `create_with_report` and `regenerate_report`:

```python
import time
from app.observability.metrics import ai_generation_total, ai_generation_duration, companies_created_total, report_regenerations_total, errors_total

# inside create_with_report, replace the try/except around ai.generate_report:
start = time.perf_counter()
try:
    report = await ai.generate_report(payload)
    ai_generation_total.labels(result="success", kind="report").inc()
except Exception as e:
    ai_generation_total.labels(result="failure", kind="report").inc()
    errors_total.labels(kind="ai").inc()
    company.status = "failed"
    company.error_message = str(e)[:500]
    await db.commit()
    raise
finally:
    ai_generation_duration.observe(time.perf_counter() - start)

# at the end of successful create_with_report (before return):
companies_created_total.inc()

# inside regenerate_report after successful generation:
report_regenerations_total.inc()
ai_generation_total.labels(result="success", kind="regenerate").inc()
# inside regenerate_report exception path:
ai_generation_total.labels(result="failure", kind="regenerate").inc()
```

- [ ] **Step 4: Test (`api/tests/test_metrics.py`)**

```python
import pytest

@pytest.mark.asyncio
async def test_metrics_endpoint(client):
    r = await client.get("/metrics")
    assert r.status_code == 200
    assert "ai_generation_total" in r.text  # registered counter is exposed
    assert "companies_created_total" in r.text

@pytest.mark.asyncio
async def test_companies_created_counter_increments(client):
    before = (await client.get("/metrics")).text
    await client.post("/api/companies", json={"name": "Acme"})
    after = (await client.get("/metrics")).text
    # crude check: counter line moved from 0 to >=1
    assert "companies_created_total 1.0" in after or "companies_created_total{" in after
```

- [ ] **Step 5: Run, commit**

```bash
pytest -v
git add api/
git commit -m "feat(api): prometheus metrics + custom counters"
```

### Task 5.2: Prometheus + Grafana docker-compose services + provisioning

**Files:**
- Modify: `docker-compose.yml`
- Modify: `prometheus.yml`
- Create: `grafana-provisioning/datasources/datasource.yml`
- Create: `grafana-provisioning/dashboards/dashboard.yml`
- Create: `grafana-provisioning/dashboards/company-intel.json`

- [ ] **Step 1: Append to `docker-compose.yml`**

```yaml
  prometheus:
    image: prom/prometheus:latest
    volumes:
      - ./prometheus.yml:/etc/prometheus/config.yml:ro
    command: ["--config.file=/etc/prometheus/config.yml"]
    ports: ["9090:9090"]
    depends_on: { api: { condition: service_started } }

  grafana:
    image: grafana/grafana:latest
    environment:
      GF_SECURITY_ADMIN_USER: admin
      GF_SECURITY_ADMIN_PASSWORD: admin
      GF_AUTH_ANONYMOUS_ENABLED: "true"
      GF_AUTH_ANONYMOUS_ORG_ROLE: Viewer
    volumes:
      - ./grafana-provisioning:/etc/grafana/provisioning:ro
      - grafana-data:/var/lib/grafana
    ports: ["3000:3000"]
    depends_on: [prometheus]
```

Add `grafana-data:` to the `volumes:` block at the bottom.

- [ ] **Step 2: `grafana-provisioning/datasources/datasource.yml`**

```yaml
apiVersion: 1
datasources:
  - name: Prometheus
    type: prometheus
    access: proxy
    url: http://prometheus:9090
    isDefault: true
```

- [ ] **Step 3: `grafana-provisioning/dashboards/dashboard.yml`**

```yaml
apiVersion: 1
providers:
  - name: default
    folder: ""
    type: file
    options:
      path: /etc/grafana/provisioning/dashboards
```

- [ ] **Step 4: `grafana-provisioning/dashboards/company-intel.json`**

A minimal dashboard with 4 panels: HTTP request rate, request p95 latency, AI success/failure ratio, AI duration p95.

```json
{
  "title": "Company Intel — Service",
  "schemaVersion": 39,
  "version": 1,
  "panels": [
    {"type": "timeseries", "title": "HTTP requests / sec", "targets": [{"expr": "sum(rate(http_requests_total[1m]))"}], "gridPos": {"h":8,"w":12,"x":0,"y":0}},
    {"type": "timeseries", "title": "p95 request latency",  "targets": [{"expr": "histogram_quantile(0.95, sum(rate(http_request_duration_seconds_bucket[5m])) by (le))"}], "gridPos": {"h":8,"w":12,"x":12,"y":0}},
    {"type": "stat",        "title": "AI successes",        "targets": [{"expr": "sum(ai_generation_total{result=\"success\"})"}], "gridPos": {"h":8,"w":6,"x":0,"y":8}},
    {"type": "stat",        "title": "AI failures",         "targets": [{"expr": "sum(ai_generation_total{result=\"failure\"})"}], "gridPos": {"h":8,"w":6,"x":6,"y":8}},
    {"type": "timeseries",  "title": "AI duration p95",     "targets": [{"expr": "histogram_quantile(0.95, sum(rate(ai_generation_duration_seconds_bucket[5m])) by (le))"}], "gridPos": {"h":8,"w":12,"x":12,"y":8}}
  ]
}
```

- [ ] **Step 5: Verify locally**

```bash
docker compose up -d prometheus grafana
open http://localhost:9090   # Status > Targets — api endpoint appears (will be DOWN until api container runs)
open http://localhost:3000   # Dashboards > Company Intel — Service
```

- [ ] **Step 6: Commit**

```bash
git add docker-compose.yml prometheus.yml grafana-provisioning/
git commit -m "feat(infra): prometheus + grafana with provisioned dashboard"
```

---

## Phase 6 — PDF Export

### Task 6.1: PDF export endpoint

**Files:**
- Create: `api/app/services/pdf_service.py`
- Modify: `api/app/api/routes/companies.py`
- Create: `api/tests/test_pdf.py`

- [ ] **Step 1: `api/app/services/pdf_service.py`**

```python
from io import BytesIO
from weasyprint import HTML
from app.models.company import Company

def render_pdf(company: Company) -> bytes:
    html = _render_html(company)
    return HTML(string=html).write_pdf()

def _render_html(c: Company) -> str:
    competitors_html = "".join(
        f"<li><b>{x.name}</b> (strength {x.strength_score}/100)<ul>"
        + "".join(f"<li>{b}</li>" for b in (x.summary or []))
        + "</ul></li>"
        for x in c.competitors
    )
    bullets = lambda xs: "".join(f"<li>{b}</li>" for b in (xs or []))
    return f"""
<html><head><meta charset="utf-8">
<style>
  body {{ font-family: -apple-system, Helvetica, Arial; margin: 32px; color:#1a1a1a; }}
  h1 {{ margin: 0; }}
  h2 {{ margin-top: 24px; border-bottom: 1px solid #ddd; padding-bottom: 4px; }}
  .meta {{ color: #555; font-size: 12px; margin-bottom: 16px; }}
  .score {{ font-size: 36px; font-weight: 700; }}
</style></head><body>
  <h1>{c.name}</h1>
  <div class="meta">{c.market_tag or ""} · HQ: {c.hq or "—"} · {c.website or ""}</div>
  <div class="score">Score: {c.score_total or 0}/100</div>
  <h2>Summary</h2><ul>{bullets(c.summary)}</ul>
  <h2>Investment Thesis</h2><ul>{bullets(c.investment_thesis)}</ul>
  <h2>Risks &amp; Red Flags</h2><ul>{bullets(c.risks)}</ul>
  <h2>Why This Company Matters</h2><ul>{bullets(c.why_matters)}</ul>
  <h2>Competitors</h2><ol>{competitors_html}</ol>
  <h2>Investment Memo</h2><div>{(c.memo_markdown or "").replace(chr(10), "<br/>")}</div>
</body></html>
"""
```

- [ ] **Step 2: Endpoint in `companies.py`** (append)

```python
from fastapi.responses import StreamingResponse
from app.services.pdf_service import render_pdf
from app.observability.metrics import pdf_exports_total

@router.get("/{company_id}/export.pdf")
async def export_pdf(company_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    company = await company_repo.get_company(db, company_id)
    if not company:
        raise HTTPException(status.HTTP_404_NOT_FOUND)
    pdf_bytes = render_pdf(company)
    pdf_exports_total.inc()
    headers = {"Content-Disposition": f'attachment; filename="{company.name}-report.pdf"'}
    from io import BytesIO
    return StreamingResponse(BytesIO(pdf_bytes), media_type="application/pdf", headers=headers)
```

- [ ] **Step 3: Test (`api/tests/test_pdf.py`)**

```python
import pytest

@pytest.mark.asyncio
async def test_pdf_export_returns_pdf(client):
    cid = (await client.post("/api/companies", json={"name": "Acme"})).json()["id"]
    r = await client.get(f"/api/companies/{cid}/export.pdf")
    assert r.status_code == 200
    assert r.headers["content-type"] == "application/pdf"
    assert r.content[:4] == b"%PDF"
```

- [ ] **Step 4: Run, commit**

```bash
pytest -v
git add api/
git commit -m "feat(api): PDF export of company report"
```

---

## Phase 7 — Frontend

### Task 7.1: Vite + React + TS + Tailwind + shadcn bootstrap

**Files:**
- Create: `ui/package.json`, `ui/vite.config.ts`, `ui/tsconfig.json`, `ui/tsconfig.node.json`, `ui/index.html`, `ui/postcss.config.js`, `ui/tailwind.config.ts`, `ui/.env.example`, `ui/src/main.tsx`, `ui/src/App.tsx`, `ui/src/styles/index.css`, `ui/components.json`, `ui/src/lib/cn.ts`

- [ ] **Step 1: Bootstrap Vite**

```bash
cd ui
npm create vite@latest . -- --template react-ts
npm install
```

- [ ] **Step 2: Install deps**

```bash
npm i axios react-router-dom @tanstack/react-query sonner lucide-react clsx tailwind-merge zod react-markdown
npm i -D tailwindcss postcss autoprefixer @types/node vitest @testing-library/react @testing-library/jest-dom jsdom
npx tailwindcss init -p
```

- [ ] **Step 3: `ui/.env.example`**

```
VITE_API_BASE_URL=http://localhost:8000
```

- [ ] **Step 4: `ui/tailwind.config.ts`**

```ts
import type { Config } from "tailwindcss";

export default {
  content: ["./index.html", "./src/**/*.{ts,tsx}"],
  theme: {
    extend: {
      colors: {
        background: "hsl(var(--background))",
        foreground: "hsl(var(--foreground))",
        muted: "hsl(var(--muted))",
        "muted-foreground": "hsl(var(--muted-foreground))",
        border: "hsl(var(--border))",
        primary: "hsl(var(--primary))",
        "primary-foreground": "hsl(var(--primary-foreground))",
        accent: "hsl(var(--accent))",
        destructive: "hsl(var(--destructive))",
      },
      fontFamily: { sans: ["Inter", "system-ui", "sans-serif"] },
    },
  },
} satisfies Config;
```

- [ ] **Step 5: `ui/src/styles/index.css`**

```css
@tailwind base;
@tailwind components;
@tailwind utilities;

:root {
  --background: 0 0% 100%;
  --foreground: 222 47% 11%;
  --muted: 210 40% 96%;
  --muted-foreground: 215 16% 47%;
  --border: 214 32% 91%;
  --primary: 222 47% 11%;
  --primary-foreground: 210 40% 98%;
  --accent: 210 40% 94%;
  --destructive: 0 72% 51%;
}
html, body, #root { height: 100%; }
body { @apply bg-background text-foreground antialiased; font-family: 'Inter', system-ui, sans-serif; }
```

- [ ] **Step 6: `ui/src/lib/cn.ts`**

```ts
import { clsx, type ClassValue } from "clsx";
import { twMerge } from "tailwind-merge";
export const cn = (...inputs: ClassValue[]) => twMerge(clsx(inputs));
```

- [ ] **Step 7: Wire `index.css` import in `main.tsx` and replace `App.tsx` with a placeholder**

```tsx
// ui/src/main.tsx
import React from "react";
import ReactDOM from "react-dom/client";
import { BrowserRouter } from "react-router-dom";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { Toaster } from "sonner";
import App from "./App";
import "./styles/index.css";

const qc = new QueryClient({ defaultOptions: { queries: { retry: 1, refetchOnWindowFocus: false } } });

ReactDOM.createRoot(document.getElementById("root")!).render(
  <React.StrictMode>
    <QueryClientProvider client={qc}>
      <BrowserRouter>
        <App />
        <Toaster richColors position="top-right" />
      </BrowserRouter>
    </QueryClientProvider>
  </React.StrictMode>
);
```

```tsx
// ui/src/App.tsx — placeholder, fleshed out in 7.4
export default function App() {
  return <div className="p-6">Company Intel AI — booting…</div>;
}
```

- [ ] **Step 8: Verify dev server**

```bash
npm run dev
```

Open http://localhost:5173 — page reads "Company Intel AI — booting…".

- [ ] **Step 9: Commit**

```bash
git add ui/
git commit -m "feat(ui): vite+react+ts+tailwind bootstrap"
```

### Task 7.2: API client + auth context + ProtectedRoute

**Files:**
- Create: `ui/src/lib/api.ts`, `ui/src/lib/types.ts`, `ui/src/lib/auth.tsx`, `ui/src/components/ProtectedRoute.tsx`

- [ ] **Step 1: `ui/src/lib/types.ts`** (matches backend response shapes)

```ts
export type CompanyStatus = "generating" | "ready" | "failed";

export interface ScoreBreakdown {
  market: number; team: number; moat: number; traction: number; fund_fit: number;
}

export interface Competitor {
  name: string; summary: string[]; strength_score: number;
}

export interface Note { id: string; body: string; created_at: string; }

export interface CompanyListItem {
  id: string;
  name: string;
  hq: string | null;
  website: string | null;
  market_tag: string | null;
  score_total: number | null;
  favorite: boolean;
  status: CompanyStatus;
  created_at: string;
}

export interface CompanyDetail extends CompanyListItem {
  context: string | null;
  summary: string[] | null;
  investment_thesis: string[] | null;
  risks: string[] | null;
  why_matters: string[] | null;
  score_breakdown: ScoreBreakdown | null;
  memo_markdown: string | null;
  error_message: string | null;
  competitors: Competitor[];
  notes: Note[];
}
```

- [ ] **Step 2: `ui/src/lib/api.ts`**

```ts
import axios from "axios";
import type { CompanyDetail, CompanyListItem } from "./types";

export const api = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL,
  withCredentials: true,
});

export const Auth = {
  login: (username: string, password: string) =>
    api.post("/api/auth/login", { username, password }),
  logout: () => api.post("/api/auth/logout"),
  me: () => api.get<{ username: string }>("/api/auth/me").then(r => r.data),
};

export const Companies = {
  list: (params: { q?: string; market_tag?: string; favorite?: boolean; sort?: string } = {}) =>
    api.get<CompanyListItem[]>("/api/companies", { params }).then(r => r.data),
  get: (id: string) => api.get<CompanyDetail>(`/api/companies/${id}`).then(r => r.data),
  create: (payload: { name: string; hq?: string; website?: string; context?: string }) =>
    api.post<CompanyDetail>("/api/companies", payload).then(r => r.data),
  patch: (id: string, payload: Partial<{ hq: string; website: string; context: string; favorite: boolean }>) =>
    api.patch<CompanyDetail>(`/api/companies/${id}`, payload).then(r => r.data),
  remove: (id: string) => api.delete(`/api/companies/${id}`),
  regenerate: (id: string) => api.post<CompanyDetail>(`/api/companies/${id}/regenerate`).then(r => r.data),
  exportUrl: (id: string) => `${import.meta.env.VITE_API_BASE_URL}/api/companies/${id}/export.pdf`,
};

export const Notes = {
  add: (companyId: string, body: string) =>
    api.post(`/api/companies/${companyId}/notes`, { body }).then(r => r.data),
  remove: (companyId: string, noteId: string) =>
    api.delete(`/api/companies/${companyId}/notes/${noteId}`),
};

export const Compare = {
  run: (a_id: string, b_id: string) =>
    api.post<{ a: CompanyDetail; b: CompanyDetail }>("/api/compare", { a_id, b_id }).then(r => r.data),
};
```

- [ ] **Step 3: `ui/src/lib/auth.tsx`**

```tsx
import { createContext, useContext, useEffect, useState, type ReactNode } from "react";
import { Auth } from "./api";

interface Ctx { user: string | null; loading: boolean; login: (u:string,p:string)=>Promise<void>; logout: ()=>Promise<void>; }
const AuthContext = createContext<Ctx | null>(null);

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    Auth.me().then(d => setUser(d.username)).catch(() => setUser(null)).finally(() => setLoading(false));
  }, []);

  return (
    <AuthContext.Provider value={{
      user, loading,
      login: async (u, p) => { await Auth.login(u, p); const me = await Auth.me(); setUser(me.username); },
      logout: async () => { await Auth.logout(); setUser(null); },
    }}>{children}</AuthContext.Provider>
  );
}

export const useAuth = () => {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error("useAuth outside provider");
  return ctx;
};
```

- [ ] **Step 4: `ui/src/components/ProtectedRoute.tsx`**

```tsx
import { Navigate } from "react-router-dom";
import { useAuth } from "@/lib/auth";

export function ProtectedRoute({ children }: { children: React.ReactNode }) {
  const { user, loading } = useAuth();
  if (loading) return <div className="p-6 text-muted-foreground">Loading…</div>;
  if (!user) return <Navigate to="/login" replace />;
  return <>{children}</>;
}
```

- [ ] **Step 5: Configure path alias `@`** in `ui/vite.config.ts` and `ui/tsconfig.json`

```ts
// vite.config.ts
import path from "node:path";
import react from "@vitejs/plugin-react";
import { defineConfig } from "vite";
export default defineConfig({
  plugins: [react()],
  resolve: { alias: { "@": path.resolve(__dirname, "./src") } },
});
```

In `tsconfig.json` `compilerOptions`:
```json
"baseUrl": ".",
"paths": { "@/*": ["src/*"] }
```

- [ ] **Step 6: Commit**

```bash
git add ui/
git commit -m "feat(ui): api client + auth context + ProtectedRoute"
```

### Task 7.3: shadcn primitives we need

For each component, install via the shadcn CLI or copy from the registry. We need: `button`, `input`, `label`, `dialog`, `dropdown-menu`, `card`, `badge`, `separator`, `textarea`, `tabs`, `toggle`, `tooltip`.

- [ ] **Step 1: Initialize shadcn** (uses our existing tailwind config)

```bash
cd ui
npx shadcn@latest init -y
```

When prompted, accept defaults (style: default, base color: slate, css var: yes). It will write `components.json` and tweak `tailwind.config.ts` and `index.css`. Re-apply the project palette in `index.css` if it overwrites the `:root` block.

- [ ] **Step 2: Add primitives**

```bash
npx shadcn@latest add button input label dialog dropdown-menu card badge separator textarea tabs tooltip
```

This creates `ui/src/components/ui/*.tsx`.

- [ ] **Step 3: Commit**

```bash
git add ui/
git commit -m "feat(ui): shadcn primitives (button/input/dialog/card/...)"
```

### Task 7.4: Login page + router

**Files:**
- Modify: `ui/src/App.tsx`
- Create: `ui/src/pages/Login.tsx`
- Create: `ui/src/components/layout/AppShell.tsx`, `ui/src/components/layout/TopBar.tsx`
- Create: `ui/src/pages/Dashboard.tsx` (placeholder, fleshed out in 7.5)

- [ ] **Step 1: `ui/src/pages/Login.tsx`**

```tsx
import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { useAuth } from "@/lib/auth";
import { toast } from "sonner";

export default function Login() {
  const { login } = useAuth();
  const nav = useNavigate();
  const [u, setU] = useState("admin");
  const [p, setP] = useState("");
  const [busy, setBusy] = useState(false);

  const submit = async (e: React.FormEvent) => {
    e.preventDefault(); setBusy(true);
    try { await login(u, p); nav("/"); }
    catch { toast.error("Invalid credentials"); }
    finally { setBusy(false); }
  };

  return (
    <div className="min-h-screen grid place-items-center bg-muted">
      <form onSubmit={submit} className="bg-background border rounded-2xl shadow-sm p-8 w-[380px] space-y-4">
        <div>
          <h1 className="text-xl font-semibold">Company Intel AI</h1>
          <p className="text-sm text-muted-foreground">Internal VC analyst tool · sign in to continue</p>
        </div>
        <div className="space-y-2">
          <Label>Username</Label>
          <Input value={u} onChange={e => setU(e.target.value)} autoFocus />
        </div>
        <div className="space-y-2">
          <Label>Password</Label>
          <Input type="password" value={p} onChange={e => setP(e.target.value)} />
        </div>
        <Button type="submit" disabled={busy} className="w-full">{busy ? "Signing in…" : "Sign in"}</Button>
      </form>
    </div>
  );
}
```

- [ ] **Step 2: `ui/src/components/layout/TopBar.tsx`**

```tsx
import { Link, useLocation } from "react-router-dom";
import { Button } from "@/components/ui/button";
import { useAuth } from "@/lib/auth";

export function TopBar() {
  const { user, logout } = useAuth();
  const loc = useLocation();
  return (
    <header className="border-b bg-background sticky top-0 z-10">
      <div className="max-w-7xl mx-auto flex items-center justify-between px-6 h-14">
        <Link to="/" className="font-semibold">Company Intel AI</Link>
        <nav className="flex items-center gap-3 text-sm">
          <Link to="/" className={loc.pathname === "/" ? "font-medium" : "text-muted-foreground"}>Dashboard</Link>
          <Link to="/compare" className={loc.pathname.startsWith("/compare") ? "font-medium" : "text-muted-foreground"}>Compare</Link>
          <span className="text-muted-foreground">·</span>
          <span className="text-muted-foreground">{user}</span>
          <Button variant="ghost" size="sm" onClick={logout}>Sign out</Button>
        </nav>
      </div>
    </header>
  );
}
```

- [ ] **Step 3: `ui/src/components/layout/AppShell.tsx`**

```tsx
import { TopBar } from "./TopBar";
export function AppShell({ children }: { children: React.ReactNode }) {
  return (
    <div className="min-h-screen bg-muted/30">
      <TopBar />
      <main className="max-w-7xl mx-auto px-6 py-8">{children}</main>
    </div>
  );
}
```

- [ ] **Step 4: `ui/src/App.tsx`** — full router

```tsx
import { Route, Routes } from "react-router-dom";
import { AuthProvider } from "@/lib/auth";
import { ProtectedRoute } from "@/components/ProtectedRoute";
import { AppShell } from "@/components/layout/AppShell";
import Login from "@/pages/Login";
import Dashboard from "@/pages/Dashboard";
import CompanyDetail from "@/pages/CompanyDetail";
import Compare from "@/pages/Compare";

export default function App() {
  return (
    <AuthProvider>
      <Routes>
        <Route path="/login" element={<Login />} />
        <Route path="/" element={<ProtectedRoute><AppShell><Dashboard /></AppShell></ProtectedRoute>} />
        <Route path="/companies/:id" element={<ProtectedRoute><AppShell><CompanyDetail /></AppShell></ProtectedRoute>} />
        <Route path="/compare" element={<ProtectedRoute><AppShell><Compare /></AppShell></ProtectedRoute>} />
      </Routes>
    </AuthProvider>
  );
}
```

- [ ] **Step 5: Placeholder `Dashboard.tsx`, `CompanyDetail.tsx`, `Compare.tsx`** (each just `export default function() { return <div>TODO</div>; }`) — replaced in next tasks.

- [ ] **Step 6: Manual smoke test**: `npm run dev` → http://localhost:5173 redirects to `/login`; sign in with admin/Revo123456 → lands on placeholder dashboard. Commit.

```bash
git add ui/
git commit -m "feat(ui): login page + router + protected layout"
```

### Task 7.5: Dashboard — list, filters, create modal

**Files:**
- Replace: `ui/src/pages/Dashboard.tsx`
- Create: `ui/src/components/companies/CreateCompanyModal.tsx`, `ui/src/components/companies/CompanyTable.tsx`, `ui/src/components/companies/CompanyFilters.tsx`, `ui/src/components/companies/StatusPill.tsx`, `ui/src/components/companies/EmptyState.tsx`

- [ ] **Step 1: `StatusPill.tsx`**

```tsx
import { cn } from "@/lib/cn";
import type { CompanyStatus } from "@/lib/types";
const map: Record<CompanyStatus, string> = {
  generating: "bg-yellow-100 text-yellow-800",
  ready: "bg-emerald-100 text-emerald-800",
  failed: "bg-red-100 text-red-800",
};
export function StatusPill({ status }: { status: CompanyStatus }) {
  return <span className={cn("text-xs px-2 py-0.5 rounded-full font-medium", map[status])}>{status}</span>;
}
```

- [ ] **Step 2: `EmptyState.tsx`**

```tsx
import { Button } from "@/components/ui/button";
import { Sparkles } from "lucide-react";
export function EmptyState({ onCreate }: { onCreate: () => void }) {
  return (
    <div className="border border-dashed rounded-2xl p-16 text-center bg-background">
      <Sparkles className="mx-auto mb-3 h-8 w-8 text-muted-foreground" />
      <h3 className="font-medium">No companies yet</h3>
      <p className="text-sm text-muted-foreground mb-4">Create your first AI-generated company report.</p>
      <Button onClick={onCreate}>Create company</Button>
    </div>
  );
}
```

- [ ] **Step 3: `CompanyFilters.tsx`**

```tsx
import { Input } from "@/components/ui/input";
import { Toggle } from "@/components/ui/toggle";
import { Star } from "lucide-react";

interface Props {
  q: string; setQ: (v: string) => void;
  marketTag: string; setMarketTag: (v: string) => void;
  favoritesOnly: boolean; setFavoritesOnly: (v: boolean) => void;
  marketTags: string[];
}
export function CompanyFilters(p: Props) {
  return (
    <div className="flex items-center gap-2 flex-wrap">
      <Input placeholder="Search by name or website…" value={p.q} onChange={e => p.setQ(e.target.value)} className="max-w-xs" />
      <select className="h-9 rounded-md border bg-background px-2 text-sm" value={p.marketTag} onChange={e => p.setMarketTag(e.target.value)}>
        <option value="">All markets</option>
        {p.marketTags.map(t => <option key={t} value={t}>{t}</option>)}
      </select>
      <Toggle pressed={p.favoritesOnly} onPressedChange={p.setFavoritesOnly}>
        <Star className="h-4 w-4 mr-1" /> Favorites
      </Toggle>
    </div>
  );
}
```

- [ ] **Step 4: `CompanyTable.tsx`**

```tsx
import { Link } from "react-router-dom";
import type { CompanyListItem } from "@/lib/types";
import { Star } from "lucide-react";
import { StatusPill } from "./StatusPill";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";

interface Props {
  companies: CompanyListItem[];
  onToggleFavorite: (id: string, value: boolean) => void;
}
export function CompanyTable({ companies, onToggleFavorite }: Props) {
  return (
    <div className="border rounded-2xl overflow-hidden bg-background">
      <table className="w-full text-sm">
        <thead className="bg-muted/50">
          <tr className="text-left">
            <th className="px-4 py-3 w-10"></th>
            <th className="px-4 py-3">Company</th>
            <th className="px-4 py-3">Market</th>
            <th className="px-4 py-3">HQ</th>
            <th className="px-4 py-3">Score</th>
            <th className="px-4 py-3">Status</th>
            <th className="px-4 py-3">Created</th>
            <th className="px-4 py-3"></th>
          </tr>
        </thead>
        <tbody>
          {companies.map(c => (
            <tr key={c.id} className="border-t hover:bg-muted/30">
              <td className="px-4 py-3">
                <button onClick={() => onToggleFavorite(c.id, !c.favorite)} aria-label="favorite">
                  <Star className={c.favorite ? "h-4 w-4 fill-yellow-400 text-yellow-500" : "h-4 w-4 text-muted-foreground"} />
                </button>
              </td>
              <td className="px-4 py-3 font-medium">{c.name}</td>
              <td className="px-4 py-3">{c.market_tag ? <Badge variant="secondary">{c.market_tag}</Badge> : "—"}</td>
              <td className="px-4 py-3 text-muted-foreground">{c.hq || "—"}</td>
              <td className="px-4 py-3 font-mono">{c.score_total ?? "—"}</td>
              <td className="px-4 py-3"><StatusPill status={c.status} /></td>
              <td className="px-4 py-3 text-muted-foreground">{new Date(c.created_at).toLocaleDateString()}</td>
              <td className="px-4 py-3 text-right"><Button asChild size="sm" variant="ghost"><Link to={`/companies/${c.id}`}>Open</Link></Button></td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
```

- [ ] **Step 5: `CreateCompanyModal.tsx`**

```tsx
import { useState } from "react";
import { Dialog, DialogContent, DialogFooter, DialogHeader, DialogTitle } from "@/components/ui/dialog";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";
import { Companies } from "@/lib/api";
import { toast } from "sonner";
import { useNavigate } from "react-router-dom";
import { useQueryClient } from "@tanstack/react-query";
import { Loader2, Sparkles } from "lucide-react";

interface Props { open: boolean; onOpenChange: (v: boolean) => void; }
export function CreateCompanyModal({ open, onOpenChange }: Props) {
  const [form, setForm] = useState({ name: "", hq: "", website: "", context: "" });
  const [busy, setBusy] = useState(false);
  const nav = useNavigate();
  const qc = useQueryClient();

  const submit = async (e: React.FormEvent) => {
    e.preventDefault(); setBusy(true);
    try {
      const payload: any = { name: form.name };
      if (form.hq) payload.hq = form.hq;
      if (form.website) payload.website = form.website;
      if (form.context) payload.context = form.context;
      const created = await Companies.create(payload);
      qc.invalidateQueries({ queryKey: ["companies"] });
      toast.success("Report generated");
      onOpenChange(false);
      nav(`/companies/${created.id}`);
    } catch (err: any) {
      toast.error(err.response?.data?.detail || "Failed to create company");
    } finally {
      setBusy(false);
    }
  };

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="sm:max-w-lg">
        <DialogHeader><DialogTitle>Create company</DialogTitle></DialogHeader>
        <form onSubmit={submit} className="space-y-4">
          <div className="space-y-2"><Label>Company name *</Label><Input required value={form.name} onChange={e => setForm({ ...form, name: e.target.value })} /></div>
          <div className="space-y-2"><Label>HQ</Label><Input value={form.hq} onChange={e => setForm({ ...form, hq: e.target.value })} placeholder="San Francisco, CA" /></div>
          <div className="space-y-2"><Label>Website</Label><Input type="url" value={form.website} onChange={e => setForm({ ...form, website: e.target.value })} placeholder="https://acme.com" /></div>
          <div className="space-y-2"><Label>Context (optional)</Label><Textarea rows={3} value={form.context} onChange={e => setForm({ ...form, context: e.target.value })} placeholder="Anything you'd like the AI to know" /></div>
          {busy && (
            <div className="flex items-center gap-2 text-sm text-muted-foreground bg-muted rounded-lg p-3">
              <Loader2 className="h-4 w-4 animate-spin" />
              <span>Researching, analyzing competitors, scoring… this takes ~10s</span>
            </div>
          )}
          <DialogFooter>
            <Button variant="ghost" type="button" onClick={() => onOpenChange(false)} disabled={busy}>Cancel</Button>
            <Button type="submit" disabled={busy}><Sparkles className="h-4 w-4 mr-2" />{busy ? "Generating…" : "Generate report"}</Button>
          </DialogFooter>
        </form>
      </DialogContent>
    </Dialog>
  );
}
```

- [ ] **Step 6: `Dashboard.tsx`**

```tsx
import { useMemo, useState } from "react";
import { useQuery, useQueryClient } from "@tanstack/react-query";
import { Companies } from "@/lib/api";
import { Button } from "@/components/ui/button";
import { CreateCompanyModal } from "@/components/companies/CreateCompanyModal";
import { CompanyTable } from "@/components/companies/CompanyTable";
import { CompanyFilters } from "@/components/companies/CompanyFilters";
import { EmptyState } from "@/components/companies/EmptyState";
import { Plus } from "lucide-react";
import { toast } from "sonner";

export default function Dashboard() {
  const [open, setOpen] = useState(false);
  const [q, setQ] = useState("");
  const [marketTag, setMarketTag] = useState("");
  const [favoritesOnly, setFavoritesOnly] = useState(false);
  const qc = useQueryClient();

  const { data, isLoading } = useQuery({
    queryKey: ["companies", { q, marketTag, favoritesOnly }],
    queryFn: () => Companies.list({
      q: q || undefined,
      market_tag: marketTag || undefined,
      favorite: favoritesOnly || undefined,
    }),
  });

  const marketTags = useMemo(
    () => Array.from(new Set((data ?? []).map(c => c.market_tag).filter(Boolean) as string[])).sort(),
    [data]
  );

  const toggleFavorite = async (id: string, value: boolean) => {
    try { await Companies.patch(id, { favorite: value }); qc.invalidateQueries({ queryKey: ["companies"] }); }
    catch { toast.error("Failed to update favorite"); }
  };

  return (
    <div className="space-y-6">
      <div className="flex items-end justify-between gap-4">
        <div>
          <h1 className="text-2xl font-semibold tracking-tight">Companies</h1>
          <p className="text-muted-foreground text-sm">AI-generated intelligence reports for VC analysis.</p>
        </div>
        <Button onClick={() => setOpen(true)}><Plus className="h-4 w-4 mr-2" />Create company</Button>
      </div>

      <CompanyFilters q={q} setQ={setQ} marketTag={marketTag} setMarketTag={setMarketTag}
        favoritesOnly={favoritesOnly} setFavoritesOnly={setFavoritesOnly} marketTags={marketTags} />

      {isLoading
        ? <div className="text-muted-foreground text-sm">Loading…</div>
        : (data && data.length > 0)
          ? <CompanyTable companies={data} onToggleFavorite={toggleFavorite} />
          : <EmptyState onCreate={() => setOpen(true)} />}

      <CreateCompanyModal open={open} onOpenChange={setOpen} />
    </div>
  );
}
```

- [ ] **Step 7: Smoke test, commit**

`npm run dev`, log in, create a company. Commit.

```bash
git add ui/
git commit -m "feat(ui): dashboard with filters, table, create-company modal"
```

### Task 7.6: Company detail page

**Files:**
- Replace: `ui/src/pages/CompanyDetail.tsx`
- Create: `ui/src/components/companies/ScoreGauge.tsx`, `ui/src/components/companies/CompetitorGrid.tsx`, `ui/src/components/companies/InvestmentMemo.tsx`, `ui/src/components/companies/NotesPanel.tsx`, `ui/src/components/companies/BulletList.tsx`

- [ ] **Step 1: `BulletList.tsx`**

```tsx
export function BulletList({ items }: { items: string[] | null }) {
  if (!items?.length) return <p className="text-muted-foreground text-sm">—</p>;
  return <ul className="list-disc pl-5 space-y-1.5 text-sm">{items.map((t, i) => <li key={i}>{t}</li>)}</ul>;
}
```

- [ ] **Step 2: `ScoreGauge.tsx`**

```tsx
import type { ScoreBreakdown } from "@/lib/types";
const labels: Array<[keyof ScoreBreakdown, string]> = [
  ["market", "Market"], ["team", "Team"], ["moat", "Moat"], ["traction", "Traction"], ["fund_fit", "Fund fit"],
];
export function ScoreGauge({ total, breakdown }: { total: number | null; breakdown: ScoreBreakdown | null }) {
  const score = total ?? 0;
  const tone = score >= 75 ? "text-emerald-600" : score >= 50 ? "text-amber-600" : "text-red-600";
  return (
    <div className="border rounded-2xl p-6 bg-background">
      <div className="flex items-baseline gap-3">
        <div className={`text-5xl font-bold ${tone}`}>{score}</div>
        <div className="text-muted-foreground">/ 100 deal score</div>
      </div>
      {breakdown && (
        <div className="mt-4 space-y-2">
          {labels.map(([k, label]) => (
            <div key={k}>
              <div className="flex justify-between text-xs mb-1"><span>{label}</span><span className="font-mono">{breakdown[k]}</span></div>
              <div className="h-2 rounded-full bg-muted overflow-hidden"><div className="h-full bg-primary" style={{ width: `${breakdown[k]}%` }} /></div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
```

- [ ] **Step 3: `CompetitorGrid.tsx`**

```tsx
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import type { Competitor } from "@/lib/types";

export function CompetitorGrid({ competitors }: { competitors: Competitor[] }) {
  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
      {competitors.map((c, i) => (
        <Card key={i}>
          <CardHeader className="pb-2">
            <div className="flex items-center justify-between">
              <CardTitle className="text-base">{c.name}</CardTitle>
              <span className="font-mono text-sm">{c.strength_score}/100</span>
            </div>
            <div className="h-1.5 rounded-full bg-muted overflow-hidden"><div className="h-full bg-primary" style={{ width: `${c.strength_score}%` }} /></div>
          </CardHeader>
          <CardContent><ul className="list-disc pl-5 space-y-1 text-sm">{c.summary.map((s, j) => <li key={j}>{s}</li>)}</ul></CardContent>
        </Card>
      ))}
    </div>
  );
}
```

- [ ] **Step 4: `InvestmentMemo.tsx`**

```tsx
import ReactMarkdown from "react-markdown";
export function InvestmentMemo({ markdown }: { markdown: string | null }) {
  if (!markdown) return <p className="text-muted-foreground text-sm">No memo generated.</p>;
  return <article className="prose prose-sm max-w-none"><ReactMarkdown>{markdown}</ReactMarkdown></article>;
}
```

Add `@tailwindcss/typography` or rely on a manual style. For MVP, leave default.

- [ ] **Step 5: `NotesPanel.tsx`**

```tsx
import { useState } from "react";
import { Notes } from "@/lib/api";
import type { Note } from "@/lib/types";
import { Button } from "@/components/ui/button";
import { Textarea } from "@/components/ui/textarea";
import { Trash2 } from "lucide-react";

interface Props { companyId: string; notes: Note[]; onChange: () => void; }
export function NotesPanel({ companyId, notes, onChange }: Props) {
  const [text, setText] = useState("");
  const [busy, setBusy] = useState(false);
  const add = async () => {
    if (!text.trim()) return;
    setBusy(true);
    await Notes.add(companyId, text.trim());
    setText(""); setBusy(false); onChange();
  };
  const remove = async (id: string) => { await Notes.remove(companyId, id); onChange(); };
  return (
    <div className="space-y-3">
      <Textarea rows={3} value={text} onChange={e => setText(e.target.value)} placeholder="Add a note…" />
      <Button size="sm" onClick={add} disabled={busy || !text.trim()}>Add note</Button>
      <ul className="space-y-2">
        {notes.map(n => (
          <li key={n.id} className="border rounded-lg p-3 text-sm bg-background flex items-start gap-2">
            <span className="flex-1 whitespace-pre-wrap">{n.body}</span>
            <Button variant="ghost" size="icon" onClick={() => remove(n.id)}><Trash2 className="h-4 w-4" /></Button>
          </li>
        ))}
        {notes.length === 0 && <li className="text-muted-foreground text-sm">No notes yet.</li>}
      </ul>
    </div>
  );
}
```

- [ ] **Step 6: `CompanyDetail.tsx`**

```tsx
import { useParams } from "react-router-dom";
import { useQuery, useQueryClient } from "@tanstack/react-query";
import { Companies } from "@/lib/api";
import { ScoreGauge } from "@/components/companies/ScoreGauge";
import { CompetitorGrid } from "@/components/companies/CompetitorGrid";
import { BulletList } from "@/components/companies/BulletList";
import { InvestmentMemo } from "@/components/companies/InvestmentMemo";
import { NotesPanel } from "@/components/companies/NotesPanel";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Star, RefreshCw, Download, ArrowLeft } from "lucide-react";
import { Link } from "react-router-dom";
import { toast } from "sonner";

export default function CompanyDetail() {
  const { id = "" } = useParams();
  const qc = useQueryClient();
  const { data, isLoading, refetch } = useQuery({ queryKey: ["company", id], queryFn: () => Companies.get(id), enabled: !!id });

  if (isLoading || !data) return <div className="text-muted-foreground">Loading…</div>;

  const regen = async () => {
    if (!confirm("Regenerate the AI report? Existing competitors will be replaced.")) return;
    try { await Companies.regenerate(id); await refetch(); toast.success("Report regenerated"); }
    catch (e: any) { toast.error(e.response?.data?.detail || "Failed to regenerate"); }
  };
  const fav = async () => { await Companies.patch(id, { favorite: !data.favorite }); refetch(); qc.invalidateQueries({ queryKey: ["companies"] }); };

  return (
    <div className="space-y-6">
      <div className="flex items-start justify-between gap-4">
        <div>
          <Link to="/" className="text-sm text-muted-foreground inline-flex items-center gap-1"><ArrowLeft className="h-3 w-3" /> Back</Link>
          <div className="flex items-center gap-3 mt-1">
            <h1 className="text-2xl font-semibold tracking-tight">{data.name}</h1>
            <button onClick={fav} aria-label="favorite"><Star className={data.favorite ? "h-5 w-5 fill-yellow-400 text-yellow-500" : "h-5 w-5 text-muted-foreground"} /></button>
            {data.market_tag && <Badge variant="secondary">{data.market_tag}</Badge>}
          </div>
          <div className="text-sm text-muted-foreground mt-1">
            {data.hq || "—"} · {data.website ? <a className="underline" href={data.website} target="_blank">{data.website}</a> : "—"} · created {new Date(data.created_at).toLocaleDateString()}
          </div>
        </div>
        <div className="flex gap-2">
          <Button variant="outline" onClick={regen}><RefreshCw className="h-4 w-4 mr-2" />Regenerate</Button>
          <a href={Companies.exportUrl(id)} target="_blank" rel="noreferrer">
            <Button variant="outline"><Download className="h-4 w-4 mr-2" />Export PDF</Button>
          </a>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-4">
        <div className="lg:col-span-1"><ScoreGauge total={data.score_total} breakdown={data.score_breakdown} /></div>
        <div className="lg:col-span-2 border rounded-2xl bg-background p-6">
          <h3 className="font-medium mb-2">Summary</h3>
          <BulletList items={data.summary} />
        </div>
      </div>

      <Tabs defaultValue="thesis">
        <TabsList>
          <TabsTrigger value="thesis">Investment Thesis</TabsTrigger>
          <TabsTrigger value="risks">Risks</TabsTrigger>
          <TabsTrigger value="why">Why It Matters</TabsTrigger>
          <TabsTrigger value="memo">Investment Memo</TabsTrigger>
          <TabsTrigger value="competitors">Competitors</TabsTrigger>
          <TabsTrigger value="notes">Notes</TabsTrigger>
        </TabsList>
        <TabsContent value="thesis" className="border rounded-2xl bg-background p-6"><BulletList items={data.investment_thesis} /></TabsContent>
        <TabsContent value="risks"  className="border rounded-2xl bg-background p-6"><BulletList items={data.risks} /></TabsContent>
        <TabsContent value="why"    className="border rounded-2xl bg-background p-6"><BulletList items={data.why_matters} /></TabsContent>
        <TabsContent value="memo"   className="border rounded-2xl bg-background p-6"><InvestmentMemo markdown={data.memo_markdown} /></TabsContent>
        <TabsContent value="competitors" className="border rounded-2xl bg-background p-6"><CompetitorGrid competitors={data.competitors} /></TabsContent>
        <TabsContent value="notes"  className="border rounded-2xl bg-background p-6"><NotesPanel companyId={id} notes={data.notes} onChange={() => refetch()} /></TabsContent>
      </Tabs>
    </div>
  );
}
```

- [ ] **Step 7: Smoke test, commit**

```bash
git add ui/
git commit -m "feat(ui): company detail with score, tabs, competitors, memo, notes"
```

### Task 7.7: Compare page

**Files:**
- Replace: `ui/src/pages/Compare.tsx`
- Create: `ui/src/components/companies/CompareView.tsx`

- [ ] **Step 1: `Compare.tsx`**

```tsx
import { useEffect, useMemo, useState } from "react";
import { useQuery } from "@tanstack/react-query";
import { Companies, Compare as Cmp } from "@/lib/api";
import { CompareView } from "@/components/companies/CompareView";

export default function Compare() {
  const list = useQuery({ queryKey: ["companies", "all-for-compare"], queryFn: () => Companies.list({}) });
  const [a, setA] = useState<string>(""); const [b, setB] = useState<string>("");

  useEffect(() => {
    if (!list.data) return;
    if (!a && list.data[0]) setA(list.data[0].id);
    if (!b && list.data[1]) setB(list.data[1].id);
  }, [list.data, a, b]);

  const result = useQuery({ queryKey: ["compare", a, b], queryFn: () => Cmp.run(a, b), enabled: !!a && !!b && a !== b });

  const opts = list.data ?? [];
  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-semibold tracking-tight">Compare</h1>
      <div className="flex gap-3 items-center">
        <select value={a} onChange={e => setA(e.target.value)} className="h-9 rounded-md border bg-background px-2 text-sm">
          {opts.map(c => <option key={c.id} value={c.id}>{c.name}</option>)}
        </select>
        <span className="text-muted-foreground">vs</span>
        <select value={b} onChange={e => setB(e.target.value)} className="h-9 rounded-md border bg-background px-2 text-sm">
          {opts.map(c => <option key={c.id} value={c.id}>{c.name}</option>)}
        </select>
      </div>
      {a === b && <p className="text-sm text-muted-foreground">Pick two different companies.</p>}
      {result.data && <CompareView a={result.data.a} b={result.data.b} />}
    </div>
  );
}
```

- [ ] **Step 2: `CompareView.tsx`**

```tsx
import type { CompanyDetail } from "@/lib/types";
import { Badge } from "@/components/ui/badge";
import { BulletList } from "./BulletList";

const Cell = ({ title, children }: { title: string; children: React.ReactNode }) => (
  <div className="border rounded-2xl p-5 bg-background">
    <h4 className="font-medium mb-2">{title}</h4>
    {children}
  </div>
);

const Column = ({ c }: { c: CompanyDetail }) => (
  <div className="space-y-4">
    <div className="border rounded-2xl p-5 bg-background">
      <div className="text-sm text-muted-foreground">{c.market_tag}</div>
      <h2 className="text-xl font-semibold">{c.name}</h2>
      <div className="text-3xl font-bold mt-2">{c.score_total ?? "—"}<span className="text-sm text-muted-foreground"> /100</span></div>
    </div>
    <Cell title="Summary"><BulletList items={c.summary} /></Cell>
    <Cell title="Thesis"><BulletList items={c.investment_thesis} /></Cell>
    <Cell title="Risks"><BulletList items={c.risks} /></Cell>
    <Cell title="Why it matters"><BulletList items={c.why_matters} /></Cell>
    <Cell title="Top competitor">
      {c.competitors[0] ? (
        <div className="text-sm"><Badge variant="secondary">{c.competitors[0].name}</Badge> — strength {c.competitors[0].strength_score}/100</div>
      ) : <span className="text-muted-foreground text-sm">—</span>}
    </Cell>
  </div>
);

export function CompareView({ a, b }: { a: CompanyDetail; b: CompanyDetail }) {
  return (
    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
      <Column c={a} />
      <Column c={b} />
    </div>
  );
}
```

- [ ] **Step 3: Smoke test, commit**

```bash
git add ui/
git commit -m "feat(ui): compare page (side-by-side two companies)"
```

### Task 7.8: Frontend tests for critical components

**Files:**
- Create: `ui/vitest.config.ts`, `ui/src/test-setup.ts`
- Create: `ui/src/components/companies/__tests__/StatusPill.test.tsx`, `ui/src/components/companies/__tests__/ScoreGauge.test.tsx`

- [ ] **Step 1: `vitest.config.ts`**

```ts
import path from "node:path";
import { defineConfig } from "vitest/config";
import react from "@vitejs/plugin-react";
export default defineConfig({
  plugins: [react()],
  resolve: { alias: { "@": path.resolve(__dirname, "./src") } },
  test: { environment: "jsdom", setupFiles: ["./src/test-setup.ts"], globals: true },
});
```

- [ ] **Step 2: `src/test-setup.ts`**

```ts
import "@testing-library/jest-dom/vitest";
```

- [ ] **Step 3: `StatusPill.test.tsx`**

```tsx
import { render, screen } from "@testing-library/react";
import { StatusPill } from "../StatusPill";

test("renders ready status", () => {
  render(<StatusPill status="ready" />);
  expect(screen.getByText("ready")).toBeInTheDocument();
});
```

- [ ] **Step 4: `ScoreGauge.test.tsx`**

```tsx
import { render, screen } from "@testing-library/react";
import { ScoreGauge } from "../ScoreGauge";

test("renders score value and breakdown bars", () => {
  render(<ScoreGauge total={73} breakdown={{ market: 80, team: 70, moat: 60, traction: 75, fund_fit: 80 }} />);
  expect(screen.getByText("73")).toBeInTheDocument();
  expect(screen.getByText("Market")).toBeInTheDocument();
});
```

- [ ] **Step 5: Add npm script + run + commit**

In `package.json`:
```json
"scripts": { ..., "test": "vitest run" }
```

```bash
npm test
git add ui/
git commit -m "test(ui): vitest setup + critical component tests"
```

---

## Phase 8 — Dockerization (full compose)

### Task 8.1: API Dockerfile

**Files:**
- Create: `api/Dockerfile`
- Modify: `docker-compose.yml`

- [ ] **Step 1: `api/Dockerfile`**

```dockerfile
FROM python:3.12-slim

# WeasyPrint system deps
RUN apt-get update && apt-get install -y --no-install-recommends \
    libpango-1.0-0 libpangoft2-1.0-0 libcairo2 libgdk-pixbuf2.0-0 \
    libffi-dev shared-mime-info fonts-liberation \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY pyproject.toml ./
RUN pip install --no-cache-dir -e .

COPY app ./app
COPY alembic.ini ./alembic.ini
COPY alembic ./alembic

EXPOSE 8000
CMD ["sh", "-c", "alembic upgrade head && uvicorn app.main:app --host 0.0.0.0 --port 8000"]
```

- [ ] **Step 2: Add `api` service to `docker-compose.yml`**

```yaml
  api:
    build: ./api
    environment:
      DATABASE_URL: postgresql+asyncpg://postgres:postgres@db:5432/company_intel
      JWT_SECRET: ${JWT_SECRET:-change-me}
      AI_PROVIDER: ${AI_PROVIDER:-gemini}
      AI_API_KEY: ${AI_API_KEY:-}
      AI_MODEL: ${AI_MODEL:-gemini-2.5-flash}
      CORS_ORIGINS: http://localhost:5173
    ports: ["8000:8000"]
    depends_on:
      db: { condition: service_healthy }
```

- [ ] **Step 3: Smoke test**

```bash
docker compose up --build api db
curl http://localhost:8000/healthz
```

- [ ] **Step 4: Commit**

```bash
git add api/Dockerfile docker-compose.yml
git commit -m "feat(infra): dockerize api"
```

### Task 8.2: UI Dockerfile (nginx static serve)

**Files:**
- Create: `ui/Dockerfile`, `ui/nginx.conf`
- Modify: `docker-compose.yml`

- [ ] **Step 1: `ui/Dockerfile`**

```dockerfile
FROM node:20-alpine AS build
WORKDIR /app
COPY package*.json ./
RUN npm ci
COPY . .
ARG VITE_API_BASE_URL=http://localhost:8000
ENV VITE_API_BASE_URL=$VITE_API_BASE_URL
RUN npm run build

FROM nginx:1.27-alpine
COPY --from=build /app/dist /usr/share/nginx/html
COPY nginx.conf /etc/nginx/conf.d/default.conf
EXPOSE 80
```

- [ ] **Step 2: `ui/nginx.conf`** — SPA fallback

```nginx
server {
  listen 80;
  root /usr/share/nginx/html;
  index index.html;
  location / {
    try_files $uri $uri/ /index.html;
  }
}
```

- [ ] **Step 3: Add `ui` service**

```yaml
  ui:
    build:
      context: ./ui
      args:
        VITE_API_BASE_URL: http://localhost:8000
    ports: ["5173:80"]
    depends_on: [api]
```

- [ ] **Step 4: Full smoke test**

```bash
docker compose up --build
```

Open http://localhost:5173, log in, create a company.

- [ ] **Step 5: Commit**

```bash
git add ui/Dockerfile ui/nginx.conf docker-compose.yml
git commit -m "feat(infra): dockerize ui via nginx + full compose"
```

---

## Phase 9 — Documentation polish

### Task 9.1: README.md

**Files:**
- Modify: `README.md`

- [ ] **Step 1: Replace `README.md`** with the full operator-facing version (run, env vars, all URLs, AI provider, extra feature, verifying observability)

```markdown
# Company Intel AI

AI-powered company intelligence app for VC analysts. Admin logs in, creates a company profile, and gets an AI-generated report (summary, 5 competitors with strength scores, market positioning, investment thesis, risks, "why this matters") plus a **Deal Attractiveness Score (0–100)** and a one-page **AI Investment Memo**.

Built for the Revo Capital tech intern case (2026-05-08).

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
cd api && python -m venv .venv && source .venv/bin/activate
pip install -e ".[dev]"
cp .env.example .env  # set AI_API_KEY
alembic upgrade head
uvicorn app.main:app --reload --port 8000

# 3) frontend (new terminal)
cd ui && cp .env.example .env
npm install && npm run dev
```

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
| `CORS_ORIGINS` | Comma-separated allowlist |

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
cd api && pytest -v
cd ../ui && npm test
```

## Project structure

```
company-intel-ai/
├── api/                 # FastAPI service (alembic, models, services, routes, tests)
├── ui/                  # Vite + React frontend
├── docker-compose.yml   # db, api, ui, prometheus, grafana
├── prometheus.yml
├── grafana-provisioning/
└── docs/                # design spec + plan
```

See `ARCHITECTURE.md` for system design and trade-offs.
```

- [ ] **Step 2: Commit**

```bash
git add README.md
git commit -m "docs: full README"
```

### Task 9.2: ARCHITECTURE.md

**Files:**
- Modify: `ARCHITECTURE.md`

- [ ] **Step 1: Write `ARCHITECTURE.md`** (covers: system structure, frontend, backend, DB schema at high level, AI generation flow, observability flow, design decisions, and how the differentiating feature fits in). Pull from the spec.

```markdown
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

Key components live under `src/components/companies/`: `CreateCompanyModal`, `CompanyTable`, `CompanyFilters`, `ScoreGauge`, `CompetitorGrid`, `InvestmentMemo`, `NotesPanel`, `CompareView`.

## Backend (`api/`)

FastAPI with a layered structure:
- `app/api/routes/` — HTTP handlers, thin
- `app/services/` — business logic; `ai/` contains the provider interface and Gemini implementation
- `app/models/` — SQLAlchemy models
- `app/schemas/` — Pydantic DTOs (the same schemas drive Gemini's `response_schema`)
- `app/db/` — async engine + session
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

JSONB columns hold the bullet lists and the score breakdown. Indexes on `created_at`, `name`, `market_tag`, `favorite`.

## AI generation flow

1. UI submits `POST /api/companies` with `{name, hq?, website?, context?}`.
2. The handler calls `report_service.create_with_report(...)`:
   1. Inserts a row with `status='generating'`.
   2. Synchronously awaits a single Gemini 2.5 Flash call configured with `response_schema=CompanyReport` (Pydantic model). The SDK returns a parsed `CompanyReport`.
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

- **Synchronous AI call inside the request**: Gemini Flash typically returns under 10s for our prompt size. A background queue would add complexity without user-visible benefit at this scale. The trade-off is owned (and documented) — a worker would be the obvious next step if latency grows.
- **Pydantic doubling as Gemini schema**: `CompanyReport` is the source of truth for both the API contract and the model's structured output. One schema, no drift.
- **JWT in httpOnly cookie**: protects against XSS token theft, simpler than localStorage + Authorization-header juggling, and survives refresh.
- **`AIProvider` protocol**: lets the test suite use a stub without monkey-patching, and makes swapping Gemini for OpenAI/Anthropic a one-file change.
- **Server-computed `score_total`**: weights live in `scoring.py` and are documented; the model only produces the breakdown. This keeps the headline number deterministic and auditable.

## Differentiating VC feature

The **Deal Attractiveness Score + Investment Memo** ride along on the same Gemini call. The breakdown is part of the structured output schema; the memo is a markdown field. Score weights are explicit and shown to the user as 5 bars, so the headline number never feels like a black box. The memo renders via `react-markdown` in the report's "Investment Memo" tab and is included in the PDF export.
```

- [ ] **Step 2: Commit**

```bash
git add ARCHITECTURE.md
git commit -m "docs: architecture document"
```

### Task 9.3: Final smoke test + push

- [ ] **Step 1: Tear down, rebuild, full flow**

```bash
docker compose down -v
docker compose up --build
```

- [ ] **Step 2: Manual checklist**

- Login at http://localhost:5173 with `admin` / `Revo123456` ✓
- Create company "Stripe" with website https://stripe.com — report appears with 5 competitors, score, memo ✓
- Toggle favorite ✓
- Add a note ✓
- Regenerate the report ✓
- Export PDF — opens, content matches ✓
- Create a second company; navigate to `/compare`, pick both — side-by-side renders ✓
- Search/filter works on dashboard ✓
- http://localhost:8000/docs — Swagger lists all endpoints ✓
- http://localhost:8000/metrics — counters incremented ✓
- http://localhost:9090/targets — `company-intel-api` UP ✓
- http://localhost:3000 — dashboard shows live data ✓

- [ ] **Step 3: Push**

```bash
git push origin main
```

---

## Self-review notes (for the implementer)

- Every task ends with `git commit`. Push after each phase or daily, whichever you prefer.
- If a step's command fails, fix it before checking the box. Don't move to the next step.
- The implementer is expected to read the spec at `docs/superpowers/specs/2026-05-08-company-intel-ai-design.md` once before starting.
- If something diverges from the spec mid-implementation (e.g., Gemini SDK version mismatch), update both the spec and this plan in a `docs:` commit before continuing.
- Skipping the tests at any task forfeits the safety net for downstream tasks. Don't skip.
