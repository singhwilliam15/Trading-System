"""VaR, drawdown, and risk-adjusted performance calculations."""

from __future__ import annotations

from statistics import NormalDist

import numpy as np
import pandas as pd

from alphalens.domain.risk import RiskAssessment, RiskConfig


class RiskEngine:
    """Calculate daily portfolio risk metrics from a validated return series."""

    def assess(self, returns: pd.Series, config: RiskConfig) -> RiskAssessment:
        """Produce Historical, Parametric, Monte Carlo VaR and related risk metrics."""
        clean_returns = self._validate_returns(returns)
        self._validate_config(config)
        horizon_returns = clean_returns * np.sqrt(config.horizon_days)
        lower_tail = 1 - config.confidence_level
        historical_quantile = float(np.quantile(horizon_returns, lower_tail))
        historical_var = max(0.0, -historical_quantile * config.portfolio_value)
        expected_shortfall = max(0.0, -float(horizon_returns[horizon_returns <= historical_quantile].mean()) * config.portfolio_value)
        mean_daily, daily_volatility = float(clean_returns.mean()), float(clean_returns.std(ddof=1))
        z_score = NormalDist().inv_cdf(lower_tail)
        parametric_return = mean_daily * config.horizon_days + z_score * daily_volatility * np.sqrt(config.horizon_days)
        parametric_var = max(0.0, -parametric_return * config.portfolio_value)
        simulated = self._monte_carlo(mean_daily, daily_volatility, config)
        monte_carlo_var = max(0.0, -float(np.quantile(simulated, lower_tail)) * config.portfolio_value)
        max_drawdown = self._maximum_drawdown(clean_returns)
        sharpe, sortino = self._risk_adjusted_ratios(clean_returns, config.annual_risk_free_rate)
        return RiskAssessment(
            historical_var=historical_var,
            parametric_var=parametric_var,
            monte_carlo_var=monte_carlo_var,
            expected_shortfall=expected_shortfall,
            maximum_drawdown=max_drawdown,
            sharpe_ratio=sharpe,
            sortino_ratio=sortino,
            mean_daily_return=mean_daily,
            daily_volatility=daily_volatility,
            observations=len(clean_returns),
            simulated_returns=simulated,
        )

    @staticmethod
    def returns_from_prices(prices: pd.Series) -> pd.Series:
        """Convert a positive chronological price series into simple daily returns."""
        numeric_prices = pd.to_numeric(prices, errors="coerce").dropna()
        if len(numeric_prices) < 3 or (numeric_prices <= 0).any():
            raise ValueError("At least three positive prices are required to calculate returns.")
        return numeric_prices.pct_change().dropna()

    @staticmethod
    def _validate_returns(returns: pd.Series) -> pd.Series:
        clean = pd.to_numeric(returns, errors="coerce").replace([np.inf, -np.inf], np.nan).dropna()
        if len(clean) < 30:
            raise ValueError("At least 30 valid return observations are required for risk analysis.")
        if (clean <= -1).any():
            raise ValueError("Returns must be greater than -100%.")
        return clean.astype(float)

    @staticmethod
    def _validate_config(config: RiskConfig) -> None:
        if config.portfolio_value <= 0:
            raise ValueError("Portfolio value must be positive.")
        if not 0.80 <= config.confidence_level < 1:
            raise ValueError("Confidence level must be between 80% and 100%.")
        if config.horizon_days < 1 or config.monte_carlo_simulations < 1_000:
            raise ValueError("Horizon must be positive and simulations must be at least 1,000.")

    @staticmethod
    def _monte_carlo(mean: float, volatility: float, config: RiskConfig) -> np.ndarray:
        generator = np.random.default_rng(seed=42)
        return generator.normal(
            loc=mean * config.horizon_days,
            scale=volatility * np.sqrt(config.horizon_days),
            size=config.monte_carlo_simulations,
        )

    @staticmethod
    def _maximum_drawdown(returns: pd.Series) -> float:
        equity_curve = (1 + returns).cumprod()
        drawdown = equity_curve / equity_curve.cummax() - 1
        return abs(float(drawdown.min()))

    @staticmethod
    def _risk_adjusted_ratios(returns: pd.Series, annual_risk_free_rate: float) -> tuple[float | None, float | None]:
        daily_risk_free = annual_risk_free_rate / 252
        excess_returns = returns - daily_risk_free
        volatility = float(excess_returns.std(ddof=1))
        downside = excess_returns[excess_returns < 0]
        downside_deviation = float(downside.std(ddof=1)) if len(downside) > 1 else 0.0
        sharpe = float(excess_returns.mean() / volatility * np.sqrt(252)) if volatility > 0 else None
        sortino = float(excess_returns.mean() / downside_deviation * np.sqrt(252)) if downside_deviation > 0 else None
        return sharpe, sortino
