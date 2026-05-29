"""BracketMatcher — highlights matching bracket pairs on cursor move.

Filter-style extension: binds to cursor-movement events and applies a
highlight tag to the bracket under the cursor and its matching pair.
Uses a flash-and-restore pattern borrowed from idlelib/parenmatch.py.
"""
from __future__ import annotations

import tkinter as tk
from typing import TYPE_CHECKING

from bootstack.widgets._impl.composites.textarea.filter import EditFilter

if TYPE_CHECKING:
    from bootstack.widgets._impl.composites.textarea.core import _MultilineCore

_OPENERS = "([{"
_CLOSERS = ")]}"
_PAIRS = dict(zip(_OPENERS, _CLOSERS))
_REVERSE = dict(zip(_CLOSERS, _OPENERS))

_LAYER = "bracket"
_STYLE = "match"
_TAG = f"bs::{_LAYER}::{_STYLE}"
_FLASH_MS = 500     # how long to show the highlight


class BracketMatcher(EditFilter):
    """Highlights matching bracket pairs when the cursor rests on a bracket.

    Install via `core.add_filter(BracketMatcher())`.
    The highlight tag `bs::bracket::match` is applied to both the bracket
    under the cursor and its matching partner. It is removed after
    `_FLASH_MS` milliseconds or on the next cursor move.
    """

    def __init__(self) -> None:
        super().__init__()
        self._core: _MultilineCore | None = None
        self._after_id: str | None = None

    def attach(self, core: _MultilineCore) -> None:
        self._core = core
        core.define_style(_STYLE, foreground="primary", background="primary[subtle]")
        core.register_layer(_LAYER, priority=5)
        core.text.bind("<<CursorMove>>", self._on_cursor_move, add="+")
        core.text.bind("<KeyRelease>", self._on_cursor_move, add="+")
        core.text.bind("<ButtonRelease-1>", self._on_cursor_move, add="+")

    def detach(self, core: _MultilineCore) -> None:
        self._clear()
        self._core = None

    # ── filter pass-through (BracketMatcher doesn't intercept edits) ──────

    def insert(self, index: str, chars: str, tags=None) -> None:
        self.delegate.insert(index, chars, tags)

    def delete(self, index1: str, index2: str | None = None) -> None:
        self.delegate.delete(index1, index2)

    # ── matching logic ────────────────────────────────────────────────────

    def _on_cursor_move(self, _event=None) -> None:
        self._clear()
        if self._core is None:
            return
        text = self._core.text
        cursor = text.index("insert")
        # Check character at cursor and the one before it
        for idx in (cursor, f"{cursor}-1c"):
            ch = text.get(idx)
            if ch in _OPENERS:
                partner = self._find_close(text, idx, ch)
                if partner:
                    self._highlight(idx, partner)
                return
            if ch in _CLOSERS:
                partner = self._find_open(text, idx, ch)
                if partner:
                    self._highlight(partner, idx)
                return

    def _find_close(self, text: tk.Text, start: str, opener: str) -> str | None:
        closer = _PAIRS[opener]
        depth = 1
        idx = text.index(f"{start}+1c")
        end = text.index("end")
        while text.compare(idx, "<", end):
            ch = text.get(idx)
            if ch == opener:
                depth += 1
            elif ch == closer:
                depth -= 1
                if depth == 0:
                    return idx
            idx = text.index(f"{idx}+1c")
        return None

    def _find_open(self, text: tk.Text, start: str, closer: str) -> str | None:
        opener = _REVERSE[closer]
        depth = 1
        idx = text.index(f"{start}-1c")
        while text.compare(idx, ">=", "1.0"):
            ch = text.get(idx)
            if ch == closer:
                depth += 1
            elif ch == opener:
                depth -= 1
                if depth == 0:
                    return idx
            if text.compare(idx, "==", "1.0"):
                break
            idx = text.index(f"{idx}-1c")
        return None

    def _highlight(self, a: str, b: str) -> None:
        if self._core is None:
            return
        text = self._core.text
        for idx in (a, b):
            text.tag_add(_TAG, idx, f"{idx}+1c")
        if self._after_id is not None:
            text.after_cancel(self._after_id)
        self._after_id = text.after(_FLASH_MS, self._clear)

    def _clear(self) -> None:
        if self._after_id is not None and self._core is not None:
            try:
                self._core.text.after_cancel(self._after_id)
            except Exception:
                pass
            self._after_id = None
        if self._core is not None:
            try:
                self._core.text.tag_remove(_TAG, "1.0", "end")
            except Exception:
                pass
