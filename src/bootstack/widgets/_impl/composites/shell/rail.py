"""The workspace rail — the tier-1 icon switcher.

A vertical strip of icon-only items, one per workspace, with a pinned footer
(for global workspaces like Settings). Selection is single and driven externally
by the shell from `NavModel` (the VS Code gesture lives in the model); the rail
just reports clicks and reflects the active workspace.

Rail items reuse `SideNavItem` in compact (icon-only) mode, which renders the
sidebar's subtle accent wash with no left bar — matching decision #13's rail
paradigm (wash + glyph, no bar). The decision-#13 icon-size / elevation tokens
are applied in the styling step.
"""

from __future__ import annotations

from typing import Callable

from bootstack.widgets._impl.primitives.frame import Frame
from bootstack.widgets._impl.composites.sidenav.item import SideNavItem


class Rail(Frame):
    """A single-select icon rail of workspaces.

    Args:
        master: Parent widget (the rail region).
        on_select: Called with a workspace key when its icon is clicked.
        accent: Accent token for the active item.
    """

    # Rail glyphs read as standalone, categorical marks — distinctly larger than
    # the inline sidebar icons (~20px). Decision #13's rail_icon_size.
    DEFAULT_ICON_SIZE = 28

    def __init__(
        self,
        master,
        *,
        on_select: Callable[[str], None],
        accent: str = "primary",
        icon_size: int | None = None,
    ) -> None:
        super().__init__(master, surface="chrome")
        self._on_select = on_select
        self._accent = accent
        self._icon_size = icon_size if icon_size is not None else self.DEFAULT_ICON_SIZE
        self._items: dict[str, SideNavItem] = {}
        self._selected: str | None = None

        self._footer = Frame(self, surface="chrome")
        self._footer.pack(side="bottom", fill="x")
        self._main = Frame(self, surface="chrome")
        self._main.pack(side="top", fill="both", expand=True)

    def add_workspace(self, key: str, *, icon=None, text: str = "", footer: bool = False) -> SideNavItem:
        """Add a workspace icon to the rail (or its footer)."""
        if key in self._items:
            raise ValueError(f"duplicate rail key: {key!r}")
        parent = self._footer if footer else self._main
        # Render the glyph at the larger rail size (explicit spec size overrides
        # the nav label style's default 20px).
        spec = self._icon_spec(icon)
        item = SideNavItem(parent, key=key, text=text, icon=spec, accent=self._accent)
        item.set_compact(True)              # icon-only, centered
        item.pack(fill="x")
        item.on_invoked(lambda _event, k=key: self._on_select(k))
        self._items[key] = item
        return item

    def _icon_spec(self, icon):
        """Normalize an icon name/spec to carry the rail icon size."""
        if icon is None:
            return None
        if isinstance(icon, dict):
            spec = dict(icon)
            spec.setdefault("size", self._icon_size)
            return spec
        return {"name": icon, "size": self._icon_size}

    def select(self, key: str | None) -> None:
        """Set the visual selection to `key` (or clear with `None`)."""
        for k, item in self._items.items():
            item.set_selected(k == key)
        self._selected = key

    @property
    def selected(self) -> str | None:
        """The selected workspace key, or `None`."""
        return self._selected

    def keys(self) -> tuple[str, ...]:
        """All workspace keys in insertion order."""
        return tuple(self._items)
