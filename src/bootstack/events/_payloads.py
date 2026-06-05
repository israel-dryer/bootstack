"""Typed event payloads — the catalog of every data-carrying framework event.

When a widget event carries application data (a new value, the typed text, a
validation result, a selected row), the handler bound with ``on_*()`` receives
one of the frozen dataclasses defined here, *unpacked* — the handler argument
IS the payload::

    field.on_change(lambda e: print(e.value, e.prev_value))
    field.on_input(lambda e: print(e.text))

Events that carry no payload (click, hover, focus, resize, key, scroll) instead
hand the handler a curated :class:`~bootstack.events.Event`.

Every payload is ``@dataclass(frozen=True, slots=True)`` so attributes are
discoverable by editors and immutable in handlers.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

# ---------------------------------------------------------------------------
# Field / input family
# ---------------------------------------------------------------------------


@dataclass(frozen=True, slots=True)
class InputEvent:
    """Fires on every keystroke, before the value is committed.

    Use it for live feedback — character counts, as-you-type filtering. To react
    only once editing settles, use ``on_change`` instead.
    """

    text: str = ""
    """The current raw text in the field."""


@dataclass(frozen=True, slots=True)
class ChangeEvent:
    """Fires when a field's value is committed (on blur or Enter)."""

    value: Any = None
    """The committed, parsed value."""

    prev_value: Any = None
    """The value before this change."""

    text: str = ""
    """The raw display text behind the value."""


@dataclass(frozen=True, slots=True)
class ValidationEvent:
    """Fires after validation runs — ``valid``, ``invalid``, and ``validate``."""

    value: Any = None
    """The value that was validated."""

    is_valid: bool = True
    """Whether validation passed."""

    message: str = ""
    """The failure message, or an empty string when valid."""
