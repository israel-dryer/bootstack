from __future__ import annotations

from typing import TYPE_CHECKING, Any, Callable

from bootstack.widgets._impl.composites.toolbar import Toolbar as _InternalToolbar
from bootstack.widgets._core.base import PublicWidgetBase
from bootstack.widgets.types import AccentToken, WidgetDensity, SurfaceToken, ButtonVariant

if TYPE_CHECKING:
    from bootstack.widgets._impl.composites.menu.model import MenuGroup


class Toolbar(PublicWidgetBase):
    """A horizontal strip of buttons, labels, and other widgets.

    The toolbar holds an app's commands — buttons, a search box, a theme toggle.
    Items are added left-to-right via `add_button()`, `add_label()`,
    `add_divider()`, `add_spacer()`, and `add_widget()`. Call `add_spacer()` to
    push subsequent items to the right side.

    Use this widget directly to build a standalone toolbar or a custom titlebar.

    Args:
        button_variant: Default variant applied to every button added via
            `add_button()`. Default `'ghost'`.
        density: Size of toolbar items. Default `'default'`.
        surface: Background surface token. Defaults to `None` — the toolbar
            inherits the base content surface (it blends into its parent). Pass
            `'chrome'` (or another token) to tint the bar explicitly.
        padding: Inner padding in pixels — an int (all sides) or a
            `(horizontal, vertical)` tuple. Defaults to `3` for default density
            and `(3, 1)` for compact.
        show_border: If `True`, draws a border around the toolbar frame.
            Default `False`.
        show_window_controls: If `True`, adds minimize, maximize, and close
            buttons to the right side. Default `False`.
        draggable: If `True`, clicking and dragging the toolbar repositions
            the window. Automatically enabled when `show_window_controls=True`.
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
        _toolbar: Any = None,
        **kwargs: Any,
    ) -> None:
        if _toolbar is not None:
            # Adoption: wrap a pre-built internal toolbar (e.g. an AppShell's
            # titlebar band, which already carries its window controls + drag).
            self._internal = _toolbar
            self._parent = None
            return

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
        variant: ButtonVariant | None = None,
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
            variant: Variant override. When omitted, falls back to the command
                bar's `button_variant` (default `'ghost'`).
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

    def add_menu(self, text: str, *, key: str | None = None) -> "MenuGroup":
        """Add a dropdown menu (File / Edit / …) as a toolbar item.

        A menu is just another toolbar item. The returned builder is a context
        manager, so the natural form reads::

            with toolbar.add_menu("File") as file:
                file.add_action("Open", shortcut="Mod+O", on_click=open_file)
                file.add_divider()
                file.add_action("Quit", shortcut="Mod+Q", on_click=app.close)

        On Windows/Linux the menu renders as an in-window dropdown; on macOS it
        is bridged to the native global menu bar (when the toolbar is part of a
        window's chrome).

        Args:
            text: The menu's label (e.g. `'File'`).
            key: Optional stable identifier; defaults to `text`.

        Returns:
            The menu's `MenuGroup` builder (`add_action` / `add_check` /
            `add_radio` / `add_separator`; usable as a context manager).
        """
        return self._internal.add_menu(text, key=key)

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
            font: Font token, e.g. `'heading-md'` or `'caption'`.
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

    def add_divider(self, length: int = 16) -> None:
        """Add a vertical divider.

        Args:
            length: Divider height in pixels. Defaults to `16`.
        """
        self._internal.add_separator(length=length)

    def add_spacer(self) -> None:
        """Add a flexible spacer that pushes subsequent items to the right."""
        self._internal.add_spacer()

    def add_widget(self, widget_cls: Any, **kwargs: Any) -> Any:
        """Build a widget on the toolbar from its class.

        Pass a widget **class** — the bar builds it, applying its own `density`
        and `surface` (for any the class accepts) so the widget matches the rest
        of the bar, and forwarding `kwargs` to the constructor (overriding those
        defaults):

            bar.add_widget(bs.ThemeToggle)
            bar.add_widget(bs.TextField, placeholder="Search", width=24)

        To add a widget you have already built yourself, parent it onto the bar
        directly — it attaches automatically and keeps whatever you configured:

            bs.MyCustomWidget(parent=bar)

        Args:
            widget_cls: The widget class to build on the bar.
            **kwargs: Constructor arguments for the widget.

        Returns:
            The new widget instance.
        """
        self._apply_bar_defaults(widget_cls, kwargs)
        return widget_cls(parent=self, **kwargs)

    def _apply_bar_defaults(self, widget_cls: type, kwargs: dict[str, Any]) -> None:
        """Default `density`/`surface` from the bar onto a class being built, but
        only for parameters the widget actually accepts (and not if the caller
        already passed them)."""
        import inspect

        try:
            params = inspect.signature(widget_cls).parameters
        except (TypeError, ValueError):
            return
        if "density" in params:
            kwargs.setdefault("density", self._internal.density)
        if "surface" in params:
            kwargs.setdefault("surface", self._internal._surface)

    # ----- Container protocol (so `parent=toolbar` works) -----

    def _child_master(self) -> Any:
        return self._internal.content

    def guide_layout(self, child: Any, **layout_kw: Any) -> None:
        # A widget created with `parent=toolbar` is packed into the bar.
        self._internal.add_widget(child._internal)

    def __enter__(self) -> "Toolbar":
        # A *scoping* context manager (like `menubar.add_menu`): `with
        # window.add_toolbar() as tb:` reads naturally and hands back the handle,
        # but it does NOT capture bare widgets — fill the bar with `add_button` /
        # `add_menu` / `add_widget(Class, ...)` so each item inherits the bar's
        # density and surface (a constructed-then-attached widget cannot).
        return self

    def __exit__(self, exc_type: Any, exc: Any, tb: Any) -> None:
        return None

    @property
    def content(self) -> Any:
        """The bar's content frame — parent custom widgets here."""
        return self._internal.content

    def add_theme_toggle(self, **kwargs: Any) -> Any:
        """Add a `ThemeToggle` — a sun/moon button that flips the theme.

        Args:
            **kwargs: Forwarded to `ThemeToggle` — e.g. `variant`, `density`,
                `accent`, `light_icon`, `dark_icon`.

        Returns:
            The created `ThemeToggle`.
        """
        from bootstack.widgets.theme_toggle import ThemeToggle

        self._apply_bar_defaults(ThemeToggle, kwargs)
        return ThemeToggle(parent=self, **kwargs)