import numpy as np
import pandas as pd

from alphalens.domain.risk import RiskConfig
from alphalens.services.risk_engine import RiskEngine


def test_risk_engine_calculates_non_negative_var_metrics() -> None:
    generator = np.random.default_rng(7)
    returns = pd.Series(generator.normal(0.0005, 0.015, 300))

    assessment = RiskEngine().assess(returns, RiskConfig(portfolio_value=1_000_000, confidence_level=0.95))

    assert assessment.historical_var > 0
    assert assessment.parametric_var > 0
    assert assessment.monte_carlo_var > 0
    assert assessment.expected_shortfall >= assessment.historical_var
    assert assessment.maximum_drawdown > 0


def test_returns_from_prices_rejects_non_positive_prices() -> None:
    prices = pd.Series([100, 101, 0, 103])

    try:
        RiskEngine.returns_from_prices(prices)
    except ValueError as error:
        assert "positive" in str(error)
    else:
        raise AssertionError("Expected invalid price input to be rejected.")
