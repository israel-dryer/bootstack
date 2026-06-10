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
    Fill, Justify, Orient, Padding, Relief, Side, Sticky,
    LayoutKind, AutoFlow, AccordionVariant, Region, ButtonVariant,
    IconPosition, SelectionMode, ExportScope, ExportFormat,
    WidgetState, WidgetDensity,
    AccentToken, VariantToken, SurfaceToken, WindowStyle,
    ColumnSpec, EditorType, FormOptions,
)

__all__ = [
    "BaseWidgetKwargs", "StyledKwargs",
    "Anchor", "BorderMode", "CompoundMode", "Direction",
    "Fill", "Justify", "Orient", "Padding", "Relief", "Side", "Sticky",
    "LayoutKind", "AutoFlow", "AccordionVariant", "Region", "ButtonVariant",
    "IconPosition", "SelectionMode", "ExportScope", "ExportFormat",
    "WidgetState", "WidgetDensity",
    "AccentToken", "VariantToken", "SurfaceToken", "WindowStyle",
    "ColumnSpec", "EditorType", "FormOptions",
]
