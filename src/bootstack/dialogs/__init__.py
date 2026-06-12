from __future__ import annotations

import textwrap
from datetime import date
from typing import Any, Callable, Iterable, Literal, Mapping, Sequence

from bootstack.dialogs._impl.dialog import Dialog, DialogButton, ButtonSpec, ButtonRole
from bootstack.dialogs._impl.query import QueryBox as _QueryBox
from bootstack.dialogs._impl.formdialog import FormDialog as _InternalFormDialog
from bootstack.dialogs._impl.datedialog import DateDialog as _DateDialog
from bootstack.dialogs._impl.colorchooser import ColorChooserDialog as _InternalColorChooserDialog, ColorChoice
from bootstack.dialogs._impl.fontdialog import FontDialog as _InternalFontDialog, FontChoice
from bootstack.dialogs._impl.filterdialog import FilterDialog as _InternalFilterDialog
from bootstack.widgets._impl.primitives.label import Label as _Label
from bootstack.widgets._impl.primitives.frame import Frame as _Frame
from bootstack._core.images import _ImageService
from bootstack.style.style import get_theme_color as _get_theme_color

__all__ = [
    # one-shot verbs
    "alert", "confirm",
    "ask_string", "ask_integer", "ask_float", "ask_date", "ask_date_range",
    "ask_item", "ask_color", "ask_font", "ask_filter",
    "ask_save_file", "ask_open_file", "ask_open_files", "ask_directory",
    # dialog classes
    "Dialog", "DialogButton", "FormDialog", "FilterDialog",
    "ColorChooserDialog", "ColorChoice", "FontDialog", "FontChoice",
    # type aliases
    "SeverityToken",
]


# ---------------------------------------------------------------------------
# Module-level convenience functions
# ---------------------------------------------------------------------------

_SEVERITY_ICONS: dict[str, str] = {
    "info":    "info-circle-fill",
    "warning": "exclamation-triangle-fill",
    "danger":  "x-circle-fill",
    "success": "check-circle-fill",
}

SeverityToken = Literal["info", "warning", "danger", "success"]


def _resolve_icon(
    icon: str | None, severity: SeverityToken | None
) -> tuple[str | None, str]:
    """Return (icon_name, icon_color) based on explicit icon/severity."""
    resolved = icon or _SEVERITY_ICONS.get(severity or "", None)
    if severity and not icon:
        try:
            color = _get_theme_color(severity)
        except Exception:
            color = _get_theme_color("foreground")
    else:
        try:
            color = _get_theme_color("foreground")
        except Exception:
            color = "#000000"
    return resolved, color


def _build_message_content(
    message: str, icon: str | None, icon_color: str, frame: Any
) -> None:
    """Build message body — used by alert() and confirm()."""
    # Two spacers sandwich the content for vertical centering
    _Frame(frame).pack(fill="x", expand=True)
    container = _Frame(frame, padding=(20, 0))
    container.pack(fill="x")
    _Frame(frame).pack(fill="x", expand=True)

    if icon:
        try:
            img = _ImageService.get_icon(icon, 48, icon_color)
            icon_lbl = _Label(container, image=img)
            icon_lbl.image = img  # prevent GC
            icon_lbl.pack(side="left", anchor="center", padx=(0, 16))
        except Exception:
            pass
    msg_frame = _Frame(container)
    msg_frame.pack(side="left", anchor="center")
    for line in message.split("\n"):
        wrapped = "\n".join(textwrap.wrap(line, width=60)) or line
        _Label(msg_frame, text=wrapped).pack(anchor="w", pady=(0, 3))


def alert(
    message: str,
    *,
    title: str = "",
    ok_text: str = "OK",
    severity: SeverityToken | None = None,
    icon: str | None = None,
    sound: bool | None = None,
    parent: Any = None,
) -> None:
    """Show a message dialog with an OK button.

    Args:
        message: The message text to display.
        title: Dialog window title.
        ok_text: Label for the OK button. Defaults to `'OK'`.
        severity: Visual severity level — sets a colored icon and controls the
            default sound behavior. `'warning'` and `'danger'` ring the system
            bell by default; `'info'` and `'success'` are silent.
        icon: Icon name override. Takes precedence over `severity`.
        sound: Override the alert sound. `True` always rings the bell,
            `False` always suppresses it. `None` (default) defers to
            `severity`: rings for `'warning'` and `'danger'`, silent
            otherwise.
        parent: Parent widget. Defaults to the active root window.
    """
    resolved_icon, icon_color = _resolve_icon(icon, severity)
    if sound is None:
        sound = severity in ("warning", "danger")
    dlg = Dialog(
        title=title or " ",
        content_builder=lambda f: _build_message_content(message, resolved_icon, icon_color, f),
        buttons=[DialogButton(ok_text, role="secondary", result=True, default=True)],
        alert=sound,
        min_size=(400, 140),
        parent=parent,
    )
    dlg.show()


def confirm(
    message: str,
    *,
    title: str = "",
    confirm_text: str = "Yes",
    cancel_text: str = "No",
    confirm_role: ButtonRole = "primary",
    severity: SeverityToken | None = None,
    icon: str | None = None,
    sound: bool | None = None,
    parent: Any = None,
) -> bool:
    """Show a confirmation dialog.

    Args:
        message: The question text to display.
        title: Dialog window title.
        confirm_text: Label for the confirm button. Defaults to `'Yes'`.
        cancel_text: Label for the cancel button. Defaults to `'No'`.
        confirm_role: Button role controlling styling. Use `'danger'` for
            destructive actions, `'primary'` (default) for standard
            confirmations. When `'danger'`, the confirm button is not
            focused by default so :kbd:`Enter` does not accidentally trigger it.
            Automatically overridden to `'danger'` when `severity='danger'`
            and to warning styling when `severity='warning'`, unless set
            explicitly.
        severity: Visual severity level — sets a colored icon, adjusts the
            confirm button color for `'danger'` and `'warning'`, and
            controls the default sound behavior.
        icon: Icon name override. Takes precedence over `severity`.
        sound: Override the alert sound. `True` always rings the bell,
            `False` always suppresses it. `None` (default) defers to
            `severity`: rings for `'warning'` and `'danger'`, silent
            otherwise.
        parent: Parent widget. Defaults to the active root window.

    Returns:
        `True` if the user clicked the confirm button, `False` otherwise.
    """
    resolved_icon, icon_color = _resolve_icon(icon, severity)
    if sound is None:
        sound = severity in ("warning", "danger")

    # Auto-derive confirm button styling from severity when not explicitly set
    if confirm_role == "primary" and severity == "danger":
        confirm_btn = DialogButton(confirm_text, role="danger", result=True, default=False)
    elif confirm_role == "primary" and severity == "warning":
        confirm_btn = DialogButton(confirm_text, role="secondary", accent="warning",
                                   result=True, default=True)
    else:
        is_danger = confirm_role == "danger"
        confirm_btn = DialogButton(confirm_text, role=confirm_role, result=True,
                                   default=not is_danger)

    dlg = Dialog(
        title=title or " ",
        content_builder=lambda f: _build_message_content(message, resolved_icon, icon_color, f),
        buttons=[
            DialogButton(cancel_text, role="cancel"),
            confirm_btn,
        ],
        alert=sound,
        min_size=(400, 140),
        parent=parent,
    )
    dlg.show()
    return dlg.result is True


def ask_string(
    prompt: str,
    *,
    title: str = "",
    value: str | None = None,
    value_format: str | None = None,
    parent: Any = None,
) -> str | None:
    """Show a text-input dialog.

    Args:
        prompt: Prompt text displayed above the input field.
        title: Dialog window title.
        value: Pre-filled initial value.
        value_format: ICU format pattern for parsing and displaying the value
            (e.g. a phone mask or postal code pattern). See :ref:`value-formats`.
        parent: Parent widget. Defaults to the active root window.

    Returns:
        The entered string, or `None` if canceled.
    """
    return _QueryBox.get_string(
        prompt,
        title=title or " ",
        value=value,
        value_format=value_format,
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
    value_format: str | None = None,
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
        value_format: ICU format pattern for displaying the value
            (e.g. `'#,##0'` for thousands separators). See :ref:`value-formats`.
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
        value_format=value_format,
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
    value_format: str | None = None,
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
        value_format: ICU format pattern for displaying the value
            (e.g. `'$#,##0.00'` for currency, `'#,##0.##'` for decimals).
            See :ref:`value-formats`.
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
        value_format=value_format,
        master=parent,
    )


def ask_date(
    *,
    title: str = "",
    value: date | None = None,
    min_date: date | None = None,
    max_date: date | None = None,
    first_weekday: int = 6,
    disabled_dates: list[date] | None = None,
    parent: Any = None,
) -> date | None:
    """Show a calendar date-picker dialog.

    Args:
        title: Dialog window title.
        value: Pre-selected initial date. Defaults to today.
        min_date: Earliest selectable date (inclusive).
        max_date: Latest selectable date (inclusive).
        first_weekday: First day of the week. `0` = Monday, `6` = Sunday
            (default).
        disabled_dates: Specific dates to disable from selection.
        parent: Parent widget. Defaults to the active root window.

    Returns:
        The selected `date`, or `None` if canceled.
    """
    dlg = _DateDialog(
        master=parent,
        title=title or " ",
        initial_date=value,
        min_date=min_date,
        max_date=max_date,
        first_weekday=first_weekday,
        disabled_dates=disabled_dates,
    )
    dlg.show()
    return dlg.result


def ask_date_range(
    *,
    title: str = "",
    start_date: date | None = None,
    end_date: date | None = None,
    min_date: date | None = None,
    max_date: date | None = None,
    first_weekday: int = 6,
    disabled_dates: list[date] | None = None,
    parent: Any = None,
) -> tuple[date, date] | None:
    """Show a calendar dialog for selecting a start and end date range.

    Args:
        title: Dialog window title.
        start_date: Pre-selected range start date.
        end_date: Pre-selected range end date.
        min_date: Earliest selectable date (inclusive).
        max_date: Latest selectable date (inclusive).
        first_weekday: First day of the week. `0` = Monday, `6` = Sunday
            (default).
        disabled_dates: Specific dates to disable from selection.
        parent: Parent widget. Defaults to the active root window.

    Returns:
        A `(start, end)` tuple of `date` objects, or `None` if canceled.
    """
    dlg = _DateDialog(
        master=parent,
        title=title or " ",
        selection_mode="range",
        start_date=start_date,
        end_date=end_date,
        min_date=min_date,
        max_date=max_date,
        first_weekday=first_weekday,
        disabled_dates=disabled_dates,
    )
    dlg.show()
    return dlg.result


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
        on_data_change: Callback invoked on every field change, receiving
            the current data dict.
        on_close: Callback fired when the dialog closes by any means.
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
        on_data_change: Callable[[dict[str, Any]], Any] | None = None,
        on_close: Callable[[], Any] | None = None,
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
        if on_data_change is not None:
            internal_kwargs["on_data_change"] = on_data_change
        if on_close is not None:
            internal_kwargs["on_close"] = on_close
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

        self._internal = _InternalFormDialog(parent, **internal_kwargs)

    def show(
        self,
        *,
        position: tuple[int, int] | None = None,
        modal: bool | None = None,
    ) -> "FormDialog":
        """Display the dialog and block until it is closed.

        Args:
            position: Explicit `(x, y)` screen coordinates for the dialog.
                Defaults to centered on the parent window.
            modal: Override the default modality. `True` blocks the parent;
                `False` shows a non-blocking dialog.

        Returns:
            `self` — allows chaining: `dlg = FormDialog(...).show(); dlg.result`.
        """
        self._internal.show(position=position, modal=modal)
        return self

    @property
    def result(self) -> dict[str, Any] | None:
        """Form data dict after closing, or `None` if canceled."""
        return self._internal.result

    @property
    def form(self) -> Any:
        """The embedded `Form` widget — for advanced programmatic access."""
        return self._internal.form


# ---------------------------------------------------------------------------
# ColorChooserDialog — public wrapper
# ---------------------------------------------------------------------------

class ColorChooserDialog:
    """A dialog for choosing a color using a hue/saturation spectrum.

    The chooser shows a full-spectrum canvas with a luminance slider below it.
    Numeric fields on the right allow direct entry in RGB, HSL, or hex notation.
    A screen dropper (unavailable on macOS) lets the user sample any pixel
    on the desktop.

    Args:
        title: Dialog window title. Defaults to the localized "Color" string.
        color: Initial color as a hex string (e.g. `'#ff0000'`). Defaults to
            the current theme background color.
        parent: Parent widget. Defaults to the active root window.
    """

    def __init__(
        self,
        *,
        title: str = "",
        color: str | None = None,
        parent: Any = None,
    ) -> None:
        self._internal = _InternalColorChooserDialog(
            master=parent,
            title=title or "color.chooser",
            initial_color=color,
        )

    def show(
        self,
        *,
        position: tuple[int, int] | None = None,
        modal: bool = True,
    ) -> "ColorChooserDialog":
        """Display the dialog and block until it is closed.

        Args:
            position: Explicit `(x, y)` screen coordinates for the dialog.
                Defaults to centered on the parent window.
            modal: Block the parent window until closed. Default `True`.

        Returns:
            `self` — allows chaining: `dlg = ColorChooserDialog(...).show(); dlg.result`.
        """
        self._internal.show(position=position, modal=modal)
        return self

    @property
    def result(self) -> ColorChoice | None:
        """The selected color, or `None` if canceled.

        Returns a `ColorChoice` namedtuple with three attributes:

        - `rgb` — `(r, g, b)` tuple, each 0–255.
        - `hsl` — `(h, s, l)` tuple: hue 0–360, saturation and luminance 0–100.
        - `hex` — lowercase hex string, e.g. `'#ff0000'`.
        """
        return self._internal.result


# ---------------------------------------------------------------------------
# FontDialog — public wrapper
# ---------------------------------------------------------------------------

class FontDialog:
    """A dialog for selecting a font family, size, weight, slant, and effects.

    The dialog shows a scrollable list of font families, a size list, and
    controls for weight (normal/bold), slant (roman/italic), underline, and
    overstrike. A live preview panel shows sample text rendered in the
    selected font.

    Args:
        title: Dialog window title. Defaults to the localized "Font" string.
        default_font: Font token to show initially (e.g. `'body'`, `'code'`,
            `'heading-lg'`). Defaults to `'body'`. See :doc:`/reference/typography`.
        parent: Parent widget. Defaults to the active root window.
    """

    def __init__(
        self,
        *,
        title: str = "",
        default_font: str = "body",
        parent: Any = None,
    ) -> None:
        self._internal = _InternalFontDialog(
            title=title or "font.selector",
            master=parent,
            default_font=default_font,
        )

    def show(
        self,
        *,
        position: tuple[int, int] | None = None,
        modal: bool | None = None,
    ) -> "FontDialog":
        """Display the dialog and block until it is closed.

        Args:
            position: Explicit `(x, y)` screen coordinates for the dialog.
                Defaults to centered on screen (the font dialog sizes itself on open).
            modal: Override the default modality. `True` blocks the parent;
                `False` shows a non-blocking dialog.

        Returns:
            `self` — allows chaining: `dlg = FontDialog(...).show(); dlg.result`.
        """
        self._internal.show(position=position, modal=modal)
        return self

    @property
    def result(self) -> FontChoice | None:
        """The selected font, or `None` if canceled.

        Returns a `FontChoice` namedtuple with six attributes:

        - `family` — font family name (str).
        - `size` — point size (int).
        - `weight` — `'normal'` or `'bold'`.
        - `slant` — `'roman'` or `'italic'`.
        - `underline` — `True` if underlined.
        - `overstrike` — `True` if struck through.
        """
        return self._internal.result


# ---------------------------------------------------------------------------
# FilterDialog — public wrapper
# ---------------------------------------------------------------------------

class FilterDialog:
    """A dialog for selecting multiple items from a list.

    Displays a scrollable list of checkboxes. Optionally includes a search
    box that narrows visible items and a "Select All" checkbox.

    Args:
        title: Dialog window title.
        items: Items to display. Each item is a string or a dict with keys:

            - `text` (str): Display label (required for dicts).
            - `value` (Any): Value returned when selected. Defaults to `text`.
            - `selected` (bool): Initial check state. Defaults to `False`.
        enable_search: Include a search box that filters items by text.
            Defaults to `False`.
        enable_select_all: Include a "Select All" checkbox. Defaults to `False`.
        parent: Parent widget. Defaults to the active root window.
    """

    def __init__(
        self,
        *,
        title: str = "",
        items: list[str | dict[str, Any]] | None = None,
        enable_search: bool = False,
        enable_select_all: bool = False,
        parent: Any = None,
    ) -> None:
        self._title = title
        self._items = items or []
        self._enable_search = enable_search
        self._enable_select_all = enable_select_all
        self._parent = parent
        self._result: list[Any] | None = None

    def show(
        self,
        *,
        position: tuple[int, int] | None = None,
        modal: bool | None = None,
    ) -> "FilterDialog":
        """Display the dialog and block until it is closed.

        Args:
            position: Explicit `(x, y)` screen coordinates for the dialog.
                Defaults to centered on the parent window.
            modal: Override the default modality. `True` blocks the parent;
                `False` shows a non-blocking dialog.

        Returns:
            `self` — allows chaining: `dlg = FilterDialog(...).show(); dlg.result`.
        """
        dlg = _InternalFilterDialog(
            master=self._parent,
            title=self._title or "Filter",
            items=self._items,
            enable_search=self._enable_search,
            enable_select_all=self._enable_select_all,
        )
        dlg.show(position=position, modal=modal)
        self._result = dlg.result
        return self

    @property
    def result(self) -> list[Any] | None:
        """List of selected values after closing, or `None` if canceled."""
        return self._result


# ---------------------------------------------------------------------------
# Convenience functions — color, font, filter
# ---------------------------------------------------------------------------

def ask_color(
    *,
    title: str = "",
    color: str | None = None,
    parent: Any = None,
) -> ColorChoice | None:
    """Show a color chooser dialog.

    Args:
        title: Dialog window title.
        color: Initial color as a hex string (e.g. `'#ff0000'`). Defaults to
            the current theme background color.
        parent: Parent widget. Defaults to the active root window.

    Returns:
        A `ColorChoice` with `rgb`, `hsl`, and `hex` attributes, or
        `None` if canceled.
    """
    dlg = ColorChooserDialog(title=title, color=color, parent=parent)
    dlg.show()
    return dlg.result


def ask_font(
    *,
    title: str = "",
    default_font: str = "body",
    parent: Any = None,
) -> FontChoice | None:
    """Show a font selector dialog.

    Args:
        title: Dialog window title.
        default_font: Font token to show initially (e.g. `'body'`, `'code'`,
            `'heading-lg'`). Defaults to `'body'`. See :doc:`/reference/typography`.
        parent: Parent widget. Defaults to the active root window.

    Returns:
        A `FontChoice` with `family`, `size`, `weight`, `slant`,
        `underline`, and `overstrike` attributes, or `None` if canceled.
    """
    dlg = FontDialog(title=title, default_font=default_font, parent=parent)
    dlg.show()
    return dlg.result


def ask_filter(
    items: list[str | dict[str, Any]],
    *,
    title: str = "",
    enable_search: bool = False,
    enable_select_all: bool = False,
    parent: Any = None,
) -> list[Any] | None:
    """Show a multi-select filter dialog.

    Args:
        items: Items to display. Each item is a string or a dict with keys:

            - `text` (str): Display label (required for dicts).
            - `value` (Any): Value returned when selected. Defaults to `text`.
            - `selected` (bool): Initial check state. Defaults to `False`.
        title: Dialog window title.
        enable_search: Include a search box that filters items by text.
            Defaults to `False`.
        enable_select_all: Include a "Select All" checkbox. Defaults to `False`.
        parent: Parent widget. Defaults to the active root window.

    Returns:
        A list of selected values, or `None` if canceled.
    """
    dlg = FilterDialog(
        title=title,
        items=items,
        enable_search=enable_search,
        enable_select_all=enable_select_all,
        parent=parent,
    )
    dlg.show()
    return dlg.result


# File-system dialogs (native OS choosers) ----------------------------------

def _run_file_dialog(_name: str, parent: Any, **options: Any) -> Any:
    """Call a `tkinter.filedialog` function with cleaned options."""
    import tkinter
    from tkinter import filedialog

    opts = {k: v for k, v in options.items() if v not in (None, "")}
    master = parent if parent is not None else tkinter._default_root
    if master is not None:
        opts["parent"] = master
    return getattr(filedialog, _name)(**opts)


def _coerce_file_types(file_types: Any) -> Any:
    if not file_types:
        return None
    return [tuple(ft) for ft in file_types]


def ask_save_file(
    *,
    title: str = "",
    initial_file: str = "",
    initial_dir: str = "",
    file_types: list[tuple[str, str]] | None = None,
    default_extension: str = "",
    parent: Any = None,
) -> str | None:
    """Show a native save dialog and return the chosen path.

    Args:
        title: Dialog window title.
        initial_file: Suggested file name.
        initial_dir: Directory to open in. Defaults to the last used location.
        file_types: Selectable file types as `(label, pattern)` pairs, for
            example `[('PNG image', '*.png'), ('All files', '*.*')]`.
        default_extension: Extension appended when the user omits one (for
            example `'.png'`).
        parent: Parent widget. Defaults to the active root window.

    Returns:
        The chosen file path, or `None` if canceled.
    """
    path = _run_file_dialog(
        "asksaveasfilename",
        parent,
        title=title,
        initialfile=initial_file,
        initialdir=initial_dir,
        filetypes=_coerce_file_types(file_types),
        defaultextension=default_extension,
    )
    return path or None


def ask_open_file(
    *,
    title: str = "",
    initial_dir: str = "",
    file_types: list[tuple[str, str]] | None = None,
    parent: Any = None,
) -> str | None:
    """Show a native open dialog for a single file and return its path.

    Args:
        title: Dialog window title.
        initial_dir: Directory to open in. Defaults to the last used location.
        file_types: Selectable file types as `(label, pattern)` pairs, for
            example `[('Images', '*.png *.jpg'), ('All files', '*.*')]`.
        parent: Parent widget. Defaults to the active root window.

    Returns:
        The chosen file path, or `None` if canceled.
    """
    path = _run_file_dialog(
        "askopenfilename",
        parent,
        title=title,
        initialdir=initial_dir,
        filetypes=_coerce_file_types(file_types),
    )
    return path or None


def ask_open_files(
    *,
    title: str = "",
    initial_dir: str = "",
    file_types: list[tuple[str, str]] | None = None,
    parent: Any = None,
) -> list[str]:
    """Show a native open dialog allowing several files.

    Args:
        title: Dialog window title.
        initial_dir: Directory to open in. Defaults to the last used location.
        file_types: Selectable file types as `(label, pattern)` pairs.
        parent: Parent widget. Defaults to the active root window.

    Returns:
        The chosen file paths, or an empty list if canceled.
    """
    paths = _run_file_dialog(
        "askopenfilenames",
        parent,
        title=title,
        initialdir=initial_dir,
        filetypes=_coerce_file_types(file_types),
    )
    return list(paths) if isinstance(paths, (list, tuple)) else []


def ask_directory(
    *,
    title: str = "",
    initial_dir: str = "",
    parent: Any = None,
) -> str | None:
    """Show a native folder chooser and return the chosen directory.

    Args:
        title: Dialog window title.
        initial_dir: Directory to open in. Defaults to the last used location.
        parent: Parent widget. Defaults to the active root window.

    Returns:
        The chosen directory path, or `None` if canceled.
    """
    path = _run_file_dialog(
        "askdirectory",
        parent,
        title=title,
        initialdir=initial_dir,
    )
    return path or None