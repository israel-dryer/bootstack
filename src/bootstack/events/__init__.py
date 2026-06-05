"""Event objects and subscriptions for bootstack widgets.

An ``Event`` is what a handler bound with ``on_*()`` receives; a ``Subscription``
is the cancellable handle that binding returns.
"""
from bootstack.events._event import Event
from bootstack.events._subscription import Subscription

__all__ = [
    "Event",
    "Subscription",
]
