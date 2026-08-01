"""Portfolio-construction domain models."""

from __future__ import annotations

from dataclasses import dataclass

from alphalens.domain.macro import MarketRegime
from alphalens.domain.technical import TechnicalSignal


@dataclass(frozen=True, slots=True)
class PortfolioCandidate:
    ticker: str
    sector: str
    price: float
    qgvm_score: float
    technical_signal: TechnicalSignal
    daily_volatility: float
    current_weight: float = 0.0


@dataclass(frozen=True, slots=True)
class PortfolioConstraints:
    capital: float
    macro_regime: MarketRegime
    macro_score: float
    risk_score: float
    var_limit_pct: float
    max_position_weight: float = 0.10
    max_sector_weight: float = 0.25
    var_confidence: float = 0.99


@dataclass(frozen=True, slots=True)
class PortfolioPosition:
    ticker: str
    sector: str
    score: float
    target_weight: float
    target_notional: float
    target_shares: int
    current_weight: float
    rebalance_action: str


@dataclass(frozen=True, slots=True)
class PortfolioAssessment:
    positions: tuple[PortfolioPosition, ...]
    sector_allocations: dict[str, float]
    cash_weight: float
    estimated_var: float
    invested_weight: float
    rebalancing_summary: str
    rationale: tuple[str, ...]
