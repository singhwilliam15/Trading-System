"""Typed stock-fundamental models for factor-based equity analysis."""

from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum


class Recommendation(StrEnum):
    BUY = "Buy"
    HOLD = "Hold"
    SELL = "Sell"


@dataclass(frozen=True, slots=True)
class StockInputs:
    """Current and prior-period inputs required for scoring a listed company.

    Monetary inputs must use the same currency and unit. Percent-like inputs
    (EPS growth inputs are calculated) are represented as decimal-free values.
    """

    ticker: str
    market_price: float
    shares_outstanding: float
    revenue: float
    revenue_prior: float
    gross_profit: float
    gross_profit_prior: float
    ebit: float
    ebitda: float
    net_income: float
    net_income_prior: float
    operating_cash_flow: float
    eps: float
    eps_prior: float
    book_value_per_share: float
    total_assets: float
    total_assets_prior: float
    total_debt: float
    total_debt_prior: float
    total_equity: float
    total_equity_prior: float
    retained_earnings: float
    current_assets: float
    current_assets_prior: float
    current_liabilities: float
    current_liabilities_prior: float
    cash: float
    price_return_6m: float
    price_return_12m: float
    shares_outstanding_prior: float


@dataclass(frozen=True, slots=True)
class StockMetrics:
    roe: float
    roce: float
    eps_growth: float
    debt_to_equity: float
    pe: float
    pb: float
    ev_to_ebitda: float
    piotroski_score: int
    altman_z_score: float


@dataclass(frozen=True, slots=True)
class StockAssessment:
    ticker: str
    metrics: StockMetrics
    quality_score: int
    growth_score: int
    value_score: int
    momentum_score: int
    composite_score: int
    recommendation: Recommendation
    rationale: tuple[str, ...]
