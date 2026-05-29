from __future__ import annotations

from typing import Any, Callable

from bootstack.widgets._impl.composites.appshell import AppShell as _InternalAppShell
from bootstack.widgets._core.container import PACK_KEYS, normalize_fill
from bootstack.widgets._core.context import push_container, pop_container


class _PageFrame:
    """Context-manager proxy returned by `AppShell.add_page()`.

    Push onto the context stack so widgets created inside
    ``with shell.add_page(...):`` are automatically parented to the page.
    """

    def __init__(self, tk_frame: Any) -> None:
        self._internal = tk_frame

    def _child_master(self) -> Any:
        return self._internal

    def guide_layout(self, child: Any, **layout_kw: Any) -> None:
        if "fill" in layout_kw:
            layout_kw["fill"] = normalize_fill(layout_kw["fill"])
        options = {k: v for k, v in layout_kw.items() if k in PACK_KEYS}
        child._internal.pack(in_=self._internal, **options)

    def __enter__(self) -> "_PageFrame":
        push_container(self)
        return self

    def __exit__(self, exc_type: Any, exc: Any, tb: Any) -> None:
        pop_container(self)


class AppShell:
    """Application window with built-in toolbar, sidebar navigation, and page stack.

    Wraps the internal AppShell to provide the standard desktop app scaffold:
    toolbar across the top, collapsible sidebar on the left, and a page
    content area on the right.

    Use `add_page()` to register nav items and their page frames together.
    Pages support context-manager syntax so widgets inside the ``with`` block
    are automatically parented to that page.

    Args:
        title: Window title and (in undecorated mode) toolbar label.
        size: Initial window size as `(width, height)`.
        position: Initial window position as `(x, y)`.
        min_size: Minimum window size as `(width, height)`.
        max_size: Maximum window size as `(width, height)`.
        resizable: Whether the window can be resized as `(x, y)`.
        undecorated: Remove OS window decorations and use a custom chrome.
            Automatically enables `show_window_controls` and `draggable`.
            Ignored on macOS.
        show_toolbar: Show the toolbar at the top. Default `True`.
        show_window_controls: Add minimize/maximize/close buttons to the toolbar.
        draggable: Allow window dragging via the toolbar.
        toolbar_density: Toolbar button density — `'default'` or `'compact'`.
        show_nav: Show the sidebar navigation. Default `True`.
        nav_display_mode: Initial sidebar mode — `'expanded'`, `'compact'`,
            or `'minimal'`.
        nav_accent: Accent color for the active nav item. Default `'primary'`.
        settings: `AppSettings` dict or instance for theme, locale, etc.
    """

    def __init__(
        self,
        *,
        title: str = "",
        size: tuple[int, int] | None = None,
        position: tuple[int, int] | None = None,
        min_size: tuple[int, int] | None = None,
        max_size: tuple[int, int] | None = None,
        resizable: tuple[bool, bool] | None = None,
        undecorated: bool = False,
        show_toolbar: bool = True,
        show_window_controls: bool = False,
        draggable: bool = False,
        toolbar_density: str = "default",
        show_nav: bool = True,
        nav_display_mode: str = "expanded",
        nav_accent: str = "primary",
        settings: Any = None,
        **kwargs: Any,
    ) -> None:
        init_kwargs: dict[str, Any] = {
            "title": title,
            "show_toolbar": show_toolbar,
            "show_window_controls": show_window_controls,
            "draggable": draggable,
            "toolbar_density": toolbar_density,
            "show_nav": show_nav,
            "nav_display_mode": nav_display_mode,
            "nav_accent": nav_accent,
            "undecorated": undecorated,
        }
        if size is not None:
            init_kwargs["size"] = size
        if position is not None:
            init_kwargs["position"] = position
        if min_size is not None:
            init_kwargs["minsize"] = min_size
        if max_size is not None:
            init_kwargs["maxsize"] = max_size
        if resizable is not None:
            init_kwargs["resizable"] = resizable
        if settings is not None:
            init_kwargs["settings"] = settings
        init_kwargs.update(kwargs)

        self._internal = _InternalAppShell(**init_kwargs)

    def __enter__(self) -> "AppShell":
        return self

    def __exit__(self, exc_type: Any, exc: Any, tb: Any) -> None:
        try:
            self._internal.update_idletasks()
        except Exception:
            pass

    # ----- Content -----

    def add_page(
        self,
        key: str,
        *,
        text: str = "",
        icon: str | dict | None = None,
        group: str | None = None,
        is_footer: bool = False,
        scrollable: bool = False,
        **nav_kwargs: Any,
    ) -> _PageFrame:
        """Add a nav item and its page, returning a context-manager page proxy.

        Args:
            key: Unique identifier for the nav item and page.
            text: Display label in the sidebar.
            icon: Icon name or icon configuration dict.
            group: Key of the nav group to add this item to.
            is_footer: If `True`, add the item to the footer section.
            scrollable: If `True`, wrap the page in a vertical `ScrollView`.
            **nav_kwargs: Extra kwargs forwarded to the internal nav item.

        Returns:
            A `_PageFrame` context manager. Use with ``with`` to parent
            child widgets into the page automatically.
        """
        kw: dict[str, Any] = {"text": text, "scrollable": scrollable}
        if icon is not None:
            kw["icon"] = icon
        if group is not None:
            kw["group"] = group
        if is_footer:
            kw["is_footer"] = True
        kw.update(nav_kwargs)
        tk_frame = self._internal.add_page(key, **kw)
        return _PageFrame(tk_frame)

    def add_group(
        self,
        key: str,
        *,
        text: str = "",
        icon: str | dict | None = None,
        expanded: bool = False,
        **kwargs: Any,
    ) -> Any:
        """Add a collapsible nav group.

        Args:
            key: Unique identifier for the group.
            text: Display label.
            icon: Icon name or configuration.
            expanded: Initial expansion state.

        Returns:
            The internal `SideNavGroup`.
        """
        kw: dict[str, Any] = {"text": text, "is_expanded": expanded}
        if icon is not None:
            kw["icon"] = icon
        kw.update(kwargs)
        return self._internal.add_group(key, **kw)

    def add_header(self, text: str, **kwargs: Any) -> Any:
        """Add a section header to the nav sidebar.

        Args:
            text: Header text.

        Returns:
            The internal `SideNavHeader`.
        """
        return self._internal.add_header(text, **kwargs)

    def add_nav_separator(self, **kwargs: Any) -> Any:
        """Add a separator to the nav sidebar.

        Returns:
            The internal `SideNavSeparator`.
        """
        return self._internal.add_separator(**kwargs)

    # ----- Navigation -----

    def navigate(self, key: str, data: dict | None = None) -> None:
        """Navigate programmatically, updating the nav selection and page stack.

        Args:
            key: Page key to navigate to.
            data: Optional data dict passed to the page.
        """
        self._internal.navigate(key, data=data)

    def select(self, key: str, data: dict | None = None) -> None:
        """Alias for `navigate()`.

        Args:
            key: Page key to navigate to.
            data: Optional data dict passed to the page.
        """
        self._internal.navigate(key, data=data)

    # ----- Events -----

    def on_page_changed(self, callback: Callable) -> str:
        """Register a callback for `<<PageChanged>>` events.

        Args:
            callback: Called when the active page changes.

        Returns:
            Bind ID — pass to `off_page_changed()` to unsubscribe.
        """
        return self._internal.on_page_changed(callback)

    def off_page_changed(self, bind_id: str | None = None) -> None:
        """Unsubscribe from `<<PageChanged>>`.

        Args:
            bind_id: ID returned by `on_page_changed()`. If `None`, removes all.
        """
        self._internal.off_page_changed(bind_id)

    # ----- Lifecycle -----

    def run(self) -> None:
        """Show the window and start the event loop."""
        self._internal.deiconify()
        self._internal.mainloop()

    mainloop = run

    # ----- Properties -----

    @property
    def tk(self) -> Any:
        """Underlying `tk.Tk` root window. UNSUPPORTED — escape-hatch use only."""
        return self._internal

    @property
    def toolbar(self) -> Any:
        """The internal `Toolbar`, or `None` if `show_toolbar=False`.

        Note: This is the internal composite — use `command=` (not `on_click=`)
        when calling `add_button()` on it.
        """
        return self._internal.toolbar

    @property
    def nav(self) -> Any:
        """The internal `SideNav`, or `None` if `show_nav=False`."""
        return self._internal.nav

    @property
    def pages(self) -> Any:
        """The internal `PageStack`."""
        return self._internal.pages

    @property
    def current_page(self) -> str | None:
        """Key of the currently displayed page, or `None`."""
        return self._internal.current_page