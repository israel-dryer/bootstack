"""TextArea — labeled multi-line text input."""
from __future__ import annotations

import tkinter as tk
from typing import Callable, Literal

from bootstack.widgets.primitives.frame import Frame
from bootstack.widgets.primitives.label import Label
from bootstack.widgets.composites.textarea.core import _MultilineCore, ScrollbarMode
from bootstack.widgets.types import Master

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from bootstack.signals import Signal


class TextArea(Frame):
    """A labeled, scrollable multi-line text input.

    TextArea is the multi-line counterpart to ``TextEntry``. It wraps a
    ``tk.Text`` widget with label/message chrome, scrollbars, undo/redo, and
    reactive signal binding.

    Use this for form comment boxes, note fields, and any other multi-line
    prose input. For code editing, see ``CodeEditor``.

    Replaces ``bs.ScrolledText``.
    """

    def __init__(
        self,
        master: Master = None,
        *,
        value: str = "",
        textsignal: Signal | None = None,
        label: str | None = None,
        placeholder: str | None = None,
        max_length: int | None = None,
        read_only: bool = False,
        wrap: bool = True,
        height: int = 4,
        scrollbars: ScrollbarMode = "auto",
        font: str = "body",
        on_change: Callable | None = None,
        on_input: Callable | None = None,
        on_blur: Callable | None = None,
    ) -> None:
        """Create a TextArea widget.

        Args:
            master: Parent widget. If None, uses the default root window.
            value: Initial text content.
            textsignal: Reactive ``Signal[str]`` — the TextArea displays and
                tracks the signal's value.
            label: Optional label displayed above the text area.
            placeholder: Placeholder text shown when the widget is empty.
                Removed on first focus.
            max_length: If set, inserts beyond this character count are blocked.
            read_only: If True, the text is not editable.
            wrap: If True, text wraps at the widget boundary (word wrap).
                If False, horizontal scrolling is enabled.
            height: Visible row count. Default is 4.
            scrollbars: Scrollbar visibility — ``"auto"`` (shown when needed),
                ``"vertical"`` (always), ``"both"`` (always, both axes),
                or ``"none"``.
            font: Font token. Defaults to ``"body"``.
            on_change: Callback invoked after each edit (``<<Change>>`` event).
            on_input: Alias for ``on_change`` — provided for API consistency
                with other input widgets.
            on_blur: Callback invoked when the widget loses focus.
        """
        super().__init__(master)

        self._label_text = label
        self._placeholder = placeholder
        self._max_length = max_length
        self._showing_placeholder = False

        # ── label ─────────────────────────────────────────────────────────
        if label:
            self._label_widget = Label(self, text=label, font="caption")
            self._label_widget.pack(anchor="w", pady=(0, 2))
        else:
            self._label_widget = None

        # ── core ──────────────────────────────────────────────────────────
        self._core = _MultilineCore(
            self,
            value=value,
            wrap=wrap,
            height=height,
            scrollbars=scrollbars,
            font=font,
            read_only=read_only,
        )
        self._core.pack(fill="both", expand=True)

        # ── signal binding ────────────────────────────────────────────────
        if textsignal is not None:
            self._core.bind_signal(textsignal)

        # ── placeholder ───────────────────────────────────────────────────
        self._default_fg = self._core.text.cget("foreground")
        if placeholder and not value and textsignal is None:
            self._show_placeholder()
            self._core.text.bind("<FocusIn>", self._on_focus_in, add="+")
            self._core.text.bind("<FocusOut>", self._on_focus_out, add="+")

        # ── max_length filter ─────────────────────────────────────────────
        if max_length is not None:
            from bootstack.widgets.composites.textarea.filter import EditFilter

            max_len = max_length

            class _MaxLenFilter(EditFilter):
                def insert(self, index, chars, tags=None):
                    current = len(self.get("1.0", "end-1c"))
                    allowed = max(0, max_len - current)
                    if allowed > 0:
                        self.delegate.insert(index, chars[:allowed], tags)

            self._core.add_filter(_MaxLenFilter())

        # ── callbacks ─────────────────────────────────────────────────────
        if on_change is not None:
            self._core.on_change(on_change)
        if on_input is not None:
            self._core.on_change(on_input)
        if on_blur is not None:
            self._core.text.bind("<FocusOut>", on_blur, add="+")

    # ── placeholder ───────────────────────────────────────────────────────

    def _show_placeholder(self) -> None:
        self._showing_placeholder = True
        self._core.text.configure(state=tk.NORMAL)
        self._core.text.insert("1.0", self._placeholder)
        self._core.text.configure(foreground="grey")

    def _hide_placeholder(self) -> None:
        self._showing_placeholder = False
        self._core.text.delete("1.0", tk.END)
        self._core.text.configure(foreground=self._default_fg)

    def _on_focus_in(self, _event: tk.Event) -> None:
        if self._showing_placeholder:
            self._hide_placeholder()

    def _on_focus_out(self, _event: tk.Event) -> None:
        if not self._core.value:
            self._show_placeholder()

    # ── public API ────────────────────────────────────────────────────────

    @property
    def value(self) -> str:
        """Full text content (trailing newline stripped)."""
        if self._showing_placeholder:
            return ""
        return self._core.value

    @value.setter
    def value(self, text: str) -> None:
        if self._showing_placeholder:
            self._hide_placeholder()
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

    def focus_set(self) -> None:
        """Set focus to the text area."""
        self._core.focus_set()

    def on_change(self, callback: Callable) -> str:
        """Register a callback for ``<<Change>>`` events.

        Args:
            callback: Receives the Tk event. ``event.data`` has
                ``{"op": "insert"|"delete", "index": str}``.

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
        """Register a callback for ``<<Modified>>`` events (dirty state changed).

        Args:
            callback: Called when the dirty state changes. Check
                ``self.is_dirty`` for the new state.

        Returns:
            Bind ID — pass to ``off_modified()`` to unsubscribe.
        """
        return self._core.on_modified(callback)

    def off_modified(self, bind_id: str | None = None) -> None:
        """Unsubscribe from ``<<Modified>>``.

        Args:
            bind_id: ID returned by ``on_modified()``. If None, removes all.
        """
        self._core.off_modified(bind_id)

    def on_undo(self, callback: Callable) -> str:
        """Register a callback for ``<<Undo>>`` events.

        Args:
            callback: Called when an undo operation completes.

        Returns:
            Bind ID — pass to ``off_undo()`` to unsubscribe.
        """
        return self._core.on_undo(callback)

    def off_undo(self, bind_id: str | None = None) -> None:
        """Unsubscribe from ``<<Undo>>``.

        Args:
            bind_id: ID returned by ``on_undo()``. If None, removes all.
        """
        self._core.off_undo(bind_id)

    def on_redo(self, callback: Callable) -> str:
        """Register a callback for ``<<Redo>>`` events.

        Args:
            callback: Called when a redo operation completes.

        Returns:
            Bind ID — pass to ``off_redo()`` to unsubscribe.
        """
        return self._core.on_redo(callback)

    def off_redo(self, bind_id: str | None = None) -> None:
        """Unsubscribe from ``<<Redo>>``.

        Args:
            bind_id: ID returned by ``on_redo()``. If None, removes all.
        """
        self._core.off_redo(bind_id)

    def on_blur(self, callback: Callable) -> str:
        """Register a callback for focus-out events.

        Args:
            callback: Called when the text area loses focus.

        Returns:
            Bind ID — pass to ``off_blur()`` to unsubscribe.
        """
        return self._core.text.bind("<FocusOut>", callback, add="+")

    def off_blur(self, bind_id: str | None = None) -> None:
        """Unsubscribe from focus-out events.

        Args:
            bind_id: ID returned by ``on_blur()``. If None, removes all.
        """
        self._core.text.unbind("<FocusOut>", bind_id)

    @property
    def core(self) -> _MultilineCore:
        """The internal ``_MultilineCore`` — for advanced filter/decoration use."""
        return self._core
