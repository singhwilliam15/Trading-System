"""Yahoo Finance adapter for ticker-driven AlphaLens workflows."""

from __future__ import annotations

from dataclasses import dataclass

import pandas as pd
import yfinance as yf

from alphalens.core.exceptions import MarketDataError
from alphalens.domain.portfolio import PortfolioCandidate
from alphalens.domain.stock import StockInputs
from alphalens.domain.technical import TechnicalConfig
from alphalens.services.stock_analysis_engine import StockAnalysisEngine
from alphalens.services.technical_analysis_engine import TechnicalAnalysisEngine


@dataclass(frozen=True, slots=True)
class YahooTickerData:
    """Fetched prices and company metadata for one Yahoo Finance symbol."""

    ticker: str
    history: pd.DataFrame
    sector: str


class YahooFinanceProvider:
    """Fetch and normalise public Yahoo Finance data for AlphaLens services.

    Yahoo Finance availability varies by exchange and issuer. The adapter raises
    a clear error when a required fundamental field is unavailable rather than
    silently fabricating a financial ratio.
    """

    def price_history(self, ticker: str, period: str = "5y") -> YahooTickerData:
        symbol = self._normalise_ticker(ticker)
        try:
            instrument = yf.Ticker(symbol)
            history = instrument.history(period=period, auto_adjust=False)
            info = instrument.get_info()
        except Exception as error:  # Network/provider boundary.
            raise MarketDataError(f"Yahoo Finance request failed for {symbol}: {error}") from error
        if history.empty or len(history) < 60:
            raise MarketDataError(f"Yahoo Finance returned insufficient price history for {symbol}.")
        history = history.reset_index()
        return YahooTickerData(symbol, history, str(info.get("sector") or "Unclassified"))

    def stock_inputs(self, ticker: str) -> StockInputs:
        """Build validated StockInputs from Yahoo Finance statements and prices."""
        symbol = self._normalise_ticker(ticker)
        try:
            instrument = yf.Ticker(symbol)
            history = instrument.history(period="2y", auto_adjust=False)
            info = instrument.get_info()
            income = instrument.get_income_stmt(freq="yearly")
            balance = instrument.get_balance_sheet(freq="yearly")
            cashflow = instrument.get_cash_flow(freq="yearly")
        except Exception as error:  # Network/provider boundary.
            raise MarketDataError(f"Yahoo Finance request failed for {symbol}: {error}") from error
        if history.empty or len(history) < 252:
            raise MarketDataError(f"At least one year of price history is required for {symbol}.")
        price = float(history["Close"].iloc[-1])
        shares = self._number(info.get("sharesOutstanding"), "shares outstanding", symbol)
        revenue, revenue_prior = self._current_prior(income, ("TotalRevenue", "OperatingRevenue"), "revenue", symbol)
        gross_profit, gross_profit_prior = self._current_prior(income, ("GrossProfit",), "gross profit", symbol)
        ebit, _ = self._current_prior(income, ("EBIT", "OperatingIncome"), "EBIT", symbol)
        ebitda, _ = self._current_prior(income, ("EBITDA",), "EBITDA", symbol)
        net_income, net_income_prior = self._current_prior(income, ("NetIncome", "NetIncomeCommonStockholders"), "net income", symbol)
        eps, eps_prior = self._current_prior(income, ("DilutedEPS", "BasicEPS"), "EPS", symbol)
        assets, assets_prior = self._current_prior(balance, ("TotalAssets",), "total assets", symbol)
        debt, debt_prior = self._current_prior(balance, ("TotalDebt",), "total debt", symbol)
        equity, equity_prior = self._current_prior(balance, ("StockholdersEquity", "TotalStockholderEquity"), "total equity", symbol)
        current_assets, current_assets_prior = self._current_prior(balance, ("CurrentAssets",), "current assets", symbol)
        current_liabilities, current_liabilities_prior = self._current_prior(balance, ("CurrentLiabilities",), "current liabilities", symbol)
        retained_earnings, _ = self._current_prior(balance, ("RetainedEarnings",), "retained earnings", symbol)
        cash, _ = self._current_prior(balance, ("CashCashEquivalentsAndShortTermInvestments", "CashAndCashEquivalents"), "cash", symbol)
        operating_cash_flow, _ = self._current_prior(cashflow, ("OperatingCashFlow", "TotalCashFromOperatingActivities"), "operating cash flow", symbol)
        book_value = float(info.get("bookValue") or equity / shares)
        close = history["Close"].dropna()
        return StockInputs(
            ticker=symbol, market_price=price, shares_outstanding=shares, revenue=revenue, revenue_prior=revenue_prior,
            gross_profit=gross_profit, gross_profit_prior=gross_profit_prior, ebit=ebit, ebitda=ebitda,
            net_income=net_income, net_income_prior=net_income_prior, operating_cash_flow=operating_cash_flow,
            eps=eps, eps_prior=eps_prior, book_value_per_share=book_value, total_assets=assets,
            total_assets_prior=assets_prior, total_debt=debt, total_debt_prior=debt_prior,
            total_equity=equity, total_equity_prior=equity_prior, retained_earnings=retained_earnings,
            current_assets=current_assets, current_assets_prior=current_assets_prior,
            current_liabilities=current_liabilities, current_liabilities_prior=current_liabilities_prior,
            cash=cash, price_return_6m=(close.iloc[-1] / close.iloc[-126] - 1) * 100,
            price_return_12m=(close.iloc[-1] / close.iloc[-252] - 1) * 100,
            shares_outstanding_prior=shares,
        )

    def portfolio_candidate(self, ticker: str) -> PortfolioCandidate:
        """Fetch the analysis inputs needed for one portfolio candidate."""
        data = self.price_history(ticker, period="2y")
        stock = StockAnalysisEngine().assess(self.stock_inputs(data.ticker))
        technical = TechnicalAnalysisEngine().assess(data.history, TechnicalConfig(capital=1.0))
        close = data.history["Close"].dropna()
        return PortfolioCandidate(
            ticker=data.ticker, sector=data.sector, price=float(close.iloc[-1]), qgvm_score=stock.composite_score,
            technical_signal=technical.signal, daily_volatility=float(close.pct_change().dropna().std(ddof=1)),
        )

    @staticmethod
    def _normalise_ticker(ticker: str) -> str:
        symbol = ticker.strip().upper()
        if not symbol:
            raise MarketDataError("Enter a Yahoo Finance ticker, for example RELIANCE.NS or AAPL.")
        return symbol

    @staticmethod
    def _number(value: object, label: str, ticker: str) -> float:
        try:
            number = float(value)  # type: ignore[arg-type]
        except (TypeError, ValueError) as error:
            raise MarketDataError(f"Yahoo Finance has no usable {label} for {ticker}.") from error
        if number <= 0:
            raise MarketDataError(f"Yahoo Finance returned a non-positive {label} for {ticker}.")
        return number

    def _current_prior(self, statement: pd.DataFrame, labels: tuple[str, ...], label: str, ticker: str) -> tuple[float, float]:
        if statement.empty:
            raise MarketDataError(f"Yahoo Finance has no annual financial statement for {ticker}.")
        for row_label in labels:
            if row_label in statement.index and statement.loc[row_label].notna().sum() >= 2:
                values = statement.loc[row_label].dropna().iloc[:2]
                return self._number(values.iloc[0], label, ticker), self._number(values.iloc[1], f"prior {label}", ticker)
        raise MarketDataError(f"Yahoo Finance lacks two annual observations for {label} on {ticker}.")
