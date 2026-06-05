from __future__ import annotations

import tkinter
from contextlib import contextmanager
from typing import overload, Any, Callable, Iterator, TYPE_CHECKING

from bootstack.widgets._impl.composites.textarea.codeeditor import CodeEditor as _InternalCodeEditor
from bootstack.widgets._impl.composites.textarea.filter import EditFilter
from bootstack.widgets._core.base import PublicWidgetBase, adapt_handler
from bootstack.widgets._core.events import resolve_event, register_widget_events
from bootstack.events import Subscription
from bootstack.streams import Stream
from bootstack.widgets.types import AccentToken, Event

if TYPE_CHECKING:
    from bootstack.signals import Signal

_CODEEDITOR_EVENTS: dict[str, str] = {
    "change":      "<<Change>>",
    "input":       "<KeyRelease>",
    "modified":    "<<TextModified>>",
    "undo":        "<<TextUndo>>",
    "redo":        "<<TextRedo>>",
    "cursor_move": "<<CursorMove>>",
    "focus":       "<FocusIn>",
    "blur":        "<FocusOut>",
}

_INNER_SEQUENCES = frozenset({
    "<<Change>>", "<<TextModified>>", "<<TextUndo>>", "<<TextRedo>>",
    "<<CursorMove>>", "<KeyRelease>", "<FocusIn>", "<FocusOut>",
})


class CodeEditor(PublicWidgetBase):
    """A full-featured code editor with line numbers, bracket matching, and syntax highlighting.

    Not Field-wrapped — use `TextArea` for labeled form inputs.

    Args:
        value: Initial text content.
        textsignal: Reactive `Signal[str]` bound to the editor content.
        language: Pygments lexer name for syntax highlighting (e.g. `'python'`,
            `'sql'`). `None` disables highlighting.
        theme: Pygments color scheme. `'auto'` (default) switches between
            `light_theme` and `dark_theme` when the bootstack theme changes.
            Pass an explicit Pygments style name (e.g. `'monokai'`, `'dracula'`)
            to pin the scheme regardless of the bootstack theme.
        light_theme: Pygments style used when `theme='auto'` and the active
            bootstack theme is light. Default `'default'`.
        dark_theme: Pygments style used when `theme='auto'` and the active
            bootstack theme is dark. Default `'monokai'`.
        read_only: If True, content is visible but not editable.
        wrap: If True, long lines wrap. Default `False` (horizontal scroll).
        tab_width: Number of spaces per tab stop. Default `4`.
        insert_spaces: If True, Tab inserts spaces instead of a tab character.
        auto_indent: If True, Return replicates the current line's indentation.
        show_line_numbers: If True (default), shows a line-number gutter.
        show_indent_guides: If True, draws subtle vertical guide marks at
            each indent stop.
        height: Visible row count. Default `20`.
        scrollbars: Scrollbar visibility — `'both'` (default), `'auto'`,
            `'vertical'`, or `'none'`.
        font: Font for the editor. Default `'TkFixedFont'`.
        show_border: If True (default), styles the editor frame as a themed
            border with a focus ring.
        accent: Accent token for the focus border. Default `'primary'`.
        extensions: Additional `EditFilter` instances to install on top of
            the built-in set.
        parent: Override the context-stack parent.
    """

    def __init__(
        self,
        value: str = "",
        *,
        textsignal: "Signal[str] | None" = None,
        language: str | None = None,
        theme: str = "auto",
        light_theme: str = "default",
        dark_theme: str = "monokai",
        read_only: bool = False,
        wrap: bool = False,
        tab_width: int = 4,
        insert_spaces: bool = True,
        auto_indent: bool = True,
        show_line_numbers: bool = True,
        show_indent_guides: bool = False,
        height: int = 20,
        scrollbars: str = "both",
        font: str = "TkFixedFont",
        show_border: bool = True,
        accent: AccentToken | str = "primary",
        extensions: list[EditFilter] | None = None,
        parent: Any = None,
        **kwargs: Any,
    ) -> None:
        self._parent = self._resolve_parent(parent)
        layout_kw = self._split_layout_kwargs(kwargs)

        tk_master = self._parent._child_master() if self._parent else None

        internal_kwargs: dict[str, Any] = {
            "value": value,
            "language": language,
            "pygments_style": theme,
            "light_theme": light_theme,
            "dark_theme": dark_theme,
            "read_only": read_only,
            "wrap": wrap,
            "tab_width": tab_width,
            "insert_spaces": insert_spaces,
            "auto_indent": auto_indent,
            "show_line_numbers": show_line_numbers,
            "show_indent_guides": show_indent_guides,
            "height": height,
            "scrollbars": scrollbars,
            "font": font,
            "show_border": show_border,
            "accent": accent,
        }
        if textsignal is not None:
            internal_kwargs["textsignal"] = textsignal
        if extensions is not None:
            internal_kwargs["extensions"] = extensions

        self._internal = _InternalCodeEditor(tk_master, **internal_kwargs)

        # Generate <<CursorMove>> so on_cursor_move() subscribers always work.
        t = self._internal._core.text
        t.bind("<KeyRelease>",      lambda e: t.event_generate("<<CursorMove>>"), add="+")
        t.bind("<ButtonRelease-1>", lambda e: t.event_generate("<<CursorMove>>"), add="+")

        self._attach_to_parent(layout_kw)

    # ----- Event routing -----

    def _text_widget(self) -> tkinter.Misc:
        return self._internal._core.text

    @overload
    def on(self, event: str) -> Stream: ...
    @overload
    def on(self, event: str, handler: Callable[[Event], Any]) -> Subscription: ...
    def on(self, event: str, handler: Callable[[Event], Any] | None = None) -> Stream | Subscription:
        sequence = resolve_event(self, str(event))
        target = self._text_widget() if sequence in _INNER_SEQUENCES else self._internal
        if handler is None:
            def _source(h):
                t = self._text_widget() if sequence in _INNER_SEQUENCES else self._internal
                bid = t.bind(sequence, adapt_handler(h), add="+")
                return Subscription(t, sequence, bid)
            return Stream(self._internal, _source=_source)
        bid = target.bind(sequence, adapt_handler(handler), add="+")
        return Subscription(target, sequence, bid)

    # ----- Properties -----

    @property
    def value(self) -> str:
        """Full text content (trailing newline stripped)."""
        return self._internal.value

    @value.setter
    def value(self, v: str) -> None:
        self._internal.value = v

    @property
    def signal(self) -> "Signal[str] | None":
        """The reactive `Signal` bound to this editor, or `None`."""
        return getattr(self._internal._core, "signal", None)

    @property
    def is_dirty(self) -> bool:
        """True if content has changed since the last `mark_saved()` call."""
        return self._internal.is_dirty

    @property
    def language(self) -> str | None:
        """Active syntax highlighting language, or `None` if disabled."""
        return self._internal._language

    @language.setter
    def language(self, v: str | None) -> None:
        self._internal.set_language(v)

    @property
    def theme(self) -> str:
        """Active Pygments color scheme, or `'auto'` if tracking the bootstack theme."""
        return self._internal._pygments_style

    @theme.setter
    def theme(self, v: str) -> None:
        self._internal._pygments_style = v
        if self._internal._highlighter is not None:
            self._internal._highlighter._auto = (v == "auto")
            if v != "auto":
                self._internal._highlighter._load_style(v)
                for sname, color in self._internal._highlighter._style_colors.items():
                    self._internal._core.define_style(sname, foreground=color)
            self._internal._highlighter._apply_widget_colors(self._internal._core)
            self._internal._highlighter._schedule()

    @property
    def read_only(self) -> bool:
        """Whether the editor content is visible but not editable."""
        return self._internal._core._read_only

    @read_only.setter
    def read_only(self, v: bool) -> None:
        self._internal._core._read_only = v
        self._internal._core.text.configure(
            state=tkinter.DISABLED if v else tkinter.NORMAL
        )

    # ----- Methods -----

    def clear(self) -> None:
        """Clear all text content."""
        self._internal.value = ""

    def insert(self, index: str, text: str) -> None:
        """Insert `text` at `index`.

        `index` is a text position: `'end'` for the end of the content, or a
        `'line.column'` string such as `'1.0'` (line 1, column 0).

        Args:
            index: Target text position, e.g. `'end'` or `'1.0'`.
            text: Text to insert.
        """
        self._internal._core.text.insert(index, text)

    def select_all(self) -> None:
        """Select all text content."""
        tw = self._internal._core.text
        tw.focus_set()
        tw.tag_add("sel", "1.0", "end-1c")
        tw.mark_set("insert", "end-1c")

    def focus(self) -> None:
        """Move keyboard focus to the editor."""
        self._internal.focus_set()

    def goto_line(self, n: int) -> None:
        """Move the cursor to the start of line `n` and scroll it into view.

        Args:
            n: 1-indexed line number.
        """
        self._internal.focus_set()
        self._internal.goto_line(n)

    def undo(self) -> None:
        """Undo the last edit."""
        self._internal.undo()

    def redo(self) -> None:
        """Redo the last undone edit."""
        self._internal.redo()

    @contextmanager
    def undo_block(self) -> Iterator[None]:
        """Context manager that groups edits into a single undo step.

        Usage::

            with editor.undo_block():
                editor.insert("1.0", "# header\\n")
                editor.value = new_content
        """
        self._internal.undo_block_start()
        try:
            yield
        finally:
            self._internal.undo_block_stop()

    def mark_saved(self) -> None:
        """Mark the current state as the saved baseline (clears `is_dirty`)."""
        self._internal.mark_saved()

    def install(self, f: EditFilter) -> None:
        """Install a custom filter extension.

        Args:
            f: The `EditFilter` to add.
        """
        self._internal.install(f)

    def uninstall(self, f: EditFilter) -> None:
        """Remove a previously installed filter extension.

        Args:
            f: The `EditFilter` to remove.
        """
        self._internal.uninstall(f)

    def show_search(self) -> None:
        """Show the find bar and focus the search input."""
        self._internal.show_search()

    def show_replace(self) -> None:
        """Show the find/replace bar with the replace row visible."""
        self._internal.show_replace()

    def hide_search(self) -> None:
        """Hide the find/replace bar."""
        self._internal.hide_search()

    # ----- Event shorthands -----

    @overload
    def on_change(self) -> Stream: ...
    @overload
    def on_change(self, handler: Callable[[Event], Any]) -> Subscription: ...
    def on_change(self, handler: Callable[[Event], Any] | None = None) -> Stream | Subscription:
        """Register a callback fired on every edit.

        Returns:
            `Subscription` (with handler) or `Stream` (without handler).
        """
        return self.on("change", handler)

    @overload
    def on_input(self) -> Stream: ...
    @overload
    def on_input(self, handler: Callable[[Event], Any]) -> Subscription: ...
    def on_input(self, handler: Callable[[Event], Any] | None = None) -> Stream | Subscription:
        """Register a callback fired on every keystroke.

        Returns:
            `Subscription` (with handler) or `Stream` (without handler).
        """
        return self.on("input", handler)

    @overload
    def on_modified(self) -> Stream: ...
    @overload
    def on_modified(self, handler: Callable[[Event], Any]) -> Subscription: ...
    def on_modified(self, handler: Callable[[Event], Any] | None = None) -> Stream | Subscription:
        """Register a callback fired when `is_dirty` changes.

        Returns:
            `Subscription` (with handler) or `Stream` (without handler).
        """
        return self.on("modified", handler)

    @overload
    def on_undo(self) -> Stream: ...
    @overload
    def on_undo(self, handler: Callable[[Event], Any]) -> Subscription: ...
    def on_undo(self, handler: Callable[[Event], Any] | None = None) -> Stream | Subscription:
        """Register a callback fired after an undo operation.

        Returns:
            `Subscription` (with handler) or `Stream` (without handler).
        """
        return self.on("undo", handler)

    @overload
    def on_redo(self) -> Stream: ...
    @overload
    def on_redo(self, handler: Callable[[Event], Any]) -> Subscription: ...
    def on_redo(self, handler: Callable[[Event], Any] | None = None) -> Stream | Subscription:
        """Register a callback fired after a redo operation.

        Returns:
            `Subscription` (with handler) or `Stream` (without handler).
        """
        return self.on("redo", handler)

    @overload
    def on_cursor_move(self) -> Stream: ...
    @overload
    def on_cursor_move(self, handler: Callable[[Event], Any]) -> Subscription: ...
    def on_cursor_move(self, handler: Callable[[Event], Any] | None = None) -> Stream | Subscription:
        """Register a callback fired when the cursor position changes.

        Returns:
            `Subscription` (with handler) or `Stream` (without handler).
        """
        return self.on("cursor_move", handler)

    @overload
    def on_focus(self) -> Stream: ...
    @overload
    def on_focus(self, handler: Callable[[Event], Any]) -> Subscription: ...
    def on_focus(self, handler: Callable[[Event], Any] | None = None) -> Stream | Subscription:
        """Register a callback fired when the editor gains focus.

        Returns:
            `Subscription` (with handler) or `Stream` (without handler).
        """
        return self.on("focus", handler)

    @overload
    def on_blur(self) -> Stream: ...
    @overload
    def on_blur(self, handler: Callable[[Event], Any]) -> Subscription: ...
    def on_blur(self, handler: Callable[[Event], Any] | None = None) -> Stream | Subscription:
        """Register a callback fired when the editor loses focus.

        Returns:
            `Subscription` (with handler) or `Stream` (without handler).
        """
        return self.on("blur", handler)


register_widget_events(CodeEditor, _CODEEDITOR_EVENTS)
