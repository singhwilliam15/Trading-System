"""OHLCV-based indicator calculations and risk-managed technical trade planning."""

from __future__ import annotations

import math

import pandas as pd

from alphalens.domain.technical import TechnicalAssessment, TechnicalConfig, TechnicalSignal, TradePlan


class TechnicalAnalysisEngine:
    """Calculate transparent technical indicators from a chronological OHLCV series."""

    _REQUIRED_COLUMNS = {"open", "high", "low", "close", "volume"}

    def assess(self, ohlcv: pd.DataFrame, config: TechnicalConfig) -> TechnicalAssessment:
        """Compute indicators, signal, and a long-side risk-managed trade plan."""
        frame = self._prepare(ohlcv)
        self._validate_config(config)
        enriched = self._indicators(frame, config)
        latest = enriched.iloc[-1]
        support = float(enriched["low"].rolling(20).min().iloc[-1])
        resistance = float(enriched["high"].rolling(20).max().iloc[-1])
        breakout = self._breakout(enriched)
        signal = self._signal(latest, breakout)
        trade_plan = self._trade_plan(float(latest["close"]), float(latest["atr"]), support, config)
        indicators = {
            "RSI (14)": float(latest["rsi"]),
            "MACD": float(latest["macd"]),
            "MACD Signal": float(latest["macd_signal"]),
            "SMA (20)": float(latest["sma_20"]),
            "SMA (50)": float(latest["sma_50"]),
            "EMA (20)": float(latest["ema_20"]),
            "ADX (14)": float(latest["adx"]),
            "ATR (14)": float(latest["atr"]),
            "SuperTrend": float(latest["supertrend"]),
            "Bollinger Upper": float(latest["bb_upper"]),
            "Bollinger Lower": float(latest["bb_lower"]),
            "Volume ratio": float(latest["volume_ratio"]),
        }
        return TechnicalAssessment(
            signal=signal,
            breakout=breakout,
            indicators=indicators,
            support=support,
            resistance=resistance,
            volume_assessment=self._volume_assessment(float(latest["volume_ratio"])),
            trade_plan=trade_plan,
            indicator_frame=enriched,
            rationale=self._rationale(latest, breakout, signal),
        )

    def _prepare(self, ohlcv: pd.DataFrame) -> pd.DataFrame:
        frame = ohlcv.copy()
        frame.columns = [str(column).strip().lower() for column in frame.columns]
        missing = self._REQUIRED_COLUMNS - set(frame.columns)
        if missing:
            raise ValueError(f"OHLCV data is missing columns: {', '.join(sorted(missing))}.")
        if "date" in frame.columns:
            frame["date"] = pd.to_datetime(frame["date"], errors="coerce")
            frame = frame.sort_values("date", kind="stable")
        if len(frame) < 60:
            raise ValueError("At least 60 chronological OHLCV rows are required for SMA(50) analysis.")
        for column in self._REQUIRED_COLUMNS:
            frame[column] = pd.to_numeric(frame[column], errors="coerce")
        frame = frame.dropna(subset=list(self._REQUIRED_COLUMNS)).reset_index(drop=True)
        invalid_prices = (frame[["open", "high", "low", "close"]] <= 0).any().any()
        if len(frame) < 60 or invalid_prices or (frame["high"] < frame["low"]).any() or (frame["volume"] < 0).any():
            raise ValueError("OHLCV values are invalid or insufficient after cleaning.")
        return frame

    @staticmethod
    def _validate_config(config: TechnicalConfig) -> None:
        if config.capital <= 0 or not 0 < config.risk_per_trade_pct <= 5:
            raise ValueError("Capital must be positive and risk per trade must be between 0 and 5%.")
        if config.atr_stop_multiple <= 0 or config.target_risk_reward <= 0:
            raise ValueError("ATR stop multiple and target risk-reward must be positive.")

    def _indicators(self, frame: pd.DataFrame, config: TechnicalConfig) -> pd.DataFrame:
        result = frame.copy()
        result["sma_20"] = result["close"].rolling(20).mean()
        result["sma_50"] = result["close"].rolling(50).mean()
        result["ema_20"] = result["close"].ewm(span=20, adjust=False).mean()
        result["ema_12"] = result["close"].ewm(span=12, adjust=False).mean()
        result["ema_26"] = result["close"].ewm(span=26, adjust=False).mean()
        result["macd"] = result["ema_12"] - result["ema_26"]
        result["macd_signal"] = result["macd"].ewm(span=9, adjust=False).mean()
        result["macd_histogram"] = result["macd"] - result["macd_signal"]
        delta = result["close"].diff()
        gains = delta.clip(lower=0).ewm(alpha=1 / 14, adjust=False, min_periods=14).mean()
        losses = (-delta.clip(upper=0)).ewm(alpha=1 / 14, adjust=False, min_periods=14).mean()
        result["rsi"] = 100 - 100 / (1 + gains / losses.replace(0, 1e-12))
        previous_close = result["close"].shift()
        true_range = pd.concat((result["high"] - result["low"], (result["high"] - previous_close).abs(), (result["low"] - previous_close).abs()), axis=1).max(axis=1)
        result["atr"] = true_range.ewm(alpha=1 / config.atr_period, adjust=False, min_periods=config.atr_period).mean()
        result["adx"] = self._adx(result, true_range, config.atr_period)
        result["supertrend"] = self._supertrend(result, config.atr_period, 3.0)
        result["bb_mid"] = result["close"].rolling(20).mean()
        rolling_std = result["close"].rolling(20).std(ddof=0)
        result["bb_upper"] = result["bb_mid"] + 2 * rolling_std
        result["bb_lower"] = result["bb_mid"] - 2 * rolling_std
        result["volume_sma_20"] = result["volume"].rolling(20).mean()
        result["volume_ratio"] = result["volume"] / result["volume_sma_20"]
        return result.bfill()

    @staticmethod
    def _adx(frame: pd.DataFrame, true_range: pd.Series, period: int) -> pd.Series:
        up_move = frame["high"].diff()
        down_move = -frame["low"].diff()
        plus_dm = up_move.where((up_move > down_move) & (up_move > 0), 0.0)
        minus_dm = down_move.where((down_move > up_move) & (down_move > 0), 0.0)
        atr = true_range.ewm(alpha=1 / period, adjust=False, min_periods=period).mean()
        plus_di = 100 * plus_dm.ewm(alpha=1 / period, adjust=False).mean() / atr
        minus_di = 100 * minus_dm.ewm(alpha=1 / period, adjust=False).mean() / atr
        dx = 100 * (plus_di - minus_di).abs() / (plus_di + minus_di).replace(0, 1e-12)
        return dx.ewm(alpha=1 / period, adjust=False, min_periods=period).mean()

    @staticmethod
    def _supertrend(frame: pd.DataFrame, period: int, multiplier: float) -> pd.Series:
        atr = frame["atr"]
        midpoint = (frame["high"] + frame["low"]) / 2
        basic_upper, basic_lower = midpoint + multiplier * atr, midpoint - multiplier * atr
        upper, lower = basic_upper.copy(), basic_lower.copy()
        trend = pd.Series(index=frame.index, dtype="float64")
        start = period
        trend.iloc[: start + 1] = basic_upper.iloc[: start + 1]
        for index in range(start + 1, len(frame)):
            upper.iloc[index] = min(basic_upper.iloc[index], upper.iloc[index - 1]) if frame["close"].iloc[index - 1] <= upper.iloc[index - 1] else basic_upper.iloc[index]
            lower.iloc[index] = max(basic_lower.iloc[index], lower.iloc[index - 1]) if frame["close"].iloc[index - 1] >= lower.iloc[index - 1] else basic_lower.iloc[index]
            if trend.iloc[index - 1] == upper.iloc[index - 1]:
                trend.iloc[index] = upper.iloc[index] if frame["close"].iloc[index] <= upper.iloc[index] else lower.iloc[index]
            else:
                trend.iloc[index] = lower.iloc[index] if frame["close"].iloc[index] >= lower.iloc[index] else upper.iloc[index]
        return trend

    @staticmethod
    def _breakout(frame: pd.DataFrame) -> str:
        previous_high = frame["high"].shift(1).rolling(20).max().iloc[-1]
        previous_low = frame["low"].shift(1).rolling(20).min().iloc[-1]
        close = frame["close"].iloc[-1]
        if close > previous_high:
            return "Upside breakout"
        if close < previous_low:
            return "Downside breakdown"
        return "No confirmed breakout"

    @staticmethod
    def _signal(latest: pd.Series, breakout: str) -> TechnicalSignal:
        bullish = latest["close"] > latest["ema_20"] and latest["macd_histogram"] > 0 and latest["rsi"] >= 50 and latest["adx"] >= 20
        bearish = latest["close"] < latest["ema_20"] and latest["macd_histogram"] < 0 and latest["rsi"] <= 50 and latest["adx"] >= 20
        if bullish or breakout == "Upside breakout":
            return TechnicalSignal.BULLISH
        if bearish or breakout == "Downside breakdown":
            return TechnicalSignal.BEARISH
        return TechnicalSignal.NEUTRAL

    @staticmethod
    def _trade_plan(entry: float, atr: float, support: float, config: TechnicalConfig) -> TradePlan:
        atr_stop = entry - atr * config.atr_stop_multiple
        stop_loss = min(atr_stop, support * 0.995)
        risk_per_share = entry - stop_loss
        position_size = min(math.floor(config.capital * config.risk_per_trade_pct / 100 / risk_per_share), math.floor(config.capital / entry))
        target_price = entry + risk_per_share * config.target_risk_reward
        return TradePlan(entry, stop_loss, target_price, max(0, position_size), position_size * risk_per_share, config.target_risk_reward)

    @staticmethod
    def _volume_assessment(ratio: float) -> str:
        if ratio >= 1.5:
            return "High conviction volume"
        if ratio >= 1.0:
            return "Above-average volume"
        if ratio >= 0.7:
            return "Below-average volume"
        return "Low-conviction volume"

    @staticmethod
    def _rationale(latest: pd.Series, breakout: str, signal: TechnicalSignal) -> tuple[str, ...]:
        return (
            f"{signal.value} signal: close {latest['close']:.2f}, EMA(20) {latest['ema_20']:.2f}, RSI {latest['rsi']:.1f}, ADX {latest['adx']:.1f}.",
            f"MACD histogram is {latest['macd_histogram']:.3f}; market state: {breakout.lower()}.",
            "Trade levels use ATR and 20-period support; position size is capped by capital and risk-per-trade.",
        )
