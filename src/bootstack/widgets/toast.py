from __future__ import annotations

from typing import Any, Callable, Sequence

from bootstack.widgets._impl.composites.toast import Toast as _InternalToast
from bootstack.widgets.types import AccentToken


class Toast:
    """A temporary notification that appears in a corner of the screen.

    Create a toast, then call ``show()`` to display it. Auto-dismisses after
    ``duration`` milliseconds if set; otherwise stays until the user closes it.

    Args:
        title: Header text. Shown at a larger weight when there is no message.
        message: Main body text shown below the title.
        detail: Small muted metadata string (e.g. ``'just now'``). Displayed
            on the right side of the header row.
        icon: Bootstrap Icons name (e.g. ``'check-circle'``) or an icon spec
            dict with keys ``name`` (str), ``size`` (int), and ``color`` (str).
        duration: Auto-dismiss delay in milliseconds. ``None`` keeps the toast
            visible until the user closes it manually. Defaults to ``None``.
        accent: Semantic color accent. One of ``'default'``, ``'primary'``,
            ``'secondary'``, ``'info'``, ``'success'``, ``'warning'``,
            ``'danger'``, ``'muted'``. Defaults to the theme's default surface.
        show_close_button: Show the × close button. Defaults to ``True``.
        actions: Sequence of button kwargs dicts. Each dict is passed to an
            internal Button; clicking a button dismisses the toast and passes
            the dict to ``on_dismiss``.
        position: Tkinter geometry string (e.g. ``'-25-75'`` for 25 px from
            the right edge and 75 px from the bottom). ``None`` uses platform
            defaults (bottom-right on Windows/macOS, top-right on Linux).
        play_sound: Play a system bell when the toast appears. Defaults to
            ``False``.
        on_dismiss: Callback fired on dismiss. Receives the button dict when
            dismissed via an action button, or ``None`` otherwise.
    """

    def __init__(
        self,
        *,
        title: str | None = None,
        message: str | None = None,
        detail: str | None = None,
        icon: str | dict | None = None,
        duration: int | None = None,
        accent: AccentToken | None = None,
        show_close_button: bool = True,
        actions: Sequence[dict[str, Any]] | None = None,
        position: str | None = None,
        play_sound: bool = False,
        on_dismiss: Callable[[Any], None] | None = None,
    ) -> None:
        self._internal = _InternalToast(
            title=title,
            message=message,
            memo=detail,
            icon=icon,
            duration=duration,
            accent=accent,
            show_close_button=show_close_button,
            buttons=actions,
            position=position,
            alert=play_sound,
            on_dismissed=on_dismiss,
        )

    def show(self) -> None:
        """Display the toast."""
        self._internal.show()

    def hide(self) -> None:
        """Dismiss the toast immediately."""
        self._internal.hide()

    def destroy(self) -> None:
        """Destroy the toast window and free resources."""
        self._internal.destroy()


def toast(
    message: str,
    *,
    title: str | None = None,
    duration: int = 3000,
    accent: AccentToken | None = None,
    icon: str | dict | None = None,
    on_dismiss: Callable[[Any], None] | None = None,
) -> None:
    """Show a simple notification toast and return immediately.

    Args:
        message: Body text of the notification.
        title: Optional header text.
        duration: Auto-dismiss delay in milliseconds. Defaults to ``3000``.
        accent: Semantic color accent. One of ``'default'``, ``'primary'``,
            ``'secondary'``, ``'info'``, ``'success'``, ``'warning'``,
            ``'danger'``, ``'muted'``.
        icon: Bootstrap Icons name or icon spec dict with ``name``, ``size``,
            and ``color`` keys.
        on_dismiss: Called when the toast is dismissed.
    """
    t = Toast(
        message=message,
        title=title,
        duration=duration,
        accent=accent,
        icon=icon,
        on_dismiss=on_dismiss,
    )
    t.show()