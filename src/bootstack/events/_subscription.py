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
        """Remove the binding. Safe to call more than once, and on a dead widget.

        `cancelled` afterwards means the removal was carried out as far as this
        handle can carry it — the handler will not be delivered to again through
        this subscription.
        """
        if self._cancelled:
            return
        try:
            self._widget.unbind(self._sequence, self._bind_id)
        except tkinter.TclError:
            # The removal failed partway, which leaves the handler bound and
            # still firing. Swallowed so teardown never fails, but deliberately
            # NOT marked cancelled: claiming otherwise made `cancelled` read
            # True for a live handler (#400). A later cancel() may still succeed.
            #
            # A widget that is merely gone does not reach here — unbind absorbs
            # that case itself, and rightly reports success, since a destroyed
            # widget takes its bindings with it.
            return
        # Includes the case where unbind found nothing to remove: the handler is
        # already unreachable through this widget and sequence, and no retry can
        # change that, so reporting anything but cancelled would be both wrong
        # and permanent. If it is unreachable here because it was bound
        # somewhere else, that is drift rather than a completed cancel, and
        # unbind reports it under BOOTSTACK_DEBUG (#399) — this handle has no
        # way to tell the two apart.
        self._cancelled = True

    def __enter__(self) -> "Subscription":
        return self

    def __exit__(self, exc_type, exc, tb) -> None:
        self.cancel()

    @property
    def cancelled(self) -> bool:
        """Whether `cancel()` has completed for this subscription."""
        return self._cancelled
