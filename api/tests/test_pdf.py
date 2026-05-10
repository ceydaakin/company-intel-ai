import pytest


@pytest.mark.asyncio
async def test_pdf_export_returns_pdf(client):
    cid = (await client.post("/api/companies", json={"name": "Acme"})).json()["id"]
    r = await client.get(f"/api/companies/{cid}/export.pdf")
    assert r.status_code == 200
    assert r.headers["content-type"] == "application/pdf"
    assert r.content[:4] == b"%PDF"
