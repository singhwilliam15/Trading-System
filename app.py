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

from alphalens.ui.app_shell import run


if __name__ == "__main__":
    run()
"""Streamlit entry point for AlphaLens AI."""
