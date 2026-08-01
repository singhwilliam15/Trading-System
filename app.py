"""
AlphaLens AI - Main Streamlit Application Entrypoint.
Decoupled Modular Architecture Routing UI Renderers and Core Quantitative Engines.
"""

import streamlit as st
from pathlib import Path
from config.settings import settings
from config.logging_config import logger
from ui.components.sidebar import render_sidebar
from ui.pages import (
    render_dashboard_page,
    render_macro_page,
    render_stock_page,
    render_technical_page,
    render_portfolio_page,
    render_risk_page,
    render_options_page,
    render_backtesting_page,
    render_reports_page,
    render_settings_page,
)

def load_css() -> None:
    """Loads external theme CSS stylesheet."""
    css_path = Path(__file__).parent / "ui" / "styles" / "theme.css"
    if css_path.exists():
        with open(css_path, "r", encoding="utf-8") as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
    else:
        logger.warning(f"CSS stylesheet not found at: {css_path}")

def main() -> None:
    """Main application launcher and modular router."""
    st.set_page_config(
        page_title=settings.APP_NAME,
        page_icon="⚡",
        layout="wide",
        initial_sidebar_state="expanded"
    )

    load_css()
    logger.info("AlphaLens AI Application Initialized.")

    selected_page_key = render_sidebar()

    page_router = {
        "dashboard": render_dashboard_page,
        "macro": render_macro_page,
        "stock": render_stock_page,
        "technical": render_technical_page,
        "portfolio": render_portfolio_page,
        "risk": render_risk_page,
        "options": render_options_page,
        "backtesting": render_backtesting_page,
        "reports": render_reports_page,
        "settings": render_settings_page,
    }

    render_func = page_router.get(selected_page_key, render_dashboard_page)
    render_func()

if __name__ == "__main__":
    main()
