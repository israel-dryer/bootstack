"""Public type aliases and token Literals for annotating bootstack code.

These are the names used in widget signatures — accent/variant/surface tokens,
layout Literals, density, and the keyword TypedDicts. Import them when you
annotate your own helpers or widget subclasses::

    from bootstack.types import AccentToken, WidgetDensity

They are re-exported from :mod:`bootstack.widgets.types`.
"""
from bootstack.widgets.types import (
    BaseWidgetKwargs, StyledKwargs,
    Anchor, BorderMode, CompoundMode, Direction,
    Fill, Justify, Orient, Relief, Side, Sticky,
    WidgetState, WidgetDensity,
    AccentToken, VariantToken, SurfaceToken,
)

__all__ = [
    "BaseWidgetKwargs", "StyledKwargs",
    "Anchor", "BorderMode", "CompoundMode", "Direction",
    "Fill", "Justify", "Orient", "Relief", "Side", "Sticky",
    "WidgetState", "WidgetDensity",
    "AccentToken", "VariantToken", "SurfaceToken",
]
