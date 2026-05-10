import uuid
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.api.deps import require_admin
from app.db.session import get_db
from app.models.note import Note
from app.schemas.company import NoteCreate, NoteOut
from app.services import company_repo

router = APIRouter(
    prefix="/api/companies/{company_id}/notes",
    tags=["notes"],
    dependencies=[Depends(require_admin)],
)


@router.post("", response_model=NoteOut, status_code=status.HTTP_201_CREATED)
async def create_note(
    company_id: uuid.UUID,
    payload: NoteCreate,
    db: AsyncSession = Depends(get_db),
):
    company = await company_repo.get_company(db, company_id)
    if not company:
        raise HTTPException(status.HTTP_404_NOT_FOUND)
    note = Note(company_id=company_id, body=payload.body)
    db.add(note)
    await db.commit()
    await db.refresh(note)
    return note


@router.delete("/{note_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_note(
    company_id: uuid.UUID,
    note_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
):
    note = (
        await db.scalars(
            select(Note).where(Note.id == note_id, Note.company_id == company_id)
        )
    ).one_or_none()
    if not note:
        raise HTTPException(status.HTTP_404_NOT_FOUND)
    await db.delete(note)
    await db.commit()
