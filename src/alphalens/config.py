"""Application configuration loaded once at startup."""

from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True, slots=True)
class Settings:
    """Resolved runtime paths and application metadata."""

    project_root: Path
    data_dir: Path
    log_dir: Path
    app_name: str = "AlphaLens AI"

    @classmethod
    def from_environment(cls) -> "Settings":
        project_root = Path(__file__).resolve().parents[2]
        data_dir = Path(os.getenv("ALPHALENS_DATA_DIR", project_root / "data" / "raw"))
        log_dir = Path(os.getenv("ALPHALENS_LOG_DIR", project_root / "logs"))
        return cls(project_root=project_root, data_dir=data_dir, log_dir=log_dir)
"""Application configuration loaded once at startup."""
