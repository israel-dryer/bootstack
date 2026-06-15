"""Badge style builders.

This module contains style builders for ttk.Label widget badge variants.
"""
from typing import Optional

from bootstack.style.style_builder_ttk import StyleBuilderTtk
from bootstack.style.element import Element, ElementImage
from bootstack.style.utility import recolor_element_image


@StyleBuilderTtk.register_builder('square', 'TBadge')
def build_default_badge_style(b: StyleBuilderTtk, ttk_style: str, accent: Optional[str] = None, **options):
    build_badge(b, ttk_style, accent, 'square', **options)

@StyleBuilderTtk.register_builder('pill', 'TBadge')
def build_pill_badge_style(b: StyleBuilderTtk, ttk_style: str, accent: Optional[str] = None, **options):
    build_badge(b, ttk_style, accent, 'pill', **options)


def build_badge(b: StyleBuilderTtk, ttk_style: str, accent: Optional[str] = None, variant: str = 'square', **options):
    """Create a badge style for the variant specified"""

    surface_token = options.get('surface', 'content')
    surface = b.color(surface_token)
    normal = b.color(accent or 'primary')
    foreground = b.on_color(normal)

    badge_img = recolor_element_image(f'badge_{variant}', normal, normal, surface, surface)

    b.create_style_element_image(ElementImage(f'{ttk_style}.border', badge_img.image, 
                                              border=badge_img.meta.border, 
                                              padding=badge_img.meta.padding, 
                                              height=badge_img.meta.height,
                                              sticky='nsew'))

    b.create_style_layout(
        ttk_style, Element(f"{ttk_style}.border", sticky="nsew").children(
            [
                Element("Label.padding", sticky="nsew").children(
                    [
                        Element("Label.label", sticky="ew")
                    ])
            ]))
    
    b.configure_style(ttk_style, background=surface, foreground=foreground, padding=(6, 0))
