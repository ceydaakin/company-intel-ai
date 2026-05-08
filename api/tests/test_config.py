import os
from app.core.config import Settings


def test_cors_list_parses_csv(monkeypatch):
    monkeypatch.setenv("DATABASE_URL", "postgresql+asyncpg://x")
    monkeypatch.setenv("CORS_ORIGINS", "http://a, http://b ,http://c")
    s = Settings()
    assert s.cors_origins_list == ["http://a", "http://b", "http://c"]
