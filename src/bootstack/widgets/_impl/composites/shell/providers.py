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
    """Whether the sidebar may collapse to an icon rail (false for custom panels)."""

    def mount(self, sidebar: Frame, content: Frame, *, on_select: Callable[[str], None]) -> None:
        """Build the sidebar UI in `sidebar` and prepare the `content` region."""
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

    def __init__(self, *, accent: str = "primary") -> None:
        self._accent = accent
        self._nav: NavPanel | None = None
        self._pages: PageStack | None = None
        self._keys: list[str] = []

    def mount(self, sidebar: Frame, content: Frame, *, on_select: Callable[[str], None]) -> None:
        self._nav = NavPanel(sidebar, on_select=on_select, accent=self._accent)
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

    def add_header(self, text: str) -> Any:
        """Add a static section header."""
        return self._nav.add_header(text)

    def add_separator(self) -> Any:
        """Add a separator."""
        return self._nav.add_separator()

    # ----- Provider contract -----

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

    supports_compact = True

    def __init__(
        self,
        source: Any,
        *,
        text_field: str = "text",
        icon_field: str = "icon",
        accent: str = "primary",
    ) -> None:
        self._source = source
        self._text_field = text_field
        self._icon_field = icon_field
        self._accent = accent
        self._nav: NavPanel | None = None
        self._host: ContentHost | None = None
        self._detail: Callable[[dict], Any] | None = None
        self._records: dict[str, dict] = {}
        self._order: list[str] = []

    def mount(self, sidebar: Frame, content: Frame, *, on_select: Callable[[str], None]) -> None:
        self._nav = NavPanel(sidebar, on_select=on_select, accent=self._accent)
        self._nav.pack(fill="both", expand=True)
        self._host = ContentHost(content)
        self._populate()

    def set_detail(self, fn: Callable[[dict], Any]) -> None:
        """Register the parameterized detail body builder."""
        self._detail = fn

    def _populate(self) -> None:
        self._records.clear()
        self._order.clear()
        src = self._source
        records = [src._public_record(r) for r in src.page_slice(0, src.count)]
        for rec in records:
            key = str(rec.get("id"))
            self._records[key] = rec
            self._order.append(key)
            self._nav.add_item(
                key,
                text=str(rec.get(self._text_field, "")),
                icon=rec.get(self._icon_field),
            )

    # ----- Provider contract -----

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
