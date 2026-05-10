import uuid
from datetime import datetime
from pydantic import BaseModel, ConfigDict, Field, HttpUrl
from app.schemas.report import CompetitorOut, ScoreBreakdown


class CompanyCreate(BaseModel):
    name: str = Field(min_length=1, max_length=200)
    hq: str | None = None
    website: HttpUrl | None = None
    context: str | None = None


class CompanyPatch(BaseModel):
    hq: str | None = None
    website: HttpUrl | None = None
    context: str | None = None
    favorite: bool | None = None


class NoteOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: uuid.UUID
    body: str
    created_at: datetime


class CompetitorRow(CompetitorOut):
    model_config = ConfigDict(from_attributes=True)


class CompanyListItem(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: uuid.UUID
    name: str
    hq: str | None
    website: str | None
    market_tag: str | None
    score_total: int | None
    favorite: bool
    status: str
    created_at: datetime


class CompanyDetail(CompanyListItem):
    context: str | None
    summary: list[str] | None
    investment_thesis: list[str] | None
    risks: list[str] | None
    why_matters: list[str] | None
    score_breakdown: ScoreBreakdown | None
    memo_markdown: str | None
    error_message: str | None
    competitors: list[CompetitorRow]
    notes: list[NoteOut]
