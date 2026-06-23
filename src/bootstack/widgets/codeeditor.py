from __future__ import annotations

import tkinter
from contextlib import contextmanager
from typing import overload, Any, Callable, Iterator, Literal, TYPE_CHECKING

from bootstack.widgets._impl.composites.textarea.codeeditor import CodeEditor as _InternalCodeEditor
from bootstack.widgets._impl.composites.textarea.filter import EditFilter
from bootstack.widgets._core.base import PublicWidgetBase, adapt_handler
from bootstack.widgets._core.events import resolve_event, register_widget_events
from bootstack.events import ChangeEvent, InputEvent, Subscription, TextModifiedEvent, ValidationEvent
from bootstack.streams import Stream
from bootstack.validation import RuleType
from bootstack.widgets.types import AccentToken, Event

if TYPE_CHECKING:
    from bootstack.signals import Signal

_CODEEDITOR_EVENTS: dict[str, str] = {
    "change":      "<<BsChange>>",
    "input":       "<<BsInput>>",
    "valid":       "<<Valid>>",
    "invalid":     "<<Invalid>>",
    "validate":    "<<Validate>>",
    "modified":    "<<TextModified>>",
    "undo":        "<<TextUndo>>",
    "redo":        "<<TextRedo>>",
    "cursor_move": "<<CursorMove>>",
    "focus":       "<FocusIn>",
    "blur":        "<FocusOut>",
}

# Sequences emitted on the inner text widget (bound there by `on()`). The typed
# `<<BsChange>>`/`<<BsInput>>` are re-emitted on `self._internal`, so they are
# NOT listed here.
_INNER_SEQUENCES = frozenset({
    "<<TextModified>>", "<<TextUndo>>", "<<TextRedo>>",
    "<<CursorMove>>", "<FocusIn>", "<FocusOut>",
})


class CodeEditor(PublicWidgetBase):
    """A full-featured code editor with line numbers, bracket matching, and syntax highlighting.

    Not Field-wrapped — use `TextArea` for labeled form inputs.

    Args:
        value: Initial text content.
        textsignal: Reactive `Signal[str]` bound to the editor content.
        language: Pygments lexer name for syntax highlighting (e.g. `'python'`,
            `'json'`, `'sql'`). Any Pygments lexer name works; unknown names
            fall back to plain text. `None` disables highlighting. See the full
            list at https://pygments.org/languages/.
        theme: Pygments color scheme. `'auto'` (default) switches between
            `light_theme` and `dark_theme` when the bootstack theme changes.
            Pass an explicit Pygments style name (e.g. `'monokai'`, `'dracula'`)
            to pin the scheme. See the full list at https://pygments.org/styles/.
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
        scrollbars: Scrollbar visibility. Default `'both'`. Horizontal
            scrolling requires `wrap=False`.
        font: Semantic font token for the editor. Default `'code'` (the
            monospace token). See :doc:`/reference/typography`.
        show_border: If True (default), styles the editor frame as a themed
            border with a focus ring.
        accent: Accent token applied to the focus border. Default `'primary'`.
        extensions: Additional `EditFilter` instances to install on top of
            the built-in set.
        parent: Override the context-stack parent.
        **kwargs: Layout placement options applied by the parent container —
            `fill`, `expand`, `anchor`, `margin`, `row`, `column`, `sticky`.
            See :doc:`/tasks/layout`.
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
        scrollbars: Literal["both", "auto", "vertical", "none"] = "both",
        font: str = "code",
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
        t = self._internal.core.text
        t.bind("<KeyRelease>",      lambda e: t.event_generate("<<CursorMove>>"), add="+")
        t.bind("<ButtonRelease-1>", lambda e: t.event_generate("<<CursorMove>>"), add="+")

        # Re-emit the core's raw <<Change>> (which carries a low-level
        # {"op", "index"} dict) as typed payloads on the public widget, so
        # on_change()/on_input() deliver the editor text — like TextArea.
        def _emit_typed_change(_e: Any = None) -> None:
            text = self._internal.value
            self._internal.event_generate("<<BsChange>>", data=ChangeEvent(value=text, text=text))
            self._internal.event_generate("<<BsInput>>", data=InputEvent(text=text))
        t.bind("<<Change>>", _emit_typed_change, add="+")

        self._attach_to_parent(layout_kw)

    # ----- Event routing -----

    def _text_widget(self) -> tkinter.Misc:
        return self._internal.core.text

    @overload
    def on(self, event: str) -> Stream: ...
    @overload
    def on(self, event: str, handler: Callable[[Event], Any]) -> Subscription: ...
    def on(self, event: str, handler: Callable[[Event], Any] | None = None) -> Stream | Subscription:
        """Register a callback for an event by name.

        A generic, string-keyed escape hatch — prefer the typed `on_*`
        shorthands (e.g. `on_change`), which carry the precise payload type.
        Called with no handler, returns a composable `Stream`; with a handler,
        binds it and returns a `Subscription`.

        Args:
            event: Event name (for example `'change'` or `'focus'`).
            handler: Called with the event payload. Omit to get a composable
                :class:`~bootstack.streams.Stream` instead.

        Returns:
            A cancellable :class:`~bootstack.events.Subscription` when a handler
            is given, otherwise a :class:`~bootstack.streams.Stream`.
        """
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
    def text(self) -> str:
        """The current display text. Same as `value` for a code editor (no
        formatting layer). Read-only — assign to `value` to change it."""
        return self._internal.value

    @property
    def signal(self) -> "Signal[str] | None":
        """The reactive `Signal` bound to this editor, or `None`."""
        return getattr(self._internal.core, "signal", None)

    @property
    def valid(self) -> "Signal[bool]":
        """Reactive `Signal[bool]` — `True` when all validation rules pass.

        Starts `True`. Updates after every validation run (blur or manual
        `validate()` call). Subscribe a named handler to react immediately when
        validity changes (a `lambda` cannot assign, so define a function):
        `def on_valid(ok): btn.disabled = not ok` then
        `editor.valid.subscribe(on_valid)`.
        """
        return self._internal._valid_signal

    @property
    def error(self) -> "Signal[str]":
        """Reactive `Signal[str]` — current validation error message.

        Empty string when the editor is valid. Updates in lockstep with `valid`.
        """
        return self._internal._error_signal

    @property
    def is_dirty(self) -> bool:
        """True if content has changed since the last `mark_saved()` call."""
        return self._internal.is_dirty

    @property
    def cursor_position(self) -> tuple[int, int]:
        """The insertion cursor as a 1-indexed `(line, col)` tuple.

        `(1, 1)` is the start of the content — the same coordinates `insert()`
        and `goto()` accept. Read it in an `on_cursor_move` handler to drive a
        status-bar readout. Read-only — use `goto()` to move the cursor.
        """
        idx = self._internal.core.text.index("insert")
        line, col = idx.split(".")
        return int(line), int(col) + 1

    @property
    def selection(self) -> "tuple[tuple[int, int], tuple[int, int]] | None":
        """The current text selection as `((start_line, start_col), (end_line, end_col))`.

        Both lines and columns are 1-indexed — the same coordinates `cursor_position`
        reports and `goto()` / `insert()` accept. Returns `None` when no text is
        selected. Set to a pair of `(line, col)` tuples to select a range, or
        set to `None` to clear the selection.
        """
        tw = self._internal.core.text
        ranges = tw.tag_ranges("sel")
        if not ranges:
            return None
        sl, sc = str(ranges[0]).split(".")
        el, ec = str(ranges[1]).split(".")
        return (int(sl), int(sc) + 1), (int(el), int(ec) + 1)

    @selection.setter
    def selection(self, v: "tuple[tuple[int, int], tuple[int, int]] | None") -> None:
        tw = self._internal.core.text
        tw.tag_remove("sel", "1.0", "end")
        if v is not None:
            (sl, sc), (el, ec) = v
            tw.tag_add("sel", f"{sl}.{sc - 1}", f"{el}.{ec - 1}")

    @property
    def selected_text(self) -> str:
        """The currently selected text, or an empty string when nothing is selected."""
        sel = self.selection
        if sel is None:
            return ""
        (sl, sc), (el, ec) = sel
        return self._internal.core.text.get(f"{sl}.{sc - 1}", f"{el}.{ec - 1}")

    @property
    def language(self) -> str | None:
        """Active syntax highlighting language, or `None` if disabled."""
        return self._internal.language

    @language.setter
    def language(self, v: str | None) -> None:
        self._internal.set_language(v)

    @property
    def theme(self) -> str:
        """Active Pygments color scheme, or `'auto'` if tracking the bootstack theme."""
        return self._internal.theme

    @theme.setter
    def theme(self, v: str) -> None:
        self._internal.set_theme(v)

    @property
    def read_only(self) -> bool:
        """Whether the editor content is visible but not editable."""
        return self._internal.core.read_only

    @read_only.setter
    def read_only(self, v: bool) -> None:
        # Route through the core property so the `_read_only` flag and the Tk
        # widget state stay in lockstep (the value/insert setters consult the
        # flag to lift the disabled state for programmatic writes).
        self._internal.core.read_only = v

    # ----- Methods -----

    def validate(self) -> bool:
        """Run validation rules against the current content.

        Returns:
            `True` if all rules pass, `False` otherwise.
        """
        return self._internal.validate()

    def add_validation_rule(self, rule_type: RuleType, **kwargs: Any) -> None:
        """Attach a validation rule to this editor.

        Args:
            rule_type: The kind of validation rule to apply.
            **kwargs: Rule options such as `message=`, `min=`, `max=`,
                `trigger=`.
        """
        self._internal.add_validation_rule(rule_type, **kwargs)

    def clear(self) -> None:
        """Clear all text content."""
        self._internal.value = ""

    def insert(self, text: str, line: int | None = None, col: int | None = None) -> None:
        """Insert `text` at a position, defaulting to the cursor.

        With no `line`/`col`, inserts at the current cursor. Pass `line` to
        insert at the start of that line, or `line` and `col` together for an
        exact position. Both are 1-indexed — `(1, 1)` is the start of the
        content, the same coordinates `cursor_position` reports and `goto()`
        accepts.

        Read-only blocks *user* edits, not programmatic ones: this applies even
        when `read_only=True`, leaving the editor read-only afterward.

        Args:
            text: Text to insert.
            line: 1-indexed line, or `None` to use the cursor's line. Defaults
                to `None`.
            col: 1-indexed column, or `None` for the start of the line.
                Defaults to `None`.
        """
        if line is None:
            index = "insert"
        else:
            index = f"{line}.{(col or 1) - 1}"
        self._internal.core.insert(index, text)

    def append(self, text: str) -> None:
        """Append `text` to the end of the content.

        Applies even when `read_only=True`, leaving the editor read-only
        afterward.

        Args:
            text: Text to add at the end of the content.
        """
        self._internal.core.insert("end-1c", text)

    def select_all(self) -> None:
        """Select all text content."""
        tw = self._internal.core.text
        tw.focus_set()
        tw.tag_add("sel", "1.0", "end-1c")
        tw.mark_set("insert", "end-1c")

    def focus(self) -> None:
        """Move keyboard focus to the editor."""
        self._internal.focus_set()

    def goto(self, line: int, col: int = 1) -> None:
        """Move the cursor to a position and scroll it into view.

        Both are 1-indexed — `(1, 1)` is the start of the content, the same
        coordinates `cursor_position` reports and `insert()` accepts. Omit
        `col` to land at the start of the line.

        Args:
            line: 1-indexed line number.
            col: 1-indexed column, or omit for the start of the line. Defaults
                to 1.
        """
        self._internal.focus_set()
        self._internal.goto(line, col)

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
                editor.insert("# header\\n", 1, 1)
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

    def indent(self) -> None:
        """Indent selected lines by one tab stop, or insert a tab stop at the cursor.

        With a selection, every selected line is indented by one tab stop (spaces
        or a tab character, depending on the editor's `insert_spaces` setting).
        The affected lines stay selected afterward (a partial-line selection is
        re-selected to span the whole lines).

        Without a selection, inserts spaces to the next tab stop at the cursor
        (same as pressing Tab with no selection).
        """
        self._internal.indent()

    def dedent(self) -> None:
        """Dedent selected lines (or the current line) by one tab stop.

        Removes up to one tab stop of leading whitespace from each line in the
        selection. With no selection, dedents the line the cursor is on. The
        affected lines stay selected afterward (a partial-line selection is
        re-selected to span the whole lines).
        """
        self._internal.dedent()

    # ----- Event shorthands -----

    @overload
    def on_change(self) -> Stream: ...
    @overload
    def on_change(self, handler: Callable[[ChangeEvent], Any]) -> Subscription: ...
    def on_change(self, handler: Callable[[ChangeEvent], Any] | None = None) -> Stream | Subscription:
        """Register a callback fired on every edit.

        Args:
            handler: Called with a :class:`~bootstack.events.ChangeEvent` whose
                `value` is the editor text. Omit to get a composable
                :class:`~bootstack.streams.Stream`.

        Returns:
            A cancellable :class:`~bootstack.events.Subscription` when a handler
            is given, otherwise a :class:`~bootstack.streams.Stream`.
        """
        return self.on("change", handler)

    @overload
    def on_input(self) -> Stream: ...
    @overload
    def on_input(self, handler: Callable[[InputEvent], Any]) -> Subscription: ...
    def on_input(self, handler: Callable[[InputEvent], Any] | None = None) -> Stream | Subscription:
        """Register a callback fired on every edit, before commit.

        Args:
            handler: Called with an :class:`~bootstack.events.InputEvent` whose
                `text` is the current content. Omit to get a composable
                :class:`~bootstack.streams.Stream`.

        Returns:
            A cancellable :class:`~bootstack.events.Subscription` when a handler
            is given, otherwise a :class:`~bootstack.streams.Stream`.
        """
        return self.on("input", handler)

    @overload
    def on_valid(self) -> Stream: ...
    @overload
    def on_valid(self, handler: Callable[[ValidationEvent], Any]) -> Subscription: ...
    def on_valid(self, handler: Callable[[ValidationEvent], Any] | None = None) -> Stream | Subscription:
        """Register a callback fired when validation passes.

        Args:
            handler: Called with a :class:`~bootstack.events.ValidationEvent`. Omit to
                get a composable :class:`~bootstack.streams.Stream` instead.

        Returns:
            A cancellable :class:`~bootstack.events.Subscription` when a
            handler is given, otherwise a :class:`~bootstack.streams.Stream`.
        """
        return self.on("valid", handler)

    @overload
    def on_invalid(self) -> Stream: ...
    @overload
    def on_invalid(self, handler: Callable[[ValidationEvent], Any]) -> Subscription: ...
    def on_invalid(self, handler: Callable[[ValidationEvent], Any] | None = None) -> Stream | Subscription:
        """Register a callback fired when validation fails.

        Args:
            handler: Called with a :class:`~bootstack.events.ValidationEvent`. Omit to
                get a composable :class:`~bootstack.streams.Stream` instead.

        Returns:
            A cancellable :class:`~bootstack.events.Subscription` when a
            handler is given, otherwise a :class:`~bootstack.streams.Stream`.
        """
        return self.on("invalid", handler)

    @overload
    def on_validate(self) -> Stream: ...
    @overload
    def on_validate(self, handler: Callable[[ValidationEvent], Any]) -> Subscription: ...
    def on_validate(self, handler: Callable[[ValidationEvent], Any] | None = None) -> Stream | Subscription:
        """Register a callback fired after any validation run.

        Args:
            handler: Called with a :class:`~bootstack.events.ValidationEvent`. Omit to
                get a composable :class:`~bootstack.streams.Stream` instead.

        Returns:
            A cancellable :class:`~bootstack.events.Subscription` when a
            handler is given, otherwise a :class:`~bootstack.streams.Stream`.
        """
        return self.on("validate", handler)

    @overload
    def on_modified(self) -> Stream: ...
    @overload
    def on_modified(self, handler: Callable[[TextModifiedEvent], Any]) -> Subscription: ...
    def on_modified(self, handler: Callable[[TextModifiedEvent], Any] | None = None) -> Stream | Subscription:
        """Register a callback fired when `is_dirty` changes.

        Args:
            handler: Called with a :class:`~bootstack.events.TextModifiedEvent`. Omit to
                get a composable :class:`~bootstack.streams.Stream` instead.

        Returns:
            A cancellable :class:`~bootstack.events.Subscription` when a
            handler is given, otherwise a :class:`~bootstack.streams.Stream`.
        """
        return self.on("modified", handler)

    @overload
    def on_undo(self) -> Stream: ...
    @overload
    def on_undo(self, handler: Callable[[InputEvent], Any]) -> Subscription: ...
    def on_undo(self, handler: Callable[[InputEvent], Any] | None = None) -> Stream | Subscription:
        """Register a callback fired after an undo operation.

        Args:
            handler: Called with an :class:`~bootstack.events.InputEvent`. Omit to
                get a composable :class:`~bootstack.streams.Stream` instead.

        Returns:
            A cancellable :class:`~bootstack.events.Subscription` when a
            handler is given, otherwise a :class:`~bootstack.streams.Stream`.
        """
        return self.on("undo", handler)

    @overload
    def on_redo(self) -> Stream: ...
    @overload
    def on_redo(self, handler: Callable[[InputEvent], Any]) -> Subscription: ...
    def on_redo(self, handler: Callable[[InputEvent], Any] | None = None) -> Stream | Subscription:
        """Register a callback fired after a redo operation.

        Args:
            handler: Called with an :class:`~bootstack.events.InputEvent`. Omit to
                get a composable :class:`~bootstack.streams.Stream` instead.

        Returns:
            A cancellable :class:`~bootstack.events.Subscription` when a
            handler is given, otherwise a :class:`~bootstack.streams.Stream`.
        """
        return self.on("redo", handler)

    @overload
    def on_cursor_move(self) -> Stream: ...
    @overload
    def on_cursor_move(self, handler: Callable[[Event], Any]) -> Subscription: ...
    def on_cursor_move(self, handler: Callable[[Event], Any] | None = None) -> Stream | Subscription:
        """Register a callback fired when the cursor position changes.

        Args:
            handler: Called with an :class:`~bootstack.events.Event`. Omit to
                get a composable :class:`~bootstack.streams.Stream` instead.

        Returns:
            A cancellable :class:`~bootstack.events.Subscription` when a
            handler is given, otherwise a :class:`~bootstack.streams.Stream`.
        """
        return self.on("cursor_move", handler)

    @overload
    def on_focus(self) -> Stream: ...
    @overload
    def on_focus(self, handler: Callable[[Event], Any]) -> Subscription: ...
    def on_focus(self, handler: Callable[[Event], Any] | None = None) -> Stream | Subscription:
        """Register a callback fired when the editor gains focus.

        Args:
            handler: Called with an :class:`~bootstack.events.Event`. Omit to
                get a composable :class:`~bootstack.streams.Stream` instead.

        Returns:
            A cancellable :class:`~bootstack.events.Subscription` when a
            handler is given, otherwise a :class:`~bootstack.streams.Stream`.
        """
        return self.on("focus", handler)

    @overload
    def on_blur(self) -> Stream: ...
    @overload
    def on_blur(self, handler: Callable[[Event], Any]) -> Subscription: ...
    def on_blur(self, handler: Callable[[Event], Any] | None = None) -> Stream | Subscription:
        """Register a callback fired when the editor loses focus.

        Args:
            handler: Called with an :class:`~bootstack.events.Event`. Omit to
                get a composable :class:`~bootstack.streams.Stream` instead.

        Returns:
            A cancellable :class:`~bootstack.events.Subscription` when a
            handler is given, otherwise a :class:`~bootstack.streams.Stream`.
        """
        return self.on("blur", handler)


register_widget_events(CodeEditor, _CODEEDITOR_EVENTS)
