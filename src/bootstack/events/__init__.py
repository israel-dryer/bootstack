"""Event objects, typed payloads, and subscriptions for bootstack widgets.

This package is the single catalog of every framework event shape:

- :class:`Event` — the curated object handed to native/context handlers
  (click, hover, focus, resize, key, scroll).
- The payload dataclasses (:class:`ChangeEvent`, :class:`InputEvent`, …) — the
  *unpacked* objects handed to data-carrying handlers (``on_change``,
  ``on_input``, ``on_select``, …).
- :class:`Subscription` — the cancellable handle that binding returns.
"""
from bootstack.events._event import Event
from bootstack.events._payloads import (
    ChangeEvent,
    InputEvent,
    ValidationEvent,
)
from bootstack.events._subscription import Subscription

__all__ = [
    "Event",
    "Subscription",
    # Payloads
    "ChangeEvent",
    "InputEvent",
    "ValidationEvent",
]
