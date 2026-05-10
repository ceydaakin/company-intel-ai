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
