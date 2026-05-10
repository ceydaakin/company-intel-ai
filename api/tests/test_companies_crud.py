import uuid
import pytest


@pytest.mark.asyncio
async def test_list_empty(client):
    r = await client.get("/api/companies")
    assert r.status_code == 200
    assert r.json() == []


@pytest.mark.asyncio
async def test_list_requires_auth(client):
    client.cookies.clear()
    r = await client.get("/api/companies")
    assert r.status_code == 401


@pytest.mark.asyncio
async def test_404_on_missing(client):
    r = await client.get(f"/api/companies/{uuid.uuid4()}")
    assert r.status_code == 404
