from sqlalchemy.ext.asyncio import AsyncSession
from app.models.company import Company
from app.models.competitor import Competitor
from app.schemas.company import CompanyCreate
from app.services.ai.provider import AIProvider
from app.services.ai.scoring import compute_score_total


async def create_with_report(db: AsyncSession, payload: CompanyCreate, ai: AIProvider) -> Company:
    company = Company(
        name=payload.name,
        hq=payload.hq,
        website=str(payload.website) if payload.website else None,
        context=payload.context,
        status="generating",
    )
    db.add(company)
    await db.commit()
    await db.refresh(company)
    try:
        report = await ai.generate_report(payload)
    except Exception as e:
        company.status = "failed"
        company.error_message = str(e)[:500]
        await db.commit()
        raise
    _apply_report(company, report)
    db.add_all(_build_competitors(company.id, report))
    company.status = "ready"
    company.error_message = None
    await db.commit()
    await db.refresh(company, attribute_names=["competitors", "notes"])
    return company


async def regenerate_report(db: AsyncSession, company: Company, ai: AIProvider) -> Company:
    company.status = "generating"
    await db.commit()
    # wipe old competitors
    for c in list(company.competitors):
        await db.delete(c)
    await db.commit()
    payload = CompanyCreate(
        name=company.name,
        hq=company.hq,
        website=company.website,
        context=company.context,
    )
    try:
        report = await ai.generate_report(payload)
    except Exception as e:
        company.status = "failed"
        company.error_message = str(e)[:500]
        await db.commit()
        raise
    _apply_report(company, report)
    db.add_all(_build_competitors(company.id, report))
    company.status = "ready"
    company.error_message = None
    await db.commit()
    await db.refresh(company, attribute_names=["competitors", "notes"])
    return company


def _apply_report(company: Company, report) -> None:
    company.summary = report.summary
    company.market_tag = report.market_tag
    company.investment_thesis = report.investment_thesis
    company.risks = report.risks
    company.why_matters = report.why_matters
    company.score_breakdown = report.score_breakdown.model_dump()
    company.score_total = compute_score_total(report.score_breakdown)
    company.memo_markdown = report.memo_markdown


def _build_competitors(company_id, report):
    return [
        Competitor(
            company_id=company_id,
            name=c.name,
            summary=c.summary,
            strength_score=c.strength_score,
            position=i + 1,
        )
        for i, c in enumerate(report.competitors)
    ]
