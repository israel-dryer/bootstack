from __future__ import annotations

from typing import Any, Callable, Sequence

from bootstack.widgets.composites.toast import Toast as _InternalToast


class Toast:
    """A temporary notification that appears in a corner of the screen.

    Create a toast, then call `.show()` to display it. Auto-dismisses after
    `duration` milliseconds if set; otherwise stays until closed by the user.

    Usage::

        t = bs.Toast(message="File saved.", accent="success", duration=3000)
        t.show()

    Args:
        title: Header text. Shown larger when there is no message.
        message: Main body text. Shown below the title when both are provided.
        detail: Small muted metadata string (e.g. `"just now"`).
        icon: Icon name string, or an `IconSpec` dict with `name`, `size`, `color`.
        duration: Auto-dismiss delay in milliseconds. `None` = no auto-dismiss.
        accent: Accent token for the container (e.g. `'success'`, `'danger'`).
        show_close_button: Show the × close button. Default `True`.
        actions: Sequence of button kwargs dicts. Each dict is passed to an
            internal Button. Clicking a button dismisses the toast and passes
            the button's dict to `on_dismiss`.
        position: Tkinter geometry offset string (e.g. `'-25-75'`). `None` uses
            platform defaults (bottom-right on Windows/macOS, top-right on Linux).
        play_sound: Play a system bell when shown.
        on_dismiss: Callback invoked on dismiss. Receives the button dict when
            dismissed via a button, or `None` otherwise.
    """

    def __init__(
        self,
        *,
        title: str | None = None,
        message: str | None = None,
        detail: str | None = None,
        icon: str | dict | None = None,
        duration: int | None = None,
        accent: str | None = None,
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
    accent: str | None = None,
    icon: str | dict | None = None,
    on_dismiss: Callable[[Any], None] | None = None,
) -> None:
    """Show a simple notification toast and return immediately.

    Args:
        message: Body text of the notification.
        title: Optional header text.
        duration: Auto-dismiss delay in milliseconds. Default `3000`.
        accent: Accent token (e.g. `'success'`, `'danger'`).
        icon: Icon name or `IconSpec` dict.
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