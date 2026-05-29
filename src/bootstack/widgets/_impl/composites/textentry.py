from typing import Any

from typing_extensions import Unpack

from bootstack.widgets._impl.composites.field import Field, FieldOptions
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
        """Args:
            master: Parent widget. If None, uses the default root window.
            value: Initial value to display. Default is None.
            label: Optional label text to display above the entry field.
                If required=True, an asterisk (*) is automatically appended.
            message: Optional message text to display below the entry field.
                This is replaced by validation error messages when validation fails.

        Other Parameters:
            accent: Accent token for the focus ring and active border.
            density: Widget density — 'default' or 'compact'.
            state: Initial widget state — 'normal', 'disabled', or 'readonly'.
            allow_blank: Allow empty input. Default is True.
            cursor: Cursor style when hovering.
            value_format: ICU format pattern for parsing/formatting.
            exportselection: Export selection to clipboard.
            font: Font for text display.
            foreground: Text color.
            initial_focus: If True, widget receives focus on creation.
            justify: Text alignment ('left', 'center', 'right').
            show_message: If True, displays message area. Defaults to False,
                but auto-enables when `message=` or `required=True` is set.
            padding: Padding around entry widget.
            show: Character to mask input (e.g., '*' for passwords).
            takefocus: If True, widget accepts Tab focus.
            textvariable: Tkinter Variable to link with text.
                See [tkinter Variables](https://docs.python.org/3/library/tkinter.html#tkinter-variables).
            textsignal: Signal object for reactive updates.
            width: Width in characters.
            required: If True, field cannot be empty. Adds 'required'
                validation rule and appends '*' to label.
            xscrollcommand: Callback for horizontal scrolling.
        """
        super().__init__(master, value=value, label=label, message=message, **kwargs)

