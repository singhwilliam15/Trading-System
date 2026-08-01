import pandas as pd

from alphalens.domain.technical import TechnicalConfig
from alphalens.services.technical_analysis_engine import TechnicalAnalysisEngine


def _ohlcv() -> pd.DataFrame:
    closes = [100 + index * 0.5 for index in range(70)]
    return pd.DataFrame({
        "Open": [price - 0.2 for price in closes],
        "High": [price + 1 for price in closes],
        "Low": [price - 1 for price in closes],
        "Close": closes,
        "Volume": [1_000_000 + index * 1_000 for index in range(70)],
    })


def test_engine_calculates_indicators_and_bounded_position_size() -> None:
    assessment = TechnicalAnalysisEngine().assess(_ohlcv(), TechnicalConfig(capital=100_000))

    assert assessment.indicators["RSI (14)"] > 50
    assert assessment.trade_plan.stop_loss < assessment.trade_plan.entry_price
    assert assessment.trade_plan.target_price > assessment.trade_plan.entry_price
    assert 0 < assessment.trade_plan.position_size <= int(100_000 / assessment.trade_plan.entry_price)


def test_engine_requires_minimum_history() -> None:
    short_data = _ohlcv().head(20)

    try:
        TechnicalAnalysisEngine().assess(short_data, TechnicalConfig(capital=100_000))
    except ValueError as error:
        assert "60" in str(error)
    else:
        raise AssertionError("Expected insufficient historical data to be rejected.")
