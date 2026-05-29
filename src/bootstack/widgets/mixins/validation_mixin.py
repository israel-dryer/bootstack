"""Validation mixin for widgets with enhanced event system.

This mixin provides validation functionality using the enhanced event system
that allows passing data directly through virtual events.
"""

from __future__ import annotations

import tkinter
from tkinter import TclError
from tkinter.ttk import Widget
from typing import Any, Callable

from bootstack.validation import ValidationRule
from bootstack.validation.types import RuleTriggerType, RuleType, ValidationOptions


class ValidationMixin(Widget):
    """Pure-Tkinter validation mixin for bound widgets.

    Provides debounced auto-validation on key/blur with virtual event emission.
    Event data is accessible via `event.data` in handlers.

    """

    EVENT_VALID = '<<Valid>>'
    EVENT_INVALID = '<<Invalid>>'
    EVENT_VALIDATED = '<<Validate>>'
    SEQ_KEYUP = '<KeyRelease>'
    SEQ_BLUR = '<FocusOut>'

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        """Set up validation state before the widget is fully initialized.

        Initialises the rule list, debounce tracking, and optional convenience
        callbacks. Binds ``<<KeyRelease>>`` and ``<<FocusOut>>`` to trigger
        debounced validation automatically.
        """
        # Validation rules
        self._rules: list[ValidationRule] = []

        # Debounce tracking
        self._debounce_ids: dict[str, str] = {}

        # Optional convenience callbacks
        self._on_invalid_command: Callable | None = None
        self._on_valid_command: Callable | None = None
        self._on_validated_command: Callable | None = None

        super().__init__(*args, **kwargs)  # next in MRO must be a Tk/ttk widget
        self._setup_validation_binds()

    # ---------------- Public API ----------------

    def value(self) -> Any:
        """Default value accessor; override for non-Entry widgets.

        Returns:
            Current widget value
        """
        if hasattr(self, 'get'):
            try:
                return self.get()
            except AttributeError:
                return None
        return None

    def add_validation_rule(self, rule_type: RuleType, **kwargs: ValidationOptions) -> None:
        """Add a single validation rule.

        Args:
            rule_type: Type of validation rule (e.g., 'required', 'min_length')
            **kwargs: Rule-specific options (e.g., min_length=5, message='...')
        """
        self._rules.append(ValidationRule(rule_type, **kwargs))

    def add_validation_rules(self, rules: list[ValidationRule]) -> None:
        """Replace all validation rules.

        Args:
            rules: List of ValidationRule objects
        """
        self._rules = list(rules)

    def validate(self, value: Any, trigger: RuleTriggerType = "manual") -> bool:
        """Run validation rules against a value.

        Emits `<<Valid>>`, `<<Invalid>>`, and `<<Validate>>` events
        with data payload containing validation results.

        Args:
            value: Value to validate
            trigger: Trigger type ('manual', 'key', 'blur', or 'always')

        Returns:
            True if validation was performed (regardless of result)
        """
        ran_rule = False
        payload: dict[str, Any] = {"value": value, "is_valid": True, "message": ""}

        for rule in self._rules:
            if trigger != "manual" and rule.trigger not in ("always", trigger):
                continue

            ran_rule = True
            result = rule.validate(value)
            payload.update(is_valid=result.is_valid, message=result.message)

            if not result.is_valid:
                # Emit invalid and validated events with data
                self.event_generate(self.EVENT_INVALID, data=payload)
                self.event_generate(self.EVENT_VALIDATED, data=payload)
                return False

        if ran_rule:
            # Emit valid and validated events with data
            self.event_generate(self.EVENT_VALID, data=payload)
            self.event_generate(self.EVENT_VALIDATED, data=payload)

        return ran_rule

    # Optional: ergonomic callback registration
    def on_invalid(self, func: Callable) -> None:
        """Register callback for `<<Invalid>>`. Callback receives the event; `event.data` is a `ValidationEventData` dict."""
        self._on_invalid_command = func

    def off_invalid(self, bind_id: str | None = None) -> None:
        """Unsubscribe from `<<Invalid>>` events.

        Args:
            bind_id: ID returned by `on_invalid()`. If None, removes all bindings.
        """
        self.unbind('<<Invalid>>', bind_id)

    def on_valid(self, func: Callable) -> None:
        """Register callback for `<<Valid>>`. Callback receives the event; `event.data` is a `ValidationEventData` dict."""
        self._on_valid_command = func

    def off_valid(self, bind_id: str | None = None) -> None:
        """Unsubscribe from `<<Valid>>` events.

        Args:
            bind_id: ID returned by `on_valid()`. If None, removes all bindings.
        """
        self.unbind('<<Valid>>', bind_id)

    def on_validated(self, func: Callable) -> None:
        """Register callback for `<<Validate>>`. Callback receives the event; `event.data` is a `ValidationEventData` dict."""
        self._on_validated_command = func

    def off_validated(self, bind_id: str | None = None) -> None:
        """Unsubscribe from `<<Validate>>` events.

        Args:
            bind_id: ID returned by `on_validated()`. If None, removes all bindings.
        """
        self.unbind('<<Validate>>', bind_id)

    # ---------------- Internals ----------------

    def _get_validation_value(self) -> Any:
        """Get the current value for validation purposes.

        For entry widgets, this should return the current text being typed,
        not the committed value. Prefers get() method over value() method.
        """
        if hasattr(self, 'get'):
            try:
                return self.get()
            except (AttributeError, TclError):
                pass
        return self.value()

    def _setup_validation_binds(self, keyup_delay_ms: int = 50, blur_delay_ms: int = 50) -> None:
        """Set up automatic validation bindings with debouncing."""
        # Auto-validate (debounced)
        self.bind(self.SEQ_KEYUP, lambda e: self._debounced("key", keyup_delay_ms), add=True)
        self.bind(self.SEQ_BLUR, lambda e: self._debounced("blur", blur_delay_ms), add=True)

        # Wire optional convenience callbacks
        self.bind(self.EVENT_VALIDATED, self._dispatch_validated, add=True)
        self.bind(self.EVENT_VALID, self._dispatch_valid, add=True)
        self.bind(self.EVENT_INVALID, self._dispatch_invalid, add=True)

    def _debounced(self, trigger: RuleTriggerType, ms: int) -> None:
        """Debounce validation to avoid excessive checks during typing."""
        key = f"debounce:{trigger}"
        aid: str | None = self._debounce_ids.get(key)
        if aid:
            try:
                self.after_cancel(aid)
            except TclError:
                pass
        # defer reading value until the timer fires
        self._debounce_ids[key] = self.after(ms, lambda: self.validate(self._get_validation_value(), trigger))

    # ----- optional dispatchers for on_* convenience -----

    def _dispatch_validated(self, event: tkinter.Event) -> None:
        if self._on_validated_command:
            self._on_validated_command(event)

    def _dispatch_valid(self, event: tkinter.Event) -> None:
        if self._on_valid_command:
            self._on_valid_command(event)

    def _dispatch_invalid(self, event: tkinter.Event) -> None:
        if self._on_invalid_command:
            self._on_invalid_command(event)
