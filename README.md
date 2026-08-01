# AlphaLens AI

AlphaLens AI is a modular Streamlit prototype for institutional-style trading and investment decisions. Phase 1 establishes the application shell, navigation, source-data boundaries, and engineering foundation; quantitative models and document/workbook extraction follow in later phases.

## Features in Phase 1

- Responsive dark Streamlit interface with ten application modules.
- Centralized configuration, logging, error handling, and source registry.
- Source catalogue for the supplied strategy reports and risk-management workbooks.
- UI and domain/service layers are intentionally separated.
- Test-ready, GitHub-ready Python package layout.

## Macro Analysis

The Market Regime Engine is a deterministic, explainable service built around
the strategy material's macro-to-allocation workflow. It uses GDP growth,
inflation, policy-rate changes, PMI, unemployment, equity returns, volatility,
the yield curve, and credit spreads to classify **Recovery**, **Expansion**,
**Late Expansion**, **Peak**, or **Contraction**. It returns a Macro Score,
Risk Score, sector outlook, decision rationale, and investment recommendation.

The thresholds and sector mappings live in
`src/alphalens/services/market_regime_engine.py`, not the page layer, so they
can be reviewed and calibrated as source-document extraction is added.

## Stock Analysis

The Stock Analysis Engine calculates ROE, ROCE, EPS growth, debt/equity, P/E,
P/B, EV/EBITDA, Piotroski F-score, and Altman Z-score. It combines transparent
Quality, Growth, Value, and Momentum factor scores into a Buy, Hold, or Sell
screening recommendation. Inputs should be consistent in currency and unit;
the result is a research screen, not personalised financial advice.

### Yahoo Finance automation

Stock Analysis can fetch annual financial statements and two years of price
history directly from a Yahoo Finance ticker. Technical Analysis and Risk
Management can fetch OHLCV history from the same ticker, while Portfolio can
turn a comma-separated ticker list into scored candidates automatically. Use
the Yahoo symbol exactly as published; for example, Indian NSE symbols normally
use the `.NS` suffix (`RELIANCE.NS`, `TCS.NS`).

Yahoo Finance occasionally omits a fundamental field or prior-year statement.
In that case AlphaLens displays a clear data-availability error rather than
substituting an invented ratio. The CSV and workbook workflows remain
available as a fallback.

## Technical Analysis

Upload a chronological OHLCV CSV with `Open`, `High`, `Low`, `Close`, and
`Volume` columns (at least 60 rows). The Technical Analysis Engine computes
RSI, MACD, EMA, SMA, ADX, ATR, SuperTrend, Bollinger Bands, volume ratios,
20-period support/resistance, and breakout status. It also creates an
ATR-and-support-based long trade plan with position size, stop loss, target,
capital at risk, and risk-reward from the entered risk settings.

## Risk Management

The Risk Dashboard accepts a worksheet from the supplied VaR workbook, or a
CSV containing a numeric price or return column. Select whether the source is
prices, decimal returns, or percentage returns. It calculates Historical VaR,
Parametric VaR, Monte Carlo VaR, Expected Shortfall, Maximum Drawdown, Sharpe
Ratio, and Sortino Ratio using the selected confidence level, horizon, and
portfolio value.

## Portfolio Construction

The Portfolio Engine accepts a candidate CSV containing ticker, sector, price,
QGVM score, technical signal, daily volatility, and optional current weight.
It uses the selected Macro Regime, Macro Score, Risk Score, and daily VaR limit
to construct target holdings. The resulting allocation applies maximum position
and sector limits, preserves an appropriate cash reserve, calculates whole-share
position sizes, and issues Buy/Hold/Sell rebalancing instructions.

## Project layout

```text
alphalens-ai/
├── .streamlit/             # Streamlit UI/runtime configuration
├── data/
│   ├── raw/                # Local source reports and workbooks (gitignored)
│   └── processed/          # Derived datasets (gitignored)
├── logs/                   # Local application logs (gitignored)
├── src/alphalens/
│   ├── core/               # Exceptions and logging
│   ├── domain/             # Source metadata and future domain models
│   ├── services/           # Non-UI application services
│   └── ui/                 # Streamlit app shell and pages
├── tests/                  # Automated tests
├── app.py                  # Streamlit entry point
├── requirements.txt
└── pyproject.toml
```

## Setup

1. Create and activate a Python 3.11+ virtual environment.
2. Install dependencies and the local package: `pip install -r requirements.txt && pip install -e .`
3. Copy the supplied `.docx` and `.xlsx` files into `data/raw/` (they are intentionally not committed).
4. Run: `streamlit run app.py`

## Streamlit Community Cloud deployment

Deploy the **entire contents** of this repository, not `app.py` by itself. In
the repository root, the deployment should include both `app.py` and
`src/alphalens/`; `app.py` adds `src/` to the import path before loading the
modular application. It also provides a deployment-safe Phase 1 shell when a
Cloud repository contains only the entry point. Set the Cloud main file path
to `app.py`, then reboot the app after pushing the update.

## Supplied source material

The source catalogue expects these files in `data/raw/`:

- `DalalStreet_Elite_Strategy_Report.docx`
- `Enhanced_Final_Report.docx`
- `Full_Strategy_Report.docx`
- `Phase_1_Market_Understanding.docx` through `Phase_5_Derivatives_Strategies.docx`
- `BS-FIRST PRINCIPLE-STUDENT.xlsx`
- `VaR_Risk_Management_Tool.xlsx`

Phase 2 will convert these inputs into validated, traceable datasets and quantitative services. This repository does not commit personal or source data.

## Engineering conventions

- Add calculations in `src/alphalens/services/`, not in Streamlit page code.
- Keep page modules limited to presentation and input orchestration.
- Configure file locations with `ALPHALENS_DATA_DIR` when `data/raw/` is not appropriate.
- Run tests with `pytest`.
# AlphaLens AI
