from __future__ import annotations

import sys
from dataclasses import dataclass
from typing import Any

# Platform detection for modifier decoding. Tk reports the modifier bitmask in
# the event `state` field using the X11 ButtonState convention, but which bit
# the Alt/Meta keys land on differs per platform (see the Tk bind(n) manual).
_IS_MAC = sys.platform == "darwin"
_IS_WIN = sys.platform == "win32"

# X11 ButtonState bit masks (the values Tk reports in `state`).
_SHIFT = 0x0001
_CONTROL = 0x0004
_MOD1 = 0x0008  # X11: Alt;       macOS: Command
_MOD2 = 0x0010  # X11: Num Lock;  macOS: Option (Alt)
_MOD4 = 0x0040  # X11: Super
_ALT_WIN = 0x20000  # Windows reports the Alt key on this bit


def _as_int(value: Any) -> int:
    """Coerce a Tk substitution value to int, tolerating `'??'` and `''`."""
    try:
        return int(value)
    except (TypeError, ValueError):
        return 0


@dataclass(frozen=True, slots=True)
class Event:
    """The object a handler receives for native and context events.

    Native events carry no application payload — pointer clicks, hover, focus,
    blur, resize, key presses, and scrolling. For those, the handler bound with
    `on_*()` receives this curated `Event`: where the pointer was, the size
    of the widget, which modifier keys were held, and (for keyboard events) which
    key. Events that *do* carry data — `change`, `input`, `select` — hand
    the handler a typed payload object instead (see the rest of this module).

    The fields are deliberately modern: modifier keys are plain booleans
    (`ctrl`, `shift`, `alt`, `meta`) and the key is a clean `key`
    string, with none of the low-level bitmask or serial-number plumbing of the
    underlying toolkit.
    """

    widget: Any = None
    """The widget that received the event."""

    x: int = 0
    """Pointer x position relative to the widget."""

    y: int = 0
    """Pointer y position relative to the widget."""

    x_root: int = 0
    """Pointer x position relative to the screen."""

    y_root: int = 0
    """Pointer y position relative to the screen."""

    width: int = 0
    """Widget width at the time of the event."""

    height: int = 0
    """Widget height at the time of the event."""

    delta: int = 0
    """Scroll-wheel delta (positive = scroll up)."""

    ctrl: bool = False
    """Whether the Control key was held."""

    shift: bool = False
    """Whether the Shift key was held."""

    alt: bool = False
    """Whether the Alt (Option on macOS) key was held."""

    meta: bool = False
    """Whether the Meta key was held (Command on macOS, Super on Linux)."""

    key: str = ""
    """Symbolic name of the key, for keyboard events (e.g. `"Return"`).
    Empty for non-keyboard events."""

    char: str = ""
    """The character typed, for keyboard events. Empty if the key produced no
    character."""

    time: int = 0
    """Event timestamp in milliseconds — useful for manual debounce/throttle."""

    @classmethod
    def _from_tk(cls, e: Any) -> "Event":
        """Build a curated `Event` from a raw toolkit event object.

        Decodes the modifier bitmask into booleans (platform-aware) and cleans
        up the key/char fields. Internal — called by the public `on_*` layer.
        """
        state = _as_int(getattr(e, "state", 0))
        if _IS_MAC:
            alt = bool(state & _MOD2)
            meta = bool(state & _MOD1)
        elif _IS_WIN:
            alt = bool(state & _ALT_WIN)
            meta = False
        else:
            alt = bool(state & _MOD1)
            meta = bool(state & _MOD4)

        key = getattr(e, "keysym", "") or ""
        if key == "??":
            key = ""
        char = getattr(e, "char", "") or ""
        if char == "??":
            char = ""

        return cls(
            widget=getattr(e, "widget", None),
            x=_as_int(getattr(e, "x", 0)),
            y=_as_int(getattr(e, "y", 0)),
            x_root=_as_int(getattr(e, "x_root", 0)),
            y_root=_as_int(getattr(e, "y_root", 0)),
            width=_as_int(getattr(e, "width", 0)),
            height=_as_int(getattr(e, "height", 0)),
            delta=_as_int(getattr(e, "delta", 0)),
            ctrl=bool(state & _CONTROL),
            shift=bool(state & _SHIFT),
            alt=alt,
            meta=meta,
            key=key,
            char=char,
            time=_as_int(getattr(e, "time", 0)),
        )
