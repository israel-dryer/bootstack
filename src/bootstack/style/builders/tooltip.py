from __future__ import annotations

from bootstack.style.style_builder_ttk import StyleBuilderTtk
from bootstack.style.element import Element


@StyleBuilderTtk.register_builder('tooltip', 'TFrame')
def build_tooltip_frame(b: StyleBuilderTtk, ttk_style: str, accent: str = None, **options):
    surface_token = options.get('surface') or accent or "background"
    if accent:
        background = b.color(accent)
    else:
        background = b.color(surface_token)

    border_color = b.border(background)

    b.create_style_layout(ttk_style, Element(f'{ttk_style}.Frame.border', sticky="nsew"))

    b.configure_style(
        ttk_style,
        background=background,
        border_color=border_color,
        darkcolor=background,
        lightcolor=background,
        relief='flat',
        )
