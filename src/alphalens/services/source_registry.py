"""Services for locating and reporting supplied research sources."""

from __future__ import annotations

from pathlib import Path

from alphalens.domain.source_catalog import SOURCE_CATALOG, SourceDefinition


class SourceRegistry:
    """Provides a filesystem-aware view of the approved source catalogue."""

    def __init__(self, data_dir: Path) -> None:
        self._data_dir = data_dir

    @property
    def data_dir(self) -> Path:
        """Return the configured directory containing raw source material."""
        return self._data_dir

    @property
    def sources(self) -> tuple[SourceDefinition, ...]:
        return SOURCE_CATALOG

    def available_sources(self) -> tuple[SourceDefinition, ...]:
        """Return catalogue entries whose expected file exists locally."""
        return tuple(source for source in self.sources if (self._data_dir / source.filename).is_file())

    def missing_sources(self) -> tuple[SourceDefinition, ...]:
        """Return catalogue entries not yet available under the configured data directory."""
        return tuple(source for source in self.sources if not (self._data_dir / source.filename).is_file())

    def readiness_ratio(self) -> float:
        """Return the share of registered data sources presently available."""
        return len(self.available_sources()) / len(self.sources)
"""Services for locating and reporting supplied research sources."""
