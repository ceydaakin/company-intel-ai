import uuid
from sqlalchemy import select, func, or_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from app.models.company import Company


async def list_companies(
    db: AsyncSession,
    q: str | None = None,
    market_tag: str | None = None,
    favorite: bool | None = None,
    sort: str = "created_desc",
) -> list[Company]:
    stmt = select(Company)
    if q:
        like = f"%{q.lower()}%"
        stmt = stmt.where(or_(func.lower(Company.name).like(like), func.lower(Company.website).like(like)))
    if market_tag:
        stmt = stmt.where(Company.market_tag == market_tag)
    if favorite is not None:
        stmt = stmt.where(Company.favorite == favorite)
    stmt = stmt.order_by(
        Company.created_at.desc() if sort == "created_desc" else Company.created_at.asc()
    )
    return list((await db.scalars(stmt)).all())


async def get_company(db: AsyncSession, company_id: uuid.UUID) -> Company | None:
    stmt = select(Company).where(Company.id == company_id).options(
        selectinload(Company.competitors), selectinload(Company.notes)
    )
    return (await db.scalars(stmt)).one_or_none()


async def delete_company(db: AsyncSession, company: Company) -> None:
    await db.delete(company)
    await db.commit()
