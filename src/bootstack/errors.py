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


class InvalidChoiceError(BootstackError, ValueError):
    """Raised when a keyword argument is given a value outside its valid set.

    Applies to arguments that name a behavior mode drawn from a closed set,
    such as `selection_mode` or `scrollbars`. The message names the value that
    was rejected and lists the values that are accepted.

    Also a `ValueError`, so either `BootstackError` or `ValueError` catches it.
    """


class NavigationError(BootstackError):
    """Raised when a navigation operation references a wrong key.

    Examples: adding a page, tab, or workspace whose key already exists, or
    selecting, looking up, or removing one whose key does not exist.
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
    "InvalidChoiceError",
    "NavigationError",
    "ParentResolutionError",
    "SerializationError",
    "StyleBuilderError",
    "ThemeError",
    "UnknownEventError",
]
