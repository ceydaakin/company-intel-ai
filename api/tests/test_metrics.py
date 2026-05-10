import pytest


@pytest.mark.asyncio
async def test_metrics_endpoint(client):
    r = await client.get("/metrics")
    assert r.status_code == 200
    body = r.text
    assert "ai_generation_total" in body
    assert "companies_created_total" in body


@pytest.mark.asyncio
async def test_companies_created_counter_increments(client):
    await client.post("/api/companies", json={"name": "Acme"})
    r = await client.get("/metrics")
    assert r.status_code == 200
    # Counter should have been incremented at least once
    body = r.text
    assert "companies_created_total" in body
