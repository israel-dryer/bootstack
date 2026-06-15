"""Separator widget style builders.

This module contains style builders for ttk.Separator widgets and variants.
"""

from __future__ import annotations

from bootstack.style.style_builder_ttk import StyleBuilderTtk
from bootstack.style.element import ElementImage, Element
from bootstack.style.utility import create_box_image


@StyleBuilderTtk.register_builder('default', 'TSeparator')
def build_separator_style(b: StyleBuilderTtk, ttk_style: str, accent: str = None, **options):
    accent_token = accent or 'border'
    surface_token = options.get('surface', 'content')
    orient = options.get('orient', 'horizontal')
    thickness = options.get('thickness', 1)
    length = options.get('length')  # None means stretch to fill

    # Default length for the image (will stretch if packed with fill)
    default_length = length or 40
    width, height = (default_length, thickness)
    if orient == 'vertical':
        width, height = (thickness, default_length)

    surface = b.color(surface_token)
    if accent_token == 'border':
        # `border_strength` (0..1) blends the stroke toward the surface's on-color;
        # higher = closer to the surface = quieter line. Omitted = the b.border
        # default. Lets callers (e.g. the shell dividers) soften the stroke.
        strength = options.get('border_strength')
        accent_color = b.border(surface) if strength is None else b.border(surface, strength)
    else:
        accent_color = b.color(accent_token)

    img = create_box_image(width, height, accent_color)
    sticky = "ew" if orient == "horizontal" else "ns"

    # When length is specified, set explicit dimensions to prevent stretching
    if length and orient == 'vertical':
        b.create_style_element_image(ElementImage(f"{ttk_style}.Separator", img, border=0, sticky=sticky, height=length))
    elif length and orient == 'horizontal':
        b.create_style_element_image(ElementImage(f"{ttk_style}.Separator", img, border=0, sticky=sticky, width=length))
    else:
        b.create_style_element_image(ElementImage(f"{ttk_style}.Separator", img, border=0, sticky=sticky))

    b.create_style_layout(ttk_style, Element(f"{ttk_style}.Separator", sticky=sticky))
    b.configure_style(ttk_style, background=surface)
