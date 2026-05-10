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
