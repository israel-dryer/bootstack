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


__all__ = [
    "BootstackError",
    "DuplicateIdError",
    "ParentResolutionError",
    "SerializationError",
    "UnknownEventError",
]
