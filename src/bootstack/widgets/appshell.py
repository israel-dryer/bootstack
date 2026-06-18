from __future__ import annotations

from typing import TYPE_CHECKING, Any, Callable, Literal, Sequence, overload

if TYPE_CHECKING:
    from bootstack.images import AppIcon, Image
    from bootstack.widgets.listview import ListView
    from bootstack.widgets.tree import Tree

from bootstack._runtime.app import LocalizeMode
from bootstack.widgets._impl.composites.shell.shell import Shell as _InternalShell
from bootstack.widgets._core.app_config import AppConfigMixin, APP_CONFIG_KWARGS
from bootstack.widgets._core.base import PublicWidgetBase, _RawTkContainer
from bootstack.widgets._core.events import register_widget_events
from bootstack.widgets._impl.primitives.flexframe import FlexFrame
from bootstack.widgets._impl.primitives.gridframe import GridFrame
from bootstack.widgets._core.container import (
    GRID_KEYS, grid_sticky, place_flex_child, _reject_legacy_child_kwargs,
    _expand_margin,
)
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
from bootstack.widgets.types import (
    AccentToken, AutoFlow, LayoutKind, Padding, SurfaceToken, WidgetDensity, WindowStyle,
)

SidebarMode = Literal["expanded", "compact", "hidden"]
NavVariant = Literal["ghost", "solid"]


class Page:
    """Context-manager proxy for a content page or custom sidebar container.

    A page IS a layout container: it accepts the same layout kwargs as
    `PageStack.add` (`layout` / `padding` / `gap` / `horizontal_items` /
    `vertical_items` / `grow_items` / `columns` / `rows` / `auto_flow`), so
    children placed inside it need no extra `Column` / `Grid` wrapper. Widgets
    created inside `with page:` parent here automatically; `scrollable=True` wraps
    the content in a vertical scroll area.

    The column default stretches children across the width (page content fills the
    content area), unlike a standalone `Column`.
    """

    def __init__(
        self,
        tk_frame: Any,
        *,
        scrollable: bool = False,
        layout: LayoutKind = "column",
        padding: Padding | None = None,
        gap: int = 0,
        horizontal_items: str | None = None,
        vertical_items: str | None = None,
        grow_items: bool = False,
        columns: int | list[int | str] | None = None,
        rows: int | list[int | str] | None = None,
        auto_flow: AutoFlow = "row",
    ) -> None:
        self._internal = tk_frame
        self._scroll: Any = None
        host = tk_frame
        if scrollable:
            from bootstack.widgets.scrollview import ScrollView

            self._scroll = ScrollView(
                parent=_RawTkContainer(tk_frame), scroll_direction="vertical"
            )
            host = self._scroll._child_master()

        # Page content fills the content area, so a column stretches its children
        # across the width by default (a standalone Column centers them).
        if horizontal_items is None:
            horizontal_items = "stretch" if layout in ("grid", "column") else "left"
        if vertical_items is None:
            vertical_items = "stretch" if layout == "grid" else "center" if layout == "row" else "top"
        self._layout = layout
        self._horizontal_items = horizontal_items
        self._vertical_items = vertical_items

        if layout in ("column", "row"):
            self._layout_frame: Any = FlexFrame(
                host, direction="vertical" if layout == "column" else "horizontal",
                padding=padding, gap=gap, horizontal_items=horizontal_items,
                vertical_items=vertical_items, grow_items=grow_items,
            )
        elif layout == "grid":
            self._layout_frame = GridFrame(
                host, columns=columns, rows=rows, padding=padding, gap=gap, auto_flow=auto_flow,
            )
        else:
            raise ValueError(f"page layout must be 'column', 'row', or 'grid', got {layout!r}")
        self._layout_frame.pack(fill="both", expand=True)

    def _child_master(self) -> Any:
        return self._layout_frame

    def guide_layout(self, child: Any, **layout_kw: Any) -> None:
        if self._layout == "grid":
            _reject_legacy_child_kwargs(layout_kw, "AppShell page")
            _expand_margin(layout_kw)
            options = {k: v for k, v in layout_kw.items() if k in GRID_KEYS}
            h = layout_kw.get("horizontal") or self._horizontal_items
            v = layout_kw.get("vertical") or self._vertical_items
            options["sticky"] = grid_sticky(h, v)
            child._internal.grid(in_=self._child_master(), **options)
            return
        place_flex_child(self._layout_frame, child, layout_kw, "AppShell page")

    def __enter__(self) -> "Page":
        push_container(self)
        return self

    def __exit__(self, exc_type: Any, exc: Any, tb: Any) -> None:
        pop_container(self)


class PageNav:
    """Authorable page-list sidebar — the handle returned by `page_nav()`.

    A page nav is a flat list of authored nav items, each paired with a content
    page. Author it with `add_page()` (and `add_header()` / `add_divider()` to
    chunk the list, `add_footer_page()` to pin an item to the bottom). Use it as a
    context manager for grouping; the items themselves are added via the handle,
    not parented into it.
    """

    def __init__(self, internal_host: Any) -> None:
        # The internal Shell (single-tier, delegates to its default workspace) or
        # internal Workspace — both expose add_page/add_header/add_divider.
        self._host = internal_host

    def __enter__(self) -> "PageNav":
        return self

    def __exit__(self, exc_type: Any, exc: Any, tb: Any) -> None:
        upd = getattr(self._host, "update_idletasks", None)
        if upd is not None:
            try:
                upd()
            except Exception:
                pass

    def add_page(
        self,
        key: str,
        *,
        text: str = "",
        icon: str | dict | None = None,
        scrollable: bool = False,
        pin_to_footer: bool = False,
        layout: LayoutKind = "column",
        padding: Padding | None = None,
        gap: int = 0,
        horizontal_items: str | None = None,
        vertical_items: str | None = None,
        grow_items: bool = False,
        columns: int | list[int | str] | None = None,
        rows: int | list[int | str] | None = None,
        auto_flow: AutoFlow = "row",
    ) -> Page:
        """Add a nav item and its content page; return a context-manager page.

        The page IS a layout container — the `layout` / `padding` / `gap` /
        `horizontal_items` / `vertical_items` / `grow_items` / `columns` / `rows` /
        `auto_flow` kwargs configure it directly (same as `PageStack.add`), so
        children inside the `with` block need no extra `Column` / `Grid` wrapper.

        Args:
            key: Unique identifier for the nav item and page.
            text: Display label in the sidebar.
            icon: Icon name or icon configuration dict.
            scrollable: If `True`, wrap the page in a vertical `ScrollView`.
            pin_to_footer: If `True`, pin the nav item to the bottom of the
                sidebar (the non-scrolling footer zone) instead of the scrolling
                main list — handy for a Settings or Account entry.
            layout: Page layout — `'column'` (default), `'row'`, or `'grid'`.
            padding: Space inside the page around its content.
            gap: Space between the page's children in pixels.
            horizontal_items: Cross/main-axis alignment of children on the x-axis.
            vertical_items: Cross/main-axis alignment of children on the y-axis.
            grow_items: For `'column'`/`'row'`, every child grows to share the axis.
            columns: Column definitions for `'grid'` layout.
            rows: Row definitions for `'grid'` layout.
            auto_flow: Grid auto-flow direction for `'grid'` layout.
        """
        frame = self._host.add_page(key, text=text, icon=icon, footer=pin_to_footer)
        return Page(
            frame, scrollable=scrollable, layout=layout, padding=padding, gap=gap,
            horizontal_items=horizontal_items, vertical_items=vertical_items,
            grow_items=grow_items, columns=columns, rows=rows, auto_flow=auto_flow,
        )

    def add_header(self, text: str) -> None:
        """Add a plain section-label header that chunks the list (grouped-static)."""
        self._host.add_header(text)

    def add_divider(self) -> None:
        """Add a divider to the list."""
        self._host.add_divider()


class _SidebarHost:
    """Mixin for anything that owns one sidebar: `AppShell` and `Workspace`.

    Exposes the four parallel provider front doors — `page_nav()` (authored
    pages), `list_nav()` / `tree_nav()` (data-bound master-detail), and
    `custom_nav()` (hand-built) — plus `detail()` and the `content` escape hatch.
    A sidebar is filled by exactly one provider; the methods are mutually
    exclusive at runtime.

    Subclasses provide `_sidebar_internal()` (the internal Shell or Workspace that
    carries the provider methods) and `_content_frame()` (the content region).
    """

    def _sidebar_internal(self) -> Any:  # pragma: no cover - overridden
        raise NotImplementedError

    def _content_frame(self) -> Any:  # pragma: no cover - overridden
        raise NotImplementedError

    def page_nav(self) -> PageNav:
        """Declare the sidebar as an authored page list; return its handle.

        Returns:
            A `PageNav` handle — author items with `add_page()` / `add_header()` /
            `add_divider()` / `add_footer_page()`.
        """
        internal = self._sidebar_internal()
        internal.page_nav()
        return PageNav(internal)

    def list_nav(
        self,
        source: Any,
        *,
        separator: bool = False,
        density: WidgetDensity = "default",
        placeholder: str = "Select an item to view",
        chevron: bool = False,
    ) -> "ListView":
        """Declare a data-bound list sidebar from a `DataSource` (flat master-detail).

        Records render their `icon`/`title`/`text` in a recycling list. Pair it
        with `@detail` to render the body for the selected record. Returns the
        `ListView` driving the sidebar — use it to read `.selection` or drive
        selection (`select_items`).

        Args:
            source: A `DataSource` (or `rows=`-compatible record list).
            separator: Draw divider lines between rows. Default `False` (flush).
            density: `'default'` (richer two-line rows) or `'compact'` (one-line).
            placeholder: Empty-state message shown when the source has no records.
            chevron: Add a per-row disclosure chevron. Default `False`.
        """
        return self._sidebar_internal().list_nav(
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
        """Declare a data-bound tree sidebar (hierarchical master-detail).

        Declare the hierarchy inline with `nodes=` or project a flat adjacency-list
        `source=` (each row names its parent via `parent_field`). Pair it with
        `@detail` to render the body for the selected node. Returns the `Tree`
        driving the sidebar — use it to drive the view
        (`expand`/`expand_all`/`collapse`/`select`/`find`).

        Args:
            nodes: Inline hierarchy as a node list, or `None` to use `source`.
            source: A flat adjacency-list `DataSource`, or `None` to use `nodes`.
            parent_field: Field naming each row's parent (for `source`).
            label_field: Field providing each node's label.
            icon_field: Field providing each node's icon name.
            density: `'default'` or `'compact'`.
            placeholder: Empty-state message shown until a node is picked.
        """
        return self._sidebar_internal().tree_nav(
            nodes=nodes, source=source, parent_field=parent_field,
            label_field=label_field, icon_field=icon_field,
            density=density, placeholder=placeholder,
        ).tree

    def custom_nav(self) -> Page:
        """Declare a hand-built sidebar; return its container.

        The escape hatch when none of the providers fit — fill the returned
        container with your own sidebar UI (e.g. a `bs.Accordion`) and drive the
        content region yourself via `content`.
        """
        return Page(self._sidebar_internal().panel())

    def detail(self, fn: Callable[[dict], Any]) -> Callable[[dict], Any]:
        """Register the detail-body renderer for a data-bound sidebar (decorator).

        Pairs with `list_nav` / `tree_nav` to form a master-detail view: when the
        selection changes, `fn` runs with the selected record and rebuilds the
        content area. The first row is selected on load, so the detail is never
        empty on open.

        Args:
            fn: Builder called with the selected record `dict` (for `tree_nav`,
                the node's record `dict`). Its return value is ignored.

        Returns:
            `fn` unchanged, so it works as a decorator.
        """
        return self._sidebar_internal().detail(fn)

    @property
    def content(self) -> Page:
        """The content region as a container for hand-driven content.

        Use with `with host.content:` or `parent=host.content` to place widgets in
        the content area directly — the escape hatch for `custom_nav` mode.
        """
        frame = self._content_frame()
        host = getattr(self, "_content_host", None)
        if host is None or host._internal is not frame:
            host = self._content_host = Page(frame)
        return host


class Workspace(_SidebarHost):
    """One workspace in a `Workbench` (returned by `add_workspace()`).

    A sidebar host (see `_SidebarHost`) plus its own `navigate()`: declare its
    sidebar with `page_nav()` / `list_nav()` / `tree_nav()` / `custom_nav()`,
    exactly as you would a single-tier `AppShell`.
    """

    def __init__(self, internal_ws: Any, internal_shell: Any) -> None:
        self._internal = internal_ws
        self._shell_internal = internal_shell

    @property
    def key(self) -> str:
        """The workspace identifier."""
        return self._internal.key

    def __enter__(self) -> "Workspace":
        return self

    def __exit__(self, exc_type: Any, exc: Any, tb: Any) -> None:
        try:
            self._shell_internal.update_idletasks()
        except Exception:
            pass

    def _sidebar_internal(self) -> Any:
        return self._internal

    def _content_frame(self) -> Any:
        return self._internal.content

    def navigate(self, page: str, *, data: dict | None = None) -> None:
        """Navigate to a page in this workspace."""
        self._shell_internal.navigate(self.key, page, data=data)

    @property
    def current(self) -> str | None:
        """Key of this workspace's active page, or `None`."""
        return self._shell_internal.model.active_page(self.key)


class Rail:
    """The workspace rail (returned by `workbench.rail`).

    The rail is mostly framework-driven; its public surface switches workspaces
    and observes changes. Methods are no-ops when the rail is not rendered (a
    single-workspace workbench).
    """

    def __init__(self, shell: "Workbench") -> None:
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


class _ShellBase(AppConfigMixin, WindowControlsMixin, ChromeHostMixin, PublicWidgetBase):
    """Shared window/chrome/lifecycle scaffolding for `AppShell` and `Workbench`.

    Private base — NOT a public type. Holds the parts both shells share: the
    internal-`Shell` construction, configuration (`shell.theme`, etc.), toolbar
    chrome, the status band, sidebar visibility, and the lifecycle. Navigation
    (sidebar hosting vs the workspace rail) lives on the concrete subclasses.
    """

    def _init_shell(
        self, init_kwargs: dict[str, Any], *, icon: Any, show_statusbar: bool
    ) -> None:
        self._statusbar: StatusBar | None = None
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
    def from_store(cls, store: Any, **overrides: Any):
        """Construct from a persisted `Store` (or plain dict).

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

    def __enter__(self):
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

    # ----- Events shared by both shells -----

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


def _build_init_kwargs(
    *,
    title: str,
    undecorated: bool,
    light_theme: str,
    dark_theme: str,
    follow_system_appearance: bool,
    available_themes: Sequence[str],
    scaling: float | None,
    hdpi: bool,
    locale: str | None,
    localize_mode: LocalizeMode,
    window_style: WindowStyle | str | None,
    macos_quit_behavior: str,
    remember_window_state: bool,
    state_path: str | None,
    sidebar_mode: SidebarMode,
    collapsible: bool,
    nav_accent: AccentToken | str | None,
    remember_nav_state: bool,
    sidebar_surface: SurfaceToken | str,
    statusbar_surface: SurfaceToken | str,
    size: tuple[int, int] | None,
    theme: str | None,
    position: tuple[int, int] | None,
    min_size: tuple[int, int] | None,
    max_size: tuple[int, int] | None,
    resizable: tuple[bool, bool] | None,
    on_close: Callable[[], bool | None] | None,
    sidebar_width: int | None,
) -> dict[str, Any]:
    """Assemble the shared internal-`Shell` kwargs (optionals omitted when None)."""
    kw: dict[str, Any] = {
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
        "remember_nav_state": remember_nav_state,
        "sidebar_surface": sidebar_surface,
        "statusbar_surface": statusbar_surface,
    }
    if size is not None:
        kw["size"] = size
    if theme is not None:
        kw["theme"] = theme
    if position is not None:
        kw["position"] = position
    if min_size is not None:
        kw["minsize"] = min_size
    if max_size is not None:
        kw["maxsize"] = max_size
    if resizable is not None:
        kw["resizable"] = resizable
    if on_close is not None:
        kw["on_close"] = on_close
    if sidebar_width is not None:
        kw["sidebar_width"] = sidebar_width
    return kw


class AppShell(_SidebarHost, _ShellBase):
    """Single-tier application window: one navigation sidebar plus content.

    The everyday desktop scaffold — an optional toolbar stack across the top, one
    navigation sidebar on the left, a content area that swaps as you navigate, and
    an optional status band along the bottom. For a multi-section app with a
    workspace rail, use :class:`Workbench` instead.

    Declare the sidebar with exactly one provider front door:
    `page_nav()` (authored pages), `list_nav()` / `tree_nav()` (data-bound
    master-detail), or `custom_nav()` (hand-built). Pages support context-manager
    syntax so widgets inside the `with` block are parented automatically.

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
        sidebar_surface: Surface token for the navigation sidebar.
        statusbar_surface: Surface token for the bottom status band.
        undecorated: Remove OS window decorations and draw a custom border.
            Ignored on macOS. The shell gets a built-in draggable title bar with
            min/max/close; add your own with `add_toolbar(show_window_controls=True)`
            to take over the chrome.
        show_sidebar: Render the sidebar region. Default `True`.
        sidebar_mode: Initial sidebar mode — `'expanded'`/`'compact'`/`'hidden'`.
            `'compact'` (icon-only) applies to an authored `page_nav` sidebar.
        sidebar_width: Expanded sidebar width in pixels.
        collapsible: Allow collapsing the sidebar; binds Ctrl/Cmd-B. Default `True`.
        nav_accent: Accent for the active nav item. Defaults to `'primary'`; set
            another accent token to retint, or `None` for a neutral wash.
        remember_nav_state: Persist the sidebar mode and active page across
            sessions. Default `False`.
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
        light_theme: str = "bootstrap-light",
        dark_theme: str = "bootstrap-dark",
        follow_system_appearance: bool = False,
        available_themes: Sequence[str] = (),
        locale: str | None = None,
        localize_mode: LocalizeMode = "auto",
        window_style: WindowStyle | str | None = "mica",
        macos_quit_behavior: Literal["native", "classic"] = "native",
        remember_window_state: bool = False,
        state_path: str | None = None,
        on_close: Callable[[], bool | None] | None = None,
        position: tuple[int, int] | None = None,
        min_size: tuple[int, int] | None = None,
        max_size: tuple[int, int] | None = None,
        resizable: tuple[bool, bool] | None = None,
        scaling: float | None = None,
        hdpi: bool = True,
        sidebar_surface: SurfaceToken | str = "raised",
        statusbar_surface: SurfaceToken | str = "chrome",
        undecorated: bool = False,
        show_sidebar: bool = True,
        sidebar_mode: SidebarMode = "expanded",
        sidebar_width: int | None = None,
        collapsible: bool = True,
        nav_accent: AccentToken | str | None = "primary",
        remember_nav_state: bool = False,
        show_statusbar: bool = False,
        **kwargs: Any,
    ) -> None:
        # `show_sidebar=False` is the hidden mode (the model is the truth).
        if not show_sidebar:
            sidebar_mode = "hidden"

        init_kwargs = _build_init_kwargs(
            title=title, undecorated=undecorated, light_theme=light_theme,
            dark_theme=dark_theme, follow_system_appearance=follow_system_appearance,
            available_themes=available_themes, scaling=scaling, hdpi=hdpi,
            locale=locale, localize_mode=localize_mode, window_style=window_style,
            macos_quit_behavior=macos_quit_behavior,
            remember_window_state=remember_window_state, state_path=state_path,
            sidebar_mode=sidebar_mode, collapsible=collapsible, nav_accent=nav_accent,
            remember_nav_state=remember_nav_state, sidebar_surface=sidebar_surface,
            statusbar_surface=statusbar_surface, size=size, theme=theme,
            position=position, min_size=min_size, max_size=max_size,
            resizable=resizable, on_close=on_close, sidebar_width=sidebar_width,
        )
        init_kwargs.update(kwargs)
        self._init_shell(init_kwargs, icon=icon, show_statusbar=show_statusbar)

    # ----- Sidebar hosting -----

    def _sidebar_internal(self) -> Any:
        return self._internal

    def _content_frame(self) -> Any:
        ws = self._internal.workspace
        return ws.content if ws is not None else self._internal.content

    def page_nav(self, *, variant: NavVariant = "ghost") -> PageNav:
        """Declare the sidebar as an authored page list; return its handle.

        Args:
            variant: How an accented selection reads — `'ghost'` (default) is a
                subtle accent wash behind full-strength text; `'solid'` fills the
                selected item with the accent and uses on-accent (white) text for
                higher emphasis. Needs `nav_accent`; with `nav_accent=None` it
                falls back to a neutral wash.

        Returns:
            A `PageNav` handle — author items with `add_page()` / `add_header()` /
            `add_divider()` / `add_footer_page()`.
        """
        self._internal.page_nav(selection=variant)
        return PageNav(self._internal)

    # ----- Navigation -----

    def navigate(self, page: str, *, data: dict | None = None) -> None:
        """Navigate to a page; the sidebar selection follows.

        Args:
            page: The page key to activate.
            data: Optional data dict passed to the page's change event.
        """
        self._internal.navigate(page, data=data)

    @property
    def current(self) -> str | None:
        """Key of the active page, or `None`."""
        return self._internal.current_page


class Workbench(_ShellBase):
    """Two-tier application window: a workspace rail plus per-workspace sidebars.

    The advanced, VS Code-style scaffold — a vertical icon **rail** of workspaces
    down the far left, each revealing its own navigation sidebar and content. Add
    workspaces with `add_workspace()`; each is itself a sidebar host, authored with
    the same `page_nav()` / `list_nav()` / `tree_nav()` / `custom_nav()` front
    doors as a single-tier :class:`AppShell`.

    For a single sidebar with no rail, use :class:`AppShell` instead.

    Args:
        title: Window title and (in undecorated mode) chrome label.
        size: Initial window size as `(width, height)`.
        theme: Theme name to apply on startup (e.g. `'bootstrap-dark'`).
        icon: Title-bar and taskbar icon — a path, an `Image`, or an `AppIcon`.
        light_theme: Theme used for the light end of system-appearance tracking.
        dark_theme: Theme used for the dark end of system-appearance tracking.
        follow_system_appearance: If True, track the OS appearance (macOS).
        available_themes: Theme names to expose to theme pickers.
        locale: Locale identifier (e.g. `'en_US'`, `'de_DE'`).
        localize_mode: Localization behavior.
        window_style: Windows-only window effect, or None to disable.
        macos_quit_behavior: macOS close / Cmd+Q behavior. No-op on Win/Linux.
        remember_window_state: If True, window geometry is saved and restored.
        state_path: Optional override for the persisted window-state file.
        on_close: Handler invoked on the window's close button. Return `False` to
            veto the close; `None` or `True` to allow it.
        position: Initial window position as `(x, y)`.
        min_size: Minimum window size as `(width, height)`.
        max_size: Maximum window size as `(width, height)`.
        resizable: Whether the window can be resized as `(x, y)`.
        scaling: Explicit UI scaling factor. When None, scaling is automatic.
        hdpi: Enable high-DPI awareness for the application. Default `True`.
        rail_surface: Surface token for the workspace rail.
        sidebar_surface: Surface token for the per-workspace navigation sidebar.
        statusbar_surface: Surface token for the bottom status band.
        undecorated: Remove OS window decorations and draw a custom border.
        show_sidebar: Render the sidebar region. Default `True`.
        sidebar_mode: Initial sidebar mode — `'expanded'`/`'hidden'`.
        sidebar_width: Expanded sidebar width in pixels.
        rail_width: Workspace-rail width in pixels.
        rail_labels: Show a caption under each rail icon (widens the rail).
        collapsible: Allow collapsing the sidebar; binds Ctrl/Cmd-B. Default `True`.
        nav_accent: Accent for the active nav item and the rail indicator. Defaults
            to `'primary'`; another token retints, or `None` for a neutral wash.
        remember_nav_state: Persist the sidebar mode and per-workspace active page
            across sessions. Default `False`.
        show_statusbar: Force the bottom status band on. Default `False`.
    """

    def __init__(
        self,
        *,
        title: str = "",
        size: tuple[int, int] | None = None,
        theme: str | None = None,
        icon: "str | Image | AppIcon | None" = None,
        light_theme: str = "bootstrap-light",
        dark_theme: str = "bootstrap-dark",
        follow_system_appearance: bool = False,
        available_themes: Sequence[str] = (),
        locale: str | None = None,
        localize_mode: LocalizeMode = "auto",
        window_style: WindowStyle | str | None = "mica",
        macos_quit_behavior: Literal["native", "classic"] = "native",
        remember_window_state: bool = False,
        state_path: str | None = None,
        on_close: Callable[[], bool | None] | None = None,
        position: tuple[int, int] | None = None,
        min_size: tuple[int, int] | None = None,
        max_size: tuple[int, int] | None = None,
        resizable: tuple[bool, bool] | None = None,
        scaling: float | None = None,
        hdpi: bool = True,
        rail_surface: SurfaceToken | str = "chrome",
        sidebar_surface: SurfaceToken | str = "raised",
        statusbar_surface: SurfaceToken | str = "chrome",
        undecorated: bool = False,
        show_sidebar: bool = True,
        sidebar_mode: SidebarMode = "expanded",
        sidebar_width: int | None = None,
        rail_width: int | None = None,
        rail_labels: bool = False,
        collapsible: bool = True,
        nav_accent: AccentToken | str | None = "primary",
        remember_nav_state: bool = False,
        show_statusbar: bool = False,
        **kwargs: Any,
    ) -> None:
        self._rail: Rail | None = None

        # `show_sidebar=False` is the hidden mode (the model is the truth).
        if not show_sidebar:
            sidebar_mode = "hidden"

        init_kwargs = _build_init_kwargs(
            title=title, undecorated=undecorated, light_theme=light_theme,
            dark_theme=dark_theme, follow_system_appearance=follow_system_appearance,
            available_themes=available_themes, scaling=scaling, hdpi=hdpi,
            locale=locale, localize_mode=localize_mode, window_style=window_style,
            macos_quit_behavior=macos_quit_behavior,
            remember_window_state=remember_window_state, state_path=state_path,
            sidebar_mode=sidebar_mode, collapsible=collapsible, nav_accent=nav_accent,
            remember_nav_state=remember_nav_state, sidebar_surface=sidebar_surface,
            statusbar_surface=statusbar_surface, size=size, theme=theme,
            position=position, min_size=min_size, max_size=max_size,
            resizable=resizable, on_close=on_close, sidebar_width=sidebar_width,
        )
        # Rail-only chrome (two-tier).
        init_kwargs["rail_surface"] = rail_surface
        init_kwargs["rail_labels"] = rail_labels
        if rail_width is not None:
            init_kwargs["rail_width"] = rail_width
        init_kwargs.update(kwargs)
        self._init_shell(init_kwargs, icon=icon, show_statusbar=show_statusbar)

    # ----- Workspaces -----

    def add_workspace(
        self,
        key: str,
        *,
        text: str = "",
        icon: str | dict | None = None,
        pin_to_footer: bool = False,
    ) -> Workspace:
        """Add a workspace — a rail icon revealing its own sidebar + content.

        The rail appears once there is more than one workspace. The returned
        `Workspace` is a sidebar host: declare its sidebar with `page_nav()` /
        `list_nav()` / `tree_nav()` / `custom_nav()`.

        Args:
            key: Unique workspace identifier.
            text: Tooltip / rail label for the workspace icon.
            icon: Rail icon name or icon configuration dict.
            pin_to_footer: If `True`, pin the rail icon to the bottom of the rail
                (the conventional spot for Settings / Account) instead of the top
                cluster.
        """
        add = self._internal.add_footer_workspace if pin_to_footer else self._internal.add_workspace
        return Workspace(add(key, text=text, icon=icon), self._internal)

    # ----- Navigation -----

    def navigate(self, workspace: str, page: str, *, data: dict | None = None) -> None:
        """Switch to `workspace` and select `page` within it.

        Args:
            workspace: The workspace key to activate.
            page: The page key to activate within that workspace.
            data: Optional data dict passed to the page's change event.
        """
        self._internal.navigate(workspace, page, data=data)

    @property
    def current(self) -> str | None:
        """Key of the active workspace's active page, or `None`."""
        return self._internal.current_page

    @property
    def current_workspace(self) -> str | None:
        """Key of the active workspace, or `None`."""
        return self._internal.current_workspace

    @property
    def rail(self) -> Rail:
        """The workspace switcher. Methods no-op when the rail is not rendered."""
        if self._rail is None:
            self._rail = Rail(self)
        return self._rail

    # ----- Events -----

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


_SHELL_EVENTS = {
    "page_change":         "<<PageChange>>",
    "sidebar_toggle":      "<<SidebarToggle>>",
    "sidebar_mode_change": "<<SidebarModeChange>>",
}
_WORKBENCH_EVENTS = dict(_SHELL_EVENTS, workspace_change="<<WorkspaceChange>>")

register_widget_events(AppShell, _SHELL_EVENTS)
register_widget_events(Workbench, _WORKBENCH_EVENTS)