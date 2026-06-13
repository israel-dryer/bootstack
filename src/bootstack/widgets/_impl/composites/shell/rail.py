"""The workspace rail — the tier-1 icon switcher.

A vertical strip of icon-only items, one per workspace, with a pinned footer
(for global workspaces like Settings). The rail is a single-select **radio
group**: every item is a `RadioToggle` sharing one `Signal`, so single-select is
the radio machinery itself — no hand-rolled selection state.

The items use the `rail` Toolbutton style variant (the VS Code activity-bar
treatment: muted glyph -> full-strength glyph + accent indicator bar on the
chrome surface). Selection truth still lives in the shell's `NavModel`; the rail
reports clicks and reflects the active workspace by setting its shared signal.

The VS Code gesture (click the active icon -> hide the sidebar) needs *every*
click — including a re-click on the already-selected item, which a radio does not
report as a change — so each item also has a direct click binding that routes to
the shell.
"""

from __future__ import annotations

from typing import Callable

from bootstack.signals import Signal
from bootstack.widgets._impl.primitives.frame import Frame
from bootstack.widgets._impl.primitives.radiotoggle import RadioToggle


class Rail(Frame):
    """A single-select icon rail of workspaces (a radio-toggle group).

    Args:
        master: Parent widget (the rail region).
        on_select: Called with a workspace key when its icon is clicked.
        accent: Accent token for the active item.
    """

    # Rail glyphs read as standalone, categorical marks — distinctly larger than
    # the inline sidebar icons. Decision #13's rail_icon_size.
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
        # Shared selection signal: the value is the active workspace key, so the
        # matching RadioToggle renders selected (radio single-select). A Signal is
        # typed by its initial value, so use an empty-string sentinel for "none"
        # (no workspace key is empty) rather than None.
        self._signal: Signal = Signal("")
        self._items: dict[str, RadioToggle] = {}

        self._footer = Frame(self, surface="chrome")
        self._footer.pack(side="bottom", fill="x")
        self._main = Frame(self, surface="chrome")
        self._main.pack(side="top", fill="both", expand=True)

    def add_workspace(self, key: str, *, icon=None, text: str = "", footer: bool = False) -> RadioToggle:
        """Add a workspace icon to the rail (or its footer)."""
        if key in self._items:
            raise ValueError(f"duplicate rail key: {key!r}")
        parent = self._footer if footer else self._main
        item = RadioToggle(
            parent,
            value=key,
            signal=self._signal,
            icon=self._icon_spec(icon),
            icon_only=True,
            accent=self._accent,
            variant="rail",
            surface="chrome",
        )
        item.pack(fill="x")
        # Catch ALL clicks (including a re-click on the active item) so the shell
        # can run the VS Code gesture; the radio itself only reports changes.
        item.bind("<Button-1>", lambda _e, k=key: self._on_select(k), add="+")
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
        self._signal.set(key if key is not None else "")

    @property
    def selected(self) -> str | None:
        """The selected workspace key, or `None`."""
        return self._signal() or None

    def keys(self) -> tuple[str, ...]:
        """All workspace keys in insertion order."""
        return tuple(self._items)
