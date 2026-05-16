"""Spinner entry field widget.

Provides a specialized entry field with a built-in spinbox for selecting
values from a list or numeric range.
"""

from __future__ import annotations

from typing_extensions import Unpack

from bootstack.widgets.composites.field import Field, FieldOptions
from bootstack.widgets.mixins import configure_delegate
from bootstack.widgets.types import Master


class SpinnerEntry(Field):
    """A spinner entry field widget with built-in spin controls.

    SpinnerEntry extends the Field widget to provide a spinbox input that can
    handle both predefined text values and numeric ranges. The widget includes
    built-in up/down arrow buttons and supports keyboard/mouse wheel interaction.
    """

    def __init__(
            self,
            master: Master = None,
            value: int | float | str = '',
            label: str = None,
            message: str = None,
            values: list[str] = None,
            minvalue: int | float = None,
            maxvalue: int | float = None,
            increment: int | float = 1,
            wrap: bool = False,
            **kwargs: Unpack[FieldOptions]
    ):
        """Args:
            master: Parent widget. If None, uses the default root window.
            value: Initial value to display. Can be string, integer, or float
                depending on whether using text values or numeric range.
                Default is empty string.
            label: Optional label text to display above the entry field.
                If required=True, an asterisk (*) is automatically appended.
            message: Optional message text to display below the entry field.
                Used for hints or help text. Replaced by validation errors when
                validation fails.
            values: List of valid string values for the spinner. If provided,
                the spinner cycles through these values. Mutually exclusive with
                minvalue/maxvalue/increment. Example: ['Low', 'Medium', 'High']
            minvalue: Minimum numeric value (inclusive). Only used for numeric spinners.
                If provided along with 'maxvalue', creates a numeric range spinner.
            maxvalue: Maximum numeric value (inclusive). Only used for numeric spinners.
                If provided along with 'minvalue', creates a numeric range spinner.
            increment: Step size for increment/decrement in numeric mode.
                Default is 1. Only applies when using minvalue/maxvalue.
            wrap: If True, values wrap around at boundaries. Default is False.

        Other Parameters:
            value_format: ICU format pattern for parsing/formatting.
            locale: Locale identifier for formatting (e.g., 'en_US').
            required: If True, field cannot be empty.
            accent: Accent token for the focus ring and active border.
            allow_blank: If True, empty input is allowed.
            cursor: Cursor style when hovering.
            font: Font for text display.
            foreground: Text color.
            initial_focus: If True, widget receives focus on creation.
            justify: Text alignment.
            show_message: If True, displays message area.
            padding: Padding around entry widget.
            takefocus: If True, widget accepts Tab focus.
            textvariable: Tkinter Variable to link with text.
            textsignal: Signal object for reactive updates.
            width: Width in characters.
        """
        # Build kwargs for Field initialization
        # Map minvalue/maxvalue to from_/to for the underlying Spinbox
        field_kwargs = {
            'values': values,
            'from_': minvalue,
            'to': maxvalue,
            'increment': increment,
            'wrap': wrap,
        }
        field_kwargs.update(kwargs)

        super().__init__(
            master,
            value=value,
            label=label,
            message=message,
            kind="spinbox",
            **field_kwargs
        )

        # Store configuration
        self._values = values
        self._minvalue = minvalue
        self._maxvalue = maxvalue
        self._increment = increment
        self._wrap = wrap

    @property
    def values(self) -> list[str]:
        """Get the list of valid values (text mode only)."""
        return self._values

    @configure_delegate('values')
    def _delegate_values(self, value: list[str] = None):
        """Get or set the list of valid values."""
        if value is None:
            return self._values

        self._values = value
        # Update the underlying spinbox
        try:
            self.entry_widget.configure(values=value)
        except Exception:
            pass
        return None

    @configure_delegate('minvalue')
    def _delegate_minvalue(self, value: int | float = None):
        """Get or set the minimum value (numeric mode)."""
        if value is None:
            return self._minvalue

        self._minvalue = value
        # Update the underlying spinbox (uses from_)
        try:
            self.entry_widget.configure(from_=value)
        except Exception:
            pass
        return None

    @configure_delegate('maxvalue')
    def _delegate_maxvalue(self, value: int | float = None):
        """Get or set the maximum value (numeric mode)."""
        if value is None:
            return self._maxvalue

        self._maxvalue = value
        # Update the underlying spinbox (uses to)
        try:
            self.entry_widget.configure(to=value)
        except Exception:
            pass
        return None

    @configure_delegate('increment')
    def _delegate_increment(self, value: int | float = None):
        """Get or set the increment step size (numeric mode)."""
        if value is None:
            return self._increment

        self._increment = value
        # Update the underlying spinbox
        try:
            self.entry_widget.configure(increment=value)
        except Exception:
            pass
        return None

    @configure_delegate('wrap')
    def _delegate_wrap(self, value: bool = None):
        """Get or set the wrap setting."""
        if value is None:
            return self._wrap

        self._wrap = bool(value)
        # Update the underlying spinbox
        try:
            self.entry_widget.configure(wrap=value)
        except Exception:
            pass
        return None
