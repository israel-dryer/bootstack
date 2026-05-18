"""CodeEditor — a full-featured code editing widget."""
from __future__ import annotations

import tkinter as tk
from typing import Callable, Literal

from bootstack.widgets.primitives.frame import Frame
from bootstack.widgets.composites.textarea.core import _MultilineCore, ScrollbarMode
from bootstack.widgets.composites.textarea.filter import EditFilter
from bootstack.widgets.composites.textarea.extensions.line_numbers import LineNumbers
from bootstack.widgets.composites.textarea.extensions.bracket_matcher import BracketMatcher
from bootstack.widgets.composites.textarea.extensions.smart_indent import SmartIndent
from bootstack.widgets.composites.textarea.extensions.indent_guides import IndentGuides
from bootstack.widgets.composites.textarea.search_overlay import SearchOverlay
from bootstack.widgets.types import Master

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from bootstack.signals import Signal


class CodeEditor(Frame):
    """A code editor widget with line numbers, bracket matching, and smart indent.

    CodeEditor wraps ``_MultilineCore`` with editor-grade defaults and
    pre-installed extensions. It is not Field-wrapped — use ``TextArea``
    for labeled form inputs.

    Pre-installed extensions:
    - ``LineNumbers`` sidebar (when ``show_line_numbers=True``)
    - ``BracketMatcher`` — highlights matching bracket pairs
    - ``SmartIndent`` — auto-indent on Return, Tab-to-spaces

    Add your own extensions with ``editor.install(filter)`` and remove
    them with ``editor.uninstall(filter)``.
    """

    def __init__(
        self,
        master: Master = None,
        *,
        value: str = "",
        textsignal: Signal | None = None,
        language: str | None = None,
        pygments_style: str = "default",
        read_only: bool = False,
        wrap: bool = False,
        tab_width: int = 4,
        insert_spaces: bool = True,
        auto_indent: bool = True,
        show_line_numbers: bool = True,
        show_indent_guides: bool = False,
        scrollbars: ScrollbarMode = "both",
        font: str = "TkFixedFont",
        extensions: list[EditFilter] | None = None,
        on_change: Callable | None = None,
        on_cursor_move: Callable | None = None,
    ) -> None:
        """Create a CodeEditor widget.

        Args:
            master: Parent widget. If None, uses the default root window.
            value: Initial text content.
            textsignal: Reactive `Signal[str]` bound to the editor content.
            language: Pygments lexer name for syntax highlighting (e.g.
                `'python'`, `'sql'`). Pass `None` to disable highlighting.
            pygments_style: Pygments style name for syntax colors (e.g.
                `'default'`, `'monokai'`, `'dracula'`). Defaults to
                `'default'`.
            read_only: If True, the editor is not editable.
            wrap: If True, long lines wrap. Defaults to False (horizontal
                scroll) which is the typical code editor behavior.
            tab_width: Number of spaces per tab stop. Default is 4.
            insert_spaces: If True, Tab inserts spaces. Default is True.
            auto_indent: If True, Return replicates the current line's
                indentation. Default is True.
            show_line_numbers: If True (default), shows a line number
                gutter to the left of the text.
            show_indent_guides: If True, draws subtle vertical guide marks
                at each indent stop. Defaults to False.
            scrollbars: Scrollbar visibility mode. Defaults to `"both"`
                (always show both axes).
            font: Font for the editor. Defaults to the system fixed-width
                font (`"TkFixedFont"`).
            extensions: Additional `EditFilter` instances to install
                on top of the built-in set.
            on_change: Callback for `<<Change>>` events.
            on_cursor_move: Callback for cursor movement events.
        """
        super().__init__(master)

        self._language = language
        self._pygments_style = pygments_style
        self._show_line_numbers = show_line_numbers
        self._highlighter = None

        # ── core ──────────────────────────────────────────────────────────
        self._core = _MultilineCore(
            self,
            value=value,
            wrap=wrap,
            height=20,
            scrollbars=scrollbars,
            font=font,
            read_only=read_only,
        )

        # ── search overlay ────────────────────────────────────────────────
        self._search = SearchOverlay(self, self._core)

        # _core fills the frame; _search is permanently placed at the bottom
        # and rendered at all times — hidden by keeping _core on top (lift).
        # show_search() just lifts _search; hide_search() lifts _core back.
        # This means there is never a first-render delay on open.
        self._core.pack(fill="both", expand=True)
        self._search.place(
            x=0, rely=1.0, relwidth=1.0,
            height=self._search._height, anchor="sw",
        )
        self._core.lift()

        # ── signal binding ────────────────────────────────────────────────
        if textsignal is not None:
            self._core.bind_signal(textsignal)

        # ── pre-installed extensions ──────────────────────────────────────
        if show_line_numbers:
            self._line_numbers = LineNumbers()
            self._core.add_sidebar(self._line_numbers)
        else:
            self._line_numbers = None

        self._bracket_matcher = BracketMatcher()
        self._core.add_filter(self._bracket_matcher)

        if auto_indent:
            self._smart_indent = SmartIndent(
                tab_width=tab_width,
                insert_spaces=insert_spaces,
            )
            self._core.add_filter(self._smart_indent)
        else:
            self._smart_indent = None

        # ── indent guides ─────────────────────────────────────────────────
        if show_indent_guides:
            self._indent_guides = IndentGuides(tab_width=tab_width)
            self._core.add_filter(self._indent_guides)
        else:
            self._indent_guides = None

        # ── user-supplied extensions ──────────────────────────────────────
        if extensions:
            for ext in extensions:
                self._core.add_filter(ext)

        # ── syntax highlighting ───────────────────────────────────────────
        if language is not None:
            self._try_install_highlighter(language)

        # ── callbacks ─────────────────────────────────────────────────────
        if on_change is not None:
            self._core.on_change(on_change)

        if on_cursor_move is not None:
            self._core.text.bind("<<CursorMove>>", on_cursor_move, add="+")
            self._core.text.bind("<KeyRelease>", on_cursor_move, add="+")
            self._core.text.bind("<ButtonRelease-1>", on_cursor_move, add="+")

    # ── public API ────────────────────────────────────────────────────────

    @property
    def value(self) -> str:
        """Full text content (trailing newline stripped)."""
        return self._core.value

    @value.setter
    def value(self, text: str) -> None:
        self._core.value = text

    @property
    def is_dirty(self) -> bool:
        """True if the content has changed since last save."""
        return self._core.is_dirty

    def mark_saved(self) -> None:
        """Mark the current state as the saved baseline."""
        self._core.mark_saved()

    def undo(self) -> None:
        """Undo the last edit."""
        self._core.undo()

    def redo(self) -> None:
        """Redo the last undone edit."""
        self._core.redo()

    def undo_block_start(self) -> None:
        """Begin a compound undo block."""
        self._core.undo_block_start()

    def undo_block_stop(self) -> None:
        """End a compound undo block."""
        self._core.undo_block_stop()

    def goto_line(self, n: int) -> None:
        """Move the cursor to the start of line *n* and scroll it into view.

        Args:
            n: 1-indexed line number.
        """
        idx = f"{n}.0"
        try:
            self._core.text.mark_set("insert", idx)
            self._core.text.see(idx)
        except tk.TclError:
            pass

    def set_language(self, language: str | None) -> None:
        """Set or change the syntax highlighting language.

        Args:
            language: Pygments lexer name (e.g. `'python'`), or `None`
                to disable syntax highlighting.
        """
        self._language = language
        if self._highlighter is not None:
            self._core.remove_filter(self._highlighter)
            self._highlighter = None
        if language is not None:
            self._try_install_highlighter(language)

    def install(self, f: EditFilter) -> None:
        """Install a custom filter extension.

        Args:
            f: The ``EditFilter`` to add.
        """
        self._core.add_filter(f)

    def uninstall(self, f: EditFilter) -> None:
        """Remove a previously installed filter extension.

        Args:
            f: The ``EditFilter`` to remove.
        """
        self._core.remove_filter(f)

    def focus_set(self) -> None:
        """Set focus to the editor."""
        self._core.focus_set()

    def on_change(self, callback: Callable) -> str:
        """Register a callback for ``<<Change>>`` events.

        Args:
            callback: Receives the Tk event.

        Returns:
            Bind ID — pass to ``off_change()`` to unsubscribe.
        """
        return self._core.on_change(callback)

    def off_change(self, bind_id: str | None = None) -> None:
        """Unsubscribe from ``<<Change>>``.

        Args:
            bind_id: ID returned by ``on_change()``. If None, removes all.
        """
        self._core.off_change(bind_id)

    def on_modified(self, callback: Callable) -> str:
        """Register a callback for ``<<TextModified>>`` events.

        Args:
            callback: Receives event with ``event.data = {"is_dirty": bool}``.

        Returns:
            Bind ID — pass to ``off_modified()`` to unsubscribe.
        """
        return self._core.on_modified(callback)

    def off_modified(self, bind_id: str | None = None) -> None:
        """Unsubscribe from ``<<TextModified>>``.

        Args:
            bind_id: ID returned by ``on_modified()``. If None, removes all.
        """
        self._core.off_modified(bind_id)

    def on_undo(self, callback: Callable) -> str:
        """Register a callback for ``<<TextUndo>>`` events.

        Args:
            callback: Receives event with ``event.data = {"value": str}``.

        Returns:
            Bind ID — pass to ``off_undo()`` to unsubscribe.
        """
        return self._core.on_undo(callback)

    def off_undo(self, bind_id: str | None = None) -> None:
        """Unsubscribe from ``<<TextUndo>>``.

        Args:
            bind_id: ID returned by ``on_undo()``. If None, removes all.
        """
        self._core.off_undo(bind_id)

    def on_redo(self, callback: Callable) -> str:
        """Register a callback for ``<<TextRedo>>`` events.

        Args:
            callback: Receives event with ``event.data = {"value": str}``.

        Returns:
            Bind ID — pass to ``off_redo()`` to unsubscribe.
        """
        return self._core.on_redo(callback)

    def off_redo(self, bind_id: str | None = None) -> None:
        """Unsubscribe from ``<<TextRedo>>``.

        Args:
            bind_id: ID returned by ``on_redo()``. If None, removes all.
        """
        self._core.off_redo(bind_id)

    @property
    def core(self) -> _MultilineCore:
        """The internal ``_MultilineCore`` — for advanced extension use."""
        return self._core

    def show_search(self) -> None:
        """Show the find bar and focus the search input."""
        self._search.show()

    def hide_search(self) -> None:
        """Hide the find bar and clear search highlights."""
        self._search.hide()


    # ── internal ─────────────────────────────────────────────────────────

    def _try_install_highlighter(self, language: str) -> None:
        from bootstack.widgets.composites.textarea.extensions.pygments_highlighter import (
            PygmentsHighlighter,
        )
        h = PygmentsHighlighter(language, pygments_style=self._pygments_style)
        self._core.add_filter(h)
        self._highlighter = h
