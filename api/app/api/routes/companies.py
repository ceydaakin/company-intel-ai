import uuid
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.api.deps import get_ai, require_admin
from app.db.session import get_db
from app.schemas.company import CompanyCreate, CompanyDetail, CompanyListItem, CompanyPatch
from app.services import company_repo, report_service
from app.services.ai.provider import AIProvider

router = APIRouter(prefix="/api/companies", tags=["companies"], dependencies=[Depends(require_admin)])


@router.get("", response_model=list[CompanyListItem])
async def list_endpoint(
    q: str | None = Query(default=None),
    market_tag: str | None = Query(default=None),
    favorite: bool | None = Query(default=None),
    sort: str = Query(default="created_desc"),
    db: AsyncSession = Depends(get_db),
):
    return await company_repo.list_companies(db, q=q, market_tag=market_tag, favorite=favorite, sort=sort)


@router.get("/{company_id}", response_model=CompanyDetail)
async def get_endpoint(company_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    company = await company_repo.get_company(db, company_id)
    if not company:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "company not found")
    return company


@router.patch("/{company_id}", response_model=CompanyDetail)
async def patch_endpoint(company_id: uuid.UUID, payload: CompanyPatch, db: AsyncSession = Depends(get_db)):
    company = await company_repo.get_company(db, company_id)
    if not company:
        raise HTTPException(status.HTTP_404_NOT_FOUND)
    data = payload.model_dump(exclude_unset=True)
    for k, v in data.items():
        setattr(company, k, str(v) if k == "website" and v is not None else v)
    await db.commit()
    await db.refresh(company)
    return company


@router.delete("/{company_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_endpoint(company_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    company = await company_repo.get_company(db, company_id)
    if not company:
        raise HTTPException(status.HTTP_404_NOT_FOUND)
    await company_repo.delete_company(db, company)


@router.post("", response_model=CompanyDetail, status_code=status.HTTP_201_CREATED)
async def create_endpoint(
    payload: CompanyCreate,
    db: AsyncSession = Depends(get_db),
    ai: AIProvider = Depends(get_ai),
):
    try:
        company = await report_service.create_with_report(db, payload, ai)
    except Exception as e:
        raise HTTPException(status.HTTP_502_BAD_GATEWAY, f"AI generation failed: {e}") from e
    # eagerly load relationships for response
    return await company_repo.get_company(db, company.id)


@router.post("/{company_id}/regenerate", response_model=CompanyDetail)
async def regenerate_endpoint(
    company_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    ai: AIProvider = Depends(get_ai),
):
    company = await company_repo.get_company(db, company_id)
    if not company:
        raise HTTPException(status.HTTP_404_NOT_FOUND)
    try:
        await report_service.regenerate_report(db, company, ai)
    except Exception as e:
        raise HTTPException(status.HTTP_502_BAD_GATEWAY, f"AI generation failed: {e}") from e
    return await company_repo.get_company(db, company_id)
