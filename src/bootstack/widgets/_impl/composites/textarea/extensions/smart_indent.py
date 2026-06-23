"""SmartIndent — auto-indent on Enter and Tab-to-spaces conversion.

Filter-style extension: intercepts Return and Tab key events to provide
editor-grade indentation. Does not intercept insert/delete in the chain
(key bindings are used instead to avoid interfering with clipboard ops).
"""
from __future__ import annotations

import tkinter as tk
from typing import TYPE_CHECKING

from bootstack.widgets._impl.composites.textarea.filter import EditFilter

if TYPE_CHECKING:
    from bootstack.widgets._impl.composites.textarea.core import _MultilineCore


class SmartIndent(EditFilter):
    """Provides auto-indent on Return, Tab-to-spaces, and block indent/dedent.

    On `<Return>`:
        Inserts a newline followed by the same leading whitespace as the
        current line, so the cursor lands at the same indent level.

    On `<Tab>` with a selection:
        Indents every selected line by one tab stop.

    On `<Tab>` with no selection (when `insert_spaces=True`):
        Inserts spaces to the next tab stop instead of a literal tab character.

    On `<Shift-Tab>`:
        Dedents every selected line (or the current line) by one tab stop.

    Install via `core.add_filter(SmartIndent())`.
    """

    def __init__(self, tab_width: int = 4, insert_spaces: bool = True) -> None:
        super().__init__()
        self._tab_width = tab_width
        self._insert_spaces = insert_spaces
        self._core: _MultilineCore | None = None

    def attach(self, core: _MultilineCore) -> None:
        self._core = core
        core.text.bind("<Return>", self._on_return, add="+")
        core.text.bind("<Tab>", self._on_tab, add="+")
        core.text.bind("<Shift-Tab>", self._on_shift_tab, add="+")
        core.text.bind("<ISO_Left_Tab>", self._on_shift_tab, add="+")  # Linux/X11

    def detach(self, core: _MultilineCore) -> None:
        self._core = None

    # ── filter pass-through ───────────────────────────────────────────────

    def insert(self, index: str, chars: str, tags=None) -> None:
        self.delegate.insert(index, chars, tags)

    def delete(self, index1: str, index2: str | None = None) -> None:
        self.delegate.delete(index1, index2)

    # ── public block operations ───────────────────────────────────────────

    def indent(self) -> None:
        """Indent selected lines by one tab stop, or insert at cursor."""
        if self._core is None:
            return
        tw = self._core.text
        ranges = tw.tag_ranges("sel")
        if ranges:
            self._indent_block(tw, ranges)
        else:
            col = int(tw.index("insert").split(".")[1])
            spaces = self._tab_width - (col % self._tab_width)
            tw.insert("insert", " " * spaces if self._insert_spaces else "\t")

    def dedent(self) -> None:
        """Dedent selected lines (or current line) by one tab stop."""
        if self._core is None:
            return
        self._dedent_block(self._core.text, self._core.text.tag_ranges("sel"))

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

    def _on_tab(self, _event: tk.Event) -> str | None:
        """Indent selection, or insert spaces / fall through for a literal tab."""
        if self._core is None:
            return None
        tw = self._core.text
        ranges = tw.tag_ranges("sel")
        if ranges:
            self._indent_block(tw, ranges)
            return "break"
        if self._insert_spaces:
            col = int(tw.index("insert").split(".")[1])
            spaces = self._tab_width - (col % self._tab_width)
            tw.insert("insert", " " * spaces)
            return "break"
        # insert_spaces=False, no selection: let native Tab insert \t
        return None

    def _on_shift_tab(self, _event: tk.Event) -> str:
        """Dedent selection or current line."""
        if self._core is None:
            return "break"
        self._dedent_block(self._core.text, self._core.text.tag_ranges("sel"))
        return "break"

    # ── helpers ───────────────────────────────────────────────────────────

    def _indent_block(self, tw: tk.Text, ranges: tuple) -> None:
        start_line, end_line = _sel_line_range(ranges)
        indent = " " * self._tab_width if self._insert_spaces else "\t"
        self._core.undo_block_start()
        try:
            for ln in range(start_line, end_line + 1):
                if tw.get(f"{ln}.0", f"{ln}.end"):  # skip blank lines
                    tw.insert(f"{ln}.0", indent)
        finally:
            self._core.undo_block_stop()
        tw.tag_add("sel", f"{start_line}.0", f"{end_line}.end")

    def _dedent_block(self, tw: tk.Text, ranges: tuple) -> None:
        if ranges:
            start_line, end_line = _sel_line_range(ranges)
        else:
            start_line = end_line = int(tw.index("insert").split(".")[0])
        self._core.undo_block_start()
        try:
            for ln in range(start_line, end_line + 1):
                line_text = tw.get(f"{ln}.0", f"{ln}.end")
                if self._insert_spaces:
                    n = min(self._tab_width, len(line_text) - len(line_text.lstrip(" ")))
                    if n:
                        tw.delete(f"{ln}.0", f"{ln}.{n}")
                else:
                    if line_text.startswith("\t"):
                        tw.delete(f"{ln}.0", f"{ln}.1")
        finally:
            self._core.undo_block_stop()
        if ranges:
            tw.tag_add("sel", f"{start_line}.0", f"{end_line}.end")


def _leading_whitespace(line: str) -> str:
    """Return the leading whitespace characters of *line*."""
    return line[: len(line) - len(line.lstrip())]


def _sel_line_range(ranges: tuple) -> tuple[int, int]:
    """Return (start_line, end_line) from a tag_ranges("sel") result.

    If the selection ends exactly at column 0 of the last line (i.e. the user
    selected to the very start of a line without including any content), that
    trailing line is excluded so we don't indent/dedent a line the user didn't
    intend to touch.
    """
    start_str, end_str = str(ranges[0]), str(ranges[1])
    start_line = int(start_str.split(".")[0])
    end_line = int(end_str.split(".")[0])
    if end_str.split(".")[1] == "0" and end_line > start_line:
        end_line -= 1
    return start_line, end_line
