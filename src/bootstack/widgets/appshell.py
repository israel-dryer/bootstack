from __future__ import annotations

from typing import Any, Callable, Literal, Sequence, overload

from bootstack._runtime.app import LocalizeMode
from bootstack.widgets._impl.composites.appshell import AppShell as _InternalAppShell
from bootstack.widgets._core.app_config import AppConfigMixin, APP_CONFIG_KWARGS
from bootstack.widgets._core.base import adapt_handler
from bootstack.widgets._core.container import PACK_KEYS, normalize_fill
from bootstack.widgets._core.context import push_container, pop_container
from bootstack.events import PageChangeEvent, Subscription
from bootstack.streams import Stream
from bootstack.widgets.types import Event, AccentToken, WidgetDensity


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


class AppShell(AppConfigMixin):
    """Application window with built-in toolbar, sidebar navigation, and page stack.

    Wraps the internal AppShell to provide the standard desktop app scaffold:
    toolbar across the top, collapsible sidebar on the left, and a page
    content area on the right.

    Use `add_page()` to register nav items and their page frames together.
    Pages support context-manager syntax so widgets inside the ``with`` block
    are automatically parented to that page.

    Like `App`, configuration is a single flat path: pass options as
    constructor kwargs and read or change them through matching `app.*`
    properties (e.g. `shell.theme`, `shell.locale`).

    Args:
        title: Window title and (in undecorated mode) toolbar label.
        size: Initial window size as `(width, height)`.
        theme: Theme name to apply on startup (e.g. ``'bootstrap-dark'``).
        app_author: Application author. Reserved for config-path use.
        app_version: Application version string.
        light_theme: Theme used for the light end of system-appearance
            tracking and `toggle_theme`.
        dark_theme: Theme used for the dark end of system-appearance
            tracking and `toggle_theme`.
        follow_system_appearance: If True, switch between `light_theme` and
            `dark_theme` to match the OS (currently effective on macOS).
        available_themes: Theme names to expose to theme pickers.
        inherit_surface_color: If True, child widgets inherit the parent's
            surface color.
        locale: Locale identifier (e.g. `'en_US'`, `'de_DE'`).
        localize_mode: Localization behavior — `'auto'`, `True`, or `False`.
        window_style: Windows-only window effect or None to disable.
        macos_quit_behavior: macOS close / Cmd+Q behavior — `'native'` or
            `'classic'`.
        remember_window_state: If True, window geometry is saved and restored.
        state_path: Optional override for the persisted window-state file.
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
    """

    def __init__(
        self,
        *,
        title: str = "",
        size: tuple[int, int] | None = None,
        theme: str | None = None,
        # application identity
        app_author: str | None = None,
        app_version: str | None = None,
        # theme
        light_theme: str = "bootstrap-light",
        dark_theme: str = "bootstrap-dark",
        follow_system_appearance: bool = False,
        available_themes: Sequence[str] = (),
        inherit_surface_color: bool = True,
        # localization
        locale: str | None = None,
        localize_mode: LocalizeMode = "auto",
        # platform / window-state persistence
        window_style: str | None = "mica",
        macos_quit_behavior: str = "native",
        remember_window_state: bool = False,
        state_path: str | None = None,
        # window placement
        position: tuple[int, int] | None = None,
        min_size: tuple[int, int] | None = None,
        max_size: tuple[int, int] | None = None,
        resizable: tuple[bool, bool] | None = None,
        # scaffold
        undecorated: bool = False,
        show_toolbar: bool = True,
        show_window_controls: bool = False,
        draggable: bool = False,
        toolbar_density: WidgetDensity = "default",
        show_nav: bool = True,
        nav_display_mode: Literal["expanded", "compact", "minimal"] = "expanded",
        nav_accent: AccentToken = "primary",
        **kwargs: Any,
    ) -> None:
        init_kwargs: dict[str, Any] = {
            "title": title,
            "app_author": app_author,
            "app_version": app_version,
            "light_theme": light_theme,
            "dark_theme": dark_theme,
            "follow_system_appearance": follow_system_appearance,
            "available_themes": available_themes,
            "inherit_surface_color": inherit_surface_color,
            "locale": locale,
            "localize_mode": localize_mode,
            "window_style": window_style,
            "macos_quit_behavior": macos_quit_behavior,
            "remember_window_state": remember_window_state,
            "state_path": state_path,
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
        if theme is not None:
            init_kwargs["theme"] = theme
        if position is not None:
            init_kwargs["position"] = position
        if min_size is not None:
            init_kwargs["minsize"] = min_size
        if max_size is not None:
            init_kwargs["maxsize"] = max_size
        if resizable is not None:
            init_kwargs["resizable"] = resizable
        init_kwargs.update(kwargs)

        self._internal = _InternalAppShell(**init_kwargs)

    @classmethod
    def from_store(cls, store: Any, **overrides: Any) -> "AppShell":
        """Construct an `AppShell` from a persisted `Store` (or plain dict).

        Reads configuration from `store`, tolerantly ignoring keys that are not
        valid configuration (so version skew does not raise). Explicit keyword
        `overrides` win over stored values. See `App.from_store`.
        """
        data = store.as_dict() if hasattr(store, "as_dict") else dict(store)
        kwargs = {k: v for k, v in data.items() if k in APP_CONFIG_KWARGS}
        kwargs.update(overrides)
        return cls(**kwargs)

    def _config_app(self) -> Any:
        return self._internal

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
        scrollable: bool = False,
        **nav_kwargs: Any,
    ) -> _PageFrame:
        """Add a nav item and its page, returning a context-manager page proxy.

        Args:
            key: Unique identifier for the nav item and page.
            text: Display label in the sidebar.
            icon: Icon name or icon configuration dict.
            group: Key of the nav group to add this item to.
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
        kw.update(nav_kwargs)
        tk_frame = self._internal.add_page(key, **kw)
        return _PageFrame(tk_frame)

    def add_footer_page(
        self,
        key: str,
        *,
        text: str = "",
        icon: str | dict | None = None,
        scrollable: bool = False,
        **nav_kwargs: Any,
    ) -> _PageFrame:
        """Add a nav item pinned to the sidebar footer and its page.

        Args:
            key: Unique identifier for the nav item and page.
            text: Display label in the sidebar footer.
            icon: Icon name or icon configuration dict.
            scrollable: If `True`, wrap the page in a vertical `ScrollView`.
            **nav_kwargs: Extra kwargs forwarded to the internal nav item.

        Returns:
            A `_PageFrame` context manager. Use with ``with`` to parent
            child widgets into the page automatically.
        """
        kw: dict[str, Any] = {"text": text, "scrollable": scrollable, "is_footer": True}
        if icon is not None:
            kw["icon"] = icon
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

    def add_separator(self, **kwargs: Any) -> Any:
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

    # ----- Events -----

    @overload
    def on_page_change(self) -> Stream: ...
    @overload
    def on_page_change(self, handler: Callable[[PageChangeEvent], Any]) -> Subscription: ...
    def on_page_change(self, handler: Callable[[PageChangeEvent], Any] | None = None) -> Stream | Subscription:
        """Register a callback fired when the active page changes.

        Returns:
            ``Subscription`` (with handler) or ``Stream`` (without handler).
        """
        if handler is None:
            def _source(h: Callable) -> Subscription:
                bid = self._internal.bind("<<PageChange>>", adapt_handler(h), add="+")
                return Subscription(self._internal, "<<PageChange>>", bid)
            return Stream(self._internal, _source=_source)
        bid = self._internal.bind("<<PageChange>>", adapt_handler(handler), add="+")
        return Subscription(self._internal, "<<PageChange>>", bid)

    # ----- Lifecycle -----

    def run(self) -> None:
        """Show the window and start the event loop."""
        self._internal.deiconify()
        self._internal.mainloop()

    # ----- Properties -----

    @property
    def tk(self) -> Any:
        """Underlying `tk.Tk` root window. UNSUPPORTED — escape-hatch use only."""
        return self._internal

    @property
    def toolbar(self) -> Any:
        """The internal toolbar composite, or `None` if ``show_toolbar=False``.

        Use ``command=`` (not ``on_click=``) when calling ``add_button()`` on
        this object — it exposes the internal API, not the public `Toolbar`
        wrapper.
        """
        return self._internal.toolbar

    @property
    def nav(self) -> Any:
        """The internal sidebar navigation, or `None` if ``show_nav=False``.

        Exposes the internal composite — not the public `SideNav` wrapper.
        """
        return self._internal.nav

    @property
    def pages(self) -> Any:
        """The internal `PageStack`."""
        return self._internal.pages

    @property
    def current(self) -> str | None:
        """Key of the currently displayed page, or `None`."""
        return self._internal.current_page