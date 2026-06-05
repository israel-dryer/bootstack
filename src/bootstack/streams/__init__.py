"""Composable event-stream pipelines for bootstack widgets.

Call an ``on_*()`` shorthand with no handler to get a ``Stream``; chain
operators (``map``, ``filter``, ``debounce``, …) and finish with ``listen()``,
which returns a cancellable ``Handle``.
"""
from bootstack.streams._stream import Handle, Stream

__all__ = [
    "Handle",
    "Stream",
]
