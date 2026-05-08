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
