"""UndoManager filter — word-level undo via character-class grouping.

Adaptation of IDLE's UndoDelegator (idlelib/undo.py). Key differences:
- Renamed UndoManager / _Command for clarity.
- Character-class merging gives word-level undo without needing Tk's
  built-in undo stack (undo=False on the Text widget).
- Canonical line.col indices recorded before forwarding so undo positions
  stay correct after the cursor moves.
- Adjacency check uses line/col arithmetic rather than Tk mark resolution.
"""
from __future__ import annotations

from typing import TYPE_CHECKING

from bootstack.widgets._impl.composites.textarea.filter import EditFilter

if TYPE_CHECKING:
    from bootstack.widgets._impl.composites.textarea.core import _MultilineCore

# Character classes for merging adjacent typed characters into one undo step
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

    def __init__(self, op: str, index: str, chars: str, tags=None) -> None:
        self.op = op        # 'insert' or 'delete'
        self.index = index  # canonical line.col (e.g. "1.5")
        self.chars = chars
        self.tags = tags

    def do(self, core: _MultilineCore) -> None:
        """Re-apply this operation (used by redo)."""
        if self.op == 'insert':
            core.text.insert(self.index, self.chars, self.tags or ())
        else:
            end = core.text.index(f'{self.index} +{len(self.chars)}c')
            core.text.delete(self.index, end)

    def undo(self, core: _MultilineCore) -> None:
        """Reverse this operation."""
        if self.op == 'insert':
            end = core.text.index(f'{self.index} +{len(self.chars)}c')
            core.text.delete(self.index, end)
        else:
            core.text.insert(self.index, self.chars, self.tags or ())

    def merge(self, other: '_Command') -> bool:
        """Try to merge *other* into this command (in-place). Returns True if merged.

        Two single-character inserts merge when they are:
        - Both inserts
        - Adjacent (other starts where self ends, same row)
        - Same character class
        - Neither contains a newline (newlines always start a new block)
        """
        if self.op != 'insert' or other.op != 'insert':
            return False
        if len(other.chars) != 1 or '\n' in other.chars:
            return False
        if not self.chars or '\n' in self.chars:
            return False
        if _char_class(self.chars[-1]) != _char_class(other.chars[0]):
            return False
        # Adjacency: other must start exactly where self ends (same row)
        try:
            row1, col1 = map(int, self.index.split('.'))
            row2, col2 = map(int, other.index.split('.'))
            if row1 == row2 and col1 + len(self.chars) == col2:
                self.chars += other.chars
                return True
        except (ValueError, AttributeError):
            pass
        return False


class UndoManager(EditFilter):
    """Undo/redo filter with character-class word-level grouping.

    Intercepts every insert/delete, records canonical operations, and groups
    consecutive same-class single-character inserts into one undo block.
    Provides `undo()`, `redo()`, `undo_block_start()`,
    `undo_block_stop()`, and `reset_undo()` via the owning core.
    """

    MAX_UNDO = 1000

    def __init__(self) -> None:
        super().__init__()
        self._stack: list[list[_Command]] = []
        self._redo_stack: list[list[_Command]] = []
        self._current_block: list[_Command] | None = None
        self._block_depth: int = 0
        self._saved_index: int = 0   # stack length at last save
        self._core: _MultilineCore | None = None
        self._undoing: bool = False

    # ── lifecycle ──────────────────────────────────────────────────────────

    def attach(self, core: _MultilineCore) -> None:
        self._core = core

    def detach(self, core: _MultilineCore) -> None:
        self._core = None

    # ── filter chain ───────────────────────────────────────────────────────

    def insert(self, index: str, chars: str, tags=None) -> None:
        if not self._undoing:
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
        # Try to merge with the last single-command block
        if self._stack and len(self._stack[-1]) == 1:
            if self._stack[-1][0].merge(cmd):
                return
        self._stack.append([cmd])
        if len(self._stack) > self.MAX_UNDO:
            self._stack.pop(0)
            if self._saved_index > 0:
                self._saved_index -= 1

    # ── public API ────────────────────────────────────────────────────────

    def undo_block_start(self) -> None:
        """Begin a compound undo block. Nested calls are safe."""
        if self._block_depth == 0:
            self._current_block = []
        self._block_depth += 1

    def undo_block_stop(self) -> None:
        """End a compound undo block. Commits when depth reaches zero."""
        self._block_depth -= 1
        if self._block_depth == 0 and self._current_block is not None:
            if self._current_block:
                self._stack.append(self._current_block)
            self._current_block = None

    def undo(self) -> None:
        """Undo the last edit group."""
        if not self._stack or self._core is None:
            return
        block = self._stack.pop()
        self._redo_stack.append(block)
        self._undoing = True
        try:
            for cmd in reversed(block):
                cmd.undo(self._core)
        finally:
            self._undoing = False
        self._core.text.event_generate(
            '<<TextUndo>>', data={'value': self._core.value}, when='tail'
        )

    def redo(self) -> None:
        """Redo the last undone edit group."""
        if not self._redo_stack or self._core is None:
            return
        block = self._redo_stack.pop()
        self._stack.append(block)
        self._undoing = True
        try:
            for cmd in block:
                cmd.do(self._core)
        finally:
            self._undoing = False
        self._core.text.event_generate(
            '<<TextRedo>>', data={'value': self._core.value}, when='tail'
        )

    def reset_undo(self) -> None:
        """Clear undo/redo history and mark current state as saved."""
        self._stack.clear()
        self._redo_stack.clear()
        self._redo_stack.clear()
        self._saved_index = 0

    def mark_saved(self) -> None:
        """Mark the current stack depth as the saved baseline."""
        self._saved_index = len(self._stack)

    @property
    def is_dirty(self) -> bool:
        """True if the stack depth differs from the saved baseline."""
        return len(self._stack) != self._saved_index
