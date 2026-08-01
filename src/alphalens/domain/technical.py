"""Typed models for OHLCV technical analysis and risk-managed trade plans."""

from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum

import pandas as pd


class TechnicalSignal(StrEnum):
    BULLISH = "Bullish"
    BEARISH = "Bearish"
    NEUTRAL = "Neutral"


@dataclass(frozen=True, slots=True)
class TechnicalConfig:
    capital: float
    risk_per_trade_pct: float = 1.0
    atr_period: int = 14
    atr_stop_multiple: float = 2.0
    target_risk_reward: float = 2.0


@dataclass(frozen=True, slots=True)
class TradePlan:
    entry_price: float
    stop_loss: float
    target_price: float
    position_size: int
    capital_at_risk: float
    risk_reward: float


@dataclass(frozen=True, slots=True)
class TechnicalAssessment:
    signal: TechnicalSignal
    breakout: str
    indicators: dict[str, float]
    support: float
    resistance: float
    volume_assessment: str
    trade_plan: TradePlan
    indicator_frame: pd.DataFrame
    rationale: tuple[str, ...]
