from app.schemas.company import CompanyCreate
from app.schemas.report import CompanyReport, CompetitorOut, ScoreBreakdown


class StubClient:
    def __init__(self, fail: bool = False) -> None:
        self.fail = fail

    async def generate_report(self, payload: CompanyCreate) -> CompanyReport:
        if self.fail:
            raise RuntimeError("AI provider unavailable")
        return CompanyReport(
            summary=[f"{payload.name} is a stubbed company.", "Bullet 2.", "Bullet 3.", "Bullet 4."],
            market_tag="AI Tooling",
            competitors=[
                CompetitorOut(name=f"Comp{i}", summary=["a", "b", "c", "d"], strength_score=60 + i)
                for i in range(5)
            ],
            investment_thesis=["t1", "t2", "t3", "t4"],
            risks=["r1", "r2", "r3", "r4"],
            why_matters=["w1", "w2", "w3", "w4"],
            score_breakdown=ScoreBreakdown(market=70, team=70, moat=70, traction=70, fund_fit=70),
            memo_markdown="# Memo\n\nStubbed memo body.",
        )
