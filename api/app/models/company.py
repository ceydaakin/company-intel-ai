import uuid
from datetime import datetime
from sqlalchemy import Boolean, DateTime, Integer, String, Text, func
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base import Base

class Company(Base):
    __tablename__ = "companies"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(String(200), nullable=False, index=True)
    hq: Mapped[str | None] = mapped_column(String(200))
    website: Mapped[str | None] = mapped_column(String(500))
    context: Mapped[str | None] = mapped_column(Text)

    market_tag: Mapped[str | None] = mapped_column(String(100), index=True)
    summary: Mapped[list | None] = mapped_column(JSONB)
    investment_thesis: Mapped[list | None] = mapped_column(JSONB)
    risks: Mapped[list | None] = mapped_column(JSONB)
    why_matters: Mapped[list | None] = mapped_column(JSONB)
    score_total: Mapped[int | None] = mapped_column(Integer)
    score_breakdown: Mapped[dict | None] = mapped_column(JSONB)
    memo_markdown: Mapped[str | None] = mapped_column(Text)

    status: Mapped[str] = mapped_column(String(20), default="generating", nullable=False)
    error_message: Mapped[str | None] = mapped_column(Text)
    favorite: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False, index=True)

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), index=True)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    competitors: Mapped[list["Competitor"]] = relationship(back_populates="company", cascade="all, delete-orphan", order_by="Competitor.position")
    notes: Mapped[list["Note"]] = relationship(back_populates="company", cascade="all, delete-orphan", order_by="Note.created_at.desc()")
