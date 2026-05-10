from app.schemas.report import ScoreBreakdown
from app.services.ai.scoring import compute_score_total


def test_perfect_breakdown_is_100():
    assert compute_score_total(ScoreBreakdown(market=100, team=100, moat=100, traction=100, fund_fit=100)) == 100


def test_zero_breakdown_is_0():
    assert compute_score_total(ScoreBreakdown(market=0, team=0, moat=0, traction=0, fund_fit=0)) == 0


def test_weighted_blend_respects_market_weight():
    # market is weighted 0.30; with market=100 and rest=0, score >= 30
    s = ScoreBreakdown(market=100, team=0, moat=0, traction=0, fund_fit=0)
    assert compute_score_total(s) == 30
