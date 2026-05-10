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
