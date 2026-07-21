from __future__ import annotations

import tkinter
from typing import overload, Any, Callable, Literal, TYPE_CHECKING

from bootstack.widgets._impl.composites.pathentry import PathEntry as _InternalPathEntry
from bootstack.widgets._core.base import PublicWidgetBase, adapt_handler
from bootstack.widgets._core.events import resolve_event, register_widget_events
from bootstack.widgets._core.field_mixin import FieldAddonMixin
from bootstack.events import ChangeEvent, InputEvent, Subscription, ValidationEvent
from bootstack.streams import Stream
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
    fires. The `dialog_result` property holds the raw result from the dialog (a
    string for single-file dialogs, a tuple of strings for multi-file dialogs).

    Args:
        value: Initial path string.
        mode: Dialog type. Default `'open'`.
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
        accent: Accent token applied to the focus ring.
        density: Widget density.
        parent: Override the context-stack parent.
        **kwargs: Layout placement options applied by the parent container —
            `fill`, `expand`, `anchor`, `margin`, `row`, `column`, `sticky`.
            See :doc:`/tasks/layout`.
    """

    def __init__(
        self,
        value: str = "",
        *,
        mode: Literal["open", "open_multiple", "save", "directory"] = "open",
        dialog_title: str | None = None,
        start_dir: str | None = None,
        file_filters: list[tuple[str, str]] | None = None,
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
        # Test against the empty value, not truthiness: `0` or `False` is a
        # value the caller passed, and dropping it here leaves the field blank.
        if value is not None and value != "":
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
        """Register a callback for an event by name.

        A generic, string-keyed escape hatch — prefer the typed `on_*`
        shorthands (e.g. `on_change`), which carry the precise payload type.
        Called with no handler, returns a composable `Stream`; with a handler,
        binds it and returns a `Subscription`.

        Args:
            event: Event name (for example `'change'` or `'focus'`).
            handler: Called with the event payload. Omit to get a composable
                :class:`~bootstack.streams.Stream` instead.

        Returns:
            A cancellable :class:`~bootstack.events.Subscription` when a handler
            is given, otherwise a :class:`~bootstack.streams.Stream`.
        """
        sequence = resolve_event(self, str(event))
        target = self._entry_widget() if sequence in _INNER_ENTRY_SEQUENCES else self._internal
        if handler is None:
            def _source(h):
                t = self._entry_widget() if sequence in _INNER_ENTRY_SEQUENCES else self._internal
                bid = t.bind(sequence, adapt_handler(h), add="+")
                return Subscription(t, sequence, bid)
            return Stream(self._internal, _source=_source)
        bid = target.bind(sequence, adapt_handler(handler), add="+")
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

    # ----- Live dialog configuration -----

    @property
    def mode(self) -> Literal["open", "open_multiple", "save", "directory"]:
        """Which native dialog the browse button opens."""
        return self._internal.cget("mode")

    @mode.setter
    def mode(self, v: Literal["open", "open_multiple", "save", "directory"]) -> None:
        self._internal.configure(mode=v)

    @property
    def dialog_title(self) -> str | None:
        """Title shown in the native picker window."""
        return self._internal.cget("dialog_title")

    @dialog_title.setter
    def dialog_title(self, v: str | None) -> None:
        self._internal.configure(dialog_title=v)

    @property
    def start_dir(self) -> str | None:
        """Directory the dialog opens in."""
        return self._internal.cget("start_dir")

    @start_dir.setter
    def start_dir(self, v: str | None) -> None:
        self._internal.configure(start_dir=v)

    @property
    def file_filters(self) -> "list[tuple[str, str]] | None":
        """File-type filters, e.g. `[('Images', '*.png *.jpg')]`. Not used for `'directory'` mode."""
        return self._internal.cget("file_filters")

    @file_filters.setter
    def file_filters(self, v: "list[tuple[str, str]] | None") -> None:
        self._internal.configure(file_filters=v)

    @property
    def default_extension(self) -> str | None:
        """Extension appended automatically when omitted (`'save'` mode only)."""
        return self._internal.cget("default_extension")

    @default_extension.setter
    def default_extension(self, v: str | None) -> None:
        self._internal.configure(default_extension=v)

    @property
    def default_filename(self) -> str | None:
        """Suggested filename pre-filled in the dialog (`'save'` mode only)."""
        return self._internal.cget("default_filename")

    @default_filename.setter
    def default_filename(self, v: str | None) -> None:
        self._internal.configure(default_filename=v)

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

    def validate(self) -> bool:
        """Run validation rules against the current value.

        Returns:
            `True` if all rules pass, `False` otherwise.
        """
        entry = self._internal._entry
        return entry.validate(entry._get_validation_value(), trigger="manual")

    def select_all(self) -> None:
        """Select all text in the field."""
        self._entry_widget().selection_range(0, "end")

    def select_range(self, start: int, end: int) -> None:
        """Select text between `start` and `end` character positions.

        Args:
            start: Start index (0-based, inclusive).
            end: End index (exclusive).
        """
        self._entry_widget().selection_range(start, end)

    def insert(self, index: int, text: str) -> None:
        """Insert `text` at `index`.

        Args:
            index: Character position to insert at.
            text: Text to insert.
        """
        self._entry_widget().insert(index, text)

    def delete(self, start: int, end: int | None = None) -> None:
        """Delete characters from `start` to `end`.

        Args:
            start: Start index (inclusive).
            end: End index (exclusive). If `None`, deletes to end of field.
        """
        self._entry_widget().delete(start, "end" if end is None else end)

    # ----- Event shorthands -----

    @overload
    def on_change(self) -> Stream: ...
    @overload
    def on_change(self, handler: Callable[[ChangeEvent], Any]) -> Subscription: ...
    def on_change(self, handler: Callable[[ChangeEvent], Any] | None = None) -> Stream | Subscription:
        """Register a callback fired when the path value changes.

        Fires after the user picks a path via the dialog or edits the field
        directly and commits (blur or Enter).

        Args:
            handler: Called with a :class:`~bootstack.events.ChangeEvent`. Omit to
                get a composable :class:`~bootstack.streams.Stream` instead.

        Returns:
            A cancellable :class:`~bootstack.events.Subscription` when a
            handler is given, otherwise a :class:`~bootstack.streams.Stream`.
        """
        return self.on("change", handler)

    @overload
    def on_input(self) -> Stream: ...
    @overload
    def on_input(self, handler: Callable[[InputEvent], Any]) -> Subscription: ...
    def on_input(self, handler: Callable[[InputEvent], Any] | None = None) -> Stream | Subscription:
        """Register a callback fired on every keystroke in the text portion.

        Args:
            handler: Called with an :class:`~bootstack.events.InputEvent`. Omit to
                get a composable :class:`~bootstack.streams.Stream` instead.

        Returns:
            A cancellable :class:`~bootstack.events.Subscription` when a
            handler is given, otherwise a :class:`~bootstack.streams.Stream`.
        """
        return self.on("input", handler)

    @overload
    def on_submit(self) -> Stream: ...
    @overload
    def on_submit(self, handler: Callable[[Event], Any]) -> Subscription: ...
    def on_submit(self, handler: Callable[[Event], Any] | None = None) -> Stream | Subscription:
        """Register a callback fired when the user presses Enter.

        Args:
            handler: Called with an :class:`~bootstack.events.Event`. Omit to
                get a composable :class:`~bootstack.streams.Stream` instead.

        Returns:
            A cancellable :class:`~bootstack.events.Subscription` when a
            handler is given, otherwise a :class:`~bootstack.streams.Stream`.
        """
        return self.on("submit", handler)

    @overload
    def on_focus(self) -> Stream: ...
    @overload
    def on_focus(self, handler: Callable[[Event], Any]) -> Subscription: ...
    def on_focus(self, handler: Callable[[Event], Any] | None = None) -> Stream | Subscription:
        """Register a callback fired when the field gains focus.

        Args:
            handler: Called with an :class:`~bootstack.events.Event`. Omit to
                get a composable :class:`~bootstack.streams.Stream` instead.

        Returns:
            A cancellable :class:`~bootstack.events.Subscription` when a
            handler is given, otherwise a :class:`~bootstack.streams.Stream`.
        """
        return self.on("focus", handler)

    @overload
    def on_blur(self) -> Stream: ...
    @overload
    def on_blur(self, handler: Callable[[Event], Any]) -> Subscription: ...
    def on_blur(self, handler: Callable[[Event], Any] | None = None) -> Stream | Subscription:
        """Register a callback fired when the field loses focus.

        Args:
            handler: Called with an :class:`~bootstack.events.Event`. Omit to
                get a composable :class:`~bootstack.streams.Stream` instead.

        Returns:
            A cancellable :class:`~bootstack.events.Subscription` when a
            handler is given, otherwise a :class:`~bootstack.streams.Stream`.
        """
        return self.on("blur", handler)

    @overload
    def on_valid(self) -> Stream: ...
    @overload
    def on_valid(self, handler: Callable[[ValidationEvent], Any]) -> Subscription: ...
    def on_valid(self, handler: Callable[[ValidationEvent], Any] | None = None) -> Stream | Subscription:
        """Register a callback fired when validation passes.

        Args:
            handler: Called with a :class:`~bootstack.events.ValidationEvent`. Omit to
                get a composable :class:`~bootstack.streams.Stream` instead.

        Returns:
            A cancellable :class:`~bootstack.events.Subscription` when a
            handler is given, otherwise a :class:`~bootstack.streams.Stream`.
        """
        return self.on("valid", handler)

    @overload
    def on_invalid(self) -> Stream: ...
    @overload
    def on_invalid(self, handler: Callable[[ValidationEvent], Any]) -> Subscription: ...
    def on_invalid(self, handler: Callable[[ValidationEvent], Any] | None = None) -> Stream | Subscription:
        """Register a callback fired when validation fails.

        Args:
            handler: Called with a :class:`~bootstack.events.ValidationEvent`. Omit to
                get a composable :class:`~bootstack.streams.Stream` instead.

        Returns:
            A cancellable :class:`~bootstack.events.Subscription` when a
            handler is given, otherwise a :class:`~bootstack.streams.Stream`.
        """
        return self.on("invalid", handler)

    @overload
    def on_validate(self) -> Stream: ...
    @overload
    def on_validate(self, handler: Callable[[ValidationEvent], Any]) -> Subscription: ...
    def on_validate(self, handler: Callable[[ValidationEvent], Any] | None = None) -> Stream | Subscription:
        """Register a callback fired after any validation run.

        Args:
            handler: Called with a :class:`~bootstack.events.ValidationEvent`. Omit to
                get a composable :class:`~bootstack.streams.Stream` instead.

        Returns:
            A cancellable :class:`~bootstack.events.Subscription` when a
            handler is given, otherwise a :class:`~bootstack.streams.Stream`.
        """
        return self.on("validate", handler)


register_widget_events(PathField, _PATHFIELD_EVENTS)