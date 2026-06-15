from __future__ import annotations

# These are defined in the public `bootstack.errors` home and re-exported here
# for the internal call sites that import from `bootstack._core`.
from bootstack.errors import (
    NavigationError,
    StyleBuilderError,
    ThemeError,
)


class ConfigurationWarning(Warning):
    """Issued when a widget receives a deprecated or questionable configuration option.

    Examples: supplying an unsupported value for a configuration key, or
    passing mutually exclusive options.
    """


__all__ = [
    "ConfigurationWarning",
    "NavigationError",
    "StyleBuilderError",
    "ThemeError",
]