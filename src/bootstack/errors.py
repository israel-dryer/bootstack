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


__all__ = [
    "BootstackError",
    "DuplicateIdError",
    "ParentResolutionError",
    "UnknownEventError",
]
