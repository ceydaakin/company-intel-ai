import pytest_asyncio
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
import app.models  # noqa: F401  — must register models before importing main/Base users
from app.api.deps import get_ai
from app.db.base import Base
from app.db.session import get_db
from app.main import app
from app.services.ai.stub_client import StubClient

TEST_DB_URL = "sqlite+aiosqlite:///:memory:"


@pytest_asyncio.fixture
async def db_engine():
    engine = create_async_engine(TEST_DB_URL)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield engine
    await engine.dispose()


@pytest_asyncio.fixture
async def db_session(db_engine):
    async_session = async_sessionmaker(db_engine, expire_on_commit=False, class_=AsyncSession)
    async with async_session() as session:
        yield session


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
