"""Explainable QGVM equity scoring with Piotroski and Altman diagnostics."""

from __future__ import annotations

from alphalens.domain.stock import Recommendation, StockAssessment, StockInputs, StockMetrics


class StockAnalysisEngine:
    """Calculate core fundamentals and a balanced Quality/Growth/Value/Momentum score.

    This is a screening model, not personalised investment advice. It applies
    absolute thresholds so recommendations remain reproducible without a
    proprietary peer database.
    """

    def assess(self, inputs: StockInputs) -> StockAssessment:
        """Return a complete factor assessment for validated company inputs."""
        self._validate(inputs)
        metrics = self._metrics(inputs)
        quality = self._quality_score(metrics)
        growth = self._growth_score(inputs, metrics)
        value = self._value_score(metrics)
        momentum = self._momentum_score(inputs)
        composite = round((quality + growth + value + momentum) / 4)
        recommendation = self._recommend(composite, metrics)
        return StockAssessment(
            ticker=inputs.ticker.strip().upper(),
            metrics=metrics,
            quality_score=quality,
            growth_score=growth,
            value_score=value,
            momentum_score=momentum,
            composite_score=composite,
            recommendation=recommendation,
            rationale=self._rationale(metrics, composite, recommendation),
        )

    @staticmethod
    def _validate(inputs: StockInputs) -> None:
        positive = {
            "market price": inputs.market_price,
            "shares outstanding": inputs.shares_outstanding,
            "revenue": inputs.revenue,
            "EBITDA": inputs.ebitda,
            "total assets": inputs.total_assets,
            "total equity": inputs.total_equity,
            "EPS": inputs.eps,
            "book value per share": inputs.book_value_per_share,
        }
        invalid = [name for name, value in positive.items() if value <= 0]
        if invalid:
            raise ValueError(f"These fields must be positive: {', '.join(invalid)}.")
        if inputs.total_debt < 0 or inputs.cash < 0:
            raise ValueError("Debt and cash cannot be negative.")
        if not inputs.ticker.strip():
            raise ValueError("Ticker is required.")

    @staticmethod
    def _metrics(inputs: StockInputs) -> StockMetrics:
        market_cap = inputs.market_price * inputs.shares_outstanding
        enterprise_value = market_cap + inputs.total_debt - inputs.cash
        capital_employed = inputs.total_assets - inputs.current_liabilities
        return StockMetrics(
            roe=inputs.net_income / inputs.total_equity * 100,
            roce=inputs.ebit / capital_employed * 100,
            eps_growth=(inputs.eps / inputs.eps_prior - 1) * 100 if inputs.eps_prior > 0 else 0.0,
            debt_to_equity=inputs.total_debt / inputs.total_equity,
            pe=inputs.market_price / inputs.eps,
            pb=inputs.market_price / inputs.book_value_per_share,
            ev_to_ebitda=enterprise_value / inputs.ebitda,
            piotroski_score=StockAnalysisEngine._piotroski(inputs),
            altman_z_score=StockAnalysisEngine._altman_z(inputs, market_cap),
        )

    @staticmethod
    def _piotroski(inputs: StockInputs) -> int:
        roa = inputs.net_income / inputs.total_assets
        roa_prior = inputs.net_income_prior / inputs.total_assets_prior
        current_ratio = inputs.current_assets / inputs.current_liabilities
        current_ratio_prior = inputs.current_assets_prior / inputs.current_liabilities_prior
        gross_margin = inputs.gross_profit / inputs.revenue
        gross_margin_prior = inputs.gross_profit_prior / inputs.revenue_prior
        turnover = inputs.revenue / inputs.total_assets
        turnover_prior = inputs.revenue_prior / inputs.total_assets_prior
        return sum((
            int(roa > 0),
            int(inputs.operating_cash_flow > 0),
            int(roa > roa_prior),
            int(inputs.operating_cash_flow > inputs.net_income),
            int(inputs.total_debt <= inputs.total_debt_prior),
            int(current_ratio >= current_ratio_prior),
            int(inputs.shares_outstanding <= inputs.shares_outstanding_prior),
            int(gross_margin >= gross_margin_prior),
            int(turnover >= turnover_prior),
        ))

    @staticmethod
    def _altman_z(inputs: StockInputs, market_cap: float) -> float:
        working_capital = inputs.current_assets - inputs.current_liabilities
        total_liabilities = inputs.total_assets - inputs.total_equity
        if total_liabilities <= 0:
            total_liabilities = 0.01
        score = (
            1.2 * working_capital / inputs.total_assets
            + 1.4 * inputs.retained_earnings / inputs.total_assets
            + 3.3 * inputs.ebit / inputs.total_assets
            + 0.6 * market_cap / total_liabilities
            + inputs.revenue / inputs.total_assets
        )
        return round(score, 2)

    @staticmethod
    def _quality_score(metrics: StockMetrics) -> int:
        roe = 35 if metrics.roe >= 20 else 25 if metrics.roe >= 15 else 15 if metrics.roe >= 10 else 5
        roce = 30 if metrics.roce >= 20 else 22 if metrics.roce >= 15 else 12 if metrics.roce >= 10 else 4
        health = 25 if metrics.piotroski_score >= 7 else 15 if metrics.piotroski_score >= 5 else 5
        leverage = 10 if metrics.debt_to_equity <= 0.5 else 5 if metrics.debt_to_equity <= 1 else 0
        return roe + roce + health + leverage

    @staticmethod
    def _growth_score(inputs: StockInputs, metrics: StockMetrics) -> int:
        revenue_growth = (inputs.revenue / inputs.revenue_prior - 1) * 100
        eps = 45 if metrics.eps_growth >= 20 else 30 if metrics.eps_growth >= 10 else 15 if metrics.eps_growth >= 0 else 0
        revenue = 35 if revenue_growth >= 15 else 25 if revenue_growth >= 8 else 12 if revenue_growth >= 0 else 0
        income_growth = (inputs.net_income / inputs.net_income_prior - 1) * 100 if inputs.net_income_prior > 0 else 0
        profitability = 20 if income_growth >= 15 else 10 if income_growth >= 0 else 0
        return eps + revenue + profitability

    @staticmethod
    def _value_score(metrics: StockMetrics) -> int:
        pe = 35 if metrics.pe <= 15 else 25 if metrics.pe <= 25 else 12 if metrics.pe <= 35 else 0
        pb = 25 if metrics.pb <= 2 else 15 if metrics.pb <= 4 else 5 if metrics.pb <= 6 else 0
        ev = 40 if metrics.ev_to_ebitda <= 10 else 28 if metrics.ev_to_ebitda <= 15 else 12 if metrics.ev_to_ebitda <= 20 else 0
        return pe + pb + ev

    @staticmethod
    def _momentum_score(inputs: StockInputs) -> int:
        six_month = 45 if inputs.price_return_6m >= 15 else 30 if inputs.price_return_6m >= 5 else 15 if inputs.price_return_6m >= 0 else 0
        twelve_month = 55 if inputs.price_return_12m >= 20 else 35 if inputs.price_return_12m >= 8 else 15 if inputs.price_return_12m >= 0 else 0
        return six_month + twelve_month

    @staticmethod
    def _recommend(composite: int, metrics: StockMetrics) -> Recommendation:
        if metrics.altman_z_score < 1.81 or metrics.piotroski_score <= 3:
            return Recommendation.SELL
        if composite >= 75 and metrics.altman_z_score >= 2.99:
            return Recommendation.BUY
        if composite >= 50:
            return Recommendation.HOLD
        return Recommendation.SELL

    @staticmethod
    def _rationale(metrics: StockMetrics, composite: int, recommendation: Recommendation) -> tuple[str, ...]:
        altman = "safe" if metrics.altman_z_score >= 2.99 else "grey-zone" if metrics.altman_z_score >= 1.81 else "distress-risk"
        return (
            f"Composite QGVM score: {composite}/100; Piotroski F-score is {metrics.piotroski_score}/9.",
            f"ROE is {metrics.roe:.1f}%, ROCE is {metrics.roce:.1f}%, and debt/equity is {metrics.debt_to_equity:.2f}x.",
            f"Altman Z-score is {metrics.altman_z_score:.2f} ({altman}); recommendation: {recommendation.value}.",
        )
