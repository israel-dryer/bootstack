class BootstackV2Error(Exception):
    """Base class for all v2 public API errors."""


class UnknownEventError(BootstackV2Error):
    """Raised by `widget.on(name, ...)` when `name` cannot be resolved."""


class ParentResolutionError(BootstackV2Error):
    """Raised when a widget cannot resolve its parent."""
