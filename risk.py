"""Typed models for portfolio risk calculations."""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np


@dataclass(frozen=True, slots=True)
class RiskConfig:
    portfolio_value: float
    confidence_level: float = 0.95
    horizon_days: int = 1
    annual_risk_free_rate: float = 0.06
    monte_carlo_simulations: int = 20_000


@dataclass(frozen=True, slots=True)
class RiskAssessment:
    historical_var: float
    parametric_var: float
    monte_carlo_var: float
    expected_shortfall: float
    maximum_drawdown: float
    sharpe_ratio: float | None
    sortino_ratio: float | None
    mean_daily_return: float
    daily_volatility: float
    observations: int
    simulated_returns: np.ndarray
