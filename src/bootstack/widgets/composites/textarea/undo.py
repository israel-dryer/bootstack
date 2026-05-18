"""UndoManager filter — undo/redo with character-class grouping.

Port of idlelib/undo.py UndoDelegator. Key differences:
- Renamed to UndoManager / _Command for clarity.
- IDLE's idleConf references replaced with direct constants.
- Integrates with _MultilineCore's is_dirty tracking via saved_change_hook.
"""
from __future__ import annotations

import tkinter as tk
from typing import TYPE_CHECKING

from bootstack.widgets.composites.textarea.filter import EditFilter

if TYPE_CHECKING:
    from bootstack.widgets.composites.textarea.core import _MultilineCore

# Character classes for merging adjacent typed chars into one undo step
_ALPHANUMERIC = frozenset(
    'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789_'
)


def _char_class(ch: str) -> str:
    if ch in _ALPHANUMERIC:
        return 'alphanum'
    if ch == '\n':
        return 'newline'
    return 'punct'


class _Command:
    """One reversible edit operation."""

    def __init__(
        self,
        op: str,
        index: str,
        chars: str,
        tags=None,
    ) -> None:
        self.op = op        # 'insert' or 'delete'
        self.index = index
        self.chars = chars
        self.tags = tags

    def do(self, text: tk.Text) -> None:
        if self.op == 'insert':
            text.insert(self.index, self.chars, self.tags or ())
        else:
            end = text.index(f'{self.index} +{len(self.chars)}c')
            text.delete(self.index, end)

    def undo(self, text: tk.Text) -> None:
        if self.op == 'insert':
            end = text.index(f'{self.index} +{len(self.chars)}c')
            text.delete(self.index, end)
        else:
            text.insert(self.index, self.chars, self.tags or ())

    def merge(self, other: '_Command') -> bool:
        """Try to merge *other* into this command. Returns True if merged."""
        if self.op != 'insert' or other.op != 'insert':
            return False
        if len(other.chars) != 1:
            return False
        # Must be adjacent
        if self.index != 'insert':
            return False
        # Same character class
        if not self.chars or _char_class(self.chars[-1]) != _char_class(other.chars[0]):
            return False
        self.chars += other.chars
        return True


class UndoManager(EditFilter):
    """Undo/redo filter with character-class merge and explicit block grouping.

    Provides ``undo()``, ``redo()``, ``undo_block_start()``,
    ``undo_block_stop()``, and ``reset_undo()`` on the core and on any
    widget that wraps the core.

    The ``is_dirty`` property on the core reflects whether the text
    differs from its last-saved state.
    """

    MAX_UNDO = 1000

    def __init__(self) -> None:
        super().__init__()
        self._stack: list[list[_Command]] = []
        self._redo_stack: list[list[_Command]] = []
        self._current_block: list[_Command] | None = None
        self._block_depth: int = 0
        self._saved_index: int = -1   # stack index at last save
        self._core: _MultilineCore | None = None
        self._undoing: bool = False

    # ── lifecycle ──────────────────────────────────────────────────────────

    def attach(self, core: _MultilineCore) -> None:
        self._core = core
        core.bind('<Control-z>', self._on_undo, add='+')
        core.bind('<Control-Z>', self._on_redo, add='+')  # Ctrl+Shift+Z

    def _on_undo(self, _event=None) -> str:
        self.undo()
        return 'break'

    def _on_redo(self, _event=None) -> str:
        self.redo()
        return 'break'

    def detach(self, core: _MultilineCore) -> None:
        self._core = None

    # ── filter chain ───────────────────────────────────────────────────────

    def insert(self, index: str, chars: str, tags=None) -> None:
        if not self._undoing:
            # Resolve marks like "insert" to canonical line.col before forwarding
            # so the recorded position stays correct after the cursor moves.
            canonical = self.index(index)
            self.delegate.insert(index, chars, tags)
            self._record(_Command('insert', canonical, chars, tags))
        else:
            self.delegate.insert(index, chars, tags)

    def delete(self, index1: str, index2: str | None = None) -> None:
        if not self._undoing:
            canonical = self.index(index1)
            end = index2 if index2 else self.index(f'{index1} +1c')
            chars = self.get(canonical, end)
            self.delegate.delete(index1, index2)
            self._record(_Command('delete', canonical, chars))
        else:
            self.delegate.delete(index1, index2)

    # ── recording ─────────────────────────────────────────────────────────

    def _record(self, cmd: _Command) -> None:
        self._redo_stack.clear()
        if self._current_block is not None:
            self._current_block.append(cmd)
            return
        # Try to merge with last single-command block
        if self._stack and len(self._stack[-1]) == 1:
            if self._stack[-1][0].merge(cmd):
                return
        self._stack.append([cmd])
        if len(self._stack) > self.MAX_UNDO:
            self._stack.pop(0)
            if self._saved_index >= 0:
                self._saved_index -= 1
        self._update_dirty()

    # ── public API ────────────────────────────────────────────────────────

    def undo_block_start(self) -> None:
        """Begin a compound undo block. Nest calls are safe."""
        if self._block_depth == 0:
            self._current_block = []
        self._block_depth += 1

    def undo_block_stop(self) -> None:
        """End a compound undo block. Commits the block if depth reaches zero."""
        self._block_depth -= 1
        if self._block_depth == 0 and self._current_block is not None:
            if self._current_block:
                self._stack.append(self._current_block)
            self._current_block = None

    def undo(self) -> None:
        """Undo the last edit group."""
        if not self._stack:
            return
        block = self._stack.pop()
        self._redo_stack.append(block)
        self._undoing = True
        try:
            for cmd in reversed(block):
                cmd.undo(self._core.text)
        finally:
            self._undoing = False
        self._update_dirty()

    def redo(self) -> None:
        """Redo the last undone edit group."""
        if not self._redo_stack:
            return
        block = self._redo_stack.pop()
        self._stack.append(block)
        self._undoing = True
        try:
            for cmd in block:
                cmd.do(self._core.text)
        finally:
            self._undoing = False
        self._update_dirty()

    def reset_undo(self) -> None:
        """Clear undo/redo history and mark current state as saved."""
        self._stack.clear()
        self._redo_stack.clear()
        self._saved_index = -1
        if self._core is not None:
            self._core._dirty = False

    def mark_saved(self) -> None:
        """Mark the current state as the saved baseline for ``is_dirty``."""
        self._saved_index = len(self._stack)
        if self._core is not None:
            self._core._dirty = False

    def _update_dirty(self) -> None:
        if self._core is not None:
            self._core._dirty = len(self._stack) != self._saved_index
