"""A workspace — one sidebar panel + content, filled by one provider.

A `Workspace` owns a single navigation provider (chosen lazily and mutually
exclusive) mounted into its own sidebar-panel frame and content frame. The shell
holds one workspace per rail icon (and an implicit default workspace for the
single-tier case). Selection truth lives in the shell's `NavModel`; the workspace
reports clicks/refreshes back to the shell, which drives the model.

The workspace exposes the same content API the shell does — `add_page` /
`list_nav` / `tree_nav` / `@detail` / headers — so a single-tier app and a
two-tier workspace are authored identically (the spec's degenerate-case
unification).
"""

from __future__ import annotations

from typing import Any, Callable

from bootstack.widgets._impl.composites.shell.providers import (
    CustomProvider,
    ListNavProvider,
    StaticProvider,
    TreeNavProvider,
)


class Workspace:
    """One workspace's provider + sidebar-panel/content frames.

    Args:
        key: Workspace identifier.
        sidebar_panel: The frame this workspace's sidebar provider mounts into.
        content_frame: The frame this workspace's content renders into.
        nav_accent: Accent token for the active nav item.
        on_select: Called `(workspace_key, page_key)` when an item is clicked.
        on_refresh: Called `(workspace_key)` after a data-bound provider rebuilds.
        on_first_page: Called `(workspace_key, page_key)` when the workspace's
            first page is added (so the shell can auto-select it).
    """

    def __init__(
        self,
        key: str,
        sidebar_panel: Any,
        content_frame: Any,
        *,
        nav_accent: str,
        on_select: Callable[[str, str], None],
        on_refresh: Callable[[str], None],
        on_first_page: Callable[[str, str], None],
        nav_variant: str = "nav-quiet",
        nav_surface: str = "card",
    ) -> None:
        self._key = key
        self._sidebar = sidebar_panel
        self._content = content_frame
        self._nav_accent = nav_accent
        self._nav_variant = nav_variant
        self._nav_surface = nav_surface
        self._on_select = on_select
        self._on_refresh = on_refresh
        self._on_first_page = on_first_page
        self._provider: Any = None

    @property
    def key(self) -> str:
        """The workspace identifier."""
        return self._key

    @property
    def provider(self) -> Any:
        """The workspace's navigation provider (or `None`)."""
        return self._provider

    @property
    def supports_compact(self) -> bool:
        """Whether this workspace's provider can render icon-only (compact)."""
        return bool(getattr(self._provider, "supports_compact", False))

    def set_compact(self, compact: bool) -> None:
        """Render the sidebar icon-only (`compact`) or with labels."""
        if self._provider is not None and hasattr(self._provider, "set_compact"):
            self._provider.set_compact(compact)

    # ----- Provider selection (lazy + mutually exclusive) -----

    def _ensure_static(self) -> StaticProvider:
        if self._provider is None:
            self._provider = StaticProvider(
                accent=self._nav_accent, variant=self._nav_variant, surface=self._nav_surface
            )
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
        self._provider.mount(
            self._sidebar,
            self._content,
            on_select=lambda page_key: self._on_select(self._key, page_key),
            on_refresh=lambda: self._on_refresh(self._key),
        )

    # ----- Static content API -----

    def add_page(self, key: str, *, text: str = "", icon=None, footer: bool = False) -> Any:
        """Add a nav item and its page; return the page frame."""
        if not key:
            raise ValueError("page key must be non-empty")
        provider = self._ensure_static()
        if key in provider.keys():
            raise ValueError(f"duplicate page key: {key!r}")
        first = not provider.keys()
        page = provider.add_page(key, text=text, icon=icon, footer=footer)
        if first:
            self._on_first_page(self._key, key)
        return page

    def add_footer_page(self, key: str, *, text: str = "", icon=None) -> Any:
        """Add a nav item pinned to the sidebar footer and its page."""
        return self.add_page(key, text=text, icon=icon, footer=True)

    def add_header(self, text: str, *, collapsible: bool = False) -> Any:
        """Add a section header (optionally a 1-level collapsible group)."""
        return self._ensure_static().add_header(text, collapsible=collapsible)

    def add_separator(self) -> Any:
        """Add a separator to the sidebar."""
        return self._ensure_static().add_separator()

    def expand_all(self) -> None:
        """Expand every collapsible group in the sidebar (if any)."""
        if self._provider is not None and hasattr(self._provider, "expand_all"):
            self._provider.expand_all()

    def collapse_all(self) -> None:
        """Collapse every collapsible group in the sidebar (if any)."""
        if self._provider is not None and hasattr(self._provider, "collapse_all"):
            self._provider.collapse_all()

    # ----- Custom mode -----

    def panel(self) -> Any:
        """Claim the workspace as a custom panel; return its sidebar container.

        The workspace enters custom mode: no provider cascade, no compaction.
        Fill the returned container with your own sidebar UI and drive the
        content region yourself via `content`.
        """
        self._claim_provider()
        self._provider = CustomProvider()
        self._mount_provider()
        return self._provider.container

    @property
    def content(self) -> Any:
        """The workspace's content region frame (for hand-driven swapping)."""
        return self._content

    # ----- Data-bound content API -----

    def list_nav(self, source: Any, *, separator: bool = False, density: str = "default") -> Any:
        """Fill the workspace from a `DataSource` (flat master-detail).

        Records render their `icon`/`title`/`text` in a recycling `ListView`
        (which inherits the sidebar surface). `separator` draws divider lines
        between rows (default flush); `density` is `'default'`/`'compact'`
        (compact suits one-line items, default suits richer two-line items).
        """
        self._claim_provider()
        self._provider = ListNavProvider(
            source, accent=self._nav_accent, separator=separator, density=density
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
        density: str = "default",
    ) -> Any:
        """Fill the workspace from a hierarchy (tree master-detail).

        `density` is `'default'`/`'compact'`.
        """
        self._claim_provider()
        self._provider = TreeNavProvider(
            nodes=nodes,
            source=source,
            parent_field=parent_field,
            label_field=label_field,
            icon_field=icon_field,
            accent=self._nav_accent,
            density=density,
        )
        self._mount_provider()
        return self._provider

    def detail(self, fn: Callable[[dict], Any]) -> Callable[[dict], Any]:
        """Register the detail body for a data-bound provider (decorator)."""
        if self._provider is None or not hasattr(self._provider, "set_detail"):
            raise RuntimeError("detail() requires a data-bound provider (list_nav/tree_nav)")
        self._provider.set_detail(fn)
        if self._provider.keys():
            self._on_first_page(self._key, self._provider.keys()[0])
        return fn

    # ----- Provider plumbing -----

    def keys(self) -> tuple[str, ...]:
        """All selectable page/record keys this workspace exposes."""
        return self._provider.keys() if self._provider is not None else ()

    def show(self, key: str, data: dict | None = None) -> None:
        """Render content for `key` (delegates to the provider)."""
        if self._provider is not None:
            self._provider.show(key, data=data)

    def select_visual(self, key: str | None) -> None:
        """Reflect the active `key` in the sidebar selection (delegates)."""
        if self._provider is not None:
            self._provider.select_visual(key)

    def close(self) -> None:
        """Release provider resources (e.g. data-source subscriptions)."""
        if self._provider is not None and hasattr(self._provider, "close"):
            try:
                self._provider.close()
            except Exception:
                pass
