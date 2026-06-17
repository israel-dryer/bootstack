from __future__ import annotations

from typing import TYPE_CHECKING, Any, Callable, Literal, Sequence, overload

if TYPE_CHECKING:
    from bootstack.images import AppIcon, Image
    from bootstack.widgets.listview import ListView
    from bootstack.widgets.tree import Tree

from bootstack._runtime.app import LocalizeMode
from bootstack.widgets._impl.composites.shell.shell import Shell as _InternalShell
from bootstack.widgets._core.app_config import AppConfigMixin, APP_CONFIG_KWARGS
from bootstack.widgets._core.base import PublicWidgetBase
from bootstack.widgets._core.events import register_widget_events
from bootstack.widgets._impl.primitives.flexframe import FlexFrame
from bootstack.widgets._core.container import place_flex_child
from bootstack.widgets._core.context import push_container, pop_container
from bootstack.widgets._core.window_controls import WindowControlsMixin
from bootstack.widgets._core.window_menu import ChromeHostMixin
from bootstack.events import (
    DisplayModeEvent,
    PageChangeEvent,
    PaneToggleEvent,
    Subscription,
    WorkspaceChangeEvent,
)
from bootstack.streams import Stream
from bootstack.widgets.statusbar import StatusBar
from bootstack.widgets.types import AccentToken, SurfaceToken, WidgetDensity, WindowStyle

SidebarMode = Literal["expanded", "compact", "hidden"]


class Page:
    """Context-manager proxy returned by `add_page()` / `panel()`.

    Pushes onto the context stack so widgets created inside
    ``with shell.add_page(...):`` are automatically parented to the page. When
    `scrollable=True`, children parent into an internal vertical `ScrollView`.
    """

    def __init__(self, tk_frame: Any, scrollable: bool = False) -> None:
        self._internal = tk_frame
        self._scroll: Any = None
        # The page content is a vertical flex frame so children flow with the
        # Row/Column vocabulary (grow / align_self). It stretches its children
        # across the width by default — page content almost always fills the
        # content area — so a page's top-level container needs no align_self.
        self._flex = FlexFrame(tk_frame, direction="vertical", horizontal_items="stretch")
        self._flex.pack(fill="both", expand=True)
        if scrollable:
            from bootstack.widgets.scrollview import ScrollView

            # The scrollview parents into this page (its `guide_layout` runs
            # while `self._scroll` is still None, placing it in the flex frame),
            # then claims subsequent children.
            self._scroll = ScrollView(parent=self, grow=True, horizontal="stretch")

    def _child_master(self) -> Any:
        if self._scroll is not None:
            return self._scroll._child_master()
        return self._flex

    def guide_layout(self, child: Any, **layout_kw: Any) -> None:
        if self._scroll is not None:
            self._scroll.guide_layout(child, **layout_kw)
            return
        place_flex_child(self._flex, child, layout_kw, "AppShell page")

    def __enter__(self) -> "Page":
        push_container(self)
        return self

    def __exit__(self, exc_type: Any, exc: Any, tb: Any) -> None:
        pop_container(self)


class Workspace:
    """Public handle for one workspace (returned by `add_workspace()`).

    A context manager exposing the same content API the shell has — so a
    single-tier app and a two-tier workspace are authored identically. Fill it
    with `add_page()` (static) or one of `list_nav()` / `tree_nav()` / `panel()`,
    then drive selection with `navigate()`.
    """

    def __init__(self, internal_ws: Any, shell: "AppShell") -> None:
        self._internal = internal_ws
        self._shell = shell

    @property
    def key(self) -> str:
        """The workspace identifier."""
        return self._internal.key

    def __enter__(self) -> "Workspace":
        return self

    def __exit__(self, exc_type: Any, exc: Any, tb: Any) -> None:
        try:
            self._shell._internal.update_idletasks()
        except Exception:
            pass

    # ----- Static content -----

    def add_page(
        self,
        key: str,
        *,
        text: str = "",
        icon: str | dict | None = None,
        scrollable: bool = False,
    ) -> Page:
        """Add a nav item and its page; return a context-manager page proxy."""
        frame = self._internal.add_page(key, text=text, icon=icon)
        return Page(frame, scrollable=scrollable)

    def add_footer_page(
        self,
        key: str,
        *,
        text: str = "",
        icon: str | dict | None = None,
        scrollable: bool = False,
    ) -> Page:
        """Add a nav item pinned to the sidebar footer and its page."""
        frame = self._internal.add_footer_page(key, text=text, icon=icon)
        return Page(frame, scrollable=scrollable)

    def add_header(self, text: str) -> None:
        """Add a plain section-label header (grouped-static)."""
        self._internal.add_header(text)

    def add_divider(self) -> None:
        """Add a divider to the sidebar."""
        self._internal.add_divider()

    def panel(self) -> Page:
        """Claim the workspace as a custom panel; return its sidebar container."""
        return Page(self._internal.panel())

    @property
    def content(self) -> Page:
        """The workspace's content region as a container for hand-driven content.

        Use with ``with ws.content:`` or ``parent=ws.content`` to place widgets
        in the content area directly — the escape hatch for custom (`panel`) mode.
        """
        host = getattr(self, "_content_host", None)
        if host is None:
            host = self._content_host = Page(self._internal.content)
        return host

    # ----- Data-bound content -----

    def list_nav(
        self,
        source: Any,
        *,
        separator: bool = False,
        density: WidgetDensity = "default",
        placeholder: str = "Select an item to view",
        chevron: bool = False,
    ) -> "ListView":
        """Fill the workspace from a `DataSource` (flat master-detail).

        Returns the `ListView` driving the sidebar — use it to read `.selection`
        or drive selection (`select_items`).
        """
        return self._internal.list_nav(
            source, separator=separator, density=density,
            placeholder=placeholder, chevron=chevron,
        ).nav

    def tree_nav(
        self,
        *,
        nodes: list | None = None,
        source: Any = None,
        parent_field: str = "parent_id",
        label_field: str = "name",
        icon_field: str = "icon",
        density: WidgetDensity = "default",
        placeholder: str = "Select an item to view",
    ) -> "Tree":
        """Fill the workspace from a hierarchy (tree master-detail).

        Declare the hierarchy inline with `nodes=` or project a flat adjacency-list
        `source=` (each row names its parent via `parent_field`). Returns the
        `Tree` driving the sidebar — use it to drive the view
        (`expand`/`expand_all`/`collapse`/`select`/`find`).
        """
        return self._internal.tree_nav(
            nodes=nodes, source=source, parent_field=parent_field,
            label_field=label_field, icon_field=icon_field,
            density=density, placeholder=placeholder,
        ).tree

    def detail(self, fn: Callable[[dict], Any]) -> Callable[[dict], Any]:
        """Register this workspace's detail renderer (decorator).

        Pairs with a data-bound sidebar (`list_nav` / `tree_nav`) to form a
        master-detail view: when the selection changes, `fn` runs with the
        selected record and rebuilds the content area. Decorate a builder that
        creates widgets the usual way — it runs inside the content frame. The
        first row is selected on load, so the detail is never empty on open.

        Args:
            fn: Builder called with the selected record — the row's `dict` (for
                `tree_nav`, the node's record `dict`). Its return value is ignored.

        Returns:
            `fn` unchanged, so it works as a decorator.
        """
        return self._internal.detail(fn)

    # ----- Navigation -----

    def navigate(self, page: str, *, data: dict | None = None) -> None:
        """Navigate to a page in this workspace."""
        self._shell._internal.navigate(self.key, page, data=data)

    @property
    def current(self) -> str | None:
        """Key of this workspace's active page, or `None`."""
        return self._shell._internal.model.active_page(self.key)


class Rail:
    """Public handle for the workspace rail (returned by `shell.rail`).

    The rail is mostly framework-driven; its public surface switches workspaces
    and observes changes. Methods are no-ops when the rail is not rendered (a
    single-workspace shell).
    """

    def __init__(self, shell: "AppShell") -> None:
        self._shell = shell

    def select(self, key: str) -> None:
        """Switch to the workspace `key` and show its sidebar."""
        model = self._shell._internal.model
        model.select_workspace(key)
        model.show_sidebar()

    @property
    def current(self) -> str | None:
        """Key of the active workspace, or `None`."""
        return self._shell._internal.current_workspace

    @overload
    def on_change(self) -> Stream: ...
    @overload
    def on_change(self, handler: Callable[[WorkspaceChangeEvent], Any]) -> Subscription: ...
    def on_change(
        self, handler: Callable[[WorkspaceChangeEvent], Any] | None = None
    ) -> Stream | Subscription:
        """Register a callback fired when the active workspace changes.

        Args:
            handler: Called with a
                :class:`~bootstack.events.WorkspaceChangeEvent`. Omit to get a
                composable :class:`~bootstack.streams.Stream`.
        """
        return self._shell.on_workspace_change(handler)


class AppShell(AppConfigMixin, WindowControlsMixin, ChromeHostMixin, PublicWidgetBase):
    """Application window with rail + swappable sidebar navigation and content.

    The shell is the standard desktop scaffold: an optional menu bar and command
    bar across the top, a navigation sidebar on the left, a content area, and an
    optional status band along the bottom. A workspace **rail** appears
    automatically once you add more than one workspace (VS Code style); with a
    single workspace the shell is a plain sidebar + content app.

    Fill the (implicit) sidebar with `add_page()` for static authored pages, or
    `list_nav()` / `tree_nav()` for data-bound master-detail. For a multi-section
    app, add named `add_workspace()` workspaces — each is authored with the same
    page API. Pages support context-manager syntax so widgets inside the ``with``
    block are parented to that page automatically.

    Like `App`, configuration is a single flat path: pass options as constructor
    kwargs and read or change them through matching `shell.*` properties (e.g.
    `shell.theme`, `shell.locale`, `shell.sidebar_mode`).

    Args:
        title: Window title and (in undecorated mode) chrome label.
        size: Initial window size as `(width, height)`.
        theme: Theme name to apply on startup (e.g. `'bootstrap-dark'`).
        icon: Title-bar and taskbar icon — an icon file path, an `Image` handle,
            or an `AppIcon`. Defaults to the bootstack icon.
        light_theme: Theme used for the light end of system-appearance tracking
            and `toggle_theme`.
        dark_theme: Theme used for the dark end of system-appearance tracking
            and `toggle_theme`.
        follow_system_appearance: If True, switch between `light_theme` and
            `dark_theme` to match the OS (currently effective on macOS).
        available_themes: Theme names to expose to theme pickers.
        locale: Locale identifier (e.g. `'en_US'`, `'de_DE'`).
        localize_mode: Localization behavior.
        window_style: Windows-only window effect, or None to disable.
        macos_quit_behavior: macOS close / Cmd+Q behavior. No-op on Win/Linux.
        remember_window_state: If True, window geometry is saved and restored.
        state_path: Optional override for the persisted window-state file.
        on_close: Handler invoked when the user clicks the window's close button.
            Return `False` to veto the close; `None` or `True` to allow it.
        position: Initial window position as `(x, y)`.
        min_size: Minimum window size as `(width, height)`.
        max_size: Maximum window size as `(width, height)`.
        resizable: Whether the window can be resized as `(x, y)`.
        scaling: Explicit UI scaling factor. When None, scaling is automatic.
        hdpi: Enable high-DPI awareness for the application. Default `True`.
        undecorated: Remove OS window decorations and draw a custom border.
            Ignored on macOS. The shell gets a built-in draggable title bar with
            min/max/close so it stays movable and closeable; add your own with
            `add_toolbar(show_window_controls=True)` to take over the chrome.
        show_sidebar: Render the sidebar region. Default `True`.
        sidebar_mode: Initial sidebar mode — `'expanded'`/`'compact'`/`'hidden'`.
            `'compact'` (icon-only) applies only to a standalone static sidebar.
        sidebar_width: Expanded sidebar width in pixels.
        rail_width: Workspace-rail (and compact-sidebar) width in pixels.
        collapsible: Allow collapsing the sidebar; binds Ctrl/Cmd-B. Default `True`.
        nav_accent: Accent for the active nav item. Defaults to `'primary'` (the
            selected nav item / rail indicator picks up the theme's primary
            accent); set another accent token to retint, or `None` for a neutral
            wash.
        rail_labels: Show a caption under each rail icon (widens the rail).
        remember_nav_state: Persist the sidebar mode and per-workspace active page
            across sessions. Default `False`.
        show_statusbar: Force the bottom status band on (otherwise it appears once
            a status segment is added). Default `False`.
    """

    def __init__(
        self,
        *,
        title: str = "",
        size: tuple[int, int] | None = None,
        theme: str | None = None,
        icon: "str | Image | AppIcon | None" = None,
        # theme
        light_theme: str = "bootstrap-light",
        dark_theme: str = "bootstrap-dark",
        follow_system_appearance: bool = False,
        available_themes: Sequence[str] = (),
        # localization
        locale: str | None = None,
        localize_mode: LocalizeMode = "auto",
        # platform / window-state persistence
        window_style: WindowStyle | str | None = "mica",
        macos_quit_behavior: Literal["native", "classic"] = "native",
        remember_window_state: bool = False,
        state_path: str | None = None,
        on_close: Callable[[], bool | None] | None = None,
        # window placement
        position: tuple[int, int] | None = None,
        min_size: tuple[int, int] | None = None,
        max_size: tuple[int, int] | None = None,
        resizable: tuple[bool, bool] | None = None,
        scaling: float | None = None,
        hdpi: bool = True,
        # region surfaces
        rail_surface: SurfaceToken | str = "chrome",
        sidebar_surface: SurfaceToken | str = "raised",
        statusbar_surface: SurfaceToken | str = "chrome",
        # scaffold / navigation
        undecorated: bool = False,
        show_sidebar: bool = True,
        sidebar_mode: Literal["expanded", "compact", "hidden"] = "expanded",
        sidebar_width: int | None = None,
        rail_width: int | None = None,
        collapsible: bool = True,
        nav_accent: AccentToken | str | None = "primary",
        nav_selection: Literal["ghost", "solid"] = "ghost",
        rail_labels: bool = False,
        remember_nav_state: bool = False,
        show_statusbar: bool = False,
        **kwargs: Any,
    ) -> None:
        self._statusbar: StatusBar | None = None
        self._rail: Rail | None = None
        self._undecorated = undecorated

        # `show_sidebar=False` is the hidden mode (the model is the truth).
        if not show_sidebar:
            sidebar_mode = "hidden"

        init_kwargs: dict[str, Any] = {
            "title": title,
            "undecorated": undecorated,
            "light_theme": light_theme,
            "dark_theme": dark_theme,
            "follow_system_appearance": follow_system_appearance,
            "available_themes": available_themes,
            "scaling": scaling,
            "hdpi": hdpi,
            "locale": locale,
            "localize_mode": localize_mode,
            "window_style": window_style,
            "macos_quit_behavior": macos_quit_behavior,
            "remember_window_state": remember_window_state,
            "state_path": state_path,
            "sidebar_mode": sidebar_mode,
            "collapsible": collapsible,
            "nav_accent": nav_accent,
            "nav_selection": nav_selection,
            "rail_labels": rail_labels,
            "remember_nav_state": remember_nav_state,
            "rail_surface": rail_surface,
            "sidebar_surface": sidebar_surface,
            "statusbar_surface": statusbar_surface,
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
        if on_close is not None:
            init_kwargs["on_close"] = on_close
        if sidebar_width is not None:
            init_kwargs["sidebar_width"] = sidebar_width
        if rail_width is not None:
            init_kwargs["rail_width"] = rail_width
        init_kwargs.update(kwargs)

        self._internal = _InternalShell(**init_kwargs)

        # Resolve the window icon AFTER the root exists (an AppIcon may resolve
        # theme tokens; a deferred Image renders against the root).
        self._app_icon_photo = None
        if icon is not None:
            from bootstack.widgets._core.image_binding import resolve_window_icon

            icon_path, icon_image = resolve_window_icon(icon)
            if icon_path is not None:
                self._internal._setup_icon(icon_path)
            elif icon_image is not None:
                self._app_icon_photo = icon_image._materialize()
                self._internal._setup_icon(self._app_icon_photo)

        if show_statusbar:
            # Materialize the band now so it is present from the first frame.
            _ = self.statusbar

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

    # ----- Chrome hooks (mount the toolbar stack into the Shell's region) -----

    def _menu_root(self) -> Any:
        # The Shell is itself a Tk root (subclasses the internal App), so the
        # native menubar and shortcut bindings attach to it.
        return self._internal

    def _ensure_toolbar_stack(self) -> Any:
        # The shell pre-builds its stacked-toolbar region as a first-class band
        # (above the body); `add_toolbar()` mounts into it rather than the base
        # mixin's content-frame stack.
        return self._internal.toolbar_stack

    # ----- Shell-level content (delegates to the implicit default workspace) ----

    def add_page(
        self,
        key: str,
        *,
        text: str = "",
        icon: str | dict | None = None,
        scrollable: bool = False,
    ) -> Page:
        """Add a nav item and its page, returning a context-manager page proxy.

        Args:
            key: Unique identifier for the nav item and page.
            text: Display label in the sidebar.
            icon: Icon name or icon configuration dict.
            scrollable: If `True`, wrap the page in a vertical `ScrollView`.

        Returns:
            A `Page` context manager. Use with ``with`` to parent child
            widgets into the page automatically.
        """
        frame = self._internal.add_page(key, text=text, icon=icon)
        return Page(frame, scrollable=scrollable)

    def add_footer_page(
        self,
        key: str,
        *,
        text: str = "",
        icon: str | dict | None = None,
        scrollable: bool = False,
    ) -> Page:
        """Add a nav item pinned to the sidebar footer and its page."""
        frame = self._internal.add_footer_page(key, text=text, icon=icon)
        return Page(frame, scrollable=scrollable)

    def add_header(self, text: str) -> None:
        """Add a plain section-label header to the sidebar (grouped-static)."""
        self._internal.add_header(text)

    def add_divider(self) -> None:
        """Add a divider to the sidebar."""
        self._internal.add_divider()

    def panel(self) -> Page:
        """Claim the implicit workspace as a custom panel; return its container."""
        return Page(self._internal.panel())

    def list_nav(
        self,
        source: Any,
        *,
        separator: bool = False,
        density: WidgetDensity = "default",
        placeholder: str = "Select an item to view",
        chevron: bool = False,
    ) -> "ListView":
        """Fill the implicit workspace from a `DataSource` (flat master-detail).

        Returns the `ListView` driving the sidebar — use it to read `.selection`
        or drive selection (`select_items`).
        """
        return self._internal.list_nav(
            source, separator=separator, density=density,
            placeholder=placeholder, chevron=chevron,
        ).nav

    def tree_nav(
        self,
        *,
        nodes: list | None = None,
        source: Any = None,
        parent_field: str = "parent_id",
        label_field: str = "name",
        icon_field: str = "icon",
        density: WidgetDensity = "default",
        placeholder: str = "Select an item to view",
    ) -> "Tree":
        """Fill the implicit workspace from a hierarchy (tree master-detail).

        Declare the hierarchy inline with `nodes=` or project a flat adjacency-list
        `source=` (each row names its parent via `parent_field`). Returns the
        `Tree` driving the sidebar — use it to drive the view
        (`expand`/`expand_all`/`collapse`/`select`/`find`).
        """
        return self._internal.tree_nav(
            nodes=nodes, source=source, parent_field=parent_field,
            label_field=label_field, icon_field=icon_field,
            density=density, placeholder=placeholder,
        ).tree

    def detail(self, fn: Callable[[dict], Any]) -> Callable[[dict], Any]:
        """Register the detail renderer for the shell's data-bound sidebar (decorator).

        The single-tier equivalent of `Workspace.detail`: pairs with a top-level
        `list_nav` / `tree_nav` to form a master-detail view. When the selection
        changes, `fn` runs with the selected record and rebuilds the content
        area. The first row is selected on load, so the detail is never empty.

        Args:
            fn: Builder called with the selected record — the row's `dict` (for
                `tree_nav`, the node's record `dict`). Its return value is ignored.

        Returns:
            `fn` unchanged, so it works as a decorator.
        """
        return self._internal.detail(fn)

    # ----- Two-tier workspaces -----

    def add_workspace(
        self, key: str, *, text: str = "", icon: str | dict | None = None
    ) -> Workspace:
        """Add a workspace (a rail icon → its own sidebar panel + content).

        Adding a second workspace reveals the rail. Mutually exclusive with the
        shell-level page methods.
        """
        return Workspace(self._internal.add_workspace(key, text=text, icon=icon), self)

    def add_footer_workspace(
        self, key: str, *, text: str = "", icon: str | dict | None = None
    ) -> Workspace:
        """Add a workspace pinned to the bottom of the rail."""
        return Workspace(
            self._internal.add_footer_workspace(key, text=text, icon=icon), self
        )

    # ----- Navigation -----

    def navigate(self, *keys: str, data: dict | None = None) -> None:
        """Navigate to a page (single-tier) or a workspace + page (two-tier).

        `navigate(page)` selects a page in the active workspace;
        `navigate(workspace, page)` switches workspace and selects a page in it.

        Args:
            *keys: One key (page) or two keys (workspace, page).
            data: Optional data dict passed to the page's change event.
        """
        self._internal.navigate(*keys, data=data)

    @property
    def current(self) -> str | None:
        """Key of the active workspace's active page, or `None`."""
        return self._internal.current_page

    @property
    def current_workspace(self) -> str | None:
        """Key of the active workspace, or `None`."""
        return self._internal.current_workspace

    # ----- Sidebar visibility / compaction -----

    def toggle_sidebar(self) -> None:
        """Toggle the sidebar between hidden and shown (the hamburger action)."""
        self._internal.toggle_sidebar()

    def show_sidebar(self) -> None:
        """Show the sidebar, restoring its last non-hidden mode."""
        self._internal.show_sidebar()

    def hide_sidebar(self) -> None:
        """Hide the sidebar entirely."""
        self._internal.hide_sidebar()

    @property
    def sidebar_mode(self) -> SidebarMode:
        """The sidebar mode (`'hidden'`/`'compact'`/`'expanded'`)."""
        return self._internal.sidebar_mode

    @sidebar_mode.setter
    def sidebar_mode(self, mode: SidebarMode) -> None:
        self._internal.sidebar_mode = mode

    # ----- Events -----

    @overload
    def on_page_change(self) -> Stream: ...
    @overload
    def on_page_change(self, handler: Callable[[PageChangeEvent], Any]) -> Subscription: ...
    def on_page_change(
        self, handler: Callable[[PageChangeEvent], Any] | None = None
    ) -> Stream | Subscription:
        """Register a callback fired when the active page changes.

        Args:
            handler: Called with a :class:`~bootstack.events.PageChangeEvent`
                (the new and previous page keys, plus any `navigate()` data).
                Omit to get a composable :class:`~bootstack.streams.Stream`.
        """
        return self.on("page_change", handler)

    @overload
    def on_workspace_change(self) -> Stream: ...
    @overload
    def on_workspace_change(
        self, handler: Callable[[WorkspaceChangeEvent], Any]
    ) -> Subscription: ...
    def on_workspace_change(
        self, handler: Callable[[WorkspaceChangeEvent], Any] | None = None
    ) -> Stream | Subscription:
        """Register a callback fired when the rail switches workspace.

        Args:
            handler: Called with a
                :class:`~bootstack.events.WorkspaceChangeEvent`. Omit to get a
                composable :class:`~bootstack.streams.Stream`.
        """
        return self.on("workspace_change", handler)

    @overload
    def on_sidebar_toggle(self) -> Stream: ...
    @overload
    def on_sidebar_toggle(self, handler: Callable[[PaneToggleEvent], Any]) -> Subscription: ...
    def on_sidebar_toggle(
        self, handler: Callable[[PaneToggleEvent], Any] | None = None
    ) -> Stream | Subscription:
        """Register a callback fired when the sidebar is shown or hidden.

        Args:
            handler: Called with a :class:`~bootstack.events.PaneToggleEvent`.
                Omit to get a composable :class:`~bootstack.streams.Stream`.
        """
        return self.on("sidebar_toggle", handler)

    @overload
    def on_sidebar_mode_change(self) -> Stream: ...
    @overload
    def on_sidebar_mode_change(
        self, handler: Callable[[DisplayModeEvent], Any]
    ) -> Subscription: ...
    def on_sidebar_mode_change(
        self, handler: Callable[[DisplayModeEvent], Any] | None = None
    ) -> Stream | Subscription:
        """Register a callback fired when the sidebar mode changes.

        Args:
            handler: Called with a :class:`~bootstack.events.DisplayModeEvent`
                (`compact` ↔ `expanded`). Omit to get a composable
                :class:`~bootstack.streams.Stream`.
        """
        return self.on("sidebar_mode_change", handler)

    # ----- Lifecycle -----

    def run(self) -> None:
        """Show the window and start the event loop."""
        self._ensure_default_titlebar()
        self._internal.deiconify()
        self._internal.mainloop()

    # ----- Region accessors -----

    @property
    def content(self) -> Page:
        """The content region as a container for hand-driven content.

        Use with ``with shell.content:`` or ``parent=shell.content`` to place
        widgets in the content area directly — the escape hatch for custom
        (`panel`) mode. Targets the active workspace's content frame, not the
        layout region (which hosts the page deck).
        """
        ws = self._internal.workspace
        frame = ws.content if ws is not None else self._internal.content
        host = getattr(self, "_content_host", None)
        if host is None or host._internal is not frame:
            host = self._content_host = Page(frame)
        return host

    @property
    def statusbar(self) -> StatusBar:
        """The bottom status band (passive status). Lazily created on first access.

        The band renders once a segment is added (or `show_statusbar=True`).
        """
        if self._statusbar is None:
            self._statusbar = StatusBar(
                _toolbar=self._internal.statusbar,
                _show=lambda: self._internal.set_statusbar_visible(True),
            )
        return self._statusbar

    @property
    def rail(self) -> Rail:
        """The workspace switcher. Methods no-op when the rail is not rendered."""
        if self._rail is None:
            self._rail = Rail(self)
        return self._rail

    @property
    def pages(self) -> Any:
        """The active static provider's content page deck (or `None`)."""
        return self._internal.pages

    @property
    def nav(self) -> Any:
        """The active provider's sidebar navigation panel (or `None`)."""
        return self._internal.nav

    @property
    def tk(self) -> Any:
        """Underlying `tk.Tk` root window. UNSUPPORTED — escape-hatch use only."""
        return self._internal


_APPSHELL_EVENTS = {
    "page_change":         "<<PageChange>>",
    "workspace_change":    "<<WorkspaceChange>>",
    "sidebar_toggle":      "<<SidebarToggle>>",
    "sidebar_mode_change": "<<SidebarModeChange>>",
}

register_widget_events(AppShell, _APPSHELL_EVENTS)
