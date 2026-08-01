"""Individual page renderers; each only orchestrates presentation."""

from __future__ import annotations

from io import BytesIO

import numpy as np
import pandas as pd
import streamlit as st

from alphalens.domain.macro import MacroInputs
from alphalens.domain.macro import MarketRegime
from alphalens.domain.portfolio import PortfolioCandidate, PortfolioConstraints
from alphalens.domain.risk import RiskConfig
from alphalens.domain.stock import StockInputs
from alphalens.domain.technical import TechnicalConfig, TechnicalSignal
from alphalens.core.exceptions import MarketDataError
from alphalens.services.market_regime_engine import MarketRegimeEngine
from alphalens.services.portfolio_construction_engine import PortfolioConstructionEngine
from alphalens.services.risk_engine import RiskEngine
from alphalens.services.stock_analysis_engine import StockAnalysisEngine
from alphalens.services.technical_analysis_engine import TechnicalAnalysisEngine
from alphalens.services.yahoo_finance_provider import YahooFinanceProvider
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
    st.success("Phase 2 modules are active: Macro Analysis, Stock Analysis, Technical Analysis, and Risk Management.")


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
    source = st.radio("Data source", ("Yahoo Finance ticker", "Manual financial inputs"), horizontal=True)
    if source == "Yahoo Finance ticker":
        ticker = st.text_input("Yahoo Finance ticker", placeholder="RELIANCE.NS, TCS.NS, AAPL")
        if not st.button("Fetch and score stock", type="primary"):
            st.info("Enter a ticker. Indian NSE symbols require the `.NS` suffix, for example `RELIANCE.NS`.")
            return
        try:
            assessment = StockAnalysisEngine().assess(YahooFinanceProvider().stock_inputs(ticker))
        except (MarketDataError, ValueError) as error:
            st.error(str(error))
            return
        _render_stock_assessment(assessment)
        return
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

    _render_stock_assessment(assessment)


def _render_stock_assessment(assessment: object) -> None:
    """Render StockAssessment output shared by manual and Yahoo data sources."""
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
    source = st.radio("Data source", ("Yahoo Finance ticker", "Upload OHLCV CSV"), horizontal=True, key="technical_source")
    data: pd.DataFrame
    if source == "Yahoo Finance ticker":
        ticker = st.text_input("Yahoo Finance ticker", placeholder="RELIANCE.NS, TCS.NS, AAPL", key="technical_ticker")
        if st.button("Fetch price history", type="primary", key="technical_fetch"):
            try:
                st.session_state["technical_yahoo_data"] = YahooFinanceProvider().price_history(ticker).history
            except MarketDataError as error:
                st.error(str(error))
                return
        if "technical_yahoo_data" not in st.session_state:
            st.info("Enter a ticker to fetch its OHLCV history automatically.")
            return
        data = st.session_state["technical_yahoo_data"]
    else:
        uploaded = st.file_uploader("Upload chronological OHLCV CSV", type="csv", help="Required columns: Open, High, Low, Close, Volume. At least 60 rows.")
        if uploaded is None:
            st.info("Upload an OHLCV CSV to calculate indicators. No synthetic price data is used.")
            return
        try:
            data = pd.read_csv(uploaded)
        except pd.errors.ParserError as error:
            st.error(str(error))
            return
    first, second, third = st.columns(3)
    capital = first.number_input("Trading capital", min_value=1.0, value=100_000.0, step=1_000.0)
    risk_pct = second.number_input("Risk per trade (%)", min_value=0.1, max_value=5.0, value=1.0, step=0.1)
    target_rr = third.number_input("Target risk-reward", min_value=0.5, max_value=10.0, value=2.0, step=0.5)
    try:
        assessment = TechnicalAnalysisEngine().assess(
            data,
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
    """Render the constrained portfolio construction dashboard."""
    st.title("Portfolio")
    st.caption("Macro regime · QGVM factors · Technical confirmation · VaR constraints")
    source = st.radio("Candidate source", ("Yahoo Finance tickers", "Upload candidate CSV"), horizontal=True, key="portfolio_source")
    candidates: list[PortfolioCandidate]
    if source == "Yahoo Finance tickers":
        ticker_text = st.text_area("Yahoo Finance tickers", placeholder="RELIANCE.NS, TCS.NS, HDFCBANK.NS", help="Separate tickers with commas. Each ticker is fetched, QGVM-scored, and technically analysed.")
        if st.button("Fetch candidates and construct portfolio", type="primary", key="portfolio_fetch"):
            symbols = [symbol.strip() for symbol in ticker_text.split(",") if symbol.strip()]
            if len(symbols) < 2:
                st.error("Enter at least two comma-separated tickers.")
                return
            try:
                provider = YahooFinanceProvider()
                st.session_state["portfolio_yahoo_candidates"] = [provider.portfolio_candidate(symbol) for symbol in symbols]
            except (MarketDataError, ValueError) as error:
                st.error(f"Could not build portfolio candidates: {error}")
                return
        if "portfolio_yahoo_candidates" not in st.session_state:
            st.info("Enter at least two Yahoo Finance tickers. The engine will fetch price and fundamental data automatically.")
            return
        candidates = st.session_state["portfolio_yahoo_candidates"]
    else:
        template = pd.DataFrame(columns=["ticker", "sector", "price", "qgvm_score", "technical_signal", "daily_volatility", "current_weight"])
        st.download_button("Download portfolio input template", template.to_csv(index=False), "portfolio_candidates_template.csv", "text/csv")
        uploaded = st.file_uploader("Upload portfolio candidates CSV", type="csv", help="Use the template; daily volatility and current weight must be decimal values, e.g. 0.02 and 0.05.")
        if uploaded is None:
            st.info("Upload candidate holdings to construct a portfolio. Use results from the Stock and Technical modules for QGVM score and technical signal.")
            return
        try:
            data = pd.read_csv(uploaded)
            required = {"ticker", "sector", "price", "qgvm_score", "technical_signal", "daily_volatility"}
            missing = required - set(data.columns)
            if missing:
                raise ValueError(f"Candidate file is missing: {', '.join(sorted(missing))}.")
            if "current_weight" not in data.columns:
                data["current_weight"] = 0.0
            data["current_weight"] = data["current_weight"].fillna(0.0)
            candidates = [
                PortfolioCandidate(
                    ticker=str(row.ticker), sector=str(row.sector), price=float(row.price),
                    qgvm_score=float(row.qgvm_score), technical_signal=TechnicalSignal(str(row.technical_signal).strip().title()),
                    daily_volatility=float(row.daily_volatility), current_weight=float(row.current_weight),
                )
                for row in data.itertuples(index=False)
            ]
        except (TypeError, ValueError, pd.errors.ParserError) as error:
            st.error(f"Portfolio input error: {error}")
            return
    first, second, third = st.columns(3)
    regime = first.selectbox("Macro regime", list(MarketRegime), format_func=lambda value: value.value)
    macro_score = second.number_input("Macro Score", min_value=0.0, max_value=100.0, value=60.0, step=1.0)
    risk_score = third.number_input("Risk Score", min_value=0.0, max_value=100.0, value=40.0, step=1.0)
    first, second, third, fourth = st.columns(4)
    capital = first.number_input("Portfolio capital", min_value=1.0, value=1_000_000.0, step=10_000.0)
    var_limit = second.number_input("Maximum daily VaR (%)", min_value=0.1, max_value=20.0, value=2.0, step=0.1)
    max_position = third.number_input("Maximum position (%)", min_value=1.0, max_value=100.0, value=10.0, step=1.0)
    max_sector = fourth.number_input("Maximum sector (%)", min_value=1.0, max_value=100.0, value=25.0, step=1.0)
    try:
        assessment = PortfolioConstructionEngine().construct(candidates, PortfolioConstraints(
            capital=capital, macro_regime=regime, macro_score=macro_score, risk_score=risk_score,
            var_limit_pct=var_limit / 100, max_position_weight=max_position / 100, max_sector_weight=max_sector / 100,
        ))
    except (TypeError, ValueError) as error:
        st.error(f"Portfolio input error: {error}")
        return
    first, second, third, fourth = st.columns(4)
    first.metric("Invested", f"{assessment.invested_weight:.1%}")
    second.metric("Cash reserve", f"{assessment.cash_weight:.1%}")
    third.metric("Estimated 99% daily VaR", f"{assessment.estimated_var:,.0f}")
    fourth.metric("Rebalancing", assessment.rebalancing_summary.split(" of")[0])
    st.subheader("Target holdings and rebalancing")
    st.dataframe([{
        "Ticker": item.ticker, "Sector": item.sector, "Composite signal": item.score,
        "Current weight": f"{item.current_weight:.1%}", "Target weight": f"{item.target_weight:.1%}",
        "Target notional": round(item.target_notional, 2), "Target shares": item.target_shares, "Action": item.rebalance_action,
    } for item in assessment.positions], hide_index=True, use_container_width=True)
    st.subheader("Sector allocation")
    st.bar_chart(pd.DataFrame.from_dict(assessment.sector_allocations, orient="index", columns=["Target weight"]), use_container_width=True)
    for item in assessment.rationale:
        st.write(f"• {item}")


def render_risk_management() -> None:
    """Render the VaR workbook-compatible portfolio risk dashboard."""
    st.title("Risk Management")
    st.caption("Historical · Parametric · Monte Carlo VaR · Expected Shortfall")
    source = st.radio("Data source", ("Yahoo Finance ticker", "VaR workbook or CSV"), horizontal=True, key="risk_source")
    data: pd.DataFrame
    default_column = 0
    default_input_type = 0
    if source == "Yahoo Finance ticker":
        ticker = st.text_input("Yahoo Finance ticker", placeholder="NIFTYBEES.NS, RELIANCE.NS, AAPL", key="risk_ticker")
        if st.button("Fetch price history for risk analysis", type="primary", key="risk_fetch"):
            try:
                st.session_state["risk_yahoo_data"] = YahooFinanceProvider().price_history(ticker).history
            except MarketDataError as error:
                st.error(str(error))
                return
        if "risk_yahoo_data" not in st.session_state:
            st.info("Enter a ticker to calculate VaR and risk ratios directly from its adjusted market history.")
            return
        data = st.session_state["risk_yahoo_data"]
        default_column = list(data.select_dtypes(include="number").columns).index("Close")
    else:
        uploaded = st.file_uploader("Upload VaR workbook, price CSV, or return CSV", type=["xlsx", "xls", "csv"])
        if uploaded is None:
            st.info("Upload the supplied VaR workbook or a CSV. Select the worksheet/column containing chronological prices or periodic returns.")
            return
        try:
            file_bytes = uploaded.getvalue()
            if uploaded.name.lower().endswith((".xlsx", ".xls")):
                workbook = pd.ExcelFile(BytesIO(file_bytes))
                sheet = st.selectbox("Workbook sheet", workbook.sheet_names)
                data = pd.read_excel(BytesIO(file_bytes), sheet_name=sheet)
            else:
                data = pd.read_csv(BytesIO(file_bytes))
        except (ValueError, OSError, pd.errors.ParserError) as error:
            st.error(f"Could not read the uploaded file: {error}")
            return
    numeric_columns = data.select_dtypes(include="number").columns.tolist()
    if not numeric_columns:
        st.error("No numeric columns were found in the selected data source.")
        return
    left, middle, right = st.columns(3)
    column = left.selectbox("Price or return column", numeric_columns, index=default_column)
    input_type = middle.selectbox("Input type", ("Prices", "Returns (decimal)", "Returns (%)"), index=default_input_type)
    confidence = right.selectbox("Confidence level", (0.95, 0.99), format_func=lambda value: f"{value:.0%}")
    first, second, third = st.columns(3)
    portfolio_value = first.number_input("Portfolio value", min_value=1.0, value=1_000_000.0, step=10_000.0)
    horizon = second.number_input("VaR horizon (days)", min_value=1, max_value=30, value=1)
    risk_free = third.number_input("Annual risk-free rate (%)", min_value=-10.0, max_value=30.0, value=6.0, step=0.1)
    try:
        selected = data[column]
        if input_type == "Prices":
            returns = RiskEngine.returns_from_prices(selected)
        else:
            returns = pd.to_numeric(selected, errors="coerce")
            if input_type == "Returns (%)":
                returns = returns / 100
        assessment = RiskEngine().assess(returns, RiskConfig(
            portfolio_value=portfolio_value,
            confidence_level=confidence,
            horizon_days=horizon,
            annual_risk_free_rate=risk_free / 100,
        ))
    except ValueError as error:
        st.error(str(error))
        return
    first, second, third, fourth = st.columns(4)
    first.metric("Historical VaR", f"{assessment.historical_var:,.0f}")
    second.metric("Parametric VaR", f"{assessment.parametric_var:,.0f}")
    third.metric("Monte Carlo VaR", f"{assessment.monte_carlo_var:,.0f}")
    fourth.metric("Expected Shortfall", f"{assessment.expected_shortfall:,.0f}")
    first, second, third, fourth = st.columns(4)
    first.metric("Maximum drawdown", f"{assessment.maximum_drawdown:.2%}")
    second.metric("Sharpe ratio", "N/A" if assessment.sharpe_ratio is None else f"{assessment.sharpe_ratio:.2f}")
    third.metric("Sortino ratio", "N/A" if assessment.sortino_ratio is None else f"{assessment.sortino_ratio:.2f}")
    fourth.metric("Observations", assessment.observations)
    histogram, edges = np.histogram(assessment.simulated_returns, bins=40)
    st.subheader("Monte Carlo return distribution")
    st.bar_chart(pd.DataFrame({"Frequency": histogram}, index=edges[:-1]), use_container_width=True)
    st.caption(f"Mean daily return: {assessment.mean_daily_return:.3%} · Daily volatility: {assessment.daily_volatility:.3%}")


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
