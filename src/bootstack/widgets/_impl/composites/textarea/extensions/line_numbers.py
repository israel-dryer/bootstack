"""LineNumbers sidebar — displays line numbers synced with the main text.

Port of idlelib/sidebar.py LineNumbers. Uses a sibling tk.Text widget
(read-only, no padding, matching font) placed to the left of the main text.
Width auto-adjusts when the line count crosses a power-of-ten boundary.
"""
from __future__ import annotations

import tkinter as tk
from typing import TYPE_CHECKING

from bootstack.widgets._impl.composites.textarea.sidebar import Sidebar

if TYPE_CHECKING:
    from bootstack.widgets._impl.composites.textarea.core import _MultilineCore

_PADX = 6    # horizontal padding inside the line-number gutter
_PADY = 1    # top padding to align with text widget baseline


class LineNumbers(Sidebar):
    """Displays line numbers alongside the text, scroll-synced.

    Add to a `CodeEditor` or `TextArea` core via::

        core.add_sidebar(LineNumbers())
    """

    def __init__(self) -> None:
        super().__init__()
        self._widget: tk.Text | None = None
        self._core: _MultilineCore | None = None
        self._last_line_count: int = 0
        self._current_width: int = 1     # digits in the widest line number

    # ── Sidebar protocol ──────────────────────────────────────────────────

    def _build(self, core: _MultilineCore) -> None:
        self._core = core
        font = core.text.cget("font") or "TkFixedFont"

        self._widget = tk.Text(
            core,
            width=self._current_width,
            height=core.text.cget("height"),
            padx=_PADX,
            pady=_PADY,
            state=tk.DISABLED,
            wrap=tk.NONE,
            font=font,
            cursor="arrow",
            takefocus=False,
            highlightthickness=0,
            relief=tk.FLAT,
            borderwidth=0,
        )

        # Grid in col 0 (left sidebar column), same row as the main text
        self._widget.grid(row=0, column=0, sticky="ns")

        self._apply_colors()
        self._update()

    def _destroy(self) -> None:
        if self._widget is not None:
            try:
                self._widget.destroy()
            except Exception:
                pass
            self._widget = None

    def on_scroll(self, first: str, last: str) -> None:
        """Sync the line-number gutter with the main text scroll position."""
        if self._widget is not None:
            self._widget.yview_moveto(first)

    def on_change(self) -> None:
        """Refresh line numbers after every edit."""
        self._update()

    def update_font(self) -> None:
        """Sync the gutter font with the main text font."""
        if self._widget and self._core:
            font = self._core.text.cget("font")
            self._widget.configure(font=font)

    def update_colors(self, event=None) -> None:
        """Reapply theme colors."""
        self._apply_colors()

    # ── internals ─────────────────────────────────────────────────────────

    def _update(self) -> None:
        """Recompute and render the line numbers."""
        if self._widget is None or self._core is None:
            return

        line_count = self._line_count()
        self._adjust_width(line_count)

        numbers = "\n".join(str(i) for i in range(1, line_count + 1))

        self._widget.configure(state=tk.NORMAL)
        self._widget.delete("1.0", tk.END)
        self._widget.insert("1.0", numbers)
        self._widget.configure(state=tk.DISABLED)

        self._last_line_count = line_count

    def _line_count(self) -> int:
        """Return the number of lines in the main text widget."""
        if self._core is None:
            return 1
        idx = self._core.text.index("end-1c")
        return int(idx.split(".")[0])

    def _adjust_width(self, line_count: int) -> None:
        """Expand or contract the gutter when line count crosses a decade."""
        needed = len(str(line_count))
        if needed != self._current_width:
            self._current_width = needed
            if self._widget:
                self._widget.configure(width=needed)

    def _apply_colors(self) -> None:
        """Apply theme-aware foreground/background to the gutter."""
        if self._widget is None:
            return
        try:
            from bootstack.style.style import get_theme_provider
            colors = get_theme_provider().colors
            fg = colors.get("muted", "#888888")
            bg = colors.get("chrome", "#f0f0f0")
            self._widget.configure(foreground=fg, background=bg,
                                   selectbackground=bg, selectforeground=fg,
                                   inactiveselectbackground=bg)
        except Exception:
            pass
