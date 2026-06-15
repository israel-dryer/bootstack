"""System clipboard helpers.

The clipboard is global to the running application, so these are module-level
functions rather than per-widget methods. They operate on the current `App`'s
clipboard, so **an `App` must exist when they are called** (i.e. call them from
within your app's runtime, not at import time).

    from bootstack.clipboard import get_clipboard, set_clipboard

    set_clipboard("hello")
    text = get_clipboard()

Platform note: on Linux/X11 the clipboard is owned by the running process, so its
contents are cleared when the `App` exits unless a system clipboard manager is
running. On Windows and macOS the operating system owns the clipboard, so contents
persist after the app closes.
"""

from __future__ import annotations

from bootstack._runtime.app import get_current_app

__all__ = ["get_clipboard", "set_clipboard"]


def set_clipboard(text: str) -> None:
    """Replace the system clipboard contents with `text`.

    Args:
        text: The text to place on the clipboard.

    Raises:
        RuntimeError: If called when no `App` is running.
    """
    get_current_app().clipboard_set(text)


def get_clipboard() -> str:
    """Return the current text contents of the system clipboard.

    Returns:
        The clipboard text, or an empty string when the clipboard is empty,
        holds non-text data, or no `App` is running.
    """
    try:
        return get_current_app().clipboard_get()
    except Exception:
        return ""