from __future__ import annotations

import tkinter


class Subscription:
    """Handle returned by `widget.on(...)`. Cancels the binding when `.cancel()`
    is called or the context manager exits.

    Idempotent: calling `cancel()` more than once is a no-op.
    """

    __slots__ = ("_widget", "_sequence", "_bind_id", "_cancelled")

    def __init__(self, widget: tkinter.Misc, sequence: str, bind_id: str) -> None:
        self._widget = widget
        self._sequence = sequence
        self._bind_id = bind_id
        self._cancelled = False

    def cancel(self) -> None:
        if self._cancelled:
            return
        self._cancelled = True
        try:
            self._widget.unbind(self._sequence, self._bind_id)
        except tkinter.TclError:
            pass

    def __enter__(self) -> "Subscription":
        return self

    def __exit__(self, exc_type, exc, tb) -> None:
        self.cancel()

    @property
    def cancelled(self) -> bool:
        return self._cancelled
