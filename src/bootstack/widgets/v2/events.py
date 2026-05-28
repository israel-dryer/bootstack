from __future__ import annotations

from enum import Enum


class _EventCategory(str, Enum):
    """String-valued enum so members compare equal to plain strings."""
    pass


class _Widget(_EventCategory):
    CLICK        = "click"
    DOUBLE_CLICK = "double_click"
    RIGHT_CLICK  = "right_click"
    HOVER        = "hover"
    LEAVE        = "leave"
    FOCUS        = "focus"
    BLUR         = "blur"
    RESIZE       = "resize"
    EXPAND       = "expand"
    COLLAPSE     = "collapse"
    ACTIVATE     = "activate"
    DEACTIVATE   = "deactivate"
    DISMISS      = "dismiss"


class _Input(_EventCategory):
    CHANGE   = "change"
    INPUT    = "input"
    SUBMIT   = "submit"
    VALIDATE = "validate"
    VALID    = "valid"
    INVALID  = "invalid"
    COMMIT   = "commit"


class _Selection(_EventCategory):
    SELECT   = "select"
    DESELECT = "deselect"


class _App(_EventCategory):
    THEME_CHANGE    = "theme_change"
    PAGE_MOUNT      = "page_mount"
    PAGE_UNMOUNT    = "page_unmount"
    PAGE_WILL_MOUNT = "page_will_mount"
    PAGE_CHANGE     = "page_change"


class Event:
    """Namespace of v2 event constants.

    Members compare equal to their string values, so
    `widget.on("click", h)` and `widget.on(Event.Widget.CLICK, h)` are
    interchangeable.
    """
    Widget    = _Widget
    Input     = _Input
    Selection = _Selection
    App       = _App


GLOBAL_EVENT_MAP: dict[str, str] = {
    # Widget
    "click":        "<Button-1>",
    "double_click": "<Double-Button-1>",
    "right_click":  "<Button-3>",
    "hover":        "<Enter>",
    "leave":        "<Leave>",
    "focus":        "<FocusIn>",
    "blur":         "<FocusOut>",
    "resize":       "<Configure>",
    # Input
    "input":        "<KeyRelease>",
    "submit":       "<Return>",
    # App-level
    "theme_change": "<<ThemeChanged>>",
}

# Per-class override map. Populated via `register_widget_events`.
_CLASS_EVENT_MAPS: dict[type, dict[str, str]] = {}


def register_widget_events(cls: type, mapping: dict[str, str]) -> None:
    """Attach a class-specific event map to a public widget class.

    Entries map the v2 name (e.g. "select") to the Tk sequence
    (e.g. "<<TreeviewSelect>>"). Class maps take precedence over the global map.
    """
    _CLASS_EVENT_MAPS[cls] = mapping


def resolve_event(public_widget: object, name: str) -> str:
    """Resolve a v2 event name to a Tk sequence.

    Lookup order:
        1. Walk the public widget's MRO; first class-specific match wins.
        2. Global map.
        3. Pass-through literal `<...>` or `<<...>>` strings unchanged.
        4. Raise `UnknownEventError`.
    """
    from bootstack.widgets.v2.exceptions import UnknownEventError

    if name.startswith("<") and name.endswith(">"):
        return name

    for klass in type(public_widget).__mro__:
        cmap = _CLASS_EVENT_MAPS.get(klass)
        if cmap and name in cmap:
            return cmap[name]

    if name in GLOBAL_EVENT_MAP:
        return GLOBAL_EVENT_MAP[name]

    all_known = sorted(
        set(GLOBAL_EVENT_MAP)
        | set().union(*(set(m) for m in _CLASS_EVENT_MAPS.values()))
    )
    raise UnknownEventError(
        f"Unknown event {name!r} on {type(public_widget).__name__}. "
        f"Known events: {all_known}"
    )
