from __future__ import annotations

from typing import Optional

from bootstack.style.bootstyle_builder_ttk import BootstyleBuilderTTk
from bootstack.style.element import Element, ElementImage
from bootstack.style.utility import recolor_element_image


@BootstyleBuilderTTk.register_builder('default', 'TFrame')
def build_frame(b: BootstyleBuilderTTk, ttk_style: str, _: Optional[str] = None, **options):
    surface_token = options.get('surface') or 'background'
    show_border = options.get('show_border', False)
    surface = b.color(surface_token)
    stroke = b.border(surface) if show_border else surface

    b.configure_style(
        ttk_style,
        background=surface,
        relief='raised',
        bordercolor=stroke,
        darkcolor=surface,
        lightcolor=surface,
    )



@BootstyleBuilderTTk.register_builder('card', 'TFrame')
def build_card(b: BootstyleBuilderTTk, ttk_style: str, _: Optional[str] = None, **options):
    surface_token = options.get('surface') or 'background'
    show_border = options.get('show_border', False)
    surface = b.color(surface_token)
    stroke = b.border(surface)

    b.configure_style(
        ttk_style,
        background=surface,
        bordercolor=stroke,
        darkcolor=surface,
        lightcolor=surface,
        relief='raised' if show_border else 'flat',
    )