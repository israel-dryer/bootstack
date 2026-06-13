"""The shell composite — wires `NavModel` to the region layout.

`Shell` ties Layer 1 (`ShellLayout` regions) to Layer 2 (`NavModel`) via Layer 3
workspaces. Every workspace owns one provider mounted into its own sidebar-panel
frame and content frame; the sidebar and content regions are each a *deck* of
per-workspace frames, and switching the active workspace swaps which frames show
(the nested page-stack cascade — rail chooses the panel, the panel chooses the
content). The `NavModel` is the single source of truth; the view reacts to it.

Single-tier is the degenerate case (spec decision #1): shell-level `add_page` /
`list_nav` / `tree_nav` target an implicit default workspace, so the rail never
renders. `add_workspace()` creates additional workspaces (revealing the rail in
step 6b). The two are mutually exclusive — author one style or the other.
"""

from __future__ import annotations

from typing import Any, Callable

from bootstack.events import PageChangeEvent
from bootstack.widgets._core.navmodel import NavChange, NavModel, SidebarMode
from bootstack.widgets._impl.composites.pagestack import PageStack
from bootstack.widgets._impl.composites.shell.layout import ShellLayout
from bootstack.widgets._impl.composites.shell.rail import Rail
from bootstack.widgets._impl.composites.shell.workspace import Workspace


# Key of the implicit single workspace backing the shell-level page methods.
_DEFAULT_WORKSPACE = "__shell__"


class Shell(ShellLayout):
    """Application shell with workspace-based navigation.

    Args:
        title: Window title.
        theme: Theme name, or None for the default.
        size: Initial window size as `(width, height)`.
        undecorated: Remove OS chrome and draw a custom border.
        sidebar_mode: Initial sidebar mode (`'expanded'`/`'compact'`/`'hidden'`).
            `'compact'` (icon-only) applies only to a standalone static sidebar.
        collapsible: Allow collapsing the sidebar; binds Ctrl/Cmd-B to toggle it.
        remember_nav_state: Persist the sidebar mode + per-workspace active page
            across sessions, restoring them on the next launch.
        nav_accent: Accent token for the active nav item.
        **kwargs: Forwarded to `ShellLayout` / `App` (widths, position, etc.).
    """

    def __init__(
        self,
        *,
        title: str = "",
        theme: str | None = None,
        size: tuple[int, int] | None = None,
        undecorated: bool = False,
        sidebar_mode: SidebarMode = "expanded",
        collapsible: bool = True,
        remember_nav_state: bool = False,
        nav_accent: str = "primary",
        **kwargs: Any,
    ) -> None:
        super().__init__(
            title=title, theme=theme, size=size, undecorated=undecorated, **kwargs
        )

        self._model = NavModel(sidebar_mode=sidebar_mode)
        self._nav_accent = nav_accent
        self._collapsible = collapsible
        self._remember_nav_state = remember_nav_state
        self._initial_applied = False
        self._workspaces: dict[str, Workspace] = {}
        self._pending_data: dict | None = None
        self._prev_page: str | None = None

        # Sidebar + content are decks of per-workspace frames.
        self._panel_stack = PageStack(self.sidebar)
        self._panel_stack.pack(fill="both", expand=True)
        self._content_stack = PageStack(self.content)
        self._content_stack.pack(fill="both", expand=True)

        # The tier-1 workspace switcher (hidden until > 1 workspace).
        # NB: must NOT be named `self._rail` — that is ShellLayout's rail *region*
        # frame; shadowing it orphans the region so it never packs into the body.
        self._railnav = Rail(self.rail, on_select=self._rail_select, accent=nav_accent)
        self._railnav.pack(fill="both", expand=True)

        self._model.subscribe(self._on_model_change)

        # Ctrl/Cmd-B toggles sidebar visibility (the hamburger action).
        if self._collapsible:
            self.bind("<Control-b>", self._on_toggle_shortcut, add="+")
            self.bind("<Command-b>", self._on_toggle_shortcut, add="+")

    # ----- Workspace creation -----

    def _create_workspace(self, key: str, *, text: str = "", icon=None, is_footer: bool = False) -> Workspace:
        panel = self._panel_stack.add(key)
        content = self._content_stack.add(key)
        ws = Workspace(
            key, panel, content,
            nav_accent=self._nav_accent,
            on_select=self._workspace_select,
            on_refresh=self._workspace_refresh,
            on_first_page=self._on_first_page,
        )
        self._workspaces[key] = ws
        # The implicit default workspace never gets a rail icon (single-tier).
        if key != _DEFAULT_WORKSPACE:
            self._railnav.add_workspace(key, icon=icon, text=text, footer=is_footer)
        self._model.add_workspace(key, text=text, icon=icon, is_footer=is_footer)
        if self._model.active_workspace == key:
            self._panel_stack.navigate(key)
            self._content_stack.navigate(key)
            if key != _DEFAULT_WORKSPACE:
                self._railnav.select(key)
        return ws

    def _default_workspace(self) -> Workspace:
        if _DEFAULT_WORKSPACE not in self._workspaces:
            if self._workspaces:
                raise RuntimeError(
                    "cannot use shell-level pages together with add_workspace(); "
                    "author one style or the other"
                )
            self._create_workspace(_DEFAULT_WORKSPACE)
        return self._workspaces[_DEFAULT_WORKSPACE]

    def add_workspace(self, key: str, *, text: str = "", icon=None) -> Workspace:
        """Add a workspace (a rail icon → its own sidebar panel + content).

        Adding a second workspace reveals the rail. Mutually exclusive with the
        shell-level page methods.

        Raises:
            RuntimeError: If shell-level pages already claimed the implicit
                workspace, or the key is already used.
        """
        if _DEFAULT_WORKSPACE in self._workspaces:
            raise RuntimeError("cannot mix add_workspace() with shell-level pages")
        if key in self._workspaces:
            raise RuntimeError(f"duplicate workspace key: {key!r}")
        return self._create_workspace(key, text=text, icon=icon)

    def add_footer_workspace(self, key: str, *, text: str = "", icon=None) -> Workspace:
        """Add a workspace pinned to the bottom of the rail."""
        if _DEFAULT_WORKSPACE in self._workspaces:
            raise RuntimeError("cannot mix add_workspace() with shell-level pages")
        if key in self._workspaces:
            raise RuntimeError(f"duplicate workspace key: {key!r}")
        return self._create_workspace(key, text=text, icon=icon, is_footer=True)

    # ----- Shell-level content API (delegates to the default workspace) -----

    def add_page(self, key: str, *, text: str = "", icon=None, footer: bool = False) -> Any:
        """Add a nav item and its page in the implicit workspace."""
        return self._default_workspace().add_page(key, text=text, icon=icon, footer=footer)

    def add_footer_page(self, key: str, *, text: str = "", icon=None) -> Any:
        """Add a footer-pinned nav item and its page in the implicit workspace."""
        return self._default_workspace().add_footer_page(key, text=text, icon=icon)

    def add_header(self, text: str) -> Any:
        """Add a static section header to the implicit workspace."""
        return self._default_workspace().add_header(text)

    def add_separator(self) -> Any:
        """Add a separator to the implicit workspace."""
        return self._default_workspace().add_separator()

    def list_nav(self, source: Any, *, text_field: str = "text", icon_field: str = "icon") -> Any:
        """Fill the implicit workspace from a `DataSource` (flat master-detail)."""
        return self._default_workspace().list_nav(source, text_field=text_field, icon_field=icon_field)

    def tree_nav(self, **kwargs: Any) -> Any:
        """Fill the implicit workspace from a hierarchy (tree master-detail)."""
        return self._default_workspace().tree_nav(**kwargs)

    def detail(self, fn: Callable[[dict], Any]) -> Callable[[dict], Any]:
        """Register the implicit workspace's data-bound detail body (decorator)."""
        return self._default_workspace().detail(fn)

    # ----- Navigation -----

    def navigate(self, *args: str, data: dict | None = None) -> None:
        """Navigate to a page (single-tier) or a workspace + page (two-tier).

        `navigate(page)` selects a page in the active workspace;
        `navigate(workspace, page)` switches workspace and selects a page in it.

        Raises:
            KeyError: If the workspace or page does not exist.
            TypeError: If called with other than one or two positional keys.
        """
        if len(args) == 2:
            ws_key, page = args
            if ws_key not in self._workspaces:
                raise KeyError(ws_key)
            self._model.select_workspace(ws_key)
            self._model.show_sidebar()
            self._select_page(ws_key, page, data=data)
        elif len(args) == 1:
            ws_key = self._model.active_workspace
            if ws_key is None:
                raise RuntimeError("no active workspace to navigate")
            self._select_page(ws_key, args[0], data=data)
        else:
            raise TypeError("navigate() takes 1 (page) or 2 (workspace, page) keys")

    def _select_page(self, ws_key: str, page_key: str, *, data: dict | None = None) -> None:
        if page_key not in self._workspaces[ws_key].keys():
            raise KeyError(page_key)
        self._pending_data = data
        self._model.select_page(page_key, workspace=ws_key)

    @property
    def current_page(self) -> str | None:
        """Key of the active workspace's active page, or `None`."""
        return self._model.active_page()

    @property
    def current_workspace(self) -> str | None:
        """Key of the active workspace, or `None`."""
        return self._model.active_workspace

    # ----- Sidebar visibility / compaction -----

    def toggle_sidebar(self) -> None:
        """Toggle the sidebar between hidden and shown (the hamburger action)."""
        self._model.toggle_sidebar()

    def show_sidebar(self) -> None:
        """Show the sidebar, restoring its last non-hidden mode."""
        self._model.show_sidebar()

    def hide_sidebar(self) -> None:
        """Hide the sidebar entirely."""
        self._model.hide_sidebar()

    @property
    def sidebar_mode(self) -> SidebarMode:
        """The sidebar mode (`'hidden'`/`'compact'`/`'expanded'`).

        Setting `'compact'` only takes visual effect on a standalone static
        sidebar (no rail); otherwise it renders as expanded.
        """
        return self._model.sidebar_mode

    @sidebar_mode.setter
    def sidebar_mode(self, mode: SidebarMode) -> None:
        self._model.set_sidebar_mode(mode)

    def _can_compact_active(self) -> bool:
        """Whether the active sidebar can compact (standalone static, no rail)."""
        ws = self.workspace
        return not self._model.rail_visible and ws is not None and ws.supports_compact

    def _on_toggle_shortcut(self, _event: Any = None) -> str:
        # Collapse the sidebar as far as is useful: to icons when the active
        # sidebar can compact (standalone static — never strands the only nav),
        # otherwise hide it (a data list can't compact; under a rail the rail
        # stays as nav, so hiding is safe). The explicit toggle_sidebar()/
        # show_sidebar()/hide_sidebar() verbs remain pure visibility.
        if self._can_compact_active():
            self.sidebar_mode = (
                "expanded" if self._model.sidebar_mode == "compact" else "compact"
            )
        else:
            self.toggle_sidebar()
        return "break"

    # ----- Model -> view -----

    def _rail_select(self, ws_key: str) -> None:
        # The VS Code gesture lives in the model: active icon -> hide sidebar,
        # different icon -> switch workspace + show.
        self._model.activate_rail(ws_key)

    def _workspace_select(self, ws_key: str, page_key: str) -> None:
        self._model.select_page(page_key, workspace=ws_key)

    def _on_first_page(self, ws_key: str, page_key: str) -> None:
        if self._model.active_page(ws_key) is None:
            self._model.select_page(page_key, workspace=ws_key)

    def _workspace_refresh(self, ws_key: str) -> None:
        if ws_key != self._model.active_workspace:
            return
        ws = self._workspaces[ws_key]
        keys = ws.keys()
        if keys and self._model.active_page(ws_key) not in keys:
            self._select_page(ws_key, keys[0])

    def _on_model_change(self, change: NavChange) -> None:
        if change.facet == "page" and change.page is not None:
            if change.workspace == self._model.active_workspace:
                self._render_page(change.workspace, change.page)
        elif change.facet == "workspace" and change.workspace is not None:
            self._switch_workspace(change.workspace)
        elif change.facet == "sidebar":
            self._apply_sidebar_mode(change.sidebar_mode)
        elif change.facet == "structure":
            self._sync_rail_visibility()

    def _apply_sidebar_mode(self, mode: SidebarMode | None) -> None:
        """Reflect a sidebar mode in the view.

        `compact` (icon-only + narrower width) is gated to the standalone static
        case: it applies only when no rail is showing and the active provider
        supports it; otherwise the sidebar renders expanded.
        """
        if mode is None:
            mode = self._model.sidebar_mode
        if mode == "hidden":
            self.set_sidebar_visible(False)
            return
        self.set_sidebar_visible(True)
        ws = self.workspace
        compact = (
            mode == "compact"
            and not self._model.rail_visible
            and ws is not None
            and ws.supports_compact
        )
        # Configure the slot frame directly so the stored expanded-width token is
        # not clobbered (set_sidebar_width mutates the token).
        self.sidebar.configure(width=self._rail_width if compact else self._sidebar_width)
        if ws is not None:
            ws.set_compact(compact)

    def _render_page(self, ws_key: str, page_key: str) -> None:
        ws = self._workspaces[ws_key]
        data = self._pending_data or {}
        self._pending_data = None
        ws.select_visual(page_key)
        ws.show(page_key, data=data)
        payload = PageChangeEvent(page=page_key, prev_page=self._prev_page, data=dict(data))
        self._prev_page = page_key
        self.event_generate("<<PageChange>>", data=payload, when="tail")

    def _switch_workspace(self, ws_key: str) -> None:
        self._panel_stack.navigate(ws_key)
        self._content_stack.navigate(ws_key)
        if ws_key in self._railnav.keys():
            self._railnav.select(ws_key)
        page = self._model.active_page(ws_key)
        if page is not None:
            self._render_page(ws_key, page)

    def _sync_rail_visibility(self) -> None:
        # The rail widget is wired in step 6b; for now reflect model state only.
        self.set_rail_visible(self._model.rail_visible)

    # ----- Lifecycle -----

    def mainloop(self, n: int = 0) -> None:
        """Apply the initial (and any persisted) nav state, then run the loop."""
        self._apply_initial_state()
        super().mainloop(n=n)

    def _apply_initial_state(self) -> None:
        """Restore persisted state (if enabled) and reflect the sidebar mode.

        Runs once, just before the event loop starts — after all pages have been
        authored — so a restored page/workspace overrides the authored default
        (mirroring window-geometry restore).
        """
        if self._initial_applied:
            return
        self._initial_applied = True
        if self._remember_nav_state:
            self._restore_nav_state()
        self._apply_sidebar_mode(self._model.sidebar_mode)

    # ----- Nav-state persistence -----

    def _nav_state_path(self):
        from bootstack._core.paths import app_config_file
        return app_config_file("nav_state.json", self.settings.app_name)

    def _restore_nav_state(self) -> None:
        import json
        try:
            raw = self._nav_state_path().read_text()
            data = json.loads(raw)
        except (FileNotFoundError, OSError, json.JSONDecodeError):
            return
        if not isinstance(data, dict):
            return
        # Per-workspace remembered pages (only those still present).
        pages = data.get("active_page")
        if isinstance(pages, dict):
            for ws_key, page in pages.items():
                ws = self._workspaces.get(ws_key)
                if ws is not None and page in ws.keys():
                    self._model.select_page(page, workspace=ws_key)
        # Active workspace.
        active_ws = data.get("active_workspace")
        if isinstance(active_ws, str) and self._model.has_workspace(active_ws):
            self._model.select_workspace(active_ws)
        # Sidebar mode.
        mode = data.get("sidebar_mode")
        if mode in ("hidden", "compact", "expanded"):
            self._model.set_sidebar_mode(mode)

    def _save_nav_state(self) -> None:
        import json
        path = self._nav_state_path()
        try:
            path.parent.mkdir(parents=True, exist_ok=True)
        except OSError:
            return
        pages = {
            k: self._model.active_page(k)
            for k in self._workspaces
            if self._model.active_page(k) is not None
        }
        data = {
            "sidebar_mode": self._model.sidebar_mode,
            "active_workspace": self._model.active_workspace,
            "active_page": pages,
        }
        try:
            path.write_text(json.dumps(data))
        except OSError:
            pass

    def destroy(self) -> None:
        """Persist nav state, close provider subscriptions, then tear down."""
        if getattr(self, "_remember_nav_state", False):
            try:
                self._save_nav_state()
            except Exception:
                pass
        for ws in getattr(self, "_workspaces", {}).values():
            ws.close()
        super().destroy()

    # ----- Accessors -----

    @property
    def model(self) -> NavModel:
        """The navigation model (single source of truth)."""
        return self._model

    @property
    def workspace(self) -> Workspace | None:
        """The active workspace (or `None`)."""
        return self._workspaces.get(self._model.active_workspace)

    def workspaces(self) -> tuple[Workspace, ...]:
        """All workspaces in insertion order."""
        return tuple(self._workspaces.values())

    @property
    def provider(self) -> Any:
        """The active workspace's navigation provider (or `None`)."""
        ws = self.workspace
        return ws.provider if ws is not None else None

    @property
    def pages(self) -> Any:
        """The active static provider's content page deck (or `None`)."""
        return getattr(self.provider, "pages", None)

    @property
    def nav(self) -> Any:
        """The active provider's sidebar navigation panel (or `None`)."""
        return getattr(self.provider, "nav", None)
