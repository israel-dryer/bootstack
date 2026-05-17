from __future__ import annotations

from typing import Any, TYPE_CHECKING

from typing_extensions import TypedDict

if TYPE_CHECKING:
    from typing_extensions import Unpack


class ClipboardKwargs(TypedDict, total=False):
    """Keyword options accepted by clipboard operations."""
    displayof: Any
    """Widget or window whose display to target. Omit for the main application display."""
    type: str
    """Clipboard type name (e.g., `'STRING'`, `'UTF8_STRING'`). Platform-dependent."""
    format: str
    """Data format for representing selection data to the X server (e.g., `'STRING'`). Platform-dependent."""


class ClipboardMixin:
    """Clipboard helpers (clipboard).

    Tk's `clipboard` command provides access to the system (or Tk-managed) clipboard.
    Tkinter exposes this via the `clipboard_*` methods.

    Notes:
        - Clipboard behavior can vary by platform and window system.
        - Most apps only need text clipboard operations (clear/append/get).
        - For advanced cases (multiple clipboard types, non-text formats), Tk supports
          additional options passed via `ClipboardKwargs`.
    """

    def clipboard_clear(self, **kw: Unpack[ClipboardKwargs]) -> None:
        """Clear the clipboard on the target display.

        This removes all data from the clipboard for the specified display.

        Args:
            **kw: See `ClipboardKwargs`. The `displayof` key targets a specific display.
        """
        return super().clipboard_clear(**kw)  # type: ignore[misc]

    def clipboard_append(self, string: str, **kw: Unpack[ClipboardKwargs]) -> None:
        """Append text to the clipboard.

        Appends *string* to the clipboard. To replace clipboard contents,
        call `clipboard_clear()` first.

        Args:
            string: Text to append to the clipboard.
            **kw: See `ClipboardKwargs`. Use `type` and `format` for non-text data.
        """
        return super().clipboard_append(string, **kw)  # type: ignore[misc]

    def clipboard_get(self, **kw: Unpack[ClipboardKwargs]) -> str:
        """Return clipboard contents as text.

        Args:
            **kw: See `ClipboardKwargs`. Use `type="UTF8_STRING"` to retrieve UTF-8 data.

        Returns:
            The clipboard contents as a string.

        Raises:
            tkinter.TclError: If the clipboard is empty or cannot be converted to the
                requested type.
        """
        return super().clipboard_get(**kw)  # type: ignore[misc]

    # -------------------------------------------------------------------------
    # Convenience helpers
    # -------------------------------------------------------------------------

    def clipboard_set(self, text: str, **kw: Unpack[ClipboardKwargs]) -> None:
        """Replace clipboard contents with *text*.

        Convenience wrapper for `clipboard_clear()` + `clipboard_append()`.

        Args:
            text: Text to set on the clipboard.
            **kw: See `ClipboardKwargs`. Forwarded to both clear and append.
        """
        self.clipboard_clear(**kw)
        self.clipboard_append(text, **kw)

    def clipboard_get_text(self, **kw: Unpack[ClipboardKwargs]) -> str:
        """Return clipboard contents as text (alias for `clipboard_get`)."""
        return self.clipboard_get(**kw)
