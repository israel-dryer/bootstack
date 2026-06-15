"""Transient message surfaces: toast, notification, and snackbar.

Three opinionated, single-purpose facades over the shared internal toast engine:

- `toast()` — a passive, auto-dismissing message that floats in a screen corner
  and stacks. Fire-and-forget.
- `Notification` — a persistent corner message with a close button; the user
  decides when it goes away. Stacks alongside toasts.
- `Snackbar` / `snackbar()` — a transient message bound to the app window's
  bottom edge with an optional single action (e.g. *Undo*). Only one shows at a
  time; a new one replaces it.
"""
from __future__ import annotations

from typing import Any, Callable

from bootstack.widgets._impl.composites.toast import Toast as _InternalToast
from bootstack.widgets._impl.composites.toast_stack import get_toast_manager
from bootstack.widgets.types import AccentToken, Icon, ToastCorner, SnackbarAlign

_TOAST_DEFAULT_DURATION = 4000
_SNACKBAR_DEFAULT_DURATION = 5000


def _windowing_system() -> str:
    """The active Tk windowing system (`'win32'`, `'aqua'`, or `'x11'`)."""
    from bootstack._runtime.app import get_default_root

    root = get_default_root()
    if root is not None:
        try:
            return root.tk.call("tk", "windowingsystem")
        except Exception:
            pass
    return "win32"


def _resolve_corner(corner: ToastCorner | None, *, persistent: bool) -> ToastCorner:
    """Resolve the default corner for a toast or notification.

    Notifications default to the top-right everywhere. Passive toasts default to
    the bottom-right on Windows and macOS, and the top-right on Linux (X11),
    matching each platform's native notification placement.
    """
    if corner is not None:
        return corner
    if persistent:
        return "top-right"
    return "bottom-right" if _windowing_system() in ("win32", "aqua") else "top-right"


# ---------------------------------------------------------------------------
# toast() — passive, auto-dismiss, stacks in a screen corner
# ---------------------------------------------------------------------------

def toast(
    message: str,
    *,
    title: str | None = None,
    corner: ToastCorner | None = None,
    duration: int = _TOAST_DEFAULT_DURATION,
    accent: AccentToken | str | None = None,
    icon: Icon | None = None,
    on_dismiss: Callable[[], Any] | None = None,
) -> None:
    """Show a passive toast that dismisses itself, and return immediately.

    A toast is the lightest notification — "the app telling you something" with
    no demand for a response. It floats in a corner of the monitor the app
    window is on, stacks below any toasts already there, and fades after
    `duration`. For a message the user must dismiss, use `Notification`; for one
    tied to the window with an action, use `Snackbar`.

    Args:
        message: Body text of the toast.
        title: Optional header shown above the message.
        corner: Screen corner to anchor to — `'top-left'`, `'top-right'`,
            `'bottom-left'`, or `'bottom-right'`. Defaults to the bottom-right
            (top-right on Linux).
        duration: Time on screen in milliseconds before it auto-dismisses.
            Defaults to `4000`.
        accent: Semantic color accent (e.g. `'success'`, `'danger'`). Defaults
            to a neutral surface.
        icon: Optional Bootstrap Icons name (e.g. `'check-circle'`) or an icon
            spec dict with `name`, `size`, and `color`, shown before the message.
            No icon is shown unless given.
        on_dismiss: Called with no arguments when the toast dismisses.
    """
    manager = get_toast_manager()
    resolved = _resolve_corner(corner, persistent=False)

    engine = _InternalToast(
        title=title,
        message=message,
        icon=icon,
        accent=accent,
        duration=duration,
        show_close_button=False,
        place=manager.corner_placer(resolved),
    )

    def _on_dismissed(_data: Any) -> None:
        manager.remove(resolved, engine._toplevel)
        if on_dismiss is not None:
            on_dismiss()

    engine.configure(on_dismissed=_on_dismissed)
    engine.show()


# ---------------------------------------------------------------------------
# Notification — persistent, close button, stacks in a screen corner
# ---------------------------------------------------------------------------

class Notification:
    """A persistent corner message the user closes themselves.

    Like a toast, a notification floats in a screen corner and stacks — but it
    does not auto-dismiss. It carries a close button and stays until the user
    closes it or your code calls `dismiss()`. Use it for information that should
    persist (a finished background job, an available update) rather than flash
    by. Build it, then call `show()`.

    Notifications are message-only — for a response, use a `Snackbar` action or
    a dialog.

    Args:
        title: Header text — the notification's headline.
        message: Body text shown below the title.
        detail: Small muted metadata shown in the header (e.g. `'just now'`).
        corner: Screen corner to anchor to — `'top-left'`, `'top-right'`,
            `'bottom-left'`, or `'bottom-right'`. Defaults to the top-right.
        accent: Semantic color accent. Defaults to a neutral surface.
        icon: Optional Bootstrap Icons name or an icon spec dict, shown before
            the title. No icon is shown unless given.
        on_dismiss: Called with no arguments when the notification closes.
    """

    def __init__(
        self,
        title: str | None = None,
        *,
        message: str | None = None,
        detail: str | None = None,
        corner: ToastCorner | None = None,
        accent: AccentToken | str | None = None,
        icon: Icon | None = None,
        on_dismiss: Callable[[], Any] | None = None,
    ) -> None:
        self._title = title
        self._message = message
        self._detail = detail
        self._corner = corner
        self._accent = accent
        self._icon = icon
        self._on_dismiss = on_dismiss
        self._engine: _InternalToast | None = None

    def show(self) -> "Notification":
        """Display the notification. Returns `self` for chaining."""
        manager = get_toast_manager()
        resolved = _resolve_corner(self._corner, persistent=True)

        engine = _InternalToast(
            title=self._title,
            message=self._message,
            memo=self._detail,
            icon=self._icon,
            accent=self._accent,
            duration=None,
            show_close_button=True,
            place=manager.corner_placer(resolved),
        )

        def _on_dismissed(_data: Any) -> None:
            manager.remove(resolved, engine._toplevel)
            if self._on_dismiss is not None:
                self._on_dismiss()

        engine.configure(on_dismissed=_on_dismissed)
        self._engine = engine
        engine.show()
        return self

    def dismiss(self) -> None:
        """Close the notification immediately."""
        if self._engine is not None:
            self._engine.hide()


# ---------------------------------------------------------------------------
# Snackbar — transient, one action, anchored to the window bottom edge
# ---------------------------------------------------------------------------

class Snackbar:
    """A transient message at the app window's bottom edge with one action.

    A snackbar belongs to the app, not the screen: it slides up from the bottom
    of the window and moves with it. It is for brief, in-context feedback that
    may offer a single response — the classic *"Message archived. [Undo]"*. Only
    one snackbar shows at a time; showing another replaces it. Build it, then
    call `show()`.

    Args:
        message: Body text of the snackbar.
        action: Label for the optional action button (e.g. `'Undo'`). Omit for
            a message with no action.
        on_action: Called with no arguments when the action button is pressed.
            The snackbar dismisses afterward.
        align: Horizontal placement along the window's bottom edge — `'left'`,
            `'center'`, or `'right'`. Defaults to `'center'`.
        duration: Time on screen in milliseconds before it auto-dismisses.
            Defaults to `5000`.
        accent: Semantic color accent for the action button (the surface stays
            neutral — severity coloring belongs to `toast`/`Notification`).
            Defaults to `'primary'`. No effect without an `action`.
        on_dismiss: Called with no arguments when the snackbar dismisses (whether
            by timeout, the action, or `dismiss()`).
    """

    def __init__(
        self,
        message: str,
        *,
        action: str | None = None,
        on_action: Callable[[], Any] | None = None,
        align: SnackbarAlign = "center",
        duration: int = _SNACKBAR_DEFAULT_DURATION,
        accent: AccentToken | str | None = None,
        on_dismiss: Callable[[], Any] | None = None,
    ) -> None:
        self._message = message
        self._action = action
        self._on_action = on_action
        self._align = align
        self._duration = duration
        self._accent = accent
        self._on_dismiss = on_dismiss
        self._engine: _InternalToast | None = None

    def show(self) -> "Snackbar":
        """Display the snackbar, replacing any current one. Returns `self`."""
        manager = get_toast_manager()

        buttons = None
        if self._action is not None:
            buttons = [{
                "text": self._action,
                "command": self._on_action,
                "variant": "ghost",
                "accent": self._accent or "primary",
            }]

        # Neutral surface (no accent) and no icon — a snackbar is in-app action
        # feedback, not a severity message. The accent rides only on the action.
        engine = _InternalToast(
            message=self._message,
            duration=self._duration,
            show_close_button=False,
            buttons=buttons,
            place=manager.snackbar_placer(self._align),
        )

        def _on_dismissed(_data: Any) -> None:
            manager.clear_snackbar(engine._toplevel)
            if self._on_dismiss is not None:
                self._on_dismiss()

        engine.configure(on_dismissed=_on_dismissed)
        self._engine = engine
        engine.show()
        return self

    def dismiss(self) -> None:
        """Dismiss the snackbar immediately."""
        if self._engine is not None:
            self._engine.hide()


def snackbar(
    message: str,
    *,
    action: str | None = None,
    on_action: Callable[[], Any] | None = None,
    align: SnackbarAlign = "center",
    duration: int = _SNACKBAR_DEFAULT_DURATION,
    accent: AccentToken | str | None = None,
    on_dismiss: Callable[[], Any] | None = None,
) -> None:
    """Show a snackbar at the window's bottom edge, and return immediately.

    The one-line form of `Snackbar` — see it for the full description. Use the
    class when you need a handle to `dismiss()` early.

    Args:
        message: Body text of the snackbar.
        action: Label for the optional action button (e.g. `'Undo'`).
        on_action: Called with no arguments when the action is pressed.
        align: Bottom-edge alignment — `'left'`, `'center'`, or `'right'`.
            Defaults to `'center'`.
        duration: Time on screen in milliseconds. Defaults to `5000`.
        accent: Semantic color accent for the action button (the surface stays
            neutral). No effect without an `action`.
        on_dismiss: Called with no arguments when the snackbar dismisses.
    """
    Snackbar(
        message,
        action=action,
        on_action=on_action,
        align=align,
        duration=duration,
        accent=accent,
        on_dismiss=on_dismiss,
    ).show()
