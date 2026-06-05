"""Labelframe widget style builders.

This module contains style builders for ttk.Labelframe widget and variants.

The Labelframe color is different than the normal frame in that the background color of the
labelframe is inherited only unless overridden explicitly by the surface option. The
bootstyle color is only relevant for the border color of the labelframe.
"""

from __future__ import annotations

from bootstack.style.bootstyle_builder_ttk import BootstyleBuilderTTk


@BootstyleBuilderTTk.register_builder('default', 'TLabelframe')
def build_labelframe_style(b: BootstyleBuilderTTk, ttk_style: str, accent: str = None, **options):
    accent_token = b.default(accent)
    surface_token = options.get('surface') or 'background'
    show_border = options.get('show_border', True)
    surface = b.color(surface_token)

    border = b.border(surface if accent_token is None else b.color(accent_token))
    foreground = b.on_color(surface)

    b.configure_style(f'{ttk_style}.Label', background=surface, foreground=foreground, font="label")
    b.configure_style(
        ttk_style,
        background=surface,
        borderwidth=1 if show_border else 0,
        bordercolor=border if show_border else surface,
        darkcolor=surface,
        lightcolor=surface,
        relief='raised' if show_border else 'flat'
    )
