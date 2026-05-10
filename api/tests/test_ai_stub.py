import pytest
from app.schemas.company import CompanyCreate
from app.services.ai.stub_client import StubClient


@pytest.mark.asyncio
async def test_stub_generates_full_report():
    r = await StubClient().generate_report(CompanyCreate(name="Acme"))
    assert len(r.competitors) == 5
    assert r.market_tag
    assert r.score_breakdown.market >= 0
