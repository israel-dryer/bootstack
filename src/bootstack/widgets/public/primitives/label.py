from __future__ import annotations

from typing import Any, Callable

from bootstack.widgets.primitives.label import Label as _InternalLabel
from bootstack.widgets.primitives.badge import Badge as _InternalBadge
from bootstack.widgets.public.base import PublicWidgetBase
from bootstack.widgets.public.events import register_widget_events


class Label(PublicWidgetBase):
    """Static text or formatted value display.

    Args:
        text: Text to display.
        text_signal: Reactive `Signal` linked to the label text.
        icon: Bootstrap Icons name.
        icon_only: If True, show only the icon.
        anchor: Content alignment within the label area.
        justify: Multi-line text justification.
        padding: Inner spacing.
        width: Width in character cells.
        wrap_width: Maximum pixel width before text wraps.
        font: Font token string.
        color: Text color.
        background_color: Background color.
        relief: Border style.
        disabled: If True, widget is non-interactive.
        localize: Localization mode.
        value_format: Format spec applied to the signal value.
        accent: Accent token, e.g. `'primary'`.
        variant: Style variant.
        surface: Surface token.
        parent: Override the context-stack parent.
    """

    _internal_class = _InternalLabel

    def __init__(
        self,
        text: str = "",
        *,
        text_signal: Any = None,
        icon: str | None = None,
        icon_only: bool = False,
        anchor: str | None = None,
        justify: str | None = None,
        padding: Any = None,
        width: int | None = None,
        wrap_width: int | None = None,
        font: Any = None,
        color: str | None = None,
        background_color: str | None = None,
        relief: str | None = None,
        disabled: bool = False,
        localize: Any = None,
        value_format: Any = None,
        accent: str | None = None,
        variant: str | None = None,
        surface: str | None = None,
        parent: Any = None,
        **kwargs: Any,
    ) -> None:
        self._parent = self._resolve_parent(parent)
        layout_kw = self._split_layout_kwargs(kwargs)

        tk_master = self._parent._child_master() if self._parent else None

        internal_kwargs: dict[str, Any] = {}
        if text:
            internal_kwargs["text"] = text
        if text_signal is not None:
            internal_kwargs["textsignal"] = text_signal
        if icon is not None:
            internal_kwargs["icon"] = icon
        if icon_only:
            internal_kwargs["icon_only"] = True
        if anchor is not None:
            internal_kwargs["anchor"] = anchor
        if justify is not None:
            internal_kwargs["justify"] = justify
        if padding is not None:
            internal_kwargs["padding"] = padding
        if width is not None:
            internal_kwargs["width"] = width
        if wrap_width is not None:
            internal_kwargs["wraplength"] = wrap_width
        if font is not None:
            internal_kwargs["font"] = font
        if color is not None:
            internal_kwargs["foreground"] = color
        if background_color is not None:
            internal_kwargs["background"] = background_color
        if relief is not None:
            internal_kwargs["relief"] = relief
        if disabled:
            internal_kwargs["state"] = "disabled"
        if localize is not None:
            internal_kwargs["localize"] = localize
        if value_format is not None:
            internal_kwargs["value_format"] = value_format
        if accent is not None:
            internal_kwargs["accent"] = accent
        if variant is not None:
            internal_kwargs["variant"] = variant
        if surface is not None:
            internal_kwargs["surface"] = surface
        internal_kwargs.update(kwargs)

        self._internal = self._internal_class(tk_master, **internal_kwargs)
        self._attach_to_parent(layout_kw)

    # ----- Properties -----

    @property
    def text(self) -> str:
        return str(self._internal.cget("text"))

    @text.setter
    def text(self, value: str) -> None:
        self._internal.configure(text=value)

    @property
    def color(self) -> str:
        return str(self._internal.cget("foreground"))

    @color.setter
    def color(self, value: str) -> None:
        self._internal.configure(foreground=value)

    @property
    def disabled(self) -> bool:
        return str(self._internal.cget("state")) == "disabled"

    @disabled.setter
    def disabled(self, value: bool) -> None:
        self._internal.configure(state="disabled" if value else "normal")

    # ----- Event shorthands -----

    def on_click(self, handler: Callable[[], Any]):
        """Register a click handler.

        Returns:
            Subscription — call `.cancel()` to unsubscribe.
        """
        return self.on("click", lambda e: handler())


register_widget_events(Label, {})


class Badge(Label):
    """Compact styled pill or square for status, counts, and tags.

    Inherits all `Label` kwargs. Icon and image kwargs are accepted but
    ignored at render time — the badge style layout omits the image element.

    Args:
        text: Text to display.
        accent: Accent token, e.g. `'primary'`, `'success'`, `'danger'`.
        variant: `'square'` (default) or `'pill'`.
        parent: Override the context-stack parent.
    """

    _internal_class = _InternalBadge

    def __init__(
        self,
        text: str = "",
        *,
        accent: str = "primary",
        variant: str = "square",
        **kwargs: Any,
    ) -> None:
        super().__init__(text, accent=accent, variant=variant, **kwargs)


register_widget_events(Badge, {})
