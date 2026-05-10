import pytest
from fastapi.testclient import TestClient
from app.main import app


@pytest.fixture
def client():
    """Fresh TestClient per test so cookie state is isolated."""
    with TestClient(app) as c:
        yield c


def test_login_success_sets_cookie(client):
    r = client.post("/api/auth/login", json={"username": "admin", "password": "Revo123456"})
    assert r.status_code == 204
    assert "cia_session" in client.cookies


def test_login_failure(client):
    r = client.post("/api/auth/login", json={"username": "admin", "password": "wrong"})
    assert r.status_code == 401


def test_me_requires_cookie(client):
    r = client.get("/api/auth/me")
    assert r.status_code == 401


def test_me_with_cookie(client):
    client.post("/api/auth/login", json={"username": "admin", "password": "Revo123456"})
    me = client.get("/api/auth/me")
    assert me.status_code == 200
    assert me.json() == {"username": "admin"}


def test_logout_clears_cookie(client):
    client.post("/api/auth/login", json={"username": "admin", "password": "Revo123456"})
    out = client.post("/api/auth/logout")
    assert out.status_code == 204
