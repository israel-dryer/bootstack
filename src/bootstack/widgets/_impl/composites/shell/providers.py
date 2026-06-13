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
