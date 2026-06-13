"""The shell composite — wires `NavModel` to the region layout (single-tier).

`Shell` ties Layer 1 (`ShellLayout` regions) to Layer 2 (`NavModel`): it puts a
content page deck in the `content` region and a `NavPanel` in the `sidebar`, and
`add_page()` registers a page + a nav item so that selecting an item swaps the
content. The `NavModel` is the single source of truth; the view reacts to its
notifications.

This step implements the single-tier path only — one implicit workspace, so the
rail stays hidden. Workspaces / the rail, data-bound providers, and collapse are
layered on in later steps (see `docs/_dev/appshell-navigation-spec.md`).
"""

from __future__ import annotations

from typing import Any

from bootstack.widgets._core.navmodel import NavChange, NavModel, SidebarMode
from bootstack.widgets._impl.composites.pagestack import PageStack
from bootstack.widgets._impl.composites.shell.layout import ShellLayout
from bootstack.widgets._impl.composites.shell.nav_panel import NavPanel


# Key of the implicit single workspace backing the shell-level page methods.
_DEFAULT_WORKSPACE = "__shell__"


class Shell(ShellLayout):
    """Application shell with single-tier page navigation.

    Args:
        title: Window title.
        theme: Theme name, or None for the default.
        size: Initial window size as `(width, height)`.
        undecorated: Remove OS chrome and draw a custom border.
        sidebar_mode: Initial sidebar mode (`'expanded'`/`'compact'`/`'hidden'`).
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
        nav_accent: str = "primary",
        **kwargs: Any,
    ) -> None:
        super().__init__(
            title=title, theme=theme, size=size, undecorated=undecorated, **kwargs
        )

        self._model = NavModel(sidebar_mode=sidebar_mode)
        self._page_keys: set[str] = set()
        self._pending_data: dict | None = None

        # Content deck (active page) + nav panel (sidebar items).
        self._pages = PageStack(self.content)
        self._pages.pack(fill="both", expand=True)
        self._nav = NavPanel(self.sidebar, on_select=self._on_nav_select, accent=nav_accent)
        self._nav.pack(fill="both", expand=True)

        # React to model changes; re-emit page changes on the shell itself.
        self._model.subscribe(self._on_model_change)
        self._pages.on_page_changed(self._reemit_page_change)

    # ----- Content API -----

    def add_page(self, key: str, *, text: str = "", icon=None) -> Any:
        """Add a nav item and its page; return the page frame.

        The first page added is auto-selected so the content area is never
        blank.

        Args:
            key: Unique key for the nav item and page.
            text: Sidebar label.
            icon: Icon name or icon-spec dict.

        Returns:
            The page `Frame` to parent content into.

        Raises:
            ValueError: If `key` is empty or already used.
        """
        if not key:
            raise ValueError("page key must be non-empty")
        if key in self._page_keys:
            raise ValueError(f"duplicate page key: {key!r}")

        if not self._model.has_workspace(_DEFAULT_WORKSPACE):
            self._model.add_workspace(_DEFAULT_WORKSPACE)

        page = self._pages.add(key)
        self._nav.add_item(key, text=text, icon=icon)
        self._page_keys.add(key)

        if self._model.active_page() is None:
            self.navigate(key)
        return page

    # ----- Navigation -----

    def navigate(self, key: str, data: dict | None = None) -> None:
        """Navigate to a page, updating the nav selection and content.

        Args:
            key: Page key to navigate to.
            data: Optional data passed to the page and its change event.

        Raises:
            KeyError: If no page with that key exists.
        """
        if key not in self._page_keys:
            raise KeyError(key)
        self._pending_data = data
        # Drives _on_model_change -> view sync (no-op if already active).
        self._model.select_page(key)

    @property
    def current_page(self) -> str | None:
        """Key of the active page, or `None`."""
        return self._model.active_page()

    # ----- Model -> view -----

    def _on_nav_select(self, key: str) -> None:
        self._model.select_page(key)

    def _on_model_change(self, change: NavChange) -> None:
        if change.facet == "page" and change.page is not None:
            self._sync_page(change.page)

    def _sync_page(self, key: str) -> None:
        data = self._pending_data
        self._pending_data = None
        self._nav.select(key)
        self._pages.navigate(key, data=data)

    def _reemit_page_change(self, event: Any) -> None:
        # Surface the PageStack's change on the shell so consumers bind one place.
        self.event_generate("<<PageChange>>", data=getattr(event, "data", None), when="tail")

    # ----- Accessors -----

    @property
    def model(self) -> NavModel:
        """The navigation model (single source of truth)."""
        return self._model

    @property
    def pages(self) -> PageStack:
        """The content page deck."""
        return self._pages

    @property
    def nav(self) -> NavPanel:
        """The sidebar navigation panel."""
        return self._nav
