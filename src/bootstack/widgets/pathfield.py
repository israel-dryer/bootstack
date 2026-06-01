from __future__ import annotations

import tkinter
from typing import overload, Any, Callable

from bootstack.widgets._impl.composites.pathentry import PathEntry as _InternalPathEntry
from bootstack.widgets._core.base import PublicWidgetBase
from bootstack.widgets._core.events import resolve_event, register_widget_events
from bootstack.widgets._core.field_mixin import FieldAddonMixin
from bootstack.widgets._core.subscription import Subscription
from bootstack.widgets._core.stream import Stream
from bootstack.widgets.textfield import _INNER_ENTRY_SEQUENCES
from bootstack.widgets.types import Event

_PATHFIELD_EVENTS: dict[str, str] = {
    "change": "<<Change>>",
    "submit": "<Return>",
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
        required: Mark field as required.
        disabled: If True, field is non-interactive.
        read_only: If True, value is visible but not editable.
        accent: Accent token for the focus ring.
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
        required: bool = False,
        disabled: bool = False,
        read_only: bool = False,
        accent: str | None = None,
        density: str | None = None,
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
        if required:
            internal_kwargs["required"] = True
        if disabled:
            internal_kwargs["state"] = "disabled"
        elif read_only:
            internal_kwargs["state"] = "readonly"
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
        widget = self._entry_widget() if sequence in _INNER_ENTRY_SEQUENCES else self._internal
        _w = widget
        if handler is None:
            from bootstack.widgets._core.stream import Stream as _Stream
            def _source(h):
                widget = self._entry_widget() if sequence in _INNER_ENTRY_SEQUENCES else self._internal
                _bid = _w.bind(sequence, h, add="+")
                return Subscription(_w, sequence, _bid)
            return _Stream(self._internal, _source=_source)
        bind_id = widget.bind(sequence, handler, add="+")
        return Subscription(widget, sequence, bind_id)

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
    def disabled(self) -> bool:
        return str(self._entry_widget().cget("state")) == "disabled"

    @disabled.setter
    def disabled(self, v: bool) -> None:
        self._internal.configure(state="disabled" if v else "normal")

    @property
    def read_only(self) -> bool:
        return str(self._entry_widget().cget("state")) == "readonly"

    @read_only.setter
    def read_only(self, v: bool) -> None:
        self._internal.configure(state="readonly" if v else "normal")

    # ----- Event shorthands -----

    @overload
    def on_change(self) -> Stream: ...
    @overload
    def on_change(self, handler: Callable[[Event], Any]) -> Subscription: ...
    def on_change(self, handler: Callable[[Event], Any] | None = None) -> Stream | Subscription:
        """Register a callback fired when the path value changes.

        Returns:
            Subscription — call `.cancel()` to unsubscribe.
        """
        return self.on("change", handler)


register_widget_events(PathField, _PATHFIELD_EVENTS)