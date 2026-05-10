import pytest
from app.schemas.company import CompanyCreate
from app.services.ai.stub_client import StubClient
from app.services.report_service import create_with_report


@pytest.mark.asyncio
async def test_create_with_report_persists_competitors_and_score(db_session):
    ai = StubClient()
    company = await create_with_report(db_session, CompanyCreate(name="Acme"), ai)
    assert company.status == "ready"
    assert company.score_total > 0
    assert len(company.competitors) == 5


@pytest.mark.asyncio
async def test_create_with_report_failure_sets_status_failed(db_session):
    ai = StubClient(fail=True)
    with pytest.raises(RuntimeError):
        await create_with_report(db_session, CompanyCreate(name="Acme"), ai)
    # row should still exist with status=failed
    from sqlalchemy import select
    from app.models.company import Company
    rows = (await db_session.scalars(select(Company))).all()
    assert len(rows) == 1
    assert rows[0].status == "failed"
