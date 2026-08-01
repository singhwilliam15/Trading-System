"""Rules-based portfolio construction from AlphaLens module outputs."""

from __future__ import annotations

import math
from collections import defaultdict
from statistics import NormalDist

from alphalens.domain.macro import MarketRegime
from alphalens.domain.portfolio import (
    PortfolioAssessment,
    PortfolioCandidate,
    PortfolioConstraints,
    PortfolioPosition,
)
from alphalens.domain.technical import TechnicalSignal


class PortfolioConstructionEngine:
    """Turn macro, QGVM, technical, and VaR signals into constrained weights."""

    _REGIME_EXPOSURE = {
        MarketRegime.RECOVERY: 0.90,
        MarketRegime.EXPANSION: 1.00,
        MarketRegime.LATE_EXPANSION: 0.80,
        MarketRegime.PEAK: 0.65,
        MarketRegime.CONTRACTION: 0.45,
    }
    _PREFERRED_SECTORS = {
        MarketRegime.RECOVERY: {"financials", "industrials", "consumer discretionary"},
        MarketRegime.EXPANSION: {"industrials", "technology", "materials"},
        MarketRegime.LATE_EXPANSION: {"energy", "healthcare", "consumer staples"},
        MarketRegime.PEAK: {"healthcare", "utilities", "consumer staples"},
        MarketRegime.CONTRACTION: {"healthcare", "utilities", "consumer staples"},
    }

    def construct(self, candidates: list[PortfolioCandidate], constraints: PortfolioConstraints) -> PortfolioAssessment:
        """Construct a constrained portfolio and its rebalancing instruction set."""
        self._validate(candidates, constraints)
        raw_scores = {candidate.ticker: self._candidate_score(candidate, constraints) for candidate in candidates}
        total_score = sum(raw_scores.values())
        target_exposure = self._target_exposure(constraints)
        weights = {
            candidate.ticker: min(constraints.max_position_weight, target_exposure * raw_scores[candidate.ticker] / total_score)
            for candidate in candidates
        }
        weights = self._apply_sector_caps(candidates, weights, constraints.max_sector_weight)
        weights = self._apply_var_limit(candidates, weights, constraints)
        positions = tuple(self._position(candidate, raw_scores[candidate.ticker], weights[candidate.ticker], constraints.capital) for candidate in candidates)
        sectors = self._sector_allocations(positions)
        invested_weight = sum(position.target_weight for position in positions)
        cash_weight = max(0.0, 1 - invested_weight)
        estimated_var = self._portfolio_var(candidates, weights, constraints)
        changes = sum(position.rebalance_action != "Hold" for position in positions)
        return PortfolioAssessment(
            positions=positions,
            sector_allocations=sectors,
            cash_weight=cash_weight,
            estimated_var=estimated_var,
            invested_weight=invested_weight,
            rebalancing_summary=f"{changes} of {len(positions)} holdings require a rebalance action.",
            rationale=(
                f"{constraints.macro_regime.value} sets a base equity exposure of {self._REGIME_EXPOSURE[constraints.macro_regime]:.0%}.",
                "Weights combine QGVM quality, technical confirmation, regime-sector alignment, and inverse daily volatility.",
                f"The estimated {constraints.var_confidence:.0%} one-day VaR is {estimated_var:,.0f}, constrained below the selected limit.",
            ),
        )

    @staticmethod
    def _validate(candidates: list[PortfolioCandidate], constraints: PortfolioConstraints) -> None:
        if not candidates:
            raise ValueError("Add at least one portfolio candidate.")
        if len({candidate.ticker.upper() for candidate in candidates}) != len(candidates):
            raise ValueError("Candidate tickers must be unique.")
        if constraints.capital <= 0 or not 0 < constraints.var_limit_pct <= 0.20:
            raise ValueError("Capital must be positive and the daily VaR limit must be between 0% and 20%.")
        if not 0 <= constraints.macro_score <= 100 or not 0 <= constraints.risk_score <= 100:
            raise ValueError("Macro Score and Risk Score must each be between 0 and 100.")
        if not 0 < constraints.max_position_weight <= constraints.max_sector_weight <= 1:
            raise ValueError("Position and sector limits must be positive, with sector limit at least the position limit.")
        for candidate in candidates:
            if candidate.price <= 0 or not 0 <= candidate.qgvm_score <= 100 or not 0 < candidate.daily_volatility < 1:
                raise ValueError(f"Invalid price, QGVM score, or daily volatility for {candidate.ticker}.")
            if not 0 <= candidate.current_weight <= 1:
                raise ValueError(f"Current weight must be between 0 and 100% for {candidate.ticker}.")

    def _candidate_score(self, candidate: PortfolioCandidate, constraints: PortfolioConstraints) -> float:
        technical_score = {TechnicalSignal.BULLISH: 1.0, TechnicalSignal.NEUTRAL: 0.55, TechnicalSignal.BEARISH: 0.15}[candidate.technical_signal]
        sector_alignment = 1.2 if candidate.sector.strip().lower() in self._PREFERRED_SECTORS[constraints.macro_regime] else 0.8
        macro_conviction = 0.7 + constraints.macro_score / 300
        factor_score = candidate.qgvm_score / 100 * 0.55 + technical_score * 0.25 + sector_alignment * 0.20
        return max(0.01, factor_score * macro_conviction / candidate.daily_volatility)

    def _target_exposure(self, constraints: PortfolioConstraints) -> float:
        risk_adjustment = 1 - max(0, constraints.risk_score - 50) / 100
        return min(1.0, self._REGIME_EXPOSURE[constraints.macro_regime] * risk_adjustment)

    @staticmethod
    def _apply_sector_caps(candidates: list[PortfolioCandidate], weights: dict[str, float], cap: float) -> dict[str, float]:
        adjusted = weights.copy()
        sector_weights: dict[str, float] = defaultdict(float)
        for candidate in candidates:
            sector_weights[candidate.sector] += adjusted[candidate.ticker]
        for candidate in candidates:
            sector_total = sector_weights[candidate.sector]
            if sector_total > cap:
                adjusted[candidate.ticker] *= cap / sector_total
        return adjusted

    def _apply_var_limit(self, candidates: list[PortfolioCandidate], weights: dict[str, float], constraints: PortfolioConstraints) -> dict[str, float]:
        current_var = self._portfolio_var(candidates, weights, constraints)
        maximum_var = constraints.capital * constraints.var_limit_pct
        if current_var <= maximum_var:
            return weights
        scale = maximum_var / current_var
        return {ticker: weight * scale for ticker, weight in weights.items()}

    @staticmethod
    def _portfolio_var(candidates: list[PortfolioCandidate], weights: dict[str, float], constraints: PortfolioConstraints) -> float:
        volatility = math.sqrt(sum((weights[candidate.ticker] * candidate.daily_volatility) ** 2 for candidate in candidates))
        z_score = NormalDist().inv_cdf(constraints.var_confidence)
        return constraints.capital * z_score * volatility

    @staticmethod
    def _position(candidate: PortfolioCandidate, score: float, weight: float, capital: float) -> PortfolioPosition:
        delta = weight - candidate.current_weight
        action = "Buy" if delta > 0.0025 else "Sell" if delta < -0.0025 else "Hold"
        notional = capital * weight
        return PortfolioPosition(
            ticker=candidate.ticker.upper(), sector=candidate.sector, score=round(score, 2), target_weight=weight,
            target_notional=notional, target_shares=math.floor(notional / candidate.price),
            current_weight=candidate.current_weight, rebalance_action=action,
        )

    @staticmethod
    def _sector_allocations(positions: tuple[PortfolioPosition, ...]) -> dict[str, float]:
        allocations: dict[str, float] = defaultdict(float)
        for position in positions:
            allocations[position.sector] += position.target_weight
        return dict(sorted(allocations.items(), key=lambda item: item[1], reverse=True))
