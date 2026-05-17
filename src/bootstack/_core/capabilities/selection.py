from __future__ import annotations

from typing import Any, Callable, TYPE_CHECKING

from typing_extensions import TypedDict

if TYPE_CHECKING:
    from typing_extensions import Unpack


class SelectionClearKwargs(TypedDict, total=False):
    """Keyword options for `selection_clear`."""
    selection: str
    """Selection name (e.g., `'PRIMARY'`, `'CLIPBOARD'`). Defaults to `'PRIMARY'`."""
    displayof: Any
    """Widget or window whose display to target. Defaults to `'.'`."""


class SelectionGetKwargs(TypedDict, total=False):
    """Keyword options for `selection_get`."""
    selection: str
    """Selection name (e.g., `'PRIMARY'`, `'CLIPBOARD'`). Defaults to `'PRIMARY'`."""
    type: str
    """Target type for conversion (e.g., `'STRING'`, `'UTF8_STRING'`, `'TARGETS'`). Defaults to `'STRING'`."""
    displayof: Any
    """Widget or window whose display to target. Defaults to `'.'`."""


class SelectionHandleKwargs(TypedDict, total=False):
    """Keyword options for `selection_handle`."""
    selection: str
    """Selection name. Defaults to `'PRIMARY'`."""
    type: str
    """Requested type the handler will serve. Defaults to `'STRING'`."""
    format: str
    """Representation format for transmitting data to the X server. Defaults to `'STRING'`."""


class SelectionMixin:
    """X selection helpers (selection).

    Tk's `selection` command provides access to the X selection mechanism (ICCCM),
    most commonly the **PRIMARY** selection, and also supports **CLIPBOARD** and
    other named selections.

    Portability notes:
        - On X11, PRIMARY is a system-wide selection shared across processes.
        - On Windows, PRIMARY is provided by Tk (not the OS) and is shared only
          within related interpreters, not across processes.
        - For clipboard-style usage, Tk also provides the `clipboard_*` methods,
          which are often a better cross-platform fit.

    Intended usage:
        class Widget(SelectionMixin, ttk.Widget): ...
        class App(SelectionMixin, tkinter.Tk): ...
    """

    def selection_clear(self, **kw: Unpack[SelectionClearKwargs]) -> None:
        """Clear a selection so that no window owns it.

        Args:
            **kw: See `SelectionClearKwargs`.
        """
        return super().selection_clear(**kw)  # type: ignore[misc]

    def selection_get(self, **kw: Unpack[SelectionGetKwargs]) -> str:
        """Return the current contents of a selection.

        The default selection is `'PRIMARY'` and the default type is `'STRING'`.

        Args:
            **kw: See `SelectionGetKwargs`. Use `type='UTF8_STRING'` to retrieve
                UTF-8 formatted data.

        Returns:
            The selection contents as a string.

        Notes:
            - If the owner returns a non-string representation (e.g. ATOM or INTEGER),
              Tk converts it to a space-separated string representation.
            - Tk will not retrieve UTF-8 formatted data unless you request
              `type="UTF8_STRING"`.
        """
        return super().selection_get(**kw)  # type: ignore[misc]

    def selection_handle(self, command: str | None, **kw: Unpack[SelectionHandleKwargs]) -> None:
        """Register or remove a handler for selection retrieval requests.

        When this widget owns a selection, Tk will execute *command* when another
        client attempts to retrieve the selection in the requested type.

        Args:
            command: A Tcl command (string) to execute to supply selection data.
                If None or empty, removes any existing handler for the given
                selection/type combination.
            **kw: See `SelectionHandleKwargs`.

        Notes:
            - When handling type `'STRING'`, Tk will also handle `'UTF8_STRING'`
              automatically.
            - The command is invoked with `offset` and `maxChars` appended. Return
              up to `maxChars` characters starting at `offset` — large selections
              are retrieved in chunks.
        """
        if command is None:
            command = ""
        return super().selection_handle(command, **kw)  # type: ignore[misc]

    def selection_own(self, **kw: Unpack[SelectionClearKwargs]) -> str:
        """Query the current selection owner within this application.

        Args:
            **kw: See `SelectionClearKwargs` (`selection` and `displayof`).

        Returns:
            The pathname of the owner window in this application, or an empty
            string if no window owns the selection.
        """
        return super().selection_own(**kw)  # type: ignore[misc]

    def selection_own_set(
            self,
            owner: Any,
            command: Callable[[], Any] | None = None,
            *,
            selection: str = "PRIMARY",
    ) -> None:
        """Make *owner* the selection owner.

        Args:
            owner: The widget/window that should own the selection.
            command: Optional callback invoked when this widget loses ownership
                (i.e., another window claims the selection).
            selection: The selection name to claim. Defaults to `'PRIMARY'`.
        """
        return super().selection_own(owner, command=command, selection=selection)  # type: ignore[misc]
