"""Application composition root and Streamlit navigation."""

from __future__ import annotations

import logging

import streamlit as st

from alphalens.config import Settings
from alphalens.core.logging import configure_logging
from alphalens.services.source_registry import SourceRegistry
from alphalens.ui import pages


def run() -> None:
    """Configure AlphaLens and render the selected application module."""
    settings = Settings.from_environment()
    logger = configure_logging(settings.log_dir)
    registry = SourceRegistry(settings.data_dir)

    st.set_page_config(page_title=settings.app_name, page_icon="◈", layout="wide")
    st.sidebar.title("◈ AlphaLens AI")
    st.sidebar.caption("Decision intelligence platform")

    module = st.sidebar.radio(
        "Navigation",
        ("Dashboard", "Macro Analysis", "Stock Analysis", "Technical Analysis", "Portfolio", "Risk Management", "Options Analysis", "Backtesting", "Reports", "Settings"),
    )
    try:
        _render_module(module, registry)
    except Exception:  # UI boundary: detailed diagnostics are logged, not exposed.
        logger.exception("Failed to render module: %s", module)
        st.error("The module could not be loaded. Review the application log for details.")


def _render_module(module: str, registry: SourceRegistry) -> None:
    renderers = {
        "Dashboard": lambda: pages.render_dashboard(registry),
        "Macro Analysis": pages.render_macro_analysis,
        "Stock Analysis": pages.render_stock_analysis,
        "Technical Analysis": pages.render_technical_analysis,
        "Portfolio": pages.render_portfolio,
        "Risk Management": pages.render_risk_management,
        "Options Analysis": pages.render_options_analysis,
        "Backtesting": pages.render_backtesting,
        "Reports": pages.render_reports,
        "Settings": lambda: pages.render_settings(registry),
    }
    renderers[module]()
"""Application composition root and Streamlit navigation."""
