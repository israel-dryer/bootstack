"""Localization capability for bootstack widgets.

This module provides the core framework service for localizing widget text
and values. It handles text resolution, value formatting, and locale change
propagation.

The widget mixin (LocalizationMixin) delegates to these functions to remain
a thin glue layer.
"""

from __future__ import annotations

import itertools
import weakref
from tkinter import TclError
from typing import Any, Callable, TYPE_CHECKING

from bootstack.i18n.msgcat import MessageCatalog
from bootstack.i18n.specs import (
    LocalizedSpec,
    LocalizedTextSpec,
    LocalizedValueSpec,
)

if TYPE_CHECKING:
    from bootstack.signals import Signal


# =============================================================================
# Text Resolution
# =============================================================================

def resolve_text(
    value: Any,
    *,
    localize_mode: bool | str = True,
) -> LocalizedTextSpec | None:
    """Resolve a text value into a LocalizedTextSpec.

    This function handles the logic for creating localization specs from
    string values based on the localization mode.

    Args:
        value: The value to resolve. Can be:
            - A LocalizedSpec: returned as-is (if it's a LocalizedTextSpec)
            - A string: wrapped in LocalizedTextSpec if localize_mode is truthy
            - None or empty string: returns None
        localize_mode: Controls auto-wrapping of literals:
            - True or "auto": wrap strings in LocalizedTextSpec
            - False: return None (no localization)

    Returns:
        A LocalizedTextSpec if the value should be localized, None otherwise.

    Examples:
        >>> spec = resolve_text("Hello World")
        >>> spec.key
        'Hello World'

        >>> spec = resolve_text("Hello", localize_mode=False)
        >>> spec is None
        True

        >>> from bootstack.i18n.specs import L
        >>> spec = resolve_text(L("greeting"))
        >>> spec.key
        'greeting'
    """
    if value is None:
        return None

    if isinstance(value, str) and value == "":
        return None

    # If already a LocalizedSpec, return as-is
    if isinstance(value, LocalizedTextSpec):
        return value
    if isinstance(value, LocalizedSpec):
        # Other spec types (like LocalizedValueSpec) - cannot use as text
        return None

    # Check localize mode
    if localize_mode is False:
        return None

    # Wrap string in LocalizedTextSpec
    if isinstance(value, str):
        return LocalizedTextSpec(key=value, original=value)

    return None


def resolve_variable_text(
    value: Any,
    *,
    value_format: str | None = None,
    default_format: str = "decimal",
) -> LocalizedValueSpec | None:
    """Resolve a non-string value into a LocalizedValueSpec for formatting.

    This function handles the logic for creating value formatting specs from
    numeric or other values.

    Args:
        value: The value to format. Should be a number, date, or other
            formattable type.
        value_format: The IntlFormatter spec (e.g., "currency", "decimal",
            "percent"). If None, uses default_format.
        default_format: Fallback format spec when value_format is None.

    Returns:
        A LocalizedValueSpec if the value can be formatted, None otherwise.

    Examples:
        >>> spec = resolve_variable_text(1234.56, value_format="currency")
        >>> spec.value
        1234.56
        >>> spec.format_spec
        'currency'

        >>> spec = resolve_variable_text(0.5, value_format="percent")
        >>> spec.format_spec
        'percent'
    """
    if value is None:
        return None

    if isinstance(value, LocalizedValueSpec):
        return value

    if isinstance(value, str):
        # Strings are handled by resolve_text, not this function
        return None

    fmt = value_format or default_format
    return LocalizedValueSpec(value=value, format_spec=fmt)


def apply_spec(spec: LocalizedSpec, locale: str | None = None) -> str:
    """Apply a localization spec and return the resolved string.

    Args:
        spec: The LocalizedSpec to resolve.
        locale: The locale to use. If None, uses the current locale from
            MessageCatalog.

    Returns:
        The resolved, localized string value.

    Examples:
        >>> from bootstack.i18n.specs import L, LV
        >>> spec = L("hello")
        >>> result = apply_spec(spec)  # Uses current locale
        >>> isinstance(result, str)
        True

        >>> spec = LV(1234.56, "decimal")
        >>> result = apply_spec(spec)
        >>> isinstance(result, str)
        True
    """
    if not spec.enabled:
        # Return original if possible, else empty
        if isinstance(spec, LocalizedTextSpec):
            return spec.original or spec.key
        elif isinstance(spec, LocalizedValueSpec):
            return str(spec.value)
        return ""

    current_locale = locale or MessageCatalog.locale()
    return spec.resolve(current_locale)


def get_current_locale() -> str:
    """Get the current locale from MessageCatalog.

    Returns:
        The current locale code (e.g., "en_US", "de_DE").
    """
    return MessageCatalog.locale()


# =============================================================================
# Locale Change Propagation
# =============================================================================

_LOCALE_EVENT = "<<LocaleChanged>>"


# Don't bind a widget's refresh directly on the window: nothing removes it
# when the widget is destroyed.
class _LocaleRefreshers:
    """The refresh methods one toplevel calls on a locale change."""

    def __init__(self, toplevel: Any) -> None:
        self._toplevel = toplevel
        self._refreshers: dict[int, weakref.WeakMethod] = {}
        self._keys = itertools.count()
        self._funcid: str | None = None

    def add(self, refresh: Callable[[], Any]) -> None:
        """Register `refresh`, a bound method of a widget on this toplevel."""
        self._ensure_bound()
        key = next(self._keys)
        refreshers = self._refreshers
        # Drop the entry when the widget is collected, so a window whose
        # locale never changes does not accumulate dead references either.
        refreshers[key] = weakref.WeakMethod(
            refresh, lambda _ref: refreshers.pop(key, None)
        )

    def _ensure_bound(self) -> None:
        """Bind the dispatcher, or bind it again if something replaced it.

        A `bind` of the event without `add` on this toplevel replaces every
        binding for it, the dispatcher included, which would silently stop
        every widget on the window from refreshing.
        """
        toplevel = self._toplevel
        if self._funcid is not None:
            script = str(toplevel.tk.call("bind", toplevel._w, _LOCALE_EVENT))
            # The line prefix `_patched_bind` emits, as `_patched_unbind` matches it.
            if ('if {"[%s ' % self._funcid) in script:
                return
        self._funcid = toplevel.bind(_LOCALE_EVENT, self._dispatch, add="+")

    def _dispatch(self, _event: Any = None) -> None:
        """Call each live widget's refresh, in the order they registered."""
        for key, ref in list(self._refreshers.items()):
            refresh = ref()
            if refresh is None:
                continue
            widget = refresh.__self__
            try:
                alive = widget.winfo_exists()
            except TclError:
                alive = False
            if not alive:
                # Destroyed, but still referenced from somewhere else.
                self._refreshers.pop(key, None)
                continue
            try:
                refresh()
            except Exception:
                # Report and carry on, as a handler bound on its own would:
                # one failing widget must not stop the rest from refreshing.
                widget._report_exception()


def bind_locale_refresh(refresh: Callable[[], Any]) -> None:
    """Call `refresh` on every locale change for as long as its widget exists.

    The locale-change event is generated on the root; `refresh` is called,
    with no arguments, when the event reaches the toplevel of the widget it is
    bound to, after the widgets registered before it. A destroyed widget is
    never called, and registering holds no strong reference to it.

    Args:
        refresh: A bound method of the widget to refresh.
    """
    toplevel = refresh.__self__.winfo_toplevel()
    refreshers = toplevel.__dict__.get("_bs_locale_refreshers")
    if refreshers is None:
        refreshers = toplevel._bs_locale_refreshers = _LocaleRefreshers(toplevel)
    refreshers.add(refresh)


# =============================================================================
# Signal Formatting
# =============================================================================

def create_formatted_signal(
    source_signal: 'Signal[Any]',
    value_format: str,
) -> tuple['Signal[str]', Any]:
    """Create a formatted signal that tracks a source signal.

    This creates a new Signal for formatted display that subscribes to the
    source signal and automatically formats values when they change.

    Args:
        source_signal: The source Signal to subscribe to.
        value_format: The IntlFormatter spec for formatting values.

    Returns:
        A tuple of (formatted_signal, formatter_callback) where:
        - formatted_signal: A new Signal[str] containing the formatted value
        - formatter_callback: The callback function for locale change updates

    Examples:
        >>> from bootstack.signals import Signal
        >>> price = Signal(1234.56)
        >>> formatted, formatter = create_formatted_signal(price, "currency")
        >>> # formatted() returns locale-formatted currency string
    """
    from bootstack.signals import Signal

    formatted_signal: Signal[str] = Signal("")

    def format_signal_value(value: Any) -> None:
        """Format the signal value using the current locale."""
        spec = LocalizedValueSpec(value=value, format_spec=value_format)
        locale = MessageCatalog.locale()
        formatted = spec.resolve(locale)
        formatted_signal.set(formatted)

    # Subscribe with immediate execution to format initial value
    source_signal.subscribe(format_signal_value, immediate=True)

    return formatted_signal, format_signal_value


__all__ = [
    "resolve_text",
    "resolve_variable_text",
    "apply_spec",
    "get_current_locale",
    "bind_locale_refresh",
    "create_formatted_signal",
]