from __future__ import annotations

from typing import Any, Callable

from bootstack.widgets.composites.toolbar import Toolbar as _InternalToolbar
from bootstack.widgets.public.base import PublicWidgetBase


class Toolbar(PublicWidgetBase):
    """A horizontal strip of buttons and other widgets.

    Items are added left-to-right via `add_button()`, `add_label()`,
    `add_separator()`, and `add_spacer()`. Call `add_spacer()` to push
    subsequent items to the right side.

    Args:
        button_variant: Default variant for toolbar buttons. Default `'ghost'`.
        density: Button density — `'default'` or `'compact'`.
        show_window_controls: If True, adds minimize/maximize/close buttons
            on the right side.
        draggable: If True, clicking and dragging the toolbar moves the window.
        parent: Override the context-stack parent.
    """

    def __init__(
        self,
        *,
        button_variant: str = "ghost",
        density: str = "default",
        show_window_controls: bool = False,
        draggable: bool = False,
        parent: Any = None,
        **kwargs: Any,
    ) -> None:
        self._parent = self._resolve_parent(parent)
        layout_kw = self._split_layout_kwargs(kwargs)
        tk_master = self._parent._child_master() if self._parent else None

        internal_kwargs: dict[str, Any] = {
            "button_variant": button_variant,
            "density": density,
            "show_window_controls": show_window_controls,
            "draggable": draggable,
        }
        internal_kwargs.update(kwargs)

        self._internal = _InternalToolbar(tk_master, **internal_kwargs)
        self._attach_to_parent(layout_kw)

    # ----- Content -----

    def add_button(
        self,
        label: str | None = None,
        *,
        icon: str | None = None,
        on_click: Callable[[], Any] | None = None,
        accent: str | None = None,
        variant: str | None = None,
        **kwargs: Any,
    ) -> None:
        """Add a button to the toolbar.

        Args:
            label: Button label text.
            icon: Icon name.
            on_click: Callback fired when clicked.
            accent: Accent token override.
            variant: Variant override.
        """
        kw: dict[str, Any] = {}
        if label is not None:
            kw["text"] = label
        if icon is not None:
            kw["icon"] = icon
        if on_click is not None:
            kw["command"] = on_click
        if accent is not None:
            kw["accent"] = accent
        if variant is not None:
            kw["variant"] = variant
        kw.update(kwargs)
        self._internal.add_button(**kw)

    def add_label(
        self,
        text: str | None = None,
        *,
        icon: str | None = None,
        font: Any = None,
        **kwargs: Any,
    ) -> None:
        """Add a label to the toolbar.

        Args:
            text: Label text.
            icon: Icon name.
            font: Font token.
        """
        kw: dict[str, Any] = {}
        if text is not None:
            kw["text"] = text
        if icon is not None:
            kw["icon"] = icon
        if font is not None:
            kw["font"] = font
        kw.update(kwargs)
        self._internal.add_label(**kw)

    def add_separator(self, length: int = 16) -> None:
        """Add a vertical separator.

        Args:
            length: Separator height in pixels.
        """
        self._internal.add_separator(length=length)

    def add_spacer(self) -> None:
        """Add a flexible spacer that pushes subsequent items to the right."""
        self._internal.add_spacer()

    def add_widget(self, widget: Any, **pack_kwargs: Any) -> None:
        """Add an arbitrary widget to the toolbar.

        Args:
            widget: A public widget or raw Tk widget.
            **pack_kwargs: Pack options forwarded to the widget's placement.
        """
        tk_widget = getattr(widget, "_internal", widget)
        self._internal.add_widget(tk_widget, **pack_kwargs)