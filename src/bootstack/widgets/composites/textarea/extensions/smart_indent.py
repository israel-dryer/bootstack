"""SmartIndent — auto-indent on Enter and Tab-to-spaces conversion.

Filter-style extension: intercepts Return and Tab key events to provide
editor-grade indentation. Does not intercept insert/delete in the chain
(key bindings are used instead to avoid interfering with clipboard ops).
"""
from __future__ import annotations

import tkinter as tk
from typing import TYPE_CHECKING

from bootstack.widgets.composites.textarea.filter import EditFilter

if TYPE_CHECKING:
    from bootstack.widgets.composites.textarea.core import _MultilineCore


class SmartIndent(EditFilter):
    """Provides auto-indent on Return and optional Tab-to-spaces conversion.

    On ``<Return>``:
        Inserts a newline followed by the same leading whitespace as the
        current line, so the cursor lands at the same indent level.

    On ``<Tab>`` (when ``insert_spaces=True``):
        Inserts ``tab_width`` spaces instead of a literal tab character.

    Install via ``core.add_filter(SmartIndent())``.
    """

    def __init__(self, tab_width: int = 4, insert_spaces: bool = True) -> None:
        super().__init__()
        self._tab_width = tab_width
        self._insert_spaces = insert_spaces
        self._core: _MultilineCore | None = None

    def attach(self, core: _MultilineCore) -> None:
        self._core = core
        core.text.bind("<Return>", self._on_return, add="+")
        if self._insert_spaces:
            core.text.bind("<Tab>", self._on_tab, add="+")

    def detach(self, core: _MultilineCore) -> None:
        self._core = None

    # ── filter pass-through ───────────────────────────────────────────────

    def insert(self, index: str, chars: str, tags=None) -> None:
        self.delegate.insert(index, chars, tags)

    def delete(self, index1: str, index2: str | None = None) -> None:
        self.delegate.delete(index1, index2)

    # ── key handlers ─────────────────────────────────────────────────────

    def _on_return(self, _event: tk.Event) -> str:
        """Insert a newline with matching indentation."""
        if self._core is None:
            return ""
        text = self._core.text
        cursor = text.index("insert")
        line_start = text.index(f"{cursor} linestart")
        line_text = text.get(line_start, cursor)
        indent = _leading_whitespace(line_text)
        # Use the undo block API so auto-indent is one undo step with the newline
        self._core.undo_block_start()
        text.insert("insert", f"\n{indent}")
        self._core.undo_block_stop()
        return "break"     # prevent default Return handling

    def _on_tab(self, _event: tk.Event) -> str:
        """Insert spaces instead of a literal tab."""
        if self._core is None:
            return ""
        text = self._core.text
        cursor = text.index("insert")
        line_start = text.index(f"{cursor} linestart")
        col = int(text.index(cursor).split(".")[1])
        # Round up to the next tab stop
        spaces = self._tab_width - (col % self._tab_width)
        text.insert("insert", " " * spaces)
        return "break"


def _leading_whitespace(line: str) -> str:
    """Return the leading whitespace characters of *line*."""
    return line[: len(line) - len(line.lstrip())]
