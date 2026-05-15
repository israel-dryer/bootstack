from bootstack.widgets.primitives.checkbutton import CheckButton
from bootstack.widgets.types import Master


class Switch(CheckButton):
    """bootstack wrapper for `ttk.Checkbutton` that renders with a Switch style"""

    def __init__(self, master: Master = None, **kwargs):
        """Create a themed bootstack Switch.

        Args:
            master: Parent widget. If None, uses the default root window.

        Other Parameters:
            text: Text to display on the toggle.
            textvariable: Tk variable linked to the text.
            textsignal: Reactive Signal linked to the text (auto-synced with textvariable).
            command: Callable invoked when the toggle changes state.
            image: Image to display.
            icon: Theme-aware icon spec handled by the style system.
            icon_only: If True, removes the additional padding reserved for text.
            compound: Placement of the image relative to text.
            variable: Linked variable controlling the on/off state.
            signal: Reactive Signal controlling the on/off state (auto-synced with variable).
            value: Initial state for the widget's associated variable (defaults to None when unset).
            onvalue: Value set in `variable` when selected.
            offvalue: Value set in `variable` when deselected.
            padding: Extra space around the content.
            anchor: Determines how the content is aligned in the container. Combination of 'n', 's', 'e', 'w', or 'center' (default).
            width: Width of the control in characters.
            underline: Index of character to underline in `text`.
            state: Widget state ('normal', 'active', 'disabled', 'readonly').
            takefocus: Whether the widget participates in focus traversal.
            accent: Accent token for styling, e.g. 'primary', 'success', 'danger'.
            surface: Optional surface token; otherwise inherited.
            style_options: Optional dict forwarded to the style builder.
            localize: Determines the widget's localization mode.
        """
        if 'bootstyle' not in kwargs:
            kwargs['variant'] = 'switch'
        super().__init__(master, **kwargs)
