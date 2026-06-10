from __future__ import annotations

from typing import Any, Callable

from bootstack.widgets._impl.composites.toolbar import Toolbar as _InternalToolbar
from bootstack.widgets._core.base import PublicWidgetBase
from bootstack.widgets.types import AccentToken, WidgetDensity, SurfaceToken, ButtonVariant


class Toolbar(PublicWidgetBase):
    """A horizontal strip of buttons, labels, and other widgets.

    Items are added left-to-right via `add_button()`, `add_label()`,
    `add_separator()`, `add_spacer()`, and `add_widget()`. Call
    `add_spacer()` to push subsequent items to the right side.

    Toolbars appear automatically inside `AppShell` — use this widget
    directly to build a standalone toolbar or a custom titlebar.

    Args:
        button_variant: Default variant applied to every button added via
            `add_button()`. Default `'ghost'`.
        density: Size of toolbar items. Default `'default'`.
        surface: Background surface token. Defaults to the theme's `'chrome'`
            surface.
        padding: Inner padding in pixels — an int (all sides) or a
            `(horizontal, vertical)` tuple. Defaults to `3` for default density
            and `(3, 1)` for compact.
        show_border: If `True`, draws a border around the toolbar frame.
            Default `False`.
        show_window_controls: If `True`, adds minimize, maximize, and close
            buttons to the right side. Default `False`.
        draggable: If `True`, clicking and dragging the toolbar repositions the
            window. Automatically enabled when `show_window_controls=True`.
            Default `False`.
        parent: Override the context-stack parent.
        **kwargs: Layout placement options applied by the parent container —
            `fill`, `expand`, `anchor`, `margin`, `row`, `column`, `sticky`.
            See :doc:`/tasks/layout`.
    """

    def __init__(
        self,
        *,
        button_variant: ButtonVariant = "ghost",
        density: WidgetDensity = "default",
        surface: SurfaceToken | str | None = None,
        padding: int | tuple[int, int] | None = None,
        show_border: bool = False,
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
            "show_border": show_border,
        }
        if surface is not None:
            internal_kwargs["surface"] = surface
        if padding is not None:
            internal_kwargs["padding"] = padding
        internal_kwargs.update(kwargs)

        self._internal = _InternalToolbar(tk_master, **internal_kwargs)
        self._attach_to_parent(layout_kw)

    # ----- Properties -----

    @property
    def density(self) -> WidgetDensity:
        """Current density setting for toolbar items."""
        return self._internal.density

    @property
    def button_variant(self) -> str:
        """Default variant applied to buttons added via `add_button()`."""
        return self._internal._button_variant

    # ----- Content -----

    def add_button(
        self,
        label: str | None = None,
        *,
        icon: str | None = None,
        on_click: Callable[[], Any] | None = None,
        accent: AccentToken | str | None = None,
        variant: ButtonVariant = "default",
        **kwargs: Any,
    ) -> None:
        """Add a button to the toolbar.

        When both `label` and `icon` are given, the button shows text and icon
        side by side. When only `icon` is given, the button is icon-only.

        Args:
            label: Button label text.
            icon: Icon name. When provided without `label`, renders icon-only.
            on_click: Callback fired when the button is clicked.
            accent: Color intent override.
            variant: Variant override. Falls back to the toolbar's
                `button_variant` when not specified.
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
        font: str | None = None,
        **kwargs: Any,
    ) -> None:
        """Add a non-interactive label to the toolbar.

        Args:
            text: Label text.
            icon: Icon name displayed alongside the text.
            font: Font token, e.g. ``'heading-md'`` or ``'caption'``.
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
            length: Separator height in pixels. Defaults to ``16``.
        """
        self._internal.add_separator(length=length)

    def add_spacer(self) -> None:
        """Add a flexible spacer that pushes subsequent items to the right."""
        self._internal.add_spacer()

    def add_widget(self, widget: Any, **pack_kwargs: Any) -> None:
        """Add an arbitrary widget to the toolbar.

        The widget must have been created with the toolbar as its parent, or
        pass a raw internal widget here.

        Args:
            widget: A public widget instance or raw internal widget.
            **pack_kwargs: Pack options forwarded to the widget's placement.
        """
        tk_widget = getattr(widget, "_internal", widget)
        self._internal.add_widget(tk_widget, **pack_kwargs)