from app.schemas.report import ScoreBreakdown

WEIGHTS = {"market": 0.30, "team": 0.25, "moat": 0.15, "traction": 0.20, "fund_fit": 0.10}
assert sum(WEIGHTS.values()) == 1.0


def compute_score_total(breakdown: ScoreBreakdown) -> int:
    total = (
        breakdown.market * WEIGHTS["market"]
        + breakdown.team * WEIGHTS["team"]
        + breakdown.moat * WEIGHTS["moat"]
        + breakdown.traction * WEIGHTS["traction"]
        + breakdown.fund_fit * WEIGHTS["fund_fit"]
    )
    return int(round(total))
