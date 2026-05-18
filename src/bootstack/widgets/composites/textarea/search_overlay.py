"""SearchOverlay — find bar for CodeEditor.

A compact panel that docks at the bottom of the editor. Opened with
Ctrl+F, closed with Esc. Highlights all matches via the decoration layer
system and navigates through them with arrow buttons or Enter/Shift+Enter.
"""
from __future__ import annotations

import re
import bisect
import tkinter as tk
from typing import TYPE_CHECKING

from bootstack.widgets.primitives.frame import Frame
from bootstack.widgets.primitives.label import Label
from bootstack.widgets.primitives.button import Button
from bootstack.widgets.primitives.separator import Separator
from bootstack.widgets.primitives.checktoggle import CheckToggle
from bootstack.widgets.composites.textentry import TextEntry
from bootstack.widgets.composites.textarea.decoration import Position, RangeDecoration

if TYPE_CHECKING:
    from bootstack.widgets.composites.textarea.core import _MultilineCore


_LAYER = "search"
_STYLE_MATCH = "search_match"
_STYLE_CURRENT = "search_current"
_DEBOUNCE_MS = 120


class SearchOverlay(Frame):
    """Find bar that docks at the bottom of the editor.

    Created and owned by `CodeEditor` — not part of the public API.
    Interact via `CodeEditor.show_search()` / `CodeEditor.hide_search()`.
    """

    def __init__(self, parent: tk.Misc, core: _MultilineCore) -> None:
        super().__init__(parent, padding=(6, 4), surface="chrome")
        self._core = core
        self._matches: list[tuple[int, int]] = []   # (start_offset, end_offset)
        self._current: int = -1                      # index into _matches
        self._after_id: str | None = None
        self._case_var = tk.BooleanVar(value=False)
        self._regex_var = tk.BooleanVar(value=False)
        self._syncing_colors = False

        # ── register decoration styles ─────────────────────────────────
        core.register_layer(_LAYER, priority=10)
        # foreground="#000000" ensures matched text is readable on both light
        # (yellow bg) and dark (orange bg) editor backgrounds.
        core.define_style(_STYLE_MATCH, background="#ffff60", foreground="#000000")
        core.define_style(_STYLE_CURRENT, background="#ff8000", foreground="#000000")

        # ── layout ────────────────────────────────────────────────────
        self._close_btn = Button(
            self, icon="x-lg", icon_only=True, variant="ghost", density="compact",
            command=self.hide,
        )
        self._close_btn.pack(side="left", padx=(0, 8))

        Label(self, text="Find:").pack(side="left", padx=(0, 4))

        self._find_entry = TextEntry(self, width=28, density="compact")
        self._find_entry.on_changed(self._on_query_changed)
        self._find_entry.pack(side="left")

        self._count_lbl = Label(self, text="", width=8)
        self._count_lbl.pack(side="left", padx=(6, 0))

        self._prev_btn = Button(
            self, icon="chevron-up", icon_only=True, variant="ghost",
            density="compact", command=self._prev_match,
        )
        self._prev_btn.pack(side="left")

        self._next_btn = Button(
            self, icon="chevron-down", icon_only=True, variant="ghost",
            density="compact", command=self._next_match,
        )
        self._next_btn.pack(side="left")

        Separator(self, orient="vertical").pack(side="left", fill="y", padx=10)

        self._case_toggle = CheckToggle(
            self, icon="type", icon_only=True, variable=self._case_var,
            onvalue=True, offvalue=False,
            command=self._on_option_changed,
            density="compact",
        )
        self._case_toggle.pack(side="left")

        self._regex_toggle = CheckToggle(
            self, icon="regex", icon_only=True, variable=self._regex_var,
            onvalue=True, offvalue=False,
            command=self._on_option_changed,
            density="compact",
        )
        self._regex_toggle.pack(side="left")

        # ── key bindings on the find entry ────────────────────────────
        # TextEntry wraps an inner entry widget; bind to the inner widget
        # so key events are captured when the entry has focus.
        inner = self._find_entry.entry_widget
        inner.bind("<Return>",      lambda _: self._next_match())
        inner.bind("<Shift-Return>", lambda _: self._prev_match())
        inner.bind("<Escape>",       lambda _: self.hide())

        # ── key bindings on the editor text widget ────────────────────
        # Ctrl+F on Windows/Linux; Command+F on macOS (aqua windowing system).
        core.text.bind("<Control-f>", self._on_ctrl_f, add="+")
        core.text.bind("<Control-F>", self._on_ctrl_f, add="+")
        if core.winsys == "aqua":
            core.text.bind("<Command-f>", self._on_ctrl_f, add="+")
            core.text.bind("<Command-F>", self._on_ctrl_f, add="+")
        core.text.bind("<Escape>",    self._on_editor_escape, add="+")

        # Re-run search when content changes (while search bar is open).
        core.text.bind("<<Change>>", self._on_content_changed, add="+")

        # Re-sync colors when the bootstack theme changes or when the Pygments
        # highlighter changes the editor background (<<EditorBgChanged>>).
        core.text.bind("<<ThemeChanged>>",   self._on_theme_changed, add="+")
        core.text.bind("<<EditorBgChanged>>", self._on_theme_changed, add="+")

    # ── public API ────────────────────────────────────────────────────────

    def show(self) -> None:
        """Show the find bar and focus the search input."""
        self._sync_colors()
        self.grid()
        self._find_entry.focus_set()
        self._run_search()

    def hide(self) -> None:
        """Hide the find bar and clear all highlights."""
        self.grid_remove()
        self._core.clear_decorations(_LAYER)
        self._matches = []
        self._current = -1
        self._count_lbl.configure(text="")
        self._set_entry_state("normal")
        try:
            self._core.text.focus_set()
        except Exception:
            pass

    # ── search logic ──────────────────────────────────────────────────────

    def _run_search(self) -> None:
        self._after_id = None
        query = self._find_entry.value or ""
        if not query:
            self._core.clear_decorations(_LAYER)
            self._matches = []
            self._current = -1
            self._count_lbl.configure(text="")
            self._set_entry_state("normal")
            return

        text = self._core.value
        flags = 0 if self._case_var.get() else re.IGNORECASE

        try:
            if self._regex_var.get():
                pattern = re.compile(query, flags)
            else:
                pattern = re.compile(re.escape(query), flags)
        except re.error:
            self._set_entry_state("error")
            self._core.clear_decorations(_LAYER)
            self._matches = []
            self._current = -1
            self._count_lbl.configure(text="bad regex")
            return

        self._matches = [(m.start(), m.end()) for m in pattern.finditer(text)]

        if not self._matches:
            self._core.clear_decorations(_LAYER)
            self._current = -1
            self._count_lbl.configure(text="no matches")
            self._set_entry_state("no_match")
            return

        self._set_entry_state("normal")

        # Pick the closest match to the current cursor position.
        try:
            idx = self._core.text.index("insert")
            line_no, col_no = idx.split(".")
            cursor_offset = _position_to_offset(text, int(line_no), int(col_no))
        except Exception:
            cursor_offset = 0

        starts = [m[0] for m in self._matches]
        pos = bisect.bisect_left(starts, cursor_offset)
        self._current = pos % len(self._matches)

        self._apply_decorations(text)

    def _apply_decorations(self, text: str) -> None:
        """Build and apply match decorations, scrolling the current match into view."""
        if not self._matches:
            self._core.clear_decorations(_LAYER)
            return

        line_starts = _build_line_starts(text)
        decorations: list[RangeDecoration] = []

        for i, (start, end) in enumerate(self._matches):
            style = _STYLE_CURRENT if i == self._current else _STYLE_MATCH
            decorations.append(RangeDecoration(
                _offset_to_position(line_starts, start),
                _offset_to_position(line_starts, end),
                style,
            ))

        self._core.set_decorations(_LAYER, decorations)

        total = len(self._matches)
        self._count_lbl.configure(text=f"{self._current + 1} / {total}")

        # Scroll current match into view.
        if 0 <= self._current < total:
            start_offset = self._matches[self._current][0]
            pos = _offset_to_position(line_starts, start_offset)
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

    def _set_entry_state(self, state: str) -> None:
        # Use the TextEntry's accent to signal error/warning visually.
        accent_map = {"error": "danger", "no_match": "warning"}
        accent = accent_map.get(state, "primary")
        try:
            self._find_entry.configure(accent=accent)
        except Exception:
            pass

    # ── event handlers ────────────────────────────────────────────────────

    def _on_ctrl_f(self, _event: tk.Event) -> str:
        self.show()
        return "break"

    def _on_editor_escape(self, _event: tk.Event) -> None:
        if self.winfo_ismapped():
            self.hide()

    def _on_query_changed(self, _event=None) -> None:
        self._schedule_search()

    def _on_option_changed(self) -> None:
        self._schedule_search()

    def _on_content_changed(self, _event: tk.Event) -> None:
        if self.winfo_ismapped():
            self._schedule_search()

    def _on_theme_changed(self, _event: tk.Event = None) -> None:
        self._sync_colors()

    def _sync_colors(self) -> None:
        """Re-apply match highlight colors to the decoration styles."""
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
    """Return the character offset of the first character on each line."""
    starts = [0]
    for i, ch in enumerate(text):
        if ch == "\n":
            starts.append(i + 1)
    return starts


def _offset_to_position(line_starts: list[int], offset: int) -> Position:
    """Convert a character offset to a (line, col) Position."""
    line_idx = bisect.bisect_right(line_starts, offset) - 1
    col = offset - line_starts[line_idx]
    return Position(line_idx + 1, col)


def _position_to_offset(text: str, line: int, col: int) -> int:
    """Convert a (1-indexed line, 0-indexed col) pair to a character offset."""
    lines = text.split("\n")
    offset = sum(len(lines[i]) + 1 for i in range(min(line - 1, len(lines))))
    return offset + min(col, len(lines[line - 1]) if line <= len(lines) else 0)


def _luminance(hex_color: str) -> float:
    """Return perceptual luminance (0–255) for a hex color string."""
    h = hex_color.lstrip("#")
    if len(h) < 6:
        return 200.0
    try:
        r, g, b = int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)
        return 0.299 * r + 0.587 * g + 0.114 * b
    except Exception:
        return 200.0