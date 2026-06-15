"""Public exception types raised by the bootstack API."""


class BootstackError(Exception):
    """Base class for all public API errors."""


class UnknownEventError(BootstackError):
    """Raised by `widget.on(name, ...)` when `name` cannot be resolved."""


class ParentResolutionError(BootstackError):
    """Raised when a widget cannot resolve its parent."""


class DuplicateIdError(BootstackError):
    """Raised when a data source receives a record whose id already exists.

    Record ids must be unique — they identify rows for selection and events.
    """


class SerializationError(BootstackError):
    """Raised when a file-backed store or data source receives a value it
    cannot persist.

    File- and database-backed sources carry non-scalar fields as JSON, and
    `Store` persists its values as JSON, so values must be JSON-serializable
    (scalars, lists, dicts). Store arbitrary Python objects in an in-memory
    source instead.
    """


class NavigationError(BootstackError):
    """Raised when a navigation operation fails.

    Examples: adding a page or tab whose key already exists, navigating to a
    key that does not exist, or supplying an out-of-range index.
    """


class ThemeError(BootstackError):
    """Raised when a theme-related operation fails.

    Examples: requesting an unknown theme name, or loading a malformed theme
    definition.
    """


class StyleBuilderError(BootstackError):
    """Raised when a widget style cannot be built.

    Examples: an unsupported `variant` for a widget, or a missing required
    theme color token.
    """


__all__ = [
    "BootstackError",
    "DuplicateIdError",
    "NavigationError",
    "ParentResolutionError",
    "SerializationError",
    "StyleBuilderError",
    "ThemeError",
    "UnknownEventError",
]
