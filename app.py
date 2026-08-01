"""Streamlit entry point for AlphaLens AI.

The explicit path bootstrap keeps ``streamlit run app.py`` compatible with
Streamlit Community Cloud, which runs the repository entry point without first
installing the local ``src`` package.
"""

from __future__ import annotations

import sys
from pathlib import Path


SRC_DIR = Path(__file__).resolve().parent / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

try:
    from alphalens.ui.app_shell import run
except ModuleNotFoundError as error:
    # A Streamlit Cloud deployment can be configured with only app.py as its
    # repository entry point. Preserve a functional Phase 1 shell when the
    # optional modular package has not been included in that deployment.
    if error.name not in {"alphalens", "alphalens.ui", "alphalens.ui.app_shell"}:
        raise

    import streamlit as st

    _MODULES: dict[str, str] = {
        "Dashboard": "Research-source readiness and platform overview.",
        "Macro Analysis": "Economic regime, market context, and cross-asset signals.",
        "Stock Analysis": "Fundamental, valuation, and company-level research.",
        "Technical Analysis": "Trend, momentum, volatility, and execution signals.",
        "Portfolio": "Portfolio construction, allocation, and attribution.",
        "Risk Management": "Exposure controls and value-at-risk monitoring.",
        "Options Analysis": "Options structures, payoff analysis, and derivatives risk.",
        "Backtesting": "Historical strategy evaluation with reproducible assumptions.",
        "Reports": "Decision-ready investment and trading reports.",
        "Settings": "Application and source-data configuration.",
    }

    def run() -> None:
        """Render a deployment-safe Phase 1 application shell."""
        st.set_page_config(page_title="AlphaLens AI", page_icon="◈", layout="wide")
        st.sidebar.title("◈ AlphaLens AI")
        st.sidebar.caption("Decision intelligence platform")
        module = st.sidebar.radio("Navigation", tuple(_MODULES))

        st.title("AlphaLens AI" if module == "Dashboard" else module)
        st.caption("Institutional Trading & Investment Decision Platform · Phase 1")
        st.info(_MODULES[module])
        if module == "Dashboard":
            left, right = st.columns(2)
            left.metric("Registered research sources", 10)
            right.metric("Application modules", len(_MODULES))
        st.write("This module is ready for validated source-data and domain-service integration.")


if __name__ == "__main__":
    run()
"""Streamlit entry point for AlphaLens AI."""
