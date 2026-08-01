"""Reusable presentation helpers for application modules."""

from __future__ import annotations

import streamlit as st


def render_module_placeholder(title: str, description: str) -> None:
    """Render a consistent, informative Phase 1 module landing page."""
    st.title(title)
    st.caption("Phase 1 · Application foundation")
    st.info(description)
    st.markdown("This module is ready for its domain service and validated source-data integration.")
"""Reusable presentation helpers for application modules."""
