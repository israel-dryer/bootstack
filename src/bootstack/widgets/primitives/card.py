from __future__ import annotations

from typing import Any, TypedDict

from typing_extensions import Unpack

from bootstack.widgets.primitives.frame import Frame
from bootstack.widgets.types import Master


class CardKwargs(TypedDict, total=False):
    # Standard ttk.Frame options
    padding: Any
    width: int
    height: int
    style: str
    cursor: str
    name: str
    takefocus: bool
    class_: str

    # bootstack-specific extensions
    accent: str
    variant: str
    surface: str
    show_border: bool
    style_options: dict[str, Any]


class Card(Frame):
    """A convenience wrapper for Frame with card styling.

    Card is a Frame with `surface='card'` and `show_border=True` by default,
    providing an elevated container with a visible border for grouping content.

    """

    def __init__(self, master: Master = None, **kwargs: Unpack[CardKwargs]) -> None:
        """Create a themed Card container.

        Args:
            master: Parent widget. If None, uses the default root window.

        Other Parameters:
            padding: Extra padding inside the card. Default 16.
            width: Requested width in pixels.
            height: Requested height in pixels.
            takefocus: Widget accepts focus during keyboard traversal.
            style: Explicit ttk style name (overrides accent/variant).
            accent: Accent/color token for the card. Default 'card'.
            variant: Style variant (if applicable).
            surface: Surface token for the parent background.
            show_border: Draw a border around the card. Default True.
            style_options: Optional dict forwarded to the style builder.
        """
        kwargs.setdefault('accent', 'card')
        kwargs.setdefault('show_border', True)
        kwargs.setdefault('padding', 16)
        super().__init__(master, **kwargs)
