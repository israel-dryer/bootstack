from __future__ import annotations

import tkinter
from typing import overload, Any, Callable, TYPE_CHECKING

from bootstack.widgets._impl.composites.pathentry import PathEntry as _InternalPathEntry
from bootstack.widgets._core.base import PublicWidgetBase
from bootstack.widgets._core.events import resolve_event, register_widget_events
from bootstack.widgets._core.field_mixin import FieldAddonMixin
from bootstack.widgets._core.subscription import Subscription
from bootstack.widgets._core.stream import Stream
from bootstack.widgets.textfield import _INNER_ENTRY_SEQUENCES
from bootstack.widgets.types import AccentToken, Event, WidgetDensity

if TYPE_CHECKING:
    from bootstack.signals import Signal

_PATHFIELD_EVENTS: dict[str, str] = {
    "input":    "<<Input>>",
    "change":   "<<Change>>",
    "valid":    "<<Valid>>",
    "invalid":  "<<Invalid>>",
    "validate": "<<Validate>>",
    "submit":   "<Return>",
    "focus":    "<FocusIn>",
    "blur":     "<FocusOut>",
}


class PathField(FieldAddonMixin, PublicWidgetBase):
    """A text field with a browse button that opens a native file/directory dialog.

    After the user picks a path, the field text is updated and a `change` event
    fires. `dialog_result` holds the raw result from the dialog (a string for
    single-file dialogs, a tuple of strings for multi-file dialogs).

    Args:
        value: Initial path string.
        mode: Dialog type — `'open'` (default), `'open_multiple'`, `'save'`,
            or `'directory'`.
        dialog_title: Title shown in the native picker window.
        start_dir: Directory the dialog opens in.
        file_filters: File type filters, e.g. `[('Images', '*.png *.jpg')]`.
            Not used for `'directory'` mode.
        default_extension: Extension appended automatically if omitted by the
            user. `'save'` mode only.
        default_filename: Suggested filename pre-filled in the dialog.
            `'save'` mode only.
        label: Label displayed above the field.
        message: Hint text displayed below the field.
        placeholder: Ghost text shown when the field is empty and unfocused.
        textsignal: Reactive `Signal[str]` bound to the field text. The
            field value and signal stay in sync automatically.
        required: Mark field as required.
        disabled: If True, field is non-interactive.
        read_only: If True, value is visible but not editable.
        width: Width in character units.
        accent: Accent token for the focus ring. One of `'primary'`,
            `'secondary'`, `'success'`, `'warning'`, `'danger'`.
        density: Widget density — `'default'` or `'compact'`.
        parent: Override the context-stack parent.
    """

    def __init__(
        self,
        value: str = "",
        *,
        mode: str = "open",
        dialog_title: str | None = None,
        start_dir: str | None = None,
        file_filters: list | None = None,
        default_extension: str | None = None,
        default_filename: str | None = None,
        label: str | None = None,
        message: str | None = None,
        placeholder: str | None = None,
        textsignal: "Signal[str] | None" = None,
        required: bool = False,
        disabled: bool = False,
        read_only: bool = False,
        width: int | None = None,
        accent: AccentToken | str | None = None,
        density: WidgetDensity | None = None,
        parent: Any = None,
        **kwargs: Any,
    ) -> None:
        self._parent = self._resolve_parent(parent)
        layout_kw = self._split_layout_kwargs(kwargs)

        tk_master = self._parent._child_master() if self._parent else None

        internal_kwargs: dict[str, Any] = {"mode": mode}
        if value:
            internal_kwargs["value"] = value
        if dialog_title is not None:
            internal_kwargs["dialog_title"] = dialog_title
        if start_dir is not None:
            internal_kwargs["start_dir"] = start_dir
        if file_filters is not None:
            internal_kwargs["file_filters"] = file_filters
        if default_extension is not None:
            internal_kwargs["default_extension"] = default_extension
        if default_filename is not None:
            internal_kwargs["default_filename"] = default_filename
        if label is not None:
            internal_kwargs["label"] = label
        if message is not None:
            internal_kwargs["message"] = message
        if placeholder is not None:
            internal_kwargs["placeholder"] = placeholder
        if textsignal is not None:
            internal_kwargs["textsignal"] = textsignal
        if required:
            internal_kwargs["required"] = True
        if disabled:
            internal_kwargs["state"] = "disabled"
        elif read_only:
            internal_kwargs["state"] = "readonly"
        if width is not None:
            internal_kwargs["width"] = width
        if accent is not None:
            internal_kwargs["accent"] = accent
        if density is not None:
            internal_kwargs["density"] = density
        internal_kwargs.update(kwargs)

        self._internal = _InternalPathEntry(tk_master, **internal_kwargs)
        self._attach_to_parent(layout_kw)

    # ----- Event routing -----

    def _entry_widget(self) -> tkinter.Misc:
        return self._internal._entry

    @overload
    def on(self, event: str) -> Stream: ...
    @overload
    def on(self, event: str, handler: Callable[[Event], Any]) -> Subscription: ...
    def on(self, event: str, handler: Callable[[Event], Any] | None = None) -> Stream | Subscription:
        sequence = resolve_event(self, str(event))
        target = self._entry_widget() if sequence in _INNER_ENTRY_SEQUENCES else self._internal
        if handler is None:
            def _source(h):
                t = self._entry_widget() if sequence in _INNER_ENTRY_SEQUENCES else self._internal
                bid = t.bind(sequence, h, add="+")
                return Subscription(t, sequence, bid)
            return Stream(self._internal, _source=_source)
        bid = target.bind(sequence, handler, add="+")
        return Subscription(target, sequence, bid)

    # ----- Properties -----

    @property
    def value(self) -> str:
        """The current path string shown in the field."""
        return self._internal.value

    @value.setter
    def value(self, v: str) -> None:
        self._internal.value = v

    @property
    def dialog_result(self) -> "str | tuple[str, ...] | None":
        """Raw result from the most recent dialog (string or tuple of strings)."""
        return self._internal.dialog_result

    @property
    def signal(self) -> "Signal[str] | None":
        """The reactive `Signal` bound to this field, or `None`."""
        return getattr(self._internal, "signal", None)

    @property
    def disabled(self) -> bool:
        """Whether the field is fully non-interactive."""
        return str(self._entry_widget().cget("state")) == "disabled"

    @disabled.setter
    def disabled(self, v: bool) -> None:
        self._internal.configure(state="disabled" if v else "normal")

    @property
    def read_only(self) -> bool:
        """Whether the field is visible but not editable."""
        return str(self._entry_widget().cget("state")) == "readonly"

    @read_only.setter
    def read_only(self, v: bool) -> None:
        self._internal.configure(state="readonly" if v else "normal")

    # ----- Methods -----

    def focus(self) -> None:
        """Give keyboard focus to this field."""
        self._entry_widget().focus_set()

    def clear(self) -> None:
        """Clear the field text."""
        self._internal.value = ""

    def commit(self) -> None:
        """Manually parse the display text, update the value, and run validation.

        Useful when you need to force a commit outside of the normal
        blur/Enter flow.
        """
        self._internal._entry.commit()

    def validate(self, trigger: str = "manual") -> bool:
        """Run validation rules against the current value.

        Args:
            trigger: Validation trigger label. One of `'manual'`,
                `'blur'`, `'key'`. Defaults to `'manual'`.

        Returns:
            `True` if all rules pass, `False` otherwise.
        """
        return self._internal._entry.validate(
            self._internal._entry.value(), trigger=trigger
        )

    def select_all(self) -> None:
        """Select all text in the field."""
        self._entry_widget().selection_range(0, "end")

    def select_range(self, start: int, end: int) -> None:
        """Select text between ``start`` and ``end`` character positions.

        Args:
            start: Start index (0-based, inclusive).
            end: End index (exclusive).
        """
        self._entry_widget().selection_range(start, end)

    def set_cursor(self, index: int) -> None:
        """Move the insertion cursor to ``index``.

        Args:
            index: Character position to place the cursor.
        """
        self._entry_widget().icursor(index)

    def insert(self, index: int, text: str) -> None:
        """Insert ``text`` at ``index``.

        Args:
            index: Character position to insert at.
            text: Text to insert.
        """
        self._entry_widget().insert(index, text)

    def delete(self, start: int, end: int | None = None) -> None:
        """Delete characters from ``start`` to ``end``.

        Args:
            start: Start index (inclusive).
            end: End index (exclusive). If ``None``, deletes to end of field.
        """
        self._entry_widget().delete(start, "end" if end is None else end)

    # ----- Event shorthands -----

    @overload
    def on_change(self) -> Stream: ...
    @overload
    def on_change(self, handler: Callable[[Event], Any]) -> Subscription: ...
    def on_change(self, handler: Callable[[Event], Any] | None = None) -> Stream | Subscription:
        """Register a callback fired when the path value changes.

        Fires after the user picks a path via the dialog or edits the field
        directly and commits (blur or Enter).

        Returns:
            `Subscription` (with handler) or `Stream` (without handler).
        """
        return self.on("change", handler)

    @overload
    def on_input(self) -> Stream: ...
    @overload
    def on_input(self, handler: Callable[[Event], Any]) -> Subscription: ...
    def on_input(self, handler: Callable[[Event], Any] | None = None) -> Stream | Subscription:
        """Register a callback fired on every keystroke in the text portion.

        Returns:
            `Subscription` (with handler) or `Stream` (without handler).
        """
        return self.on("input", handler)

    @overload
    def on_submit(self) -> Stream: ...
    @overload
    def on_submit(self, handler: Callable[[Event], Any]) -> Subscription: ...
    def on_submit(self, handler: Callable[[Event], Any] | None = None) -> Stream | Subscription:
        """Register a callback fired when the user presses Enter.

        Returns:
            `Subscription` (with handler) or `Stream` (without handler).
        """
        return self.on("submit", handler)

    @overload
    def on_focus(self) -> Stream: ...
    @overload
    def on_focus(self, handler: Callable[[Event], Any]) -> Subscription: ...
    def on_focus(self, handler: Callable[[Event], Any] | None = None) -> Stream | Subscription:
        """Register a callback fired when the field gains focus.

        Returns:
            `Subscription` (with handler) or `Stream` (without handler).
        """
        return self.on("focus", handler)

    @overload
    def on_blur(self) -> Stream: ...
    @overload
    def on_blur(self, handler: Callable[[Event], Any]) -> Subscription: ...
    def on_blur(self, handler: Callable[[Event], Any] | None = None) -> Stream | Subscription:
        """Register a callback fired when the field loses focus.

        Returns:
            `Subscription` (with handler) or `Stream` (without handler).
        """
        return self.on("blur", handler)

    @overload
    def on_valid(self) -> Stream: ...
    @overload
    def on_valid(self, handler: Callable[[Event], Any]) -> Subscription: ...
    def on_valid(self, handler: Callable[[Event], Any] | None = None) -> Stream | Subscription:
        """Register a callback fired when validation passes.

        Returns:
            `Subscription` (with handler) or `Stream` (without handler).
        """
        return self.on("valid", handler)

    @overload
    def on_invalid(self) -> Stream: ...
    @overload
    def on_invalid(self, handler: Callable[[Event], Any]) -> Subscription: ...
    def on_invalid(self, handler: Callable[[Event], Any] | None = None) -> Stream | Subscription:
        """Register a callback fired when validation fails.

        Returns:
            `Subscription` (with handler) or `Stream` (without handler).
        """
        return self.on("invalid", handler)

    @overload
    def on_validate(self) -> Stream: ...
    @overload
    def on_validate(self, handler: Callable[[Event], Any]) -> Subscription: ...
    def on_validate(self, handler: Callable[[Event], Any] | None = None) -> Stream | Subscription:
        """Register a callback fired after any validation run.

        Returns:
            `Subscription` (with handler) or `Stream` (without handler).
        """
        return self.on("validate", handler)


register_widget_events(PathField, _PATHFIELD_EVENTS)