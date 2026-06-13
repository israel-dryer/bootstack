"""The shell composite — wires `NavModel` to the region layout (single-tier).

`Shell` ties Layer 1 (`ShellLayout` regions) to Layer 2 (`NavModel`) through a
single Layer 3 provider that fills the sidebar + content for the one implicit
workspace. The `NavModel` is the single source of truth; the view reacts to its
notifications.

One provider per workspace, chosen lazily and mutually exclusive:

- `add_page()` (with `add_header`/`add_separator`/`add_footer_page`) → the static
  provider — authored items, each with its own authored page.
- `list_nav(source=...)` + `@detail` → the flat data-bound provider — records
  drive the sidebar, selection re-renders one detail body.

Mixing the two in one workspace is an error. Workspaces / the rail and collapse
are layered on in later steps (see `docs/_dev/appshell-navigation-spec.md`).
"""

from __future__ import annotations

from typing import Any, Callable

from bootstack.events import PageChangeEvent
from bootstack.widgets._core.navmodel import NavChange, NavModel, SidebarMode
from bootstack.widgets._impl.composites.shell.layout import ShellLayout
from bootstack.widgets._impl.composites.shell.providers import (
    ListNavProvider,
    StaticProvider,
    TreeNavProvider,
)


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
        self._nav_accent = nav_accent
        self._provider: Any = None          # chosen lazily on first content call
        self._pending_data: dict | None = None
        self._prev_page: str | None = None

        self._model.subscribe(self._on_model_change)

    # ----- Provider selection (lazy + mutually exclusive) -----

    def _ensure_static(self) -> StaticProvider:
        if self._provider is None:
            self._provider = StaticProvider(accent=self._nav_accent)
            self._mount_provider()
        elif not isinstance(self._provider, StaticProvider):
            raise RuntimeError(
                "cannot mix add_page() with a data-bound provider in one workspace"
            )
        return self._provider

    def _claim_provider(self) -> None:
        if self._provider is not None:
            raise RuntimeError("this workspace already has a navigation provider")

    def _mount_provider(self) -> None:
        if not self._model.has_workspace(_DEFAULT_WORKSPACE):
            self._model.add_workspace(_DEFAULT_WORKSPACE)
        self._provider.mount(
            self.sidebar,
            self.content,
            on_select=self._on_nav_select,
            on_refresh=self._on_provider_refresh,
        )

    # ----- Static content API -----

    def add_page(self, key: str, *, text: str = "", icon=None, footer: bool = False) -> Any:
        """Add a nav item and its page; return the page frame.

        The first page added is auto-selected so the content area is never blank.

        Args:
            key: Unique key for the nav item and page.
            text: Sidebar label.
            icon: Icon name or icon-spec dict.
            footer: Pin the nav item to the sidebar footer.

        Returns:
            The page `Frame` to parent content into.

        Raises:
            ValueError: If `key` is empty or already used.
            RuntimeError: If a data-bound provider already claimed the workspace.
        """
        if not key:
            raise ValueError("page key must be non-empty")
        provider = self._ensure_static()
        if key in provider.keys():
            raise ValueError(f"duplicate page key: {key!r}")

        page = provider.add_page(key, text=text, icon=icon, footer=footer)
        if self._model.active_page() is None:
            self.navigate(key)
        return page

    def add_footer_page(self, key: str, *, text: str = "", icon=None) -> Any:
        """Add a nav item pinned to the sidebar footer and its page."""
        return self.add_page(key, text=text, icon=icon, footer=True)

    def add_header(self, text: str) -> Any:
        """Add a static section header to the sidebar."""
        return self._ensure_static().add_header(text)

    def add_separator(self) -> Any:
        """Add a separator to the sidebar."""
        return self._ensure_static().add_separator()

    # ----- Data-bound content API -----

    def list_nav(self, source: Any, *, text_field: str = "text", icon_field: str = "icon") -> Any:
        """Fill the workspace from a `DataSource` (flat master-detail).

        Pair with `@detail` to declare the body rendered for the selected record.

        Args:
            source: A `DataSourceProtocol` supplying records.
            text_field: Record field used for each item's label.
            icon_field: Record field used for each item's icon.

        Returns:
            The `ListNavProvider` (so callers may inspect it).

        Raises:
            RuntimeError: If the workspace already has a provider.
        """
        self._claim_provider()
        self._provider = ListNavProvider(
            source, text_field=text_field, icon_field=icon_field, accent=self._nav_accent
        )
        self._mount_provider()
        return self._provider

    def tree_nav(
        self,
        *,
        nodes: list | None = None,
        source: Any = None,
        parent_field: str = "parent_id",
        label_field: str = "name",
        icon_field: str = "icon",
    ) -> Any:
        """Fill the workspace from a hierarchy (tree master-detail).

        Pass `nodes=` for an inline hierarchy, or `source=`/`parent_field=` to
        project a flat adjacency-list `DataSource`. Pair with `@detail` to render
        the selected node. A tree opens with nothing selected.

        Returns:
            The `TreeNavProvider`.

        Raises:
            RuntimeError: If the workspace already has a provider.
        """
        self._claim_provider()
        self._provider = TreeNavProvider(
            nodes=nodes,
            source=source,
            parent_field=parent_field,
            label_field=label_field,
            icon_field=icon_field,
            accent=self._nav_accent,
        )
        self._mount_provider()
        return self._provider

    def detail(self, fn: Callable[[dict], Any]) -> Callable[[dict], Any]:
        """Register the detail body for a data-bound provider (decorator).

        The first record is auto-selected once the detail builder is known, so
        the content renders immediately.

        Raises:
            RuntimeError: If the active provider is not data-bound.
        """
        if self._provider is None or not hasattr(self._provider, "set_detail"):
            raise RuntimeError("detail() requires a data-bound provider (list_nav)")
        self._provider.set_detail(fn)
        if self._model.active_page() is None and self._provider.keys():
            self.navigate(self._provider.keys()[0])
        return fn

    # ----- Navigation -----

    def navigate(self, key: str, data: dict | None = None) -> None:
        """Navigate to a page/record, updating the nav selection and content.

        Args:
            key: Page or record key to navigate to.
            data: Optional data passed to the page and its change event.

        Raises:
            KeyError: If no item with that key exists.
        """
        if self._provider is None or key not in self._provider.keys():
            raise KeyError(key)
        self._pending_data = data
        # Drives _on_model_change -> view sync (no-op if already active).
        self._model.select_page(key)

    @property
    def current_page(self) -> str | None:
        """Key of the active page/record, or `None`."""
        return self._model.active_page()

    # ----- Model -> view -----

    def _on_nav_select(self, key: str) -> None:
        self._model.select_page(key)

    def _on_model_change(self, change: NavChange) -> None:
        if change.facet == "page" and change.page is not None:
            self._sync_page(change.page)

    def _on_provider_refresh(self) -> None:
        # The provider rebuilt its items from a changed source; reconcile the
        # active selection if it vanished (e.g. the selected record was deleted).
        keys = self._provider.keys()
        if keys and self._model.active_page() not in keys:
            self.navigate(keys[0])

    def _sync_page(self, key: str) -> None:
        data = self._pending_data or {}
        self._pending_data = None
        self._provider.select_visual(key)
        self._provider.show(key, data=data)
        payload = PageChangeEvent(page=key, prev_page=self._prev_page, data=dict(data))
        self._prev_page = key
        self.event_generate("<<PageChange>>", data=payload, when="tail")

    # ----- Lifecycle -----

    def destroy(self) -> None:
        """Cancel provider subscriptions, then tear down the window."""
        provider = getattr(self, "_provider", None)
        if provider is not None and hasattr(provider, "close"):
            try:
                provider.close()
            except Exception:
                pass
        super().destroy()

    # ----- Accessors -----

    @property
    def model(self) -> NavModel:
        """The navigation model (single source of truth)."""
        return self._model

    @property
    def provider(self) -> Any:
        """The active workspace's navigation provider (or `None`)."""
        return self._provider

    @property
    def pages(self) -> Any:
        """The static provider's content page deck (or `None` if data-bound)."""
        return getattr(self._provider, "pages", None)

    @property
    def nav(self) -> Any:
        """The active provider's sidebar navigation panel (or `None`)."""
        return getattr(self._provider, "nav", None)
