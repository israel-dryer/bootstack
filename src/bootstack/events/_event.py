from __future__ import annotations

from typing import Any


class Event:
    """The object passed to a handler bound with ``on_*()``.

    Carries the context of what happened: the originating widget, any
    application data attached when the event was emitted, and — for pointer and
    keyboard events — where the cursor was and which key was involved.

    The first group of attributes is what handlers normally read. The remaining
    attributes are low-level fields rarely needed in application code.
    """

    # ----- commonly used -----------------------------------------------------

    widget: Any
    """The widget that received the event."""

    data: Any
    """Payload attached when the event was emitted (via ``emit(data=...)``), or
    ``None`` if none was provided. Input widgets attach a small dictionary —
    e.g. a ``change`` event carries ``value``, ``prev_value``, and ``text``."""

    x: int
    """Pointer x position relative to the widget."""

    y: int
    """Pointer y position relative to the widget."""

    x_root: int
    """Pointer x position relative to the screen."""

    y_root: int
    """Pointer y position relative to the screen."""

    char: str
    """The character typed, for keyboard events."""

    keysym: str
    """Symbolic name of the key, for keyboard events (e.g. ``"Return"``)."""

    width: int
    """Widget width at the time of the event."""

    height: int
    """Widget height at the time of the event."""

    delta: int
    """Mouse-wheel delta (positive = scroll up)."""

    # ----- low-level fields (rarely needed) ----------------------------------

    type: Any
    """Low-level event type identifier."""

    state: int
    """Low-level modifier/button state bitmask."""

    keysym_num: int
    """Low-level numeric key code."""

    num: int
    """Low-level mouse button number."""

    serial: int
    """Low-level event serial number."""

    time: int
    """Low-level event timestamp."""

    send_event: bool
    """Low-level flag: whether the event was synthesized."""
