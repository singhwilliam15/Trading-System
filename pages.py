"""Individual page renderers; each only orchestrates presentation."""

from __future__ import annotations

import pandas as pd
import streamlit as st

from alphalens.domain.macro import MacroInputs
from alphalens.domain.stock import StockInputs
from alphalens.domain.technical import TechnicalConfig
from alphalens.services.market_regime_engine import MarketRegimeEngine
from alphalens.services.stock_analysis_engine import StockAnalysisEngine
from alphalens.services.technical_analysis_engine import TechnicalAnalysisEngine
from alphalens.services.source_registry import SourceRegistry
from alphalens.ui.page_factory import render_module_placeholder


def render_dashboard(registry: SourceRegistry) -> None:
    st.title("AlphaLens AI")
    st.caption("Institutional Trading & Investment Decision Platform")
    available = len(registry.available_sources())
    total = len(registry.sources)
    left, right = st.columns(2)
    left.metric("Registered research sources", total)
    right.metric("Sources available locally", f"{available}/{total}")
    st.progress(registry.readiness_ratio(), text="Source-data readiness")
    st.info("Phase 1 is complete: navigation, architecture, and source-data boundaries are established.")


def render_macro_analysis() -> None:
    """Render the interactive, service-backed market regime assessment."""
    st.title("Macro Analysis")
    st.caption("Market Regime Engine · transparent, rules-based allocation guidance")
    st.write("Enter current macro and market observations. Rates, spreads, and returns are annualised percentages.")
    with st.form("macro_inputs"):
        first, second, third = st.columns(3)
        gdp_growth = first.number_input("GDP growth (%)", value=6.5, step=0.1)
        inflation = first.number_input("Inflation (%)", value=4.5, min_value=-5.0, step=0.1)
        policy_rate = first.number_input("Policy rate (%)", value=6.5, min_value=-5.0, step=0.1)
        policy_rate_change = second.number_input("Policy-rate change (% pts)", value=0.0, step=0.1)
        pmi = second.number_input("Manufacturing PMI", value=52.0, min_value=25.0, max_value=75.0, step=0.1)
        unemployment = second.number_input("Unemployment (%)", value=5.0, min_value=0.0, max_value=50.0, step=0.1)
        equity_return = third.number_input("12-month equity return (%)", value=8.0, step=0.1)
        volatility = third.number_input("Equity volatility index", value=18.0, min_value=0.0, max_value=150.0, step=0.1)
        yield_curve = third.number_input("Yield-curve spread (% pts)", value=0.5, step=0.1)
        credit_spread = third.number_input("Credit spread (bps)", value=175.0, min_value=0.0, step=5.0)
        submitted = st.form_submit_button("Assess market regime", type="primary")

    if not submitted:
        return
    try:
        assessment = MarketRegimeEngine().assess(
            MacroInputs(
                gdp_growth=gdp_growth,
                inflation=inflation,
                policy_rate=policy_rate,
                policy_rate_change=policy_rate_change,
                pmi=pmi,
                unemployment=unemployment,
                equity_return_12m=equity_return,
                volatility=volatility,
                yield_curve_spread=yield_curve,
                credit_spread=credit_spread,
            )
        )
    except ValueError as error:
        st.error(str(error))
        return

    first, second, third = st.columns(3)
    first.metric("Market regime", assessment.regime.value)
    second.metric("Macro Score", f"{assessment.macro_score}/100")
    third.metric("Risk Score", f"{assessment.risk_score}/100")
    st.success(assessment.recommendation)
    st.subheader("Sector outlook")
    st.dataframe(
        [{"Sector": item.sector, "Outlook": item.outlook.value, "Rationale": item.rationale} for item in assessment.sector_outlook],
        hide_index=True,
        use_container_width=True,
    )
    st.subheader("Decision rationale")
    for item in assessment.rationale:
        st.write(f"• {item}")


def render_stock_analysis() -> None:
    """Render the factor-based equity screening interface."""
    st.title("Stock Analysis")
    st.caption("Quality · Growth · Value · Momentum (QGVM) Engine")
    with st.form("stock_inputs"):
        identity, market, income, balance = st.tabs(["Identity", "Market", "Income", "Balance sheet"])
        with identity:
            ticker = st.text_input("Ticker", value="EXAMPLE")
            shares = st.number_input("Shares outstanding (millions)", min_value=0.01, value=100.0)
            shares_prior = st.number_input("Prior shares outstanding (millions)", min_value=0.01, value=100.0)
        with market:
            market_price = st.number_input("Market price", min_value=0.01, value=150.0)
            book_value = st.number_input("Book value per share", min_value=0.01, value=50.0)
            cash = st.number_input("Cash", min_value=0.0, value=1_000.0)
            return_6m = st.number_input("6-month price return (%)", value=12.0)
            return_12m = st.number_input("12-month price return (%)", value=22.0)
        with income:
            revenue = st.number_input("Revenue", min_value=0.01, value=10_000.0)
            revenue_prior = st.number_input("Prior revenue", min_value=0.01, value=8_500.0)
            gross_profit = st.number_input("Gross profit", value=4_000.0)
            gross_profit_prior = st.number_input("Prior gross profit", value=3_200.0)
            ebit = st.number_input("EBIT", value=2_000.0)
            ebitda = st.number_input("EBITDA", min_value=0.01, value=2_400.0)
            net_income = st.number_input("Net income", value=1_500.0)
            net_income_prior = st.number_input("Prior net income", value=1_100.0)
            operating_cash_flow = st.number_input("Operating cash flow", value=1_800.0)
            eps = st.number_input("EPS", min_value=0.01, value=10.0)
            eps_prior = st.number_input("Prior EPS", min_value=0.01, value=8.0)
        with balance:
            total_assets = st.number_input("Total assets", min_value=0.01, value=12_000.0)
            total_assets_prior = st.number_input("Prior total assets", min_value=0.01, value=10_500.0)
            total_debt = st.number_input("Total debt", min_value=0.0, value=1_500.0)
            total_debt_prior = st.number_input("Prior total debt", min_value=0.0, value=1_700.0)
            total_equity = st.number_input("Total equity", min_value=0.01, value=7_500.0)
            total_equity_prior = st.number_input("Prior total equity", min_value=0.01, value=6_800.0)
            retained_earnings = st.number_input("Retained earnings", value=3_500.0)
            current_assets = st.number_input("Current assets", min_value=0.01, value=4_000.0)
            current_assets_prior = st.number_input("Prior current assets", min_value=0.01, value=3_600.0)
            current_liabilities = st.number_input("Current liabilities", min_value=0.01, value=2_000.0)
            current_liabilities_prior = st.number_input("Prior current liabilities", min_value=0.01, value=2_000.0)
        submitted = st.form_submit_button("Score stock", type="primary")
    if not submitted:
        return
    try:
        assessment = StockAnalysisEngine().assess(StockInputs(
            ticker, market_price, shares, revenue, revenue_prior, gross_profit, gross_profit_prior,
            ebit, ebitda, net_income, net_income_prior, operating_cash_flow, eps, eps_prior,
            book_value, total_assets, total_assets_prior, total_debt, total_debt_prior,
            total_equity, total_equity_prior, retained_earnings, current_assets,
            current_assets_prior, current_liabilities, current_liabilities_prior, cash,
            return_6m, return_12m, shares_prior,
        ))
    except ValueError as error:
        st.error(str(error))
        return
    factor_columns = st.columns(5)
    for column, label, value in zip(factor_columns, ("Quality", "Growth", "Value", "Momentum", "Composite"), (assessment.quality_score, assessment.growth_score, assessment.value_score, assessment.momentum_score, assessment.composite_score), strict=True):
        column.metric(label, f"{value}/100")
    st.success(f"{assessment.recommendation.value.upper()} · {assessment.ticker}")
    metrics = assessment.metrics
    st.subheader("Fundamentals and valuation")
    st.dataframe([{
        "ROE": f"{metrics.roe:.1f}%", "ROCE": f"{metrics.roce:.1f}%", "EPS Growth": f"{metrics.eps_growth:.1f}%",
        "Debt/Equity": f"{metrics.debt_to_equity:.2f}x", "P/E": f"{metrics.pe:.1f}x", "P/B": f"{metrics.pb:.1f}x",
        "EV/EBITDA": f"{metrics.ev_to_ebitda:.1f}x", "Piotroski": f"{metrics.piotroski_score}/9", "Altman Z": f"{metrics.altman_z_score:.2f}",
    }], hide_index=True, use_container_width=True)
    for item in assessment.rationale:
        st.write(f"• {item}")


def render_technical_analysis() -> None:
    """Render CSV-driven technical analysis without mixing calculations into the UI."""
    st.title("Technical Analysis")
    st.caption("OHLCV indicators, breakout screening, and ATR-based trade planning")
    uploaded = st.file_uploader("Upload chronological OHLCV CSV", type="csv", help="Required columns: Open, High, Low, Close, Volume. At least 60 rows.")
    first, second, third = st.columns(3)
    capital = first.number_input("Trading capital", min_value=1.0, value=100_000.0, step=1_000.0)
    risk_pct = second.number_input("Risk per trade (%)", min_value=0.1, max_value=5.0, value=1.0, step=0.1)
    target_rr = third.number_input("Target risk-reward", min_value=0.5, max_value=10.0, value=2.0, step=0.5)
    if uploaded is None:
        st.info("Upload an OHLCV CSV to calculate indicators. No synthetic price data is used.")
        return
    try:
        assessment = TechnicalAnalysisEngine().assess(
            pd.read_csv(uploaded),
            TechnicalConfig(capital=capital, risk_per_trade_pct=risk_pct, target_risk_reward=target_rr),
        )
    except (ValueError, pd.errors.ParserError) as error:
        st.error(str(error))
        return
    left, middle, right = st.columns(3)
    left.metric("Technical signal", assessment.signal.value)
    middle.metric("Breakout status", assessment.breakout)
    right.metric("Volume", assessment.volume_assessment)
    st.subheader("Price and trend")
    st.line_chart(assessment.indicator_frame[["close", "ema_20", "sma_20", "sma_50", "supertrend", "bb_upper", "bb_lower"]], use_container_width=True)
    st.subheader("Latest indicators")
    st.dataframe([assessment.indicators], hide_index=True, use_container_width=True)
    st.subheader("Support, resistance, and trade plan")
    plan = assessment.trade_plan
    st.dataframe([{
        "Support": round(assessment.support, 2), "Resistance": round(assessment.resistance, 2),
        "Entry": round(plan.entry_price, 2), "Stop loss": round(plan.stop_loss, 2),
        "Target": round(plan.target_price, 2), "Position size": plan.position_size,
        "Capital at risk": round(plan.capital_at_risk, 2), "Risk-reward": f"1:{plan.risk_reward:.1f}",
    }], hide_index=True, use_container_width=True)
    for item in assessment.rationale:
        st.write(f"• {item}")


def render_portfolio() -> None:
    render_module_placeholder("Portfolio", "Portfolio construction, allocation, and performance attribution.")


def render_risk_management() -> None:
    render_module_placeholder("Risk Management", "Exposure controls and VaR-driven risk monitoring.")


def render_options_analysis() -> None:
    render_module_placeholder("Options Analysis", "Options structures, payoff analysis, and derivatives risk.")


def render_backtesting() -> None:
    render_module_placeholder("Backtesting", "Historical strategy evaluation with reproducible assumptions.")


def render_reports() -> None:
    render_module_placeholder("Reports", "Decision-ready investment and trading reports.")


def render_settings(registry: SourceRegistry) -> None:
    st.title("Settings")
    st.caption("Phase 1 · Application foundation")
    st.code(str(registry.data_dir), language=None)
    st.write("Configured source-data directory. Set `ALPHALENS_DATA_DIR` to change it.")
"""Individual page renderers; each only orchestrates presentation."""
