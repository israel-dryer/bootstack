"""Navigation providers — what fills a workspace's sidebar panel.

A provider owns one workspace's sidebar UI *and* its content-rendering strategy,
behind a small contract: populate the sidebar, report selections via an
`on_select` callback, and render content for the active key. The shell hosts one
provider per workspace, routes selections through `NavModel`, and asks the active
provider to show content. This is the seam that lets static (`add_page`) and the
data-bound providers (`list_nav`/`tree_nav`, later) be interchangeable.

`StaticProvider` is the first concrete provider: authored items, each with its
own authored page (N items -> N independent bodies), rendered through a
`PageStack`.
"""

from __future__ import annotations

from typing import Any, Callable, Protocol, runtime_checkable

from bootstack.widgets._impl.primitives.frame import Frame
from bootstack.widgets._impl.composites.pagestack import PageStack
from bootstack.widgets._impl.composites.shell.content_host import ContentHost
from bootstack.widgets._impl.composites.shell.nav_panel import NavPanel


@runtime_checkable
class NavProvider(Protocol):
    """The contract a workspace's sidebar provider fulfills.

    A provider populates the sidebar and renders content; selection truth lives
    in the shell's `NavModel`, so the provider only *reports* clicks (via the
    `on_select` callback given to `mount`) and *reflects* the active key (via
    `select_visual` / `show`).
    """

    supports_compact: bool
    """Whether the sidebar may render icon-only (compact).

    True only for the static provider, whose items carry authored icons. A
    data-bound list (`list_nav`) or hierarchy (`tree_nav`) cannot meaningfully
    compact, so theirs is False — they are hidden or shown, never icon-only.
    Compaction is also gated by the host to the standalone case (no rail).
    """

    def mount(
        self,
        sidebar: Frame,
        content: Frame,
        *,
        on_select: Callable[[str], None],
        on_refresh: Callable[[], None] | None = None,
    ) -> None:
        """Build the sidebar UI in `sidebar` and prepare the `content` region.

        `on_refresh` (optional) is invoked after the provider rebuilds its items
        from a changed source, so the host can reconcile the active selection.
        """
        ...

    def set_compact(self, compact: bool) -> None:
        """Render the sidebar icon-only (`compact`) or with labels.

        A no-op for providers where `supports_compact` is False.
        """
        ...

    def show(self, key: str, data: dict | None = None) -> None:
        """Render content for the selected `key`."""
        ...

    def select_visual(self, key: str | None) -> None:
        """Reflect the active `key` in the sidebar's selection visual."""
        ...

    def keys(self) -> tuple[str, ...]:
        """All selectable keys this provider exposes."""
        ...


class StaticProvider:
    """Static provider — authored items, each with its own authored page.

    Args:
        accent: Accent token for the active nav item.
    """

    supports_compact = True

    def __init__(self, *, accent: str = "primary", variant: str = "nav-quiet", surface: str = "card") -> None:
        self._accent = accent
        self._variant = variant
        self._surface = surface
        self._nav: NavPanel | None = None
        self._pages: PageStack | None = None
        self._keys: list[str] = []

    def mount(
        self,
        sidebar: Frame,
        content: Frame,
        *,
        on_select: Callable[[str], None],
        on_refresh: Callable[[], None] | None = None,
    ) -> None:
        # Static authoring never refreshes from a source; on_refresh is ignored.
        self._nav = NavPanel(
            sidebar, on_select=on_select, accent=self._accent,
            variant=self._variant, surface=self._surface,
        )
        self._nav.pack(fill="both", expand=True)
        self._pages = PageStack(content)
        self._pages.pack(fill="both", expand=True)

    # ----- Authoring -----

    def add_page(self, key: str, *, text: str = "", icon=None, footer: bool = False) -> Any:
        """Add a nav item and its page; return the page frame."""
        page = self._pages.add(key)
        if footer:
            self._nav.add_footer_item(key, text=text, icon=icon)
        else:
            self._nav.add_item(key, text=text, icon=icon)
        self._keys.append(key)
        return page

    def add_header(self, text: str, *, collapsible: bool = False) -> Any:
        """Add a section header (optionally a 1-level collapsible group)."""
        return self._nav.add_header(text, collapsible=collapsible)

    def expand_all(self) -> None:
        """Expand every collapsible group."""
        self._nav.expand_all()

    def collapse_all(self) -> None:
        """Collapse every collapsible group."""
        self._nav.collapse_all()

    def add_separator(self) -> Any:
        """Add a separator."""
        return self._nav.add_separator()

    # ----- Provider contract -----

    def set_compact(self, compact: bool) -> None:
        self._nav.set_compact(compact)

    def show(self, key: str, data: dict | None = None) -> None:
        self._pages.navigate(key, data=data)

    def select_visual(self, key: str | None) -> None:
        self._nav.select(key)

    def keys(self) -> tuple[str, ...]:
        return tuple(self._keys)

    # ----- Accessors -----

    @property
    def nav(self) -> NavPanel:
        """The sidebar navigation panel."""
        return self._nav

    @property
    def pages(self) -> PageStack:
        """The content page deck."""
        return self._pages


class ListNavProvider:
    """Flat, data-bound provider — a `DataSource` drives the sidebar list.

    Each record becomes a single-select nav item (keyed by record id); selecting
    one re-renders a single `@detail` body parameterized by that record. The
    detail body receives the **public record dict** (the universal `.selection`
    shape) — not a bespoke node object.

    Args:
        source: A `DataSourceProtocol` supplying records.
        text_field: Record field used for the item label.
        icon_field: Record field used for the item icon.
        accent: Accent token for the active nav item.
    """

    # A label-less data list is a poor nav, so list_nav is hidden-or-shown,
    # never icon-only (spec Revision 2 / R1).
    supports_compact = False

    def __init__(
        self,
        source: Any,
        *,
        text_field: str = "text",
        icon_field: str = "icon",
        accent: str = "primary",
        surface: str = "card",
    ) -> None:
        self._source = source
        self._text_field = text_field
        self._icon_field = icon_field
        self._accent = accent
        self._surface = surface
        self._nav: NavPanel | None = None
        self._host: ContentHost | None = None
        self._detail: Callable[[dict], Any] | None = None
        self._records: dict[str, dict] = {}
        self._order: list[str] = []
        self._on_refresh: Callable[[], None] | None = None
        self._sub: Any = None

    def mount(
        self,
        sidebar: Frame,
        content: Frame,
        *,
        on_select: Callable[[str], None],
        on_refresh: Callable[[], None] | None = None,
    ) -> None:
        self._on_refresh = on_refresh
        self._nav = NavPanel(
            sidebar, on_select=on_select, accent=self._accent, surface=self._surface
        )
        self._nav.pack(fill="both", expand=True)
        self._host = ContentHost(content)
        self._populate()
        # Live updates: rebuild items when the source changes (delivered on the
        # UI thread by the data layer). Stored so it can be cancelled on close.
        self._sub = self._source.on_change(self._on_source_change)

    def set_detail(self, fn: Callable[[dict], Any]) -> None:
        """Register the parameterized detail body builder."""
        self._detail = fn

    def _read(self) -> dict[str, dict]:
        """Read all current public records keyed by id, in source order."""
        src = self._source
        out: dict[str, dict] = {}
        for raw in src.page_slice(0, src.count):
            rec = src._public_record(raw)
            out[str(rec.get("id"))] = rec
        return out

    def _label(self, rec: dict) -> str:
        return str(rec.get(self._text_field, ""))

    def _icon(self, rec: dict):
        return rec.get(self._icon_field)

    def _populate(self) -> None:
        self._records = self._read()
        self._order = list(self._records)
        for key, rec in self._records.items():
            self._nav.add_item(key, text=self._label(rec), icon=self._icon(rec))

    def _on_source_change(self, _event: Any = None) -> None:
        """Reconcile the sidebar against the source (add / remove / update).

        Incremental: removed records drop their items, new records append, and
        changed labels/icons update in place. Source reordering is not reflected
        (new items append) — acceptable for a small nav list.
        """
        new = self._read()
        old_keys = set(self._records)
        new_keys = set(new)

        for key in old_keys - new_keys:
            self._nav.remove_item(key)
            self._records.pop(key, None)
            if key in self._order:
                self._order.remove(key)

        updated: set[str] = set()
        for key, rec in new.items():
            if key not in self._records:
                self._order.append(key)
                self._nav.add_item(key, text=self._label(rec), icon=self._icon(rec))
            else:
                old = self._records[key]
                if self._label(old) != self._label(rec) or self._icon(old) != self._icon(rec):
                    self._nav.update_item(key, text=self._label(rec), icon=self._icon(rec))
                if old != rec:
                    updated.add(key)
            self._records[key] = rec

        # If the selected record's data changed, re-render its detail in place
        # (only then — no flicker on unrelated changes).
        sel = self._nav.selected
        if sel is not None and sel in updated:
            self.show(sel)

        if self._on_refresh is not None:
            self._on_refresh()

    def close(self) -> None:
        """Cancel the source subscription."""
        if self._sub is not None:
            try:
                self._sub.cancel()
            except Exception:
                pass
            self._sub = None

    # ----- Provider contract -----

    def set_compact(self, compact: bool) -> None:
        # list_nav never compacts (supports_compact is False); see R1.
        pass

    def show(self, key: str, data: dict | None = None) -> None:
        record = self._records.get(key)
        self._host.clear()
        if self._detail is not None and record is not None:
            with self._host:
                self._detail(record)

    def select_visual(self, key: str | None) -> None:
        self._nav.select(key)

    def keys(self) -> tuple[str, ...]:
        return tuple(self._order)

    # ----- Accessors -----

    @property
    def nav(self) -> NavPanel:
        """The sidebar navigation panel."""
        return self._nav


class TreeNavProvider:
    """Hierarchical, data-bound provider — a `Tree` drives the sidebar.

    Nodes may be declared inline (`nodes=`) or projected from a flat
    adjacency-list `source` (`source=`/`parent_field=`). Selecting a node
    re-renders one `@detail` body with the node normalized to a record dict
    (`text` from the node label, `icon`, the node id, plus the node's data bag) —
    the same universal `.selection` shape `list_nav` uses (spec decision #10).

    Hierarchy is incompatible with the icon-rail (a branch cannot render as one
    glyph), so this provider does not support compaction.
    """

    supports_compact = False

    def __init__(
        self,
        *,
        nodes: list | None = None,
        source: Any = None,
        parent_field: str = "parent_id",
        label_field: str = "name",
        icon_field: str = "icon",
        accent: str = "primary",
    ) -> None:
        self._nodes = nodes
        self._source = source
        self._parent_field = parent_field
        self._label_field = label_field
        self._icon_field = icon_field
        self._accent = accent
        self._tree: Any = None
        self._host: ContentHost | None = None
        self._sidebar_host: ContentHost | None = None
        self._detail: Callable[[dict], Any] | None = None
        self._on_select: Callable[[str], None] | None = None
        self._nodes_by_key: dict[str, Any] = {}
        self._sub: Any = None

    def mount(
        self,
        sidebar: Frame,
        content: Frame,
        *,
        on_select: Callable[[str], None],
        on_refresh: Callable[[], None] | None = None,
    ) -> None:
        from bootstack.widgets.tree import Tree

        self._on_select = on_select
        self._host = ContentHost(content)
        self._sidebar_host = ContentHost(sidebar)

        tree_kwargs: dict[str, Any] = {
            "parent": self._sidebar_host,
            "selection_mode": "single",
            "show_scrollbar": False,
            "accent": self._accent,
            "fill": "both",
            "expand": True,
        }
        if self._source is not None:
            tree_kwargs.update(
                data_source=self._source,
                parent_field=self._parent_field,
                label_field=self._label_field,
                icon_field=self._icon_field,
            )
        elif self._nodes is not None:
            tree_kwargs["nodes"] = self._nodes
        self._tree = Tree(**tree_kwargs)
        self._sub = self._tree.on_select(self._on_tree_select)

    def set_detail(self, fn: Callable[[dict], Any]) -> None:
        """Register the parameterized detail body builder."""
        self._detail = fn

    # ----- Selection plumbing (node identity -> string key) -----

    def _key_for(self, node: Any) -> str:
        key = str(id(node))
        self._nodes_by_key[key] = node
        return key

    def _record(self, node: Any, key: str) -> dict:
        rec = dict(getattr(node, "data", {}) or {})
        rec["text"] = node.label
        rec["icon"] = node.icon
        rec["id"] = key
        return rec

    def _on_tree_select(self, _event: Any) -> None:
        node = self._tree.selection
        if node is None:
            return
        self._on_select(self._key_for(node))

    # ----- Provider contract -----

    def set_compact(self, compact: bool) -> None:
        # A hierarchy cannot render as icons; tree_nav never compacts (see R1).
        pass

    def show(self, key: str, data: dict | None = None) -> None:
        node = self._nodes_by_key.get(key)
        self._host.clear()
        if self._detail is not None and node is not None:
            with self._host:
                self._detail(self._record(node, key))

    def select_visual(self, key: str | None) -> None:
        node = self._nodes_by_key.get(key) if key is not None else None
        if node is not None:
            self._tree.select(node)

    def keys(self) -> tuple[str, ...]:
        # Trees register keys lazily as nodes are selected (nodes may be created
        # on expand). Empty until the first selection — so the shell never
        # auto-selects a tree (a tree opens with nothing selected).
        return tuple(self._nodes_by_key)

    def close(self) -> None:
        """Cancel the tree selection subscription."""
        if self._sub is not None:
            try:
                self._sub.cancel()
            except Exception:
                pass
            self._sub = None

    # ----- Accessors -----

    @property
    def tree(self) -> Any:
        """The sidebar `Tree` widget."""
        return self._tree


class CustomProvider:
    """Escape-hatch provider — a blank sidebar container the user fills.

    There is no cascade and no per-page memory: the workspace hands back the
    sidebar container (via `panel`) and its content region (via `Workspace.content`)
    and the user drives content-switching themselves. A custom panel cannot
    collapse to icons (its content is arbitrary), so `supports_compact` is False —
    it only hides.
    """

    supports_compact = False

    def __init__(self) -> None:
        self._container: Frame | None = None
        self._content: Frame | None = None

    def mount(
        self,
        sidebar: Frame,
        content: Frame,
        *,
        on_select: Callable[[str], None],
        on_refresh: Callable[[], None] | None = None,
    ) -> None:
        # No selection model: on_select/on_refresh are unused.
        self._container = Frame(sidebar)
        self._container.pack(fill="both", expand=True)
        self._content = content

    # ----- Provider contract (mostly inert) -----

    def set_compact(self, compact: bool) -> None:
        pass

    def show(self, key: str, data: dict | None = None) -> None:
        pass

    def select_visual(self, key: str | None) -> None:
        pass

    def keys(self) -> tuple[str, ...]:
        return ()

    # ----- Accessors -----

    @property
    def container(self) -> Frame:
        """The blank sidebar container to fill."""
        return self._container
