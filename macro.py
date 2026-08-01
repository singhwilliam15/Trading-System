"""Typed market-regime domain models for macro investment decisions."""

from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum


class MarketRegime(StrEnum):
    """Business-cycle states used by the AlphaLens allocation framework."""

    RECOVERY = "Recovery"
    EXPANSION = "Expansion"
    LATE_EXPANSION = "Late Expansion"
    PEAK = "Peak"
    CONTRACTION = "Contraction"


class Outlook(StrEnum):
    """Actionable sector stance."""

    OVERWEIGHT = "Overweight"
    NEUTRAL = "Neutral"
    UNDERWEIGHT = "Underweight"


@dataclass(frozen=True, slots=True)
class MacroInputs:
    """Observable macro and market inputs, expressed as annualised percentages."""

    gdp_growth: float
    inflation: float
    policy_rate: float
    policy_rate_change: float
    pmi: float
    unemployment: float
    equity_return_12m: float
    volatility: float
    yield_curve_spread: float
    credit_spread: float


@dataclass(frozen=True, slots=True)
class SectorOutlook:
    """Sector stance and rationale produced by the regime model."""

    sector: str
    outlook: Outlook
    rationale: str


@dataclass(frozen=True, slots=True)
class MacroAssessment:
    """Complete, presentation-independent output of a regime evaluation."""

    regime: MarketRegime
    macro_score: int
    risk_score: int
    recommendation: str
    sector_outlook: tuple[SectorOutlook, ...]
    rationale: tuple[str, ...]
