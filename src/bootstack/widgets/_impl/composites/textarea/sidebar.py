"""Sidebar protocol for TextArea/CodeEditor gutter widgets.

Port of idlelib/sidebar.py BaseSideBar. Sidebars are sibling widgets placed
in the core's grid, scroll-synced with the main Text widget.
"""
from __future__ import annotations

from typing import Literal, TYPE_CHECKING

if TYPE_CHECKING:
    from bootstack.widgets._impl.composites.textarea.core import _MultilineCore


class Sidebar:
    """Base class for gutter widgets placed alongside the Text area.

    Subclass and override `_build(core)` to create the sidebar widget,
    then override `on_scroll` and `on_change` as needed.

    The sidebar is placed in column 0 of the core's grid (left side).
    The core calls `on_scroll` whenever the main text scrolls and
    `on_change` (via the `<<Change>>` event) whenever content changes.
    """

    def attach(self, core: _MultilineCore, side: Literal["left"] = "left") -> None:
        """Attach this sidebar to *core* and add it to the grid.

        Args:
            core: The `_MultilineCore` to attach to.
            side: Layout side. Only `"left"` is currently supported.
        """
        self._core = core
        self._side = side
        self._build(core)
        core.text.bind("<<Change>>", self._on_change_event, add="+")

    def detach(self, core: _MultilineCore) -> None:
        """Remove this sidebar from the grid and release resources."""
        try:
            core.text.unbind("<<Change>>", None)
        except Exception:
            pass
        self._destroy()

    # ── override in subclasses ────────────────────────────────────────────

    def _build(self, core: _MultilineCore) -> None:
        """Create the sidebar widget and grid it. Called by `attach`."""

    def _destroy(self) -> None:
        """Release resources. Called by `detach`."""

    def on_scroll(self, first: str, last: str) -> None:
        """Called when the main text scrolls.

        Args:
            first: First visible fraction (0.0–1.0).
            last: Last visible fraction (0.0–1.0).
        """

    def on_change(self) -> None:
        """Called after every insert/delete in the main text."""

    def update_font(self) -> None:
        """Called when the font changes."""

    def update_colors(self) -> None:
        """Called when the theme changes."""

    def _on_change_event(self, _event=None) -> None:
        self.on_change()
