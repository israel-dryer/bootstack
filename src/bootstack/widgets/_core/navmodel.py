"""Headless navigation state for the application shell.

`NavModel` is the single source of truth for shell navigation: the ordered set
of workspaces, which workspace is active, the active page *per* workspace
(persistent memory), the sidebar's `hidden -> compact -> expanded` axis, and the
detail-dock visibility. It is deliberately **Tk-free and testable headless** —
controls dispatch into it via the transition methods, and view regions subscribe
to it via `subscribe()`.

The model encodes two design invariants:

- The sidebar is a single linear axis `hidden -> compact -> expanded`, so an
  incoherent state such as "hidden but expanded" is unrepresentable.
- The rail (workspace switcher) renders only when there is more than one
  workspace, so a single-tier app is the degenerate one-workspace case with no
  branching in the consumer.

See `development/appshell-navigation-spec.md` for the full design.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Callable, Literal

from bootstack.streams import Handle


SidebarMode = Literal["hidden", "compact", "expanded"]
"""The sidebar's position on its single linear visibility/compaction axis."""

ProviderKind = Literal["pages", "list", "tree", "custom"]
"""Which navigation provider fills a workspace's sidebar panel."""

NavFacet = Literal["workspace", "page", "sidebar", "dock", "structure"]
"""Which part of the navigation state a `NavChange` describes."""


@dataclass
class WorkspaceState:
    """A workspace registered in the navigation model.

    A workspace owns one sidebar panel (filled by a single provider) and
    remembers its own active page. The rail renders one icon per workspace.
    """

    key: str
    """Unique identifier for the workspace."""
    text: str = ""
    """Rail label / tooltip text."""
    icon: str | dict | None = None
    """Rail glyph — an icon name or icon-spec dict."""
    is_footer: bool = False
    """Whether the rail icon is pinned to the bottom of the rail."""
    provider: ProviderKind = "pages"
    """The provider that fills this workspace's sidebar panel."""


@dataclass(frozen=True)
class NavChange:
    """A notification emitted to subscribers when the model changes.

    Only the field(s) relevant to `facet` are populated; subscribers filter on
    `facet` and read the corresponding field (or the model itself).
    """

    facet: NavFacet
    """Which part of the state changed."""
    workspace: str | None = None
    """The affected workspace key, for `'workspace'`/`'page'`/`'structure'`."""
    page: str | None = None
    """The newly active page key, for `'page'`."""
    sidebar_mode: SidebarMode | None = None
    """The new sidebar mode, for `'sidebar'`."""
    dock_visible: bool | None = None
    """The new dock visibility, for `'dock'`."""


class NavModel:
    """Observable, Tk-free navigation state for the shell.

    Construct empty, register workspaces with `add_workspace()`, then drive
    selection and visibility through the transition methods. Subscribe with
    `subscribe()` to react to changes.

    Args:
        sidebar_mode: Initial sidebar mode. Default `'expanded'`.
        dock_visible: Initial detail-dock visibility. Default `False`.
    """

    def __init__(
        self,
        *,
        sidebar_mode: SidebarMode = "expanded",
        dock_visible: bool = False,
    ) -> None:
        self._workspaces: list[WorkspaceState] = []
        self._index: dict[str, WorkspaceState] = {}
        self._active_workspace: str | None = None
        self._active_page: dict[str, str] = {}
        self._sidebar_mode: SidebarMode = sidebar_mode
        # The mode to restore when un-hiding; never 'hidden'.
        self._restore_mode: SidebarMode = (
            sidebar_mode if sidebar_mode != "hidden" else "expanded"
        )
        self._dock_visible: bool = dock_visible
        self._listeners: list[Callable[[NavChange], None]] = []

    # ----- Read state -----

    @property
    def workspaces(self) -> tuple[WorkspaceState, ...]:
        """All workspaces in insertion order (footers included)."""
        return tuple(self._workspaces)

    @property
    def active_workspace(self) -> str | None:
        """Key of the active workspace, or `None` if none is active."""
        return self._active_workspace

    @property
    def sidebar_mode(self) -> SidebarMode:
        """The sidebar's current position on the `hidden/compact/expanded` axis."""
        return self._sidebar_mode

    @property
    def sidebar_visible(self) -> bool:
        """Whether the sidebar is shown (i.e. not `'hidden'`)."""
        return self._sidebar_mode != "hidden"

    @property
    def dock_visible(self) -> bool:
        """Whether the detail/inspector dock is shown."""
        return self._dock_visible

    @property
    def rail_visible(self) -> bool:
        """Whether the workspace rail renders — true with more than one workspace.

        A single-tier app has one workspace, so the rail is hidden; the switcher
        is therefore optional with no branching in the consumer.
        """
        return len(self._workspaces) > 1

    def workspace(self, key: str) -> WorkspaceState:
        """Return the workspace registered under `key`.

        Raises:
            KeyError: If no workspace with that key exists.
        """
        return self._index[key]

    def has_workspace(self, key: str) -> bool:
        """Return whether a workspace is registered under `key`."""
        return key in self._index

    def active_page(self, workspace: str | None = None) -> str | None:
        """Return the remembered active page for a workspace.

        Args:
            workspace: Workspace key; defaults to the active workspace.

        Returns:
            The remembered page key, or `None` if the workspace has none yet.
        """
        ws_key = workspace if workspace is not None else self._active_workspace
        if ws_key is None:
            return None
        return self._active_page.get(ws_key)

    # ----- Transitions -----

    def add_workspace(
        self,
        key: str,
        *,
        text: str = "",
        icon: str | dict | None = None,
        is_footer: bool = False,
        provider: ProviderKind = "pages",
    ) -> WorkspaceState:
        """Register a workspace and return its state.

        The first non-footer workspace added becomes active automatically, so a
        single-tier app shows content without an explicit `select_workspace()`.

        Args:
            key: Unique workspace identifier.
            text: Rail label / tooltip.
            icon: Rail glyph (icon name or icon-spec dict).
            is_footer: Pin the rail icon to the rail bottom.
            provider: Provider kind filling the workspace's sidebar.

        Returns:
            The created `WorkspaceState`.

        Raises:
            ValueError: If `key` is empty or already registered.
        """
        if not key:
            raise ValueError("workspace key must be non-empty")
        if key in self._index:
            raise ValueError(f"duplicate workspace key: {key!r}")

        ws = WorkspaceState(
            key=key, text=text, icon=icon, is_footer=is_footer, provider=provider
        )
        self._workspaces.append(ws)
        self._index[key] = ws

        if self._active_workspace is None and not is_footer:
            self._active_workspace = key

        self._notify(NavChange(facet="structure", workspace=key))
        return ws

    def select_workspace(self, key: str) -> None:
        """Make `key` the active workspace (no effect on sidebar visibility).

        This is the lower-level primitive; `activate_rail()` layers the VS Code
        rail gesture on top.

        Raises:
            KeyError: If no workspace with that key exists.
        """
        if key not in self._index:
            raise KeyError(key)
        if key == self._active_workspace:
            return
        self._active_workspace = key
        self._notify(NavChange(facet="workspace", workspace=key))

    def select_page(self, key: str, *, workspace: str | None = None) -> None:
        """Set the active page for a workspace (its remembered page).

        Args:
            key: Page key.
            workspace: Workspace to set it on; defaults to the active workspace.

        Raises:
            KeyError: If the target workspace does not exist.
            ValueError: If there is no active workspace and none is given.
        """
        ws_key = workspace if workspace is not None else self._active_workspace
        if ws_key is None:
            raise ValueError("no active workspace to select a page on")
        if ws_key not in self._index:
            raise KeyError(ws_key)
        if self._active_page.get(ws_key) == key:
            return
        self._active_page[ws_key] = key
        self._notify(NavChange(facet="page", workspace=ws_key, page=key))

    def activate_rail(self, key: str) -> None:
        """Handle a rail icon click — the VS Code workspace-switch gesture.

        Clicking the **active** workspace's icon hides the sidebar (or shows it
        again if already hidden); clicking a **different** workspace's icon
        switches to it and shows the sidebar.

        Raises:
            KeyError: If no workspace with that key exists.
        """
        if key not in self._index:
            raise KeyError(key)
        if key == self._active_workspace:
            self.toggle_sidebar()
        else:
            self.select_workspace(key)
            self.show_sidebar()

    def set_sidebar_mode(self, mode: SidebarMode) -> None:
        """Set the sidebar mode directly.

        Setting a non-hidden mode records it as the mode to restore when the
        sidebar is next un-hidden.

        Args:
            mode: `'hidden'`, `'compact'`, or `'expanded'`.

        Raises:
            ValueError: If `mode` is not a valid sidebar mode.
        """
        if mode not in ("hidden", "compact", "expanded"):
            raise ValueError(f"invalid sidebar mode: {mode!r}")
        if mode == self._sidebar_mode:
            return
        if mode == "hidden":
            self._restore_mode = self._sidebar_mode  # current is non-hidden here
        else:
            self._restore_mode = mode
        self._sidebar_mode = mode
        self._notify(NavChange(facet="sidebar", sidebar_mode=mode))

    def show_sidebar(self) -> None:
        """Show the sidebar, restoring the last non-hidden mode."""
        if self._sidebar_mode == "hidden":
            self.set_sidebar_mode(self._restore_mode)

    def hide_sidebar(self) -> None:
        """Hide the sidebar entirely (the visibility axis)."""
        self.set_sidebar_mode("hidden")

    def toggle_sidebar(self) -> None:
        """Toggle sidebar visibility — the hamburger / shortcut action."""
        if self._sidebar_mode == "hidden":
            self.show_sidebar()
        else:
            self.hide_sidebar()

    def toggle_dock(self) -> None:
        """Toggle the detail/inspector dock visibility (its own axis)."""
        self._dock_visible = not self._dock_visible
        self._notify(NavChange(facet="dock", dock_visible=self._dock_visible))

    # ----- Subscription -----

    def subscribe(self, listener: Callable[[NavChange], None]) -> Handle:
        """Register `listener` for change notifications.

        Args:
            listener: Called with a `NavChange` on every state transition.

        Returns:
            A cancellable `Handle` (call `.cancel()`, or use as a context
            manager) that unsubscribes the listener.
        """
        self._listeners.append(listener)

        def unsubscribe() -> None:
            try:
                self._listeners.remove(listener)
            except ValueError:
                pass

        return Handle(unsubscribe)

    def _notify(self, change: NavChange) -> None:
        # Iterate a copy so a listener may unsubscribe during dispatch.
        for listener in list(self._listeners):
            listener(change)
