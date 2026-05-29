from typing import Literal

from typing_extensions import Unpack

from bootstack.widgets._impl.primitives.checkbutton import CheckButton, CheckButtonKwargs
from bootstack.widgets.types import Master


class CheckToggle(CheckButton):
    """bootstack wrapper for `ttk.Checkbutton` that renders with a ToolButton style"""

    def __init__(self, master: Master = None, **kwargs: Unpack[CheckButtonKwargs]) -> None:
        """Create a themed bootstack CheckToggle.

        Args:
            master: Parent widget. If None, uses the default root window.

        Other Parameters:
            text: Text to display on the toggle.
            textvariable: Tk variable linked to the text.
                See [tkinter Variables](https://docs.python.org/3/library/tkinter.html#tkinter-variables).
            textsignal: Reactive Signal linked to the text (auto-synced with textvariable).
            command: Callable invoked when the toggle changes state.
            image: Image to display.
            icon: Icon shown in the label area for all states. Color shifts
                with the button's pressed/selected state automatically.
            on_icon: Icon shown when the toggle is selected (on). Shortcut
                for `state=[("selected", name)]` inside a full icon spec.
            off_icon: Icon shown when the toggle is unselected (off). Used
                as the base icon when `on_icon` is also provided.
            icon_only: If True, removes the additional padding reserved for text.
            compound: Placement of the image relative to text.
            variable: Linked variable controlling the on/off state.
                See [tkinter Variables](https://docs.python.org/3/library/tkinter.html#tkinter-variables).
            signal: Reactive Signal controlling the on/off state (auto-synced with variable).
            value: Initial state for the widget's associated variable (defaults to None when unset).
            onvalue: Value set in `variable` when selected.
            offvalue: Value set in `variable` when deselected.
            padding: Extra space around the content.
            anchor: Determines how the content is aligned in the container. Combination of 'n', 's', 'e', 'w', or 'center' (default).
            density: The vertical and horizontal compactness of widget content, e.g. 'default', 'compact'.
            width: Width of the control in characters.
            underline: Index of character to underline in `text`.
            state: Widget state ('normal', 'active', 'disabled', 'readonly').
            takefocus: Whether the widget participates in focus traversal.
            accent: Accent token for styling, e.g. 'primary', 'success', 'danger'.
            variant: Style variant (coerced to 'toolbutton').
            surface: Optional surface token; otherwise inherited.
            style_options: Optional dict forwarded to the style builder.
            localize: Determines the widget's localization mode.
        """
        self._capture_density_option(kwargs)
        kwargs.setdefault('class_', 'Toolbutton')
        super().__init__(master, **kwargs)

    @staticmethod
    def _capture_density_option(kwargs: dict) -> None:
        """Capture density from kwargs into style_options."""
        density: Literal['default', 'compact'] | None = kwargs.pop('density', None)
        if density is not None:
            style_options = kwargs.setdefault('style_options', {})
            style_options['density'] = density
