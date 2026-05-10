from pydantic import BaseModel, Field


class CompetitorOut(BaseModel):
    name: str
    summary: list[str] = Field(min_length=3, max_length=6)
    strength_score: int = Field(ge=0, le=100)


class ScoreBreakdown(BaseModel):
    market: int = Field(ge=0, le=100)
    team: int = Field(ge=0, le=100)
    moat: int = Field(ge=0, le=100)
    traction: int = Field(ge=0, le=100)
    fund_fit: int = Field(ge=0, le=100)


class CompanyReport(BaseModel):
    """The full AI-generated payload."""

    summary: list[str] = Field(min_length=3, max_length=6)
    market_tag: str
    competitors: list[CompetitorOut] = Field(min_length=5, max_length=5)
    investment_thesis: list[str] = Field(min_length=3, max_length=6)
    risks: list[str] = Field(min_length=3, max_length=6)
    why_matters: list[str] = Field(min_length=3, max_length=6)
    score_breakdown: ScoreBreakdown
    memo_markdown: str
