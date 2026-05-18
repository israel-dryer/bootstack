"""SearchOverlay — find/replace bar for CodeEditor.

Docks at the bottom of the editor as a z-order overlay (always place()'d,
shown by lift(), hidden by lowering _core back on top).  Opened with
Ctrl+F (find) or Ctrl+H (find + replace).  Closed with Esc.
"""
from __future__ import annotations

import re
import bisect
from typing import TYPE_CHECKING

from bootstack.widgets.primitives.label import Label
from bootstack.widgets.primitives.button import Button
from bootstack.widgets.primitives.separator import Separator
from bootstack.widgets.primitives.checktoggle import CheckToggle
from bootstack.widgets.primitives.packframe import PackFrame
from bootstack.widgets.composites.textentry import TextEntry
from bootstack.widgets.composites.textarea.decoration import Position, RangeDecoration
from bootstack.signals.signal import Signal

if TYPE_CHECKING:
    from bootstack.widgets.composites.textarea.core import _MultilineCore
    from bootstack.widgets.types import Master


_LAYER = "search"
_STYLE_MATCH = "search_match"
_STYLE_CURRENT = "search_current"
_DEBOUNCE_MS = 120


class SearchOverlay(PackFrame):
    """Find/replace bar that overlays the bottom of the editor.

    Created and owned by `CodeEditor` — not part of the public API.
    Use `CodeEditor.show_search()` / `CodeEditor.show_replace()` /
    `CodeEditor.hide_search()`.
    """

    def __init__(self, parent: Master, core: _MultilineCore) -> None:
        super().__init__(parent, surface="chrome", padding=(8, 4), direction="vertical")
        self._core = core
        self._matches: list[tuple[int, int]] = []
        self._current: int = -1
        self._after_id: str | None = None
        self._case_sig = Signal(False)
        self._regex_sig = Signal(False)
        self._count_sig = Signal("")
        self._syncing_colors = False
        self._visible = False
        self._replace_visible = False

        # ── decoration styles ─────────────────────────────────────────────
        core.register_layer(_LAYER, priority=10)
        core.define_style(_STYLE_MATCH, background="#ffff60", foreground="#000000")
        core.define_style(_STYLE_CURRENT, background="#ff8000", foreground="#000000")

        # ── find row ──────────────────────────────────────────────────────
        _fr = PackFrame(self, direction="horizontal").pack(fill="x")

        self._close_btn = Button(
            _fr, icon="x-lg", icon_only=True, variant="ghost",
            density="compact", command=self.hide,
        )
        self._close_btn.pack()

        self._find_entry = TextEntry(_fr, density="compact")
        self._find_entry.insert_addon(Label, position="before", icon="search")
        self._find_entry.on_changed(self._on_query_changed)
        self._find_entry.pack(fill="x", expand=True)

        Separator(_fr, orient="vertical").pack(fill="y", padx=16)

        self._case_toggle = CheckToggle(
            _fr, icon="type", icon_only=True, signal=self._case_sig,
            onvalue=True, offvalue=False,
            command=self._on_option_changed, density="compact",
        )
        self._case_toggle.pack(padx=(0, 4))

        self._regex_toggle = CheckToggle(
            _fr, icon="regex", icon_only=True, signal=self._regex_sig,
            onvalue=True, offvalue=False,
            command=self._on_option_changed, density="compact",
        )
        self._regex_toggle.pack()

        _mc = PackFrame(_fr, direction="horizontal").pack(padx=(16, 0))
        Separator(_mc, orient="vertical").pack(fill="y")

        self._count_lbl = Label(_mc, textsignal=self._count_sig)
        self._count_lbl.pack(padx=(16, 0))

        self._prev_btn = Button(
            _mc, icon="arrow-up", icon_only=True, variant="ghost",
            density="compact", command=self._prev_match,
        )
        self._prev_btn.pack()

        self._next_btn = Button(
            _mc, icon="arrow-down", icon_only=True, variant="ghost",
            density="compact", command=self._next_match,
        )
        self._next_btn.pack()

        # ── replace row (hidden by default) ───────────────────────────────
        self._replace_row = PackFrame(self, direction="horizontal", padding=(0, 4, 0, 0))

        self._replace_entry = TextEntry(self._replace_row, density="compact")
        self._replace_entry.insert_addon(Label, position="before", icon="pencil")
        self._replace_entry.pack(fill="x", expand=True)

        self._replace_btn = Button(
            self._replace_row, text="Replace",
            variant="ghost", density="compact",
            command=self._replace_current,
        )
        self._replace_btn.pack(padx=(8, 0))

        self._replace_all_btn = Button(
            self._replace_row, text="Replace All",
            variant="ghost", density="compact",
            command=self._replace_all,
        )
        self._replace_all_btn.pack(padx=(4, 0))

        # ── key bindings — find entry ─────────────────────────────────────
        _fi = self._find_entry.entry_widget
        _fi.bind("<Return>",       lambda _: self._next_match())
        _fi.bind("<Shift-Return>", lambda _: self._prev_match())
        _fi.bind("<Escape>",       lambda _: self.hide())

        # ── key bindings — replace entry ──────────────────────────────────
        _ri = self._replace_entry.entry_widget
        _ri.bind("<Return>",  lambda _: self._replace_current())
        _ri.bind("<Escape>",  lambda _: self.hide())

        # ── key bindings — editor text widget ─────────────────────────────
        core.text.bind("<Control-f>", self._on_ctrl_f, add="+")
        core.text.bind("<Control-F>", self._on_ctrl_f, add="+")
        core.text.bind("<Control-h>", self._on_ctrl_h, add="+")
        core.text.bind("<Control-H>", self._on_ctrl_h, add="+")
        if core.winsys == "aqua":
            core.text.bind("<Command-f>", self._on_ctrl_f, add="+")
            core.text.bind("<Command-F>", self._on_ctrl_f, add="+")
            core.text.bind("<Command-h>", self._on_ctrl_h, add="+")
            core.text.bind("<Command-H>", self._on_ctrl_h, add="+")
        core.text.bind("<Escape>",     self._on_editor_escape, add="+")
        core.text.bind("<<Change>>",   self._on_content_changed, add="+")
        core.text.bind("<<ThemeChanged>>",    self._on_theme_changed, add="+")
        core.text.bind("<<EditorBgChanged>>", self._on_theme_changed, add="+")

        # Measure find-row-only height for initial place() sizing.
        self.update_idletasks()
        self._height = max(self.winfo_reqheight(), 44)

    # ── public API ────────────────────────────────────────────────────────

    def show(self, replace: bool = False) -> None:
        """Show the find bar, optionally with the replace row visible.

        Args:
            replace: If True, show the replace row and focus the replace entry.
        """
        self._sync_colors()
        self._visible = True
        self._set_replace_visible(replace)
        self.lift()
        if replace and self._replace_visible:
            self._replace_entry.focus_set()
        else:
            self._find_entry.focus_set()
        self._run_search()

    def hide(self) -> None:
        """Hide the find/replace bar and clear all highlights."""
        self._visible = False
        self._core.lift()
        self._core.clear_decorations(_LAYER)
        self._matches = []
        self._current = -1
        self._count_sig.set("")
        self._set_entry_state("normal")
        try:
            self._core.text.focus_set()
        except Exception:
            pass

    # ── replace logic ─────────────────────────────────────────────────────

    def _replace_current(self) -> None:
        """Replace the current match with the replace entry text."""
        if not self._matches or self._current < 0:
            return
        if self._core._read_only:
            return
        text = self._core.value
        start, end = self._matches[self._current]
        replacement = self._expand_replacement(text[start:end])
        line_starts = _build_line_starts(text)
        s = _offset_to_position(line_starts, start).to_tk()
        e = _offset_to_position(line_starts, end).to_tk()
        self._core.undo_block_start()
        self._core.text.delete(s, e)
        self._core.text.insert(s, replacement)
        self._core.undo_block_stop()
        self._run_search()

    def _replace_all(self) -> None:
        """Replace every match with the replace entry text."""
        if not self._matches:
            return
        if self._core._read_only:
            return
        text = self._core.value
        line_starts = _build_line_starts(text)
        # Process last-to-first so earlier offsets stay valid.
        ops = [
            (
                _offset_to_position(line_starts, start).to_tk(),
                _offset_to_position(line_starts, end).to_tk(),
                self._expand_replacement(text[start:end]),
            )
            for start, end in reversed(self._matches)
        ]
        count = len(ops)
        self._core.undo_block_start()
        for s, e, r in ops:
            self._core.text.delete(s, e)
            self._core.text.insert(s, r)
        self._core.undo_block_stop()
        self._run_search()
        self._count_sig.set(f"{count} replaced")

    def _expand_replacement(self, matched_text: str) -> str:
        """Return the replacement string, expanding regex back-references."""
        replacement = self._replace_entry.value or ""
        if self._regex_sig.get():
            try:
                query = self._find_entry.value or ""
                flags = 0 if self._case_sig.get() else re.IGNORECASE
                m = re.fullmatch(query, matched_text, flags)
                if m:
                    return m.expand(replacement)
            except Exception:
                pass
        return replacement

    # ── search logic ──────────────────────────────────────────────────────

    def _run_search(self) -> None:
        self._after_id = None
        query = self._find_entry.value or ""
        if not query:
            self._core.clear_decorations(_LAYER)
            self._matches = []
            self._current = -1
            self._count_sig.set("")
            self._set_entry_state("normal")
            return

        text = self._core.value
        flags = 0 if self._case_sig.get() else re.IGNORECASE

        try:
            pattern = re.compile(
                query if self._regex_sig.get() else re.escape(query),
                flags,
            )
        except re.error:
            self._set_entry_state("error")
            self._core.clear_decorations(_LAYER)
            self._matches = []
            self._current = -1
            self._count_sig.set("bad regex")
            return

        self._matches = [(m.start(), m.end()) for m in pattern.finditer(text)]

        if not self._matches:
            self._core.clear_decorations(_LAYER)
            self._current = -1
            self._count_sig.set("")
            self._set_entry_state("no_match")
            return

        self._set_entry_state("normal")

        try:
            idx = self._core.text.index("insert")
            line_no, col_no = idx.split(".")
            cursor_offset = _position_to_offset(text, int(line_no), int(col_no))
        except Exception:
            cursor_offset = 0

        starts = [m[0] for m in self._matches]
        self._current = bisect.bisect_left(starts, cursor_offset) % len(self._matches)
        self._apply_decorations(text)

    def _apply_decorations(self, text: str) -> None:
        if not self._matches:
            self._core.clear_decorations(_LAYER)
            return

        line_starts = _build_line_starts(text)
        decorations = [
            RangeDecoration(
                _offset_to_position(line_starts, start),
                _offset_to_position(line_starts, end),
                _STYLE_CURRENT if i == self._current else _STYLE_MATCH,
            )
            for i, (start, end) in enumerate(self._matches)
        ]
        self._core.set_decorations(_LAYER, decorations)

        total = len(self._matches)
        self._count_sig.set(f"{self._current + 1} / {total}")

        if 0 <= self._current < total:
            start_offset = self._matches[self._current][0]
            pos = _offset_to_position(_build_line_starts(text), start_offset)
            try:
                self._core.text.see(pos.to_tk())
            except Exception:
                pass

    def _next_match(self) -> None:
        if not self._matches:
            return
        self._current = (self._current + 1) % len(self._matches)
        self._apply_decorations(self._core.value)

    def _prev_match(self) -> None:
        if not self._matches:
            return
        self._current = (self._current - 1) % len(self._matches)
        self._apply_decorations(self._core.value)

    def _set_replace_visible(self, visible: bool) -> None:
        if visible == self._replace_visible:
            return
        self._replace_visible = visible
        if visible:
            self._replace_row.pack(fill="x")
        else:
            self._replace_row.pack_forget()
        self.update_idletasks()
        self._height = max(self.winfo_reqheight(), 44)
        try:
            self.place_configure(height=self._height)
        except Exception:
            pass

    def _set_entry_state(self, state: str) -> None:
        accent_map = {"error": "danger", "no_match": "warning"}
        try:
            self._find_entry.configure(accent=accent_map.get(state, "primary"))
        except Exception:
            pass

    # ── event handlers ────────────────────────────────────────────────────

    def _on_ctrl_f(self, _event) -> str:
        self.show(replace=False)
        return "break"

    def _on_ctrl_h(self, _event) -> str:
        self.show(replace=True)
        return "break"

    def _on_editor_escape(self, _event) -> None:
        if self._visible:
            self.hide()

    def _on_query_changed(self, _event=None) -> None:
        self._schedule_search()

    def _on_option_changed(self) -> None:
        self._schedule_search()

    def _on_content_changed(self, _event) -> None:
        if self._visible:
            self._schedule_search()

    def _on_theme_changed(self, _event=None) -> None:
        self._sync_colors()

    def _sync_colors(self) -> None:
        if self._syncing_colors:
            return
        self._syncing_colors = True
        try:
            self._core.define_style(_STYLE_MATCH, background="#ffff60", foreground="#000000")
            self._core.define_style(_STYLE_CURRENT, background="#ff8000", foreground="#000000")
        finally:
            self._syncing_colors = False

    def _schedule_search(self) -> None:
        if self._after_id is not None:
            try:
                self._core.text.after_cancel(self._after_id)
            except Exception:
                pass
        self._after_id = self._core.text.after(_DEBOUNCE_MS, self._run_search)


# ── position helpers ──────────────────────────────────────────────────────

def _build_line_starts(text: str) -> list[int]:
    starts = [0]
    for i, ch in enumerate(text):
        if ch == "\n":
            starts.append(i + 1)
    return starts


def _offset_to_position(line_starts: list[int], offset: int) -> Position:
    line_idx = bisect.bisect_right(line_starts, offset) - 1
    col = offset - line_starts[line_idx]
    return Position(line_idx + 1, col)


def _position_to_offset(text: str, line: int, col: int) -> int:
    lines = text.split("\n")
    offset = sum(len(lines[i]) + 1 for i in range(min(line - 1, len(lines))))
    return offset + min(col, len(lines[line - 1]) if line <= len(lines) else 0)


def _luminance(hex_color: str) -> float:
    h = hex_color.lstrip("#")
    if len(h) < 6:
        return 200.0
    try:
        r, g, b = int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)
        return 0.299 * r + 0.587 * g + 0.114 * b
    except Exception:
        return 200.0