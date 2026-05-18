"""_MultilineCore — shared internal engine for TextArea and CodeEditor.

Owns the tk.Text widget, filter chain, scrollbar wiring, and the
sidebar/decoration registries used by CodeEditor extensions.
"""
from __future__ import annotations

import tkinter as tk
from typing import Callable, Literal

from bootstack.widgets.primitives.scrollbar import Scrollbar
from bootstack.widgets.composites.textarea.filter import EditFilter, FilterChain
from bootstack.widgets.composites.textarea.change import ChangeNotifier
from bootstack.widgets.composites.textarea.undo import UndoManager
from bootstack.widgets.composites.textarea.style_registry import StyleRegistry
from bootstack.widgets.composites.textarea.diff import DecorationDiff
from bootstack.widgets.composites.textarea.decoration import (
    LineDecoration, Position, RangeDecoration,
)
from bootstack.widgets.types import Master


ScrollbarMode = Literal["vertical", "both", "none", "auto"]


class _MultilineCore(tk.Frame):
    """Internal engine shared by TextArea and CodeEditor.

    Not part of the public API. Use TextArea or CodeEditor instead.

    Wraps a tk.Text widget with:
    - A FilterChain routing all inserts/deletes through registered filters.
    - Built-in ChangeNotifier (fires <<Change>>) and UndoManager.
    - Scrollbar wiring with auto/always/none/both modes.
    - value/textsignal reactive binding.
    """

    def __init__(
        self,
        master: Master = None,
        value: str = "",
        wrap: bool = True,
        height: int = 4,
        scrollbars: ScrollbarMode = "auto",
        font: str = "body",
        read_only: bool = False,
        **text_kwargs,
    ) -> None:
        super().__init__(master)

        self._scrollbar_mode = scrollbars
        self._read_only = read_only
        self._signal = None
        self._signal_trace_id = None

        # Detect windowing system for mousewheel handling
        self.winsys: str = self.tk.call("tk", "windowingsystem")

        # ── text widget ───────────────────────────────────────────────────
        # undo=False: we manage the undo stack ourselves via UndoManager
        # (character-class grouping for word-level undo, matching IDLE).
        wrap_mode = tk.WORD if wrap else tk.NONE
        self.text = tk.Text(
            self,
            wrap=wrap_mode,
            height=height,
            font=font,
            undo=False,
            **text_kwargs,
        )

        # ── scrollbars ────────────────────────────────────────────────────
        self._vscroll = Scrollbar(self, orient="vertical", command=self.text.yview)
        self._hscroll = Scrollbar(self, orient="horizontal", command=self.text.xview)

        self.text.configure(yscrollcommand=self._on_yscroll)
        if not wrap:
            self.text.configure(xscrollcommand=self._on_xscroll)

        # ── layout ────────────────────────────────────────────────────────
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)
        self.text.grid(row=0, column=0, sticky="nsew")

        self._update_scrollbar_layout()

        # ── filter chain ──────────────────────────────────────────────────
        self._chain = FilterChain(self.text)

        self._undo_manager = UndoManager()
        self._change_notifier = ChangeNotifier()

        self._install_filter(self._undo_manager)
        self._install_filter(self._change_notifier)

        # ── style registry + decoration diff ─────────────────────────────
        self._style_registry = StyleRegistry(self)
        self._decoration_diff = DecorationDiff(self, self._style_registry)

        # ── mousewheel ────────────────────────────────────────────────────
        self._scroll_tag = f"_mcore_{id(self)}"
        self._setup_mousewheel()

        # ── initial value ─────────────────────────────────────────────────
        if value:
            self.text.insert("1.0", value)
            self._undo_manager.reset_undo()   # clear history after seeding

        if read_only:
            self.text.configure(state=tk.DISABLED)

        # Keyboard undo/redo (Ctrl+Z / Ctrl+Shift+Z)
        self.text.bind("<Control-z>", lambda e: (self._undo_manager.undo(), "break")[1], add="+")
        self.text.bind("<Control-Z>", lambda e: (self._undo_manager.redo(), "break")[1], add="+")

        # <<Modified>> still fires from Tk's edit_modified flag (independent
        # of the undo stack) — enrich with is_dirty payload.
        self.text.bind("<<Modified>>", self._on_tk_modified, add="+")

        self.bind("<Destroy>", self._on_destroy, add="+")

    # ── filter management ─────────────────────────────────────────────────

    def _install_filter(self, f: EditFilter) -> None:
        self._chain.add(f)
        f.attach(self)

    def add_filter(self, f: EditFilter) -> None:
        """Install a custom filter at the top of the chain."""
        self._install_filter(f)

    def remove_filter(self, f: EditFilter) -> None:
        """Remove a custom filter from the chain."""
        f.detach(self)
        self._chain.remove(f)

    # ── scrollbars ────────────────────────────────────────────────────────

    def _on_yscroll(self, first: str, last: str) -> None:
        self._vscroll.set(first, last)
        if self._scrollbar_mode == "auto":
            if float(first) <= 0.0 and float(last) >= 1.0:
                self._vscroll.grid_remove()
            else:
                self._vscroll.grid(row=0, column=1, sticky="ns")

    def _on_xscroll(self, first: str, last: str) -> None:
        self._hscroll.set(first, last)
        if self._scrollbar_mode == "auto":
            if float(first) <= 0.0 and float(last) >= 1.0:
                self._hscroll.grid_remove()
            else:
                self._hscroll.grid(row=1, column=0, sticky="ew")

    def _update_scrollbar_layout(self) -> None:
        mode = self._scrollbar_mode
        if mode in ("vertical", "both", "auto"):
            self._vscroll.grid(row=0, column=1, sticky="ns")
        else:
            self._vscroll.grid_remove()

        if mode == "both":
            self._hscroll.grid(row=1, column=0, sticky="ew")
        else:
            self._hscroll.grid_remove()

        if mode == "auto":
            # Start hidden; _on_yscroll will show when needed
            self._vscroll.grid_remove()
            self._hscroll.grid_remove()

    # ── mousewheel ────────────────────────────────────────────────────────

    def _setup_mousewheel(self) -> None:
        if self.winsys == "x11":
            self.bind_class(self._scroll_tag, "<Button-4>", self._on_wheel)
            self.bind_class(self._scroll_tag, "<Button-5>", self._on_wheel)
        else:
            self.bind_class(self._scroll_tag, "<MouseWheel>", self._on_wheel)
        tags = list(self.text.bindtags())
        if self._scroll_tag not in tags:
            tags.insert(1, self._scroll_tag)
            self.text.bindtags(tuple(tags))

    def _on_wheel(self, event: tk.Event) -> None:
        if self.winsys == "win32":
            delta = -int(event.delta / 120)
        elif self.winsys == "aqua":
            delta = -event.delta
        elif event.num == 4:
            delta = -1
        else:
            delta = 1
        self.text.yview_scroll(delta, "units")

    # ── value / signal ────────────────────────────────────────────────────

    @property
    def value(self) -> str:
        """Full text content (trailing newline stripped)."""
        return self.text.get("1.0", "end-1c")

    @value.setter
    def value(self, text: str) -> None:
        was_disabled = self._read_only
        if was_disabled:
            self.text.configure(state=tk.NORMAL)
        self.text.delete("1.0", tk.END)
        if text:
            self.text.insert("1.0", text)
        if was_disabled:
            self.text.configure(state=tk.DISABLED)

    def bind_signal(self, signal) -> None:
        """Bind a Signal[str] — updates the text when the signal changes."""
        if self._signal is not None:
            self._unbind_signal()
        self._signal = signal
        self._signal_trace_id = signal.subscribe(self._on_signal_change)
        # Set initial value from signal
        v = signal.get()
        if v is not None:
            self.value = str(v)

    def _unbind_signal(self) -> None:
        if self._signal is not None and self._signal_trace_id is not None:
            try:
                self._signal.unsubscribe(self._signal_trace_id)
            except Exception:
                pass
        self._signal = None
        self._signal_trace_id = None

    def _on_signal_change(self, new_value) -> None:
        if new_value is not None:
            self.value = str(new_value)

    # ── dirty tracking ────────────────────────────────────────────────────

    @property
    def is_dirty(self) -> bool:
        """True if the content has changed since last save."""
        return self._undo_manager.is_dirty

    def mark_saved(self) -> None:
        """Mark current state as the clean baseline."""
        self._undo_manager.mark_saved()

    # ── undo / redo ───────────────────────────────────────────────────────

    def undo(self) -> None:
        """Undo the last edit."""
        self._undo_manager.undo()

    def redo(self) -> None:
        """Redo the last undone edit."""
        self._undo_manager.redo()

    def undo_block_start(self) -> None:
        """Begin a compound undo block."""
        self._undo_manager.undo_block_start()

    def undo_block_stop(self) -> None:
        """End a compound undo block."""
        self._undo_manager.undo_block_stop()

    # ── decoration / style API ────────────────────────────────────────────

    def register_layer(self, name: str, priority: int = 0) -> None:
        """Register a decoration layer.

        Args:
            name: Layer identifier. Used to namespace Tk tags.
            priority: Tag raise order — higher priority layers render on top.
        """
        self._decoration_diff.register_layer(name, priority)

    def define_style(self, name: str, **attrs) -> None:
        """Define a named text style for use in decorations.

        Args:
            name: Style identifier referenced in decoration objects.
            **attrs: Style attributes — ``foreground``, ``background``,
                ``font``, ``underline``, ``spacing1``, ``spacing3``.
                Values may be theme tokens (e.g. ``'primary'``) or literal
                Tk color/font strings.
        """
        self._style_registry.define_style(name, **attrs)

    def set_decorations(self, layer: str, decorations) -> None:
        """Apply a decoration set to *layer*, diffing against the previous set.

        Args:
            layer: The decoration layer to update.
            decorations: Sequence of ``RangeDecoration`` or ``LineDecoration``.
        """
        self._decoration_diff.set_decorations(layer, decorations)

    def clear_decorations(self, layer: str) -> None:
        """Remove all decorations from *layer*.

        Args:
            layer: The layer to clear.
        """
        self._decoration_diff.clear_layer(layer)

    # ── internal Tk event enrichment ─────────────────────────────────────

    def _on_tk_modified(self, _event=None) -> None:
        self.text.event_generate(
            "<<TextModified>>",
            data={"is_dirty": self.is_dirty},
            when="tail",
        )

    # ── event subscription ────────────────────────────────────────────────

    def on_change(self, callback: Callable) -> str:
        """Register a callback for ``<<Change>>`` events.

        Args:
            callback: Receives the Tk event. ``event.data`` contains
                ``{"op": "insert"|"delete", "index": str}``.

        Returns:
            Bind ID — pass to ``off_change()`` to unsubscribe.
        """
        return self.text.bind("<<Change>>", callback, add="+")

    def off_change(self, bind_id: str | None = None) -> None:
        """Unsubscribe from ``<<Change>>``.

        Args:
            bind_id: ID returned by ``on_change()``. If None, removes all.
        """
        self.text.unbind("<<Change>>", bind_id)

    def on_modified(self, callback: Callable) -> str:
        """Register a callback for ``<<TextModified>>`` events.

        Fires when the dirty state changes. ``event.data["is_dirty"]``
        reflects the new state.

        Args:
            callback: Receives the Tk event with ``event.data = {"is_dirty": bool}``.

        Returns:
            Bind ID — pass to ``off_modified()`` to unsubscribe.
        """
        return self.text.bind("<<TextModified>>", callback, add="+")

    def off_modified(self, bind_id: str | None = None) -> None:
        """Unsubscribe from ``<<TextModified>>``.

        Args:
            bind_id: ID returned by ``on_modified()``. If None, removes all.
        """
        self.text.unbind("<<TextModified>>", bind_id)

    def on_undo(self, callback: Callable) -> str:
        """Register a callback for ``<<TextUndo>>`` events.

        Fires after an undo completes. ``event.data["value"]`` is the
        text content after the undo.

        Args:
            callback: Receives the Tk event with ``event.data = {"value": str}``.

        Returns:
            Bind ID — pass to ``off_undo()`` to unsubscribe.
        """
        return self.text.bind("<<TextUndo>>", callback, add="+")

    def off_undo(self, bind_id: str | None = None) -> None:
        """Unsubscribe from ``<<TextUndo>>``.

        Args:
            bind_id: ID returned by ``on_undo()``. If None, removes all.
        """
        self.text.unbind("<<TextUndo>>", bind_id)

    def on_redo(self, callback: Callable) -> str:
        """Register a callback for ``<<TextRedo>>`` events.

        Fires after a redo completes. ``event.data["value"]`` is the
        text content after the redo.

        Args:
            callback: Receives the Tk event with ``event.data = {"value": str}``.

        Returns:
            Bind ID — pass to ``off_redo()`` to unsubscribe.
        """
        return self.text.bind("<<TextRedo>>", callback, add="+")

    def off_redo(self, bind_id: str | None = None) -> None:
        """Unsubscribe from ``<<TextRedo>>``.

        Args:
            bind_id: ID returned by ``on_redo()``. If None, removes all.
        """
        self.text.unbind("<<TextRedo>>", bind_id)

    # ── convenience: forward common Text API to self ──────────────────────

    def bind(self, sequence=None, func=None, add=None):
        return self.text.bind(sequence, func, add)

    def unbind(self, sequence, funcid=None):
        return self.text.unbind(sequence, funcid)

    def focus_set(self):
        self.text.focus_set()

    # ── cleanup ───────────────────────────────────────────────────────────

    def _on_destroy(self, event: tk.Event) -> None:
        if event.widget is not self:
            return
        self._unbind_signal()
        self._chain.destroy()
        try:
            if self.winsys == "x11":
                self.unbind_class(self._scroll_tag, "<Button-4>")
                self.unbind_class(self._scroll_tag, "<Button-5>")
            else:
                self.unbind_class(self._scroll_tag, "<MouseWheel>")
        except Exception:
            pass
