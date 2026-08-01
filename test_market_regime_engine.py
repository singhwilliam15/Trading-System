from alphalens.domain.macro import MacroInputs, MarketRegime
from alphalens.services.market_regime_engine import MarketRegimeEngine


def test_expansion_is_classified_with_positive_growth_and_low_risk() -> None:
    assessment = MarketRegimeEngine().assess(
        MacroInputs(6.0, 3.5, 5.0, 0.0, 56.0, 4.0, 12.0, 14.0, 0.8, 120.0)
    )

    assert assessment.regime is MarketRegime.EXPANSION
    assert assessment.macro_score > 50
    assert assessment.risk_score < 45


def test_contraction_takes_priority_when_growth_is_negative() -> None:
    assessment = MarketRegimeEngine().assess(
        MacroInputs(-1.5, 5.0, 6.0, -0.25, 46.0, 8.0, -15.0, 32.0, -0.5, 400.0)
    )

    assert assessment.regime is MarketRegime.CONTRACTION
    assert assessment.risk_score >= 45
