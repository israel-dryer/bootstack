from typing_extensions import Unpack
from bootstack.widgets.primitives.label import Label, LabelKwargs
from bootstack.widgets.types import Master


class Badge(Label):
    """bootstack wrapper for `ttk.Label` that renders with a badge style."""

    def __init__(self, master: Master = None, **kwargs: Unpack[LabelKwargs]):
        """Create a themed bootstack Badge.

        Args:
            master: Parent widget. If None, uses the default root window.

        Note:
            Badge is text-only by design. The TBadge ttk style layout omits the
            image element, so `image=`, `icon=`, `icon_only=`, and `compound=`
            are silently dropped at render time even though Label accepts them.

        Other Parameters:
            text: Text to display on the badge.
            anchor: Alignment of the badge content within its area.
            justify: How to justify multiple lines of text.
            localize: Determines the widget's localization mode.
            value_format: Format specification for the badge value.
            padding: Extra space around the badge content.
            width: Width of the badge in characters.
            wraplength: Maximum width before wrapping text.
            font: Font for the badge text.
            foreground: Text color.
            background: Background color.
            relief: Border style.
            state: Widget state.
            takefocus: Whether the widget participates in focus traversal.
            style: Explicit ttk style name (overrides accent/variant).
            accent: Accent token for styling, e.g. 'primary', 'success', 'danger'.
            variant: Shape of badge. 'pill' or 'square' (default).
            surface: Optional surface token; otherwise inherited.
            style_options: Optional dict forwarded to the style builder.
        """
        kwargs.setdefault('ttk_class', 'TBadge')
        kwargs.setdefault('anchor', 'center')
        kwargs.setdefault('font', '-size 8')
        kwargs.setdefault('variant', 'square')
        super().__init__(master=master, **kwargs)
