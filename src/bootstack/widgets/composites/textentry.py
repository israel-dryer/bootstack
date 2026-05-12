from typing import Any

from typing_extensions import Unpack

from bootstack.widgets.composites.field import Field, FieldOptions
from bootstack.widgets.types import Master


class TextEntry(Field):
    """A text entry field widget with label, validation, and formatting support.

    TextEntry is a composite widget that combines a label, text entry input, and
    message area into a single component. It provides internationalization-aware
    text input with deferred parsing, validation support, and visual feedback.

    The widget separates user input (display text) from the committed/parsed value,
    only parsing and formatting when the user commits via `<FocusOut>` or `<Return>`.
    """

    def __init__(
            self, master: Master = None, value: Any = None, label: str = None, message: str = None,
            **kwargs: Unpack[FieldOptions]):
        """Initialize a TextEntry widget.

        Creates a composite text entry field with optional label, validation,
        and formatting support. The widget includes a label area, entry input,
        and message area for displaying hints or validation errors.

        Args:
            master: Parent widget. If None, uses the default root window.
            value: Initial value to display. Default is None.
            label: Optional label text to display above the entry field.
                If required=True, an asterisk (*) is automatically appended.
            message: Optional message text to display below the entry field.
                This is replaced by validation error messages when validation fails.

        Other Parameters:
            accent (str): Accent token for the focus ring and active border.
            density (str): Widget density — 'default' or 'compact'.
            state (str): Initial widget state — 'normal', 'disabled', or 'readonly'.
            allow_blank (bool): Allow empty input. Default is True.
            cursor (str): Cursor style when hovering.
            value_format (str): ICU format pattern for parsing/formatting.
            exportselection (bool): Export selection to clipboard.
            font (str): Font for text display.
            foreground (str): Text color.
            initial_focus (bool): If True, widget receives focus on creation.
            justify (str): Text alignment ('left', 'center', 'right').
            show_message (bool): If True, displays message area. Defaults to False,
                but auto-enables when `message=` or `required=True` is set.
            padding: Padding around entry widget.
            show (str): Character to mask input (e.g., '*' for passwords).
            takefocus (bool): If True, widget accepts Tab focus.
            textvariable (Variable): Tkinter Variable to link with text.
            textsignal (Signal): Signal object for reactive updates.
            width (int): Width in characters.
            required (bool): If True, field cannot be empty. Adds 'required'
                validation rule and appends '*' to label.
            xscrollcommand: Callback for horizontal scrolling.
        """
        super().__init__(master, value=value, label=label, message=message, **kwargs)

