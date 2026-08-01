# AlphaLens AI 🚀📈

**AlphaLens AI** is an enterprise-grade, production-ready Streamlit application engineered for quantitative financial research, macro market analysis, stock screening, options Greeks analytics, portfolio optimization, and Value-at-Risk (VaR) risk management.

---

## 🏗️ Architecture Overview

AlphaLens AI strictly enforces a **Clean Architecture** pattern, decoupling business calculations and quantitative engines (`core/`) from presentation components (`ui/`).

```
Trading Strategy/
├── .github/
│   └── workflows/
│       └── ci.yml              # GitHub Actions Continuous Integration
├── config/                     # Application configurations & logging
│   ├── settings.py             # Global constants & file paths
│   └── logging_config.py       # Enterprise logging configuration
├── core/                       # Pure Business Logic Layer (No UI code)
│   ├── macro.py                # Economic regime models
│   ├── stock.py                # Fundamental equity valuation & metrics
│   ├── technical.py            # Technical analysis & indicator engines
│   ├── portfolio.py            # Markowitz & Risk-Parity allocation
│   ├── risk.py                 # Parametric/Historical VaR & Stress testing
│   ├── options.py              # Black-Scholes & Options Greeks pricing
│   ├── backtesting.py          # Vectorized quantitative backtest engine
│   └── reports.py              # Report generation engine
├── ui/                         # Streamlit UI & Presentation Layer
│   ├── components/             # Reusable UI widgets & sidebar navigation
│   │   ├── sidebar.py          # Navigation controller
│   │   └── widgets.py          # Financial metric cards & alert boxes
│   ├── styles/
│   │   └── theme.css           # Premium responsive Dark UI CSS
│   └── pages/                  # Modular Page Renderers
│       ├── dashboard.py        # Executive Dashboard Page
│       ├── macro_analysis.py   # Macroeconomic Analysis Page
│       ├── stock_analysis.py   # Equity Analysis & Screener Page
│       ├── technical_analysis.py # Technical Analysis Page
│       ├── portfolio.py        # Portfolio Management Page
│       ├── risk_management.py  # Risk Management & VaR Page
│       ├── options_analysis.py # Derivatives & Options Page
│       ├── backtesting.py      # Backtest & Strategy Lab Page
│       ├── reports.py          # Executive Reports & Exports Page
│       └── settings.py         # Application Settings Page
├── utils/                      # Helper & Data utilities
│   ├── excel_loader.py         # Ingestion layer for strategy documents/Excel
│   └── formatters.py           # Financial formatting helpers
├── app.py                      # Application entry point & router
├── requirements.txt            # Python dependencies
└── README.md                   # Project documentation
```

---

## ⚡ Quick Start

### 1. Prerequisites
- Python 3.10 or higher
- Virtual environment (`venv` or `conda`)

### 2. Installation & Setup
```bash
# Clone the repository
git clone https://github.com/your-username/alphalens-ai.git
cd alphalens-ai

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install production dependencies
pip install -r requirements.txt
```

### 3. Launch the Application
```bash
streamlit run app.py
```

---

## 🌟 Key Features

1. **Executive Dashboard**: Real-time overview of portfolio performance, market regime, risk metrics, and top strategy alerts.
2. **Macroeconomic Analysis**: Macro regime identification, interest rate tracking, inflation indicators, and yield curve visualization.
3. **Stock Analysis**: Equity fundamental screening, valuation metrics (P/E, EV/EBITDA, ROE), and balance sheet health checks.
4. **Technical Analysis**: Multi-timeframe indicator computation (RSI, MACD, Moving Averages, Bollinger Bands, ATR).
5. **Portfolio Allocation**: Mean-variance optimization (Sharpe ratio maximization, Minimum Volatility) & Risk Parity.
6. **Risk Management & VaR**: Parametric Value-at-Risk (VaR), Historical VaR, Conditional VaR (Expected Shortfall), and Stress Testing scenarios.
7. **Options & Derivatives**: Black-Scholes pricing, Option Greeks (Delta, Gamma, Vega, Theta, Rho), and strategy payoff diagrams.
8. **Quantitative Backtesting**: Vectorized strategy execution, drawdowns analysis, win rate, Profit Factor, and Sharpe ratio evaluation.
9. **Automated Reporting**: Export comprehensive executive reports in structured formats.
10. **Customizable Settings**: Configurable strategy parameters, risk thresholds, and visual theme settings.

---

## 💻 Tech Stack & Design

- **Language**: Python 3.10+
- **Frontend Framework**: Streamlit
- **Visualization**: Plotly, Matplotlib
- **Quantitative Engine**: NumPy, Pandas, SciPy, Scikit-learn
- **Data Ingestion**: OpenPyXL, Python-docx
- **UI Theme**: Custom Responsive Dark Mode CSS (`ui/styles/theme.css`)

---

## 📜 License

Distributed under the MIT License. See `LICENSE` for more information.
