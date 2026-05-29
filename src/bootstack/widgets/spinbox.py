from __future__ import annotations

import tkinter
from typing import Any, Callable

from bootstack.widgets._impl.primitives.spinbox import Spinbox as _InternalSpinbox
from bootstack.widgets._core.base import PublicWidgetBase
from bootstack.widgets._core.events import register_widget_events
from bootstack.widgets._core.subscription import Subscription

_SPINBOX_EVENTS: dict[str, str] = {
    "change": "<KeyRelease>",
    "submit": "<Return>",
}


class Spinbox(PublicWidgetBase):
    """A spin-box that cycles through a fixed list or numeric range.

    Pass either `options=` for a discrete list, or `min_value=`/`max_value=`
    for a numeric range. `options=` takes precedence if both are provided.

    Args:
        value: Initial display value.
        options: Fixed list of values to cycle through.
        min_value: Minimum numeric value (used when `options=` is not set).
        max_value: Maximum numeric value.
        step: Increment between values. Default `1`.
        wrap: If True, wraps from max back to min and vice versa.
        value_format: Display format string (e.g. `'%.2f'`).
        text_signal: Reactive `Signal` linked to the displayed text.
        width: Width in character cells.
        disabled: If True, widget is non-interactive.
        density: `'default'` or `'compact'`.
        accent: Accent token.
        parent: Override the context-stack parent.
    """

    def __init__(
        self,
        value: Any = "",
        *,
        options: list[Any] | None = None,
        min_value: float | None = None,
        max_value: float | None = None,
        step: float = 1,
        wrap: bool = False,
        value_format: str | None = None,
        text_signal: Any = None,
        width: int | None = None,
        disabled: bool = False,
        density: str | None = None,
        accent: str | None = None,
        parent: Any = None,
        **kwargs: Any,
    ) -> None:
        self._parent = self._resolve_parent(parent)
        layout_kw = self._split_layout_kwargs(kwargs)

        tk_master = self._parent._child_master() if self._parent else None

        internal_kwargs: dict[str, Any] = {"wrap": wrap}
        if options is not None:
            internal_kwargs["values"] = [str(o) for o in options]
        elif min_value is not None or max_value is not None:
            if min_value is not None:
                internal_kwargs["from_"] = min_value
            if max_value is not None:
                internal_kwargs["to"] = max_value
            internal_kwargs["increment"] = step
        if value_format is not None:
            internal_kwargs["format"] = value_format
        if text_signal is not None:
            internal_kwargs["textsignal"] = text_signal
        if width is not None:
            internal_kwargs["width"] = width
        if disabled:
            internal_kwargs["state"] = "disabled"
        if density is not None:
            internal_kwargs["density"] = density
        if accent is not None:
            internal_kwargs["accent"] = accent
        # Clean up any None values accidentally set
        internal_kwargs = {k: v for k, v in internal_kwargs.items() if v is not None}
        internal_kwargs.update(kwargs)

        self._internal = _InternalSpinbox(tk_master, **internal_kwargs)

        # Seed the display value after construction in all cases.
        if value != "":
            self._internal.set(str(value))

        self._attach_to_parent(layout_kw)

    # ----- Properties -----

    @property
    def value(self) -> str:
        return self._internal.get()

    @value.setter
    def value(self, v: Any) -> None:
        self._internal.set(str(v))

    @property
    def disabled(self) -> bool:
        return str(self._internal.cget("state")) == "disabled"

    @disabled.setter
    def disabled(self, v: bool) -> None:
        self._internal.configure(state="disabled" if v else "normal")

    # ----- Event shorthands -----

    def on_change(self, handler: Callable[[tkinter.Event], Any]) -> Subscription:
        """Register a callback fired on each keystroke or spin-button click.

        Returns:
            Subscription — call `.cancel()` to unsubscribe.
        """
        return self.on("change", handler)


register_widget_events(Spinbox, _SPINBOX_EVENTS)
