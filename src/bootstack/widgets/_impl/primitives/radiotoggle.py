from typing import Literal

from typing_extensions import Unpack

from bootstack.widgets._impl.primitives.radiobutton import RadioButton, RadioButtonKwargs
from bootstack.widgets.types import Master


class RadioToggle(RadioButton):
    """bootstack wrapper for `ttk.Radiobutton` that renders with a toggle badge style."""

    def __init__(self, master: Master = None, **kwargs: Unpack[RadioButtonKwargs]) -> None:
        """Create a themed bootstack RadioToggle.

        Args:
            master: Parent widget. If None, uses the default root window.

        Other Parameters:
            text: Text to display.
            textvariable: Tk variable linked to the text.
                See [tkinter Variables](https://docs.python.org/3/library/tkinter.html#tkinter-variables).
            textsignal: Reactive Signal linked to the text (auto-synced with textvariable).
            command: Callable invoked when the value is selected.
            image: Image to display.
            icon: Theme-aware icon spec handled by the style system.
            icon_only: Removes the additional padding added for label text.
            compound: Placement of the image relative to text.
            variable: Linked Tk variable that receives the selected value.
                See [tkinter Variables](https://docs.python.org/3/library/tkinter.html#tkinter-variables).
            signal: Reactive Signal that receives the selected value (auto-synced with variable).
            value: The value assigned to `variable` when this radio is selected.
            padding: Extra space around the content.
            anchor: Determines how the content is aligned in the container. Combination of 'n', 's', 'e', 'w', or 'center' (default).
            density: The vertical and horizontal compactness of widget content, e.g. 'default', 'compact'.
            width: Width of the control in characters.
            underline: Index of character to underline in `text`.
            state: Widget state ('normal', 'active', 'disabled', 'readonly').
            takefocus: Whether the widget participates in focus traversal.
            accent: Accent token for styling, e.g. 'primary', 'success', 'danger'.
            surface: Optional surface token; otherwise inherited.
            style_options: Optional dict forwarded to the style builder.
            localize: Determines the widget's localization mode.
        """
        self._capture_density_option(kwargs)
        kwargs.setdefault('ttk_class', 'Toolbutton')
        super().__init__(master, **kwargs)

    @staticmethod
    def _capture_density_option(kwargs: dict) -> None:
        """Capture density from kwargs into style_options."""
        density: Literal['default', 'compact'] | None = kwargs.pop('density', None)
        if density is not None:
            style_options = kwargs.setdefault('style_options', {})
            style_options['density'] = density
