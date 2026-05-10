from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.api.deps import require_admin
from app.db.session import get_db
from app.schemas.compare import CompareRequest, CompareResponse
from app.services import company_repo

router = APIRouter(prefix="/api/compare", tags=["compare"], dependencies=[Depends(require_admin)])


@router.post("", response_model=CompareResponse)
async def compare(payload: CompareRequest, db: AsyncSession = Depends(get_db)):
    a = await company_repo.get_company(db, payload.a_id)
    b = await company_repo.get_company(db, payload.b_id)
    if not a or not b:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "one or both companies not found")
    return CompareResponse(a=a, b=b)
