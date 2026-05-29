from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from bootstack.widgets._impl._parts.numberentry_part import NumberEntryPart
    from bootstack.widgets._impl._parts.textentry_part import TextEntryPart


class EntryMixin:
    """Exposes the text-editing API of the internal entry part on composite widgets.

    Composite widgets that embed a text or numeric entry part inherit this mixin
    so callers can manipulate content (insert, delete, select) directly on the
    composite without accessing the internal part.
    """

    _entry: TextEntryPart | NumberEntryPart

    def bbox(self, index: int | str) -> tuple[int, int, int, int]:
        """Return the bounding box of the character at index.

        Args:
            index: Character index or named position (e.g., `'insert'`, `'end'`).

        Returns:
            A tuple `(x, y, width, height)` in pixels.
        """
        return self._entry.bbox(index)

    def delete(self, first: int | str, last: int | str = None) -> None:
        """Delete text between two indices.

        Args:
            first: Start index (inclusive).
            last: End index (exclusive). If None, deletes a single character at `first`.
        """
        return self._entry.delete(first, last)

    def insert(self, index: int | str, text: str) -> None:
        """Insert text at the given index.

        Args:
            index: Position to insert at. Use `'end'` to append.
            text: Text to insert.
        """
        return self._entry.insert(index, text)

    def icursor(self, index: int | str) -> None:
        """Move the insertion cursor to index.

        Args:
            index: Target cursor position.
        """
        self._entry.icursor(index)

    def index(self, index: int | str = 'insert') -> int:
        """Return the numerical index of a position.

        Args:
            index: Named position or numerical index. Defaults to `'insert'`
                (the current cursor position).

        Returns:
            The numerical character index.
        """
        return self._entry.index(index)

    def scan_mark(self, x: int) -> None:
        """Record the starting position for a drag-to-scroll operation.

        Args:
            x: The x-coordinate (in pixels) where the drag begins.
        """
        return self._entry.scan_mark(x)

    def scan_dragto(self, x: int) -> None:
        """Scroll the entry to follow the pointer during a drag operation.

        Call after `scan_mark` as the pointer moves.

        Args:
            x: The current x-coordinate (in pixels) of the pointer.
        """
        return self._entry.scan_dragto(x)

    def selection_adjust(self, index: int | str) -> None:
        """Extend or shrink the selection to include index.

        Args:
            index: Target index to adjust the selection endpoint to.
        """
        return self._entry.selection_adjust(index)

    def selection_clear(self) -> None:
        """Clear the current text selection."""
        return self._entry.selection_clear()

    def selection_from(self, index: int | str) -> None:
        """Set the selection anchor to index.

        Args:
            index: The index at which the selection starts.
        """
        return self._entry.selection_from(index)

    def selection_to(self, index: int | str) -> None:
        """Extend the selection from the anchor to index.

        Args:
            index: The index at which the selection ends.
        """
        return self._entry.selection_to(index)

    def selection_range(self, first: int | str, last: int | str) -> None:
        """Select the text between first and last.

        Args:
            first: Start index (inclusive).
            last: End index (exclusive). Use `'end'` for the last character.
        """
        return self._entry.selection_range(first, last)

    def selection_present(self) -> bool:
        """Return True if any text is currently selected.

        Returns:
            True if a selection exists, False otherwise.
        """
        return self._entry.selection_present()

    def selection_all(self) -> None:
        """Select all text in the entry."""
        return self._entry.selection_range(0, 'end')