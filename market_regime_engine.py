"""Deterministic macro regime classification and allocation guidance."""

from __future__ import annotations

from alphalens.domain.macro import (
    MacroAssessment,
    MacroInputs,
    MarketRegime,
    Outlook,
    SectorOutlook,
)


class MarketRegimeEngine:
    """Scores the business cycle from transparent, reviewable market inputs.

    Scores are deliberately rule-based rather than predictive. This makes a
    recommendation explainable, testable, and straightforward to recalibrate
    against the supplied strategy research as source extraction matures.
    """

    _SECTOR_MAP: dict[MarketRegime, tuple[SectorOutlook, ...]] = {
        MarketRegime.RECOVERY: (
            SectorOutlook("Financials", Outlook.OVERWEIGHT, "Credit demand and earnings typically recover early."),
            SectorOutlook("Industrials", Outlook.OVERWEIGHT, "Reacceleration supports capex-sensitive businesses."),
            SectorOutlook("Consumer Discretionary", Outlook.OVERWEIGHT, "Improving employment supports discretionary spending."),
            SectorOutlook("Utilities", Outlook.UNDERWEIGHT, "Defensive income is relatively less attractive in recovery."),
        ),
        MarketRegime.EXPANSION: (
            SectorOutlook("Industrials", Outlook.OVERWEIGHT, "Broad activity and investment are supportive."),
            SectorOutlook("Technology", Outlook.OVERWEIGHT, "Growth and earnings breadth favour quality growth assets."),
            SectorOutlook("Materials", Outlook.OVERWEIGHT, "Demand and operating leverage improve in expansion."),
            SectorOutlook("Consumer Staples", Outlook.UNDERWEIGHT, "Defensive earnings generally lag cyclical growth."),
        ),
        MarketRegime.LATE_EXPANSION: (
            SectorOutlook("Energy", Outlook.OVERWEIGHT, "Inflation sensitivity can provide portfolio protection."),
            SectorOutlook("Healthcare", Outlook.OVERWEIGHT, "Resilient earnings reduce late-cycle cyclicality."),
            SectorOutlook("Consumer Staples", Outlook.OVERWEIGHT, "Pricing power and defensive demand gain importance."),
            SectorOutlook("Real Estate", Outlook.UNDERWEIGHT, "Higher financing costs pressure rate-sensitive valuations."),
        ),
        MarketRegime.PEAK: (
            SectorOutlook("Healthcare", Outlook.OVERWEIGHT, "Defensive cash flows are favoured as growth decelerates."),
            SectorOutlook("Utilities", Outlook.OVERWEIGHT, "Lower beta can help contain portfolio drawdowns."),
            SectorOutlook("Consumer Staples", Outlook.OVERWEIGHT, "Demand resilience becomes more valuable."),
            SectorOutlook("Materials", Outlook.UNDERWEIGHT, "Cyclicals are vulnerable to a turn in activity."),
        ),
        MarketRegime.CONTRACTION: (
            SectorOutlook("Healthcare", Outlook.OVERWEIGHT, "Non-discretionary demand supports earnings resilience."),
            SectorOutlook("Utilities", Outlook.OVERWEIGHT, "Stable cash flows can reduce cyclicality."),
            SectorOutlook("Consumer Staples", Outlook.OVERWEIGHT, "Essential consumption is relatively defensive."),
            SectorOutlook("Financials", Outlook.UNDERWEIGHT, "Credit losses and slower loan growth raise risk."),
        ),
    }

    def assess(self, inputs: MacroInputs) -> MacroAssessment:
        """Evaluate inputs and return a full macro allocation assessment."""
        self._validate(inputs)
        growth_score = self._growth_score(inputs)
        risk_score = self._risk_score(inputs)
        macro_score = max(0, min(100, 50 + growth_score - (risk_score - 50) // 2))
        regime = self._classify(inputs, growth_score, risk_score)
        return MacroAssessment(
            regime=regime,
            macro_score=macro_score,
            risk_score=risk_score,
            recommendation=self._recommendation(regime),
            sector_outlook=self._SECTOR_MAP[regime],
            rationale=self._rationale(inputs, growth_score, risk_score),
        )

    @staticmethod
    def _validate(inputs: MacroInputs) -> None:
        if not 25 <= inputs.pmi <= 75:
            raise ValueError("PMI must be between 25 and 75.")
        if not 0 <= inputs.volatility <= 150:
            raise ValueError("Volatility must be between 0 and 150.")
        if not 0 <= inputs.unemployment <= 50:
            raise ValueError("Unemployment must be between 0 and 50%.")

    @staticmethod
    def _growth_score(inputs: MacroInputs) -> int:
        gdp = 20 if inputs.gdp_growth >= 7 else 14 if inputs.gdp_growth >= 5 else 6 if inputs.gdp_growth >= 2.5 else -4 if inputs.gdp_growth >= 0 else -16
        pmi = 18 if inputs.pmi >= 55 else 9 if inputs.pmi >= 50 else -6 if inputs.pmi >= 45 else -18
        employment = 8 if inputs.unemployment <= 4 else 4 if inputs.unemployment <= 6 else -3 if inputs.unemployment <= 8 else -10
        market = 10 if inputs.equity_return_12m >= 10 else 4 if inputs.equity_return_12m >= 0 else -5 if inputs.equity_return_12m >= -10 else -12
        curve = 7 if inputs.yield_curve_spread > 0 else -7
        return gdp + pmi + employment + market + curve

    @staticmethod
    def _risk_score(inputs: MacroInputs) -> int:
        inflation = 10 if inputs.inflation <= 4 else 25 if inputs.inflation <= 6 else 45 if inputs.inflation <= 8 else 65
        volatility = 8 if inputs.volatility < 15 else 22 if inputs.volatility < 22 else 45 if inputs.volatility < 30 else 70
        credit = 8 if inputs.credit_spread < 150 else 25 if inputs.credit_spread < 250 else 50 if inputs.credit_spread < 400 else 70
        policy_change = 10 if inputs.policy_rate_change <= -0.50 else 20 if inputs.policy_rate_change < 0 else 35 if inputs.policy_rate_change < 0.50 else 50
        policy_level = 8 if inputs.policy_rate <= 4 else 20 if inputs.policy_rate <= 6 else 35 if inputs.policy_rate <= 8 else 50
        monetary = policy_change * 0.60 + policy_level * 0.40
        return max(0, min(100, round(inflation * 0.35 + volatility * 0.30 + credit * 0.25 + monetary * 0.10)))

    @staticmethod
    def _classify(inputs: MacroInputs, growth_score: int, risk_score: int) -> MarketRegime:
        if inputs.gdp_growth < 0 or (inputs.pmi < 48 and inputs.equity_return_12m < -8):
            return MarketRegime.CONTRACTION
        if growth_score >= 30 and inputs.inflation >= 6 and risk_score >= 45:
            return MarketRegime.PEAK
        if growth_score >= 25 and (inputs.inflation >= 5 or risk_score >= 40):
            return MarketRegime.LATE_EXPANSION
        if growth_score >= 20 and risk_score < 45:
            return MarketRegime.EXPANSION
        return MarketRegime.RECOVERY

    @staticmethod
    def _recommendation(regime: MarketRegime) -> str:
        recommendations = {
            MarketRegime.RECOVERY: "Accumulate quality cyclicals gradually; retain diversification while recovery evidence strengthens.",
            MarketRegime.EXPANSION: "Maintain a pro-growth allocation with disciplined position sizing and regular risk reviews.",
            MarketRegime.LATE_EXPANSION: "Rotate selectively toward pricing power and defensives; reduce leverage and weaker cyclicals.",
            MarketRegime.PEAK: "De-risk cyclical exposure, raise quality and liquidity, and prepare downside protection.",
            MarketRegime.CONTRACTION: "Prioritise capital preservation, defensive earnings, high-quality fixed income, and strict risk limits.",
        }
        return recommendations[regime]

    @staticmethod
    def _rationale(inputs: MacroInputs, growth_score: int, risk_score: int) -> tuple[str, ...]:
        activity = "expanding" if inputs.pmi >= 50 else "contracting"
        curve = "positive" if inputs.yield_curve_spread > 0 else "inverted"
        return (
            f"Growth composite: {growth_score:+d}; GDP growth is {inputs.gdp_growth:.1f}% and activity is {activity} (PMI {inputs.pmi:.1f}).",
            f"Risk composite: {risk_score}/100; inflation is {inputs.inflation:.1f}% and volatility is {inputs.volatility:.1f}.",
            f"The yield curve is {curve} ({inputs.yield_curve_spread:.2f} percentage points) and 12-month equity return is {inputs.equity_return_12m:.1f}%.",
        )
