from __future__ import annotations

from datetime import date
from typing import Any, Callable, Iterable, Literal, Mapping, Sequence

from bootstack.dialogs.dialog import Dialog, DialogButton, ButtonSpec
from bootstack.dialogs.message import MessageBox as _MessageBox
from bootstack.dialogs.query import QueryBox as _QueryBox
from bootstack.dialogs.formdialog import FormDialog as _InternalFormDialog


# ---------------------------------------------------------------------------
# Module-level convenience functions
# ---------------------------------------------------------------------------

def alert(
    message: str,
    *,
    title: str = "",
    parent: Any = None,
) -> None:
    """Show a message dialog with an OK button.

    Args:
        message: The message text to display.
        title: Dialog window title.
        parent: Parent widget. Defaults to the active root window.
    """
    _MessageBox.ok(message, title=title or " ", master=parent)


def confirm(
    message: str,
    *,
    title: str = "",
    parent: Any = None,
) -> bool:
    """Show a Yes/No confirmation dialog.

    Args:
        message: The question text to display.
        title: Dialog window title.
        parent: Parent widget. Defaults to the active root window.

    Returns:
        `True` if the user clicked Yes, `False` otherwise.
    """
    result = _MessageBox.yesno(message, title=title or " ", master=parent)
    return result == "Yes"


def ask_string(
    prompt: str,
    *,
    title: str = "",
    value: str | None = None,
    parent: Any = None,
) -> str | None:
    """Show a text-input dialog.

    Args:
        prompt: Prompt text displayed above the input field.
        title: Dialog window title.
        value: Pre-filled initial value.
        parent: Parent widget. Defaults to the active root window.

    Returns:
        The entered string, or `None` if canceled.
    """
    return _QueryBox.get_string(
        prompt,
        title=title or " ",
        value=value,
        master=parent,
    )


def ask_integer(
    prompt: str,
    *,
    title: str = "",
    value: int | None = None,
    min_value: int | None = None,
    max_value: int | None = None,
    step: int | None = None,
    parent: Any = None,
) -> int | None:
    """Show an integer-input dialog with optional range validation.

    Args:
        prompt: Prompt text displayed above the input field.
        title: Dialog window title.
        value: Pre-filled initial value.
        min_value: Minimum accepted value.
        max_value: Maximum accepted value.
        step: Increment/decrement step size.
        parent: Parent widget. Defaults to the active root window.

    Returns:
        The entered integer, or `None` if canceled.
    """
    return _QueryBox.get_integer(
        prompt,
        title=title or " ",
        value=value,
        minvalue=min_value,
        maxvalue=max_value,
        increment=step,
        master=parent,
    )


def ask_float(
    prompt: str,
    *,
    title: str = "",
    value: float | None = None,
    min_value: float | None = None,
    max_value: float | None = None,
    step: float | None = None,
    parent: Any = None,
) -> float | None:
    """Show a float-input dialog with optional range validation.

    Args:
        prompt: Prompt text displayed above the input field.
        title: Dialog window title.
        value: Pre-filled initial value.
        min_value: Minimum accepted value.
        max_value: Maximum accepted value.
        step: Increment/decrement step size.
        parent: Parent widget. Defaults to the active root window.

    Returns:
        The entered float, or `None` if canceled.
    """
    return _QueryBox.get_float(
        prompt,
        title=title or " ",
        value=value,
        minvalue=min_value,
        maxvalue=max_value,
        increment=step,
        master=parent,
    )


def ask_date(
    prompt: str = "",
    *,
    title: str = "",
    value: date | None = None,
    parent: Any = None,
) -> date | None:
    """Show a calendar date-picker dialog.

    Args:
        prompt: Prompt text (used as the dialog title when `title` is not set).
        title: Dialog window title. Falls back to `prompt` when omitted.
        value: Pre-selected initial date.
        parent: Parent widget. Defaults to the active root window.

    Returns:
        The selected `date`, or `None` if canceled.
    """
    return _QueryBox.get_date(
        master=parent,
        title=title or prompt or " ",
        value=value,
    )


def ask_item(
    prompt: str,
    options: list[str],
    *,
    title: str = "",
    value: str | None = None,
    parent: Any = None,
) -> str | None:
    """Show a dropdown-selection dialog.

    Args:
        prompt: Prompt text displayed above the dropdown.
        options: List of selectable items.
        title: Dialog window title.
        value: Pre-selected initial item.
        parent: Parent widget. Defaults to the active root window.

    Returns:
        The selected item string, or `None` if canceled.
    """
    return _QueryBox.get_item(
        prompt,
        title=title or " ",
        value=value,
        items=options,
        master=parent,
    )


# ---------------------------------------------------------------------------
# FormDialog — public wrapper
# ---------------------------------------------------------------------------

class FormDialog:
    """A dialog window that embeds a Form for structured data entry.

    Args:
        title: Dialog window title.
        data: Initial data backing the form. Keys become field names.
        items: Explicit form layout — `FormItem` / `GroupItem` / `TabsItem`
            instances or equivalent dicts. If omitted, fields are inferred
            from `data`.
        col_count: Number of form columns. Default `1`.
        min_col_width: Minimum column width in pixels.
        on_data_changed: Callback invoked on every field change, receiving
            the current data dict.
        width: Explicit form width in pixels.
        height: Explicit form height in pixels.
        buttons: Footer button specs. Defaults to Cancel + OK.
        min_size: Minimum dialog window size `(width, height)`.
        max_size: Maximum dialog window size `(width, height)`.
        resizable: Allow window resizing. Default `False`.
        parent: Parent widget. Defaults to the active root window.
    """

    def __init__(
        self,
        *,
        title: str = "Form",
        data: dict[str, Any] | None = None,
        items: Sequence[Any] | None = None,
        col_count: int = 1,
        min_col_width: int | None = None,
        on_data_changed: Callable[[dict[str, Any]], Any] | None = None,
        width: int | None = None,
        height: int | None = None,
        buttons: Iterable[ButtonSpec | str] | None = None,
        min_size: tuple[int, int] | None = None,
        max_size: tuple[int, int] | None = None,
        resizable: tuple[bool, bool] | bool = False,
        parent: Any = None,
    ) -> None:
        internal_kwargs: dict[str, Any] = {
            "title": title,
            "col_count": col_count,
            "resizable": resizable,
        }
        if data is not None:
            internal_kwargs["data"] = data
        if items is not None:
            internal_kwargs["items"] = items
        if min_col_width is not None:
            internal_kwargs["min_col_width"] = min_col_width
        if on_data_changed is not None:
            internal_kwargs["on_data_changed"] = on_data_changed
        if width is not None:
            internal_kwargs["width"] = width
        if height is not None:
            internal_kwargs["height"] = height
        if buttons is not None:
            internal_kwargs["buttons"] = buttons
        if min_size is not None:
            internal_kwargs["minsize"] = min_size
        if max_size is not None:
            internal_kwargs["maxsize"] = max_size

        self._internal = _InternalFormDialog(master=parent, **internal_kwargs)

    def show(self) -> "FormDialog":
        """Display the dialog and block until it is closed.

        Returns:
            `self` — allows chaining: `dlg = FormDialog(...).show(); dlg.result`.
        """
        self._internal.show()
        return self

    @property
    def result(self) -> dict[str, Any] | None:
        """Form data dict after closing, or `None` if canceled."""
        return self._internal.result

    @property
    def form(self) -> Any:
        """The embedded `Form` widget — for advanced programmatic access."""
        return self._internal.form