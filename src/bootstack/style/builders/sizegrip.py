"""Sizegrip widget style builders.

This module contains style builders for ttk.Sizegrip and variants.
"""

from __future__ import annotations

from bootstack.style.style_builder_ttk import StyleBuilderTtk


@StyleBuilderTtk.register_builder('default', 'TSizegrip')
def build_sizegrip_style(b: StyleBuilderTtk, ttk_style: str, accent: str = None, **options):
    surface_token = options.get('surface', 'content')
    surface = b.color(surface_token)
    b.configure_style(ttk_style, background=surface)
