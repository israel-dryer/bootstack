"""TextArea — labeled multi-line text input with validation support."""
from __future__ import annotations

import tkinter as tk
from typing import Callable

from bootstack.events import ChangeEvent, InputEvent, ValidationEvent
from bootstack.widgets._impl.primitives.frame import Frame
from bootstack.widgets._impl.primitives.gridframe import GridFrame
from bootstack.widgets._impl.primitives.label import Label
from bootstack.widgets._impl.composites.textarea.core import _MultilineCore, ScrollbarMode
from bootstack.widgets.types import Master, AccentToken
from bootstack._runtime.utility import scale_padding_floor

from bootstack.signals import Signal

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from bootstack.validation.validation_rules import ValidationRule


class TextArea(GridFrame):
    """A labeled, scrollable multi-line text input with validation support.

    `TextArea` is the multi-line counterpart to `TextEntry`. It provides the
    same field chrome (label, message, focus border, validation) while wrapping
    a multi-line `tk.Text` widget with undo/redo, scrollbars, and reactive
    signal binding.

    Use this for comment boxes, note fields, and any other multi-line prose
    input in a form context. For code editing see `CodeEditor`.

    Replaces `bs.ScrolledText`.
    """

    def __init__(
        self,
        master: Master = None,
        *,
        value: str = "",
        textsignal: Signal | None = None,
        label: str | None = None,
        message: str | None = None,
        show_message: bool = False,
        required: bool = False,
        placeholder: str | None = None,
        max_length: int | None = None,
        read_only: bool = False,
        wrap: bool = True,
        height: int = 4,
        width: int | None = None,
        scrollbars: ScrollbarMode = "auto",
        font: str = "body",
        accent: AccentToken | str = "primary",
        show_border: bool = True,
        on_input: Callable | None = None,
        on_changed: Callable | None = None,
        on_blur: Callable | None = None,
        on_valid: Callable | None = None,
        on_invalid: Callable | None = None,
        on_validated: Callable | None = None,
    ) -> None:
        """Create a TextArea widget.

        Args:
            master: Parent widget. If None, uses the default root window.
            value: Initial text content.
            textsignal: Reactive `Signal[str]` — the TextArea displays and
                tracks the signal's value.
            label: Optional label displayed above the text area.
            message: Optional hint text shown below the text area. Replaced
                by validation error messages when validation fails.
            show_message: If True, the message area is always visible. Auto-
                enabled when `message=` or `required=True` is set.
            required: If True, marks the field as required and adds a
                validation rule that rejects empty input.
            placeholder: Placeholder text shown when the widget is empty.
                Cleared on first focus.
            max_length: If set, inserts beyond this character count are blocked.
            read_only: If True, the text is not editable.
            wrap: If True (default), long lines wrap at the widget boundary.
                If False, horizontal scrolling is used.
            height: Visible row count. Default is 4.
            scrollbars: Scrollbar visibility mode — `"auto"` (shown when
                needed), `"vertical"`, `"both"`, or `"none"`.
            font: Font token. Defaults to `"body"`.
            accent: Accent token for the focus border. Defaults to `"primary"`.
            show_border: If True (default), wraps the text area in a themed
                border that gains a focus ring on interaction.
            on_input: Callback invoked on every edit. Receives `event.data`
                of type `InputEvent`.
            on_changed: Callback invoked when the widget loses focus. Receives
                `event.data` of type `InputEvent`.
            on_blur: Callback invoked when the widget loses focus (alias for
                `on_changed` — use either, not both).
            on_valid: Callback invoked after successful validation. Receives
                `event.data` of type `ValidationEvent`.
            on_invalid: Callback invoked after failed validation. Receives
                `event.data` of type `ValidationEvent`.
            on_validated: Callback invoked after any validation, pass or fail.
                Receives `event.data` of type `ValidationEvent`.
        """
        # GridFrame rows: auto (label) | 1 (field, expands) | auto (message)
        super().__init__(master, rows=["auto", 1, "auto"], columns=[1],
                         auto_flow="none", gap=(0, 2))

        self._accent = accent
        self._placeholder_text = placeholder
        self._max_length = max_length
        self._showing_placeholder = False
        self._original_message = message or ""
        self._rules: list[ValidationRule] = []
        self._message_showing = False
        self._valid_signal: Signal = Signal(True)
        self._error_signal: Signal = Signal("")

        # ── label (row 0) ─────────────────────────────────────────────────
        if label:
            _lbl_text = f"{label} *" if required else label
            Label(self, text=_lbl_text, font="caption").grid(
                row=0, column=0, sticky="w", padx=(4, 0),
            )

        # ── core (row 1) ──────────────────────────────────────────────────
        if show_border:
            # Padding must grow with the DPI-scaled TField border slice, else the
            # text core overpaints the border at high DPI (#90, same as Field).
            self._field_frame = Frame(
                self, accent=accent, padding=scale_padding_floor(5), ttk_class="TField",
            )
            self._field_frame.grid(row=1, column=0, sticky="nsew")
            core_parent = self._field_frame
        else:
            self._field_frame = None
            core_parent = self

        core_kwargs: dict = {}
        if width is not None:
            core_kwargs["width"] = width
        self._core = _MultilineCore(
            core_parent,
            value=value,
            wrap=wrap,
            height=height,
            scrollbars=scrollbars,
            font=font,
            read_only=read_only,
            **core_kwargs,
        )

        if show_border:
            self._core.pack(fill="both", expand=True)
            self._core.text.bind(
                "<FocusIn>",
                lambda _: self._field_frame.state(["focus"]),
                add="+",
            )
            self._core.text.bind(
                "<FocusOut>",
                lambda _: self._field_frame.state(["!focus"]),
                add="+",
            )
        else:
            self._core.grid(row=1, column=0, sticky="nsew")

        # ── Tab moves focus (not a keyboard trap) ─────────────────────────
        # A multi-line tk.Text inserts a literal tab on <Tab> and keeps focus,
        # which traps keyboard users in a form field. Rebind Tab/Shift-Tab to
        # move focus like every other field. (CodeEditor keeps Tab for indent —
        # it is a separate composite and is unaffected.)
        self._core.text.bind("<Tab>", self._focus_next, add="+")
        self._core.text.bind("<Shift-Tab>", self._focus_prev, add="+")
        self._core.text.bind("<ISO_Left_Tab>", self._focus_prev, add="+")

        # ── message label (row 2) ─────────────────────────────────────────
        self._message_lbl = Label(self, text=message or "", font="caption",
                                  accent="secondary")
        self._message_lbl.grid(row=2, column=0, sticky="w")
        self._message_lbl.grid_remove()

        if show_message or message or required:
            self._show_message_area()

        # ── signal binding ────────────────────────────────────────────────
        if textsignal is not None:
            self._core.bind_signal(textsignal)

        # ── placeholder ───────────────────────────────────────────────────
        self._default_fg = self._core.text.cget("foreground")
        if placeholder and not value and textsignal is None:
            self._show_placeholder()
        if placeholder:
            self._core.text.bind("<FocusIn>", self._on_focus_in_placeholder, add="+")

        # ── max_length filter ─────────────────────────────────────────────
        if max_length is not None:
            from bootstack.widgets._impl.composites.textarea.filter import EditFilter

            _limit = max_length

            class _MaxLenFilter(EditFilter):
                def insert(self, index, chars, tags=None):
                    current = len(self.get("1.0", "end-1c"))
                    allowed = max(0, _limit - current)
                    if allowed > 0:
                        self.delegate.insert(index, chars[:allowed], tags)

            self._core.add_filter(_MaxLenFilter())

        # ── required rule ─────────────────────────────────────────────────
        if required:
            self.add_validation_rule("required")

        # ── internal event wiring ─────────────────────────────────────────
        # Fire <<Input>> on every edit, <<Changed>> + validation on blur.
        self._core.text.bind("<<Change>>", self._on_core_change, add="+")
        self._core.text.bind("<FocusOut>", self._on_focus_out, add="+")

        # ── constructor callbacks ─────────────────────────────────────────
        if on_input is not None:
            self.on_input(on_input)
        if on_changed is not None:
            self.on_changed(on_changed)
        if on_blur is not None:
            self.on_changed(on_blur)
        if on_valid is not None:
            self.on_valid(on_valid)
        if on_invalid is not None:
            self.on_invalid(on_invalid)
        if on_validated is not None:
            self.on_validated(on_validated)

    # ── placeholder ───────────────────────────────────────────────────────

    def _show_placeholder(self) -> None:
        self._showing_placeholder = True
        was_read_only = self._core._read_only
        self._core.text.configure(state=tk.NORMAL)
        self._core.text.insert("1.0", self._placeholder_text)
        self._core.text.configure(foreground="grey")
        # Restore read-only state — showing a placeholder must not silently make
        # a read-only field editable.
        if was_read_only:
            self._core.text.configure(state=tk.DISABLED)

    def _hide_placeholder(self) -> None:
        self._showing_placeholder = False
        was_read_only = self._core._read_only
        if was_read_only:
            self._core.text.configure(state=tk.NORMAL)
        self._core.text.delete("1.0", tk.END)
        self._core.text.configure(foreground=self._default_fg)
        if was_read_only:
            self._core.text.configure(state=tk.DISABLED)

    def _on_focus_in_placeholder(self, _event: tk.Event) -> None:
        if self._showing_placeholder:
            self._hide_placeholder()

    # ── focus traversal ───────────────────────────────────────────────────

    def _focus_next(self, event: tk.Event) -> str:
        event.widget.tk_focusNext().focus_set()
        return "break"

    def _focus_prev(self, event: tk.Event) -> str:
        event.widget.tk_focusPrev().focus_set()
        return "break"

    # ── message / error area ──────────────────────────────────────────────

    def _show_message_area(self) -> None:
        if not self._message_showing:
            self._message_lbl.grid()
            self._message_showing = True

    def _show_error(self, message: str) -> None:
        self._show_message_area()
        self._message_lbl.configure(text=message, accent="danger")

    def _clear_error(self) -> None:
        self._message_lbl.configure(text=self._original_message, accent="secondary")

    # ── validation ────────────────────────────────────────────────────────

    def add_validation_rule(
        self,
        rule_type: str,
        message: str | None = None,
        **kwargs,
    ) -> None:
        """Add a validation rule to this field.

        Args:
            rule_type: Rule name — `"required"`, `"pattern"`, `"stringLength"`,
                `"email"`, `"custom"`, etc.
            message: Custom error message. If None, the rule's default is used.
            **kwargs: Rule-specific parameters (e.g. `minLength=`, `pattern=`,
                `func=` for custom rules).
        """
        from bootstack.validation.validation_rules import ValidationRule
        self._rules.append(ValidationRule(rule_type, message=message, **kwargs))
        self._show_message_area()

    def validate(self) -> bool:
        """Run all validation rules immediately and return True if valid.

        Triggers the same `<<Valid>>` / `<<Invalid>>` / `<<Validate>>` events
        as blur-triggered validation.
        """
        return self._run_validation(trigger="manual")

    def _set_validity(self, is_valid: bool, message: str) -> None:
        self._error_signal.set("" if is_valid else message)
        self._valid_signal.set(is_valid)

    def _run_validation(self, trigger: str = "blur") -> bool:
        value = self.value
        for rule in self._rules:
            if trigger != "manual" and rule.trigger not in ("always", trigger):
                continue
            result = rule.validate(value)
            if not result.is_valid:
                self._set_validity(False, result.message)
                self._show_error(result.message)
                data = ValidationEvent(
                    value=value, is_valid=False, message=result.message,
                )
                self.event_generate("<<Invalid>>", data=data, when="tail")
                self.event_generate("<<Validate>>", data=data, when="tail")
                return False
        self._set_validity(True, "")
        self._clear_error()
        data = ValidationEvent(value=value, is_valid=True, message="")
        self.event_generate("<<Valid>>", data=data, when="tail")
        self.event_generate("<<Validate>>", data=data, when="tail")
        return True

    # ── internal event dispatch ───────────────────────────────────────────

    def _on_core_change(self, _event: tk.Event) -> None:
        if not self._showing_placeholder:
            self.event_generate(
                "<<Input>>",
                data=InputEvent(text=self.value),
                when="tail",
            )

    def _on_focus_out(self, _event: tk.Event) -> None:
        if self._placeholder_text and not self._core.value:
            self._show_placeholder()
        if not self._showing_placeholder:
            self.event_generate(
                "<<Changed>>",
                data=ChangeEvent(value=self.value, text=self.value),
                when="tail",
            )
        if self._rules:
            self._run_validation(trigger="blur")

    # ── public value API ──────────────────────────────────────────────────

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

    def focus_set(self, *args, **kwargs) -> None:
        """Set focus to the text area."""
        self._core.focus_set()

    @property
    def core(self) -> _MultilineCore:
        """The internal `_MultilineCore` — for advanced filter/decoration use."""
        return self._core

    # ── event subscriptions ───────────────────────────────────────────────

    def on_input(self, callback: Callable[[InputEvent], None]) -> str:
        """Register a callback for `<<Input>>` events.

        Fires on every edit. `event.data.text` is the current text.

        Args:
            callback: Receives the Tk event. `event.data` is
                `InputEvent`.

        Returns:
            Bind ID — pass to `off_input()` to unsubscribe.
        """
        return self.bind("<<Input>>", callback, add="+")

    def off_input(self, bind_id: str | None = None) -> None:
        """Unsubscribe from `<<Input>>`.

        Args:
            bind_id: ID returned by `on_input()`. If None, removes all.
        """
        self.unbind("<<Input>>", bind_id)

    def on_changed(self, callback: Callable[[InputEvent], None]) -> str:
        """Register a callback for `<<Changed>>` events.

        Fires when the widget loses focus. `event.data.value` is the
        current text.

        Args:
            callback: Receives the Tk event. `event.data` is
                `InputEvent`.

        Returns:
            Bind ID — pass to `off_changed()` to unsubscribe.
        """
        return self.bind("<<Changed>>", callback, add="+")

    def off_changed(self, bind_id: str | None = None) -> None:
        """Unsubscribe from `<<Changed>>`.

        Args:
            bind_id: ID returned by `on_changed()`. If None, removes all.
        """
        self.unbind("<<Changed>>", bind_id)

    def on_blur(self, callback: Callable) -> str:
        """Register a callback for focus-out events.

        Args:
            callback: Called when the text area loses focus.

        Returns:
            Bind ID — pass to `off_blur()` to unsubscribe.
        """
        return self._core.text.bind("<FocusOut>", callback, add="+")

    def off_blur(self, bind_id: str | None = None) -> None:
        """Unsubscribe from focus-out events.

        Args:
            bind_id: ID returned by `on_blur()`. If None, removes all.
        """
        self._core.text.unbind("<FocusOut>", bind_id)

    def on_valid(self, callback: Callable) -> str:
        """Register a callback for `<<Valid>>` events.

        Fires after all validation rules pass.

        Args:
            callback: Receives the Tk event. `event.data` is
                `ValidationEvent`.

        Returns:
            Bind ID — pass to `off_valid()` to unsubscribe.
        """
        return self.bind("<<Valid>>", callback, add="+")

    def off_valid(self, bind_id: str | None = None) -> None:
        """Unsubscribe from `<<Valid>>`.

        Args:
            bind_id: ID returned by `on_valid()`. If None, removes all.
        """
        self.unbind("<<Valid>>", bind_id)

    def on_invalid(self, callback: Callable) -> str:
        """Register a callback for `<<Invalid>>` events.

        Fires when any validation rule fails.

        Args:
            callback: Receives the Tk event. `event.data` is
                `ValidationEvent`.

        Returns:
            Bind ID — pass to `off_invalid()` to unsubscribe.
        """
        return self.bind("<<Invalid>>", callback, add="+")

    def off_invalid(self, bind_id: str | None = None) -> None:
        """Unsubscribe from `<<Invalid>>`.

        Args:
            bind_id: ID returned by `on_invalid()`. If None, removes all.
        """
        self.unbind("<<Invalid>>", bind_id)

    def on_validated(self, callback: Callable) -> str:
        """Register a callback for `<<Validate>>` events.

        Fires after any validation pass, whether the result is valid or not.

        Args:
            callback: Receives the Tk event. `event.data` is
                `ValidationEvent`.

        Returns:
            Bind ID — pass to `off_validated()` to unsubscribe.
        """
        return self.bind("<<Validate>>", callback, add="+")

    def off_validated(self, bind_id: str | None = None) -> None:
        """Unsubscribe from `<<Validate>>`.

        Args:
            bind_id: ID returned by `on_validated()`. If None, removes all.
        """
        self.unbind("<<Validate>>", bind_id)

    def on_modified(self, callback: Callable) -> str:
        """Register a callback for `<<TextModified>>` events.

        Fires when the dirty state changes. `event.data.is_dirty` is the
        new state.

        Args:
            callback: Receives the Tk event.

        Returns:
            Bind ID — pass to `off_modified()` to unsubscribe.
        """
        return self._core.on_modified(callback)

    def off_modified(self, bind_id: str | None = None) -> None:
        """Unsubscribe from `<<TextModified>>`.

        Args:
            bind_id: ID returned by `on_modified()`. If None, removes all.
        """
        self._core.off_modified(bind_id)

    def on_undo(self, callback: Callable) -> str:
        """Register a callback for `<<TextUndo>>` events.

        Fires after an undo completes. `event.data.text` is the text
        content after the undo.

        Args:
            callback: Receives the Tk event.

        Returns:
            Bind ID — pass to `off_undo()` to unsubscribe.
        """
        return self._core.on_undo(callback)

    def off_undo(self, bind_id: str | None = None) -> None:
        """Unsubscribe from `<<TextUndo>>`.

        Args:
            bind_id: ID returned by `on_undo()`. If None, removes all.
        """
        self._core.off_undo(bind_id)

    def on_redo(self, callback: Callable) -> str:
        """Register a callback for `<<TextRedo>>` events.

        Fires after a redo completes. `event.data.text` is the text
        content after the redo.

        Args:
            callback: Receives the Tk event.

        Returns:
            Bind ID — pass to `off_redo()` to unsubscribe.
        """
        return self._core.on_redo(callback)

    def off_redo(self, bind_id: str | None = None) -> None:
        """Unsubscribe from `<<TextRedo>>`.

        Args:
            bind_id: ID returned by `on_redo()`. If None, removes all.
        """
        self._core.off_redo(bind_id)