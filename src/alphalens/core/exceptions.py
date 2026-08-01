"""Application-specific error types."""


class AlphaLensError(Exception):
    """Base class for errors safe to surface to the application layer."""


class SourceDataError(AlphaLensError):
    """Raised when a required source-data condition is not met."""


class MarketDataError(AlphaLensError):
    """Raised when a market-data provider cannot supply validated data."""
"""Application-specific error types."""
