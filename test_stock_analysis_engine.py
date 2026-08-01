from dataclasses import replace

from alphalens.domain.stock import Recommendation, StockInputs
from alphalens.services.stock_analysis_engine import StockAnalysisEngine


def _healthy_inputs() -> StockInputs:
    return StockInputs("ALPHA", 150, 100, 10_000, 8_500, 4_000, 3_200, 2_000, 2_400, 1_500, 1_100, 1_800, 10, 8, 50, 12_000, 10_500, 1_500, 1_700, 7_500, 6_800, 3_500, 4_000, 3_600, 2_000, 2_000, 1_000, 12, 22, 100)


def test_healthy_company_receives_buy_recommendation() -> None:
    assessment = StockAnalysisEngine().assess(_healthy_inputs())

    assert assessment.recommendation is Recommendation.BUY
    assert assessment.metrics.piotroski_score >= 7
    assert assessment.metrics.altman_z_score >= 2.99


def test_financial_distress_forces_sell_recommendation() -> None:
    distressed = replace(
        _healthy_inputs(),
        net_income=-500,
        net_income_prior=100,
        operating_cash_flow=-100,
        ebit=-200,
        total_debt=9_000,
        total_debt_prior=7_000,
        current_assets=500,
        current_liabilities=3_000,
        gross_profit=1_000,
        gross_profit_prior=1_500,
        revenue=7_000,
        revenue_prior=8_000,
        shares_outstanding=120,
    )

    assessment = StockAnalysisEngine().assess(distressed)

    assert assessment.recommendation is Recommendation.SELL
    assert assessment.metrics.piotroski_score <= 3
