"""Switch widget style builders.

This module contains style builders for switch (toggle) variants of ttk.Checkbutton.
"""

from __future__ import annotations

from bootstack.style.bootstyle_builder_ttk import BootstyleBuilderTTk
from bootstack.style.element import Element, ElementImage
from bootstack.style.utility import create_transparent_image, mix_colors, recolor_element_image


@BootstyleBuilderTTk.register_builder('switch', 'TCheckbutton')
def build_switch_style(b: BootstyleBuilderTTk, ttk_style: str, accent: str = 'primary', **options):
    accent_token = accent or 'primary'
    surface_token = options.get('surface', 'content')

    background = b.color(surface_token)
    foreground = b.on_color(background)
    foreground_disabled = b.disabled('text', background)

    normal = b.color(accent_token)
    border = b.border(background)
    focus = b.focus(normal)
    focus_ring = b.color('foreground')

    # Disabled ON keeps a muted (faded) accent track so it still reads as "on",
    # mixed halfway toward the surface; OFF stays a neutral gray track.
    muted_accent = mix_colors(normal, background, 0.5)

    normal_checked_img = recolor_element_image('switch_on', normal, background, background, background)
    normal_unchecked_img = recolor_element_image('switch_off', border, background, background, background)

    focus_checked_img = recolor_element_image('switch_on', focus, background, focus_ring, background)
    focus_unchecked_img = recolor_element_image('switch_off', border, background, focus_ring, background)

    disabled_checked_img = recolor_element_image('switch_on', muted_accent, background, background, background)
    disabled_unchecked_img = recolor_element_image('switch_off', border, background, background, background)

    spacer_img = create_transparent_image(6, 1)
    b.create_style_element_image(ElementImage(f'{ttk_style}.spacer', spacer_img, sticky="ew"))

    b.create_style_element_image(
        ElementImage(f'{ttk_style}.indicator', normal_unchecked_img.image, sticky="ns").state_specs(
            [
                # Disabled states
                ('disabled selected', disabled_checked_img.image),
                ('disabled !selected !alternate', disabled_unchecked_img.image),

                # Focused states
                ('background focus selected', focus_checked_img.image),
                ('background focus !selected !alternate', focus_unchecked_img.image),

                # Normal base states
                ('selected', normal_checked_img.image),
                ('!selected !alternate', normal_unchecked_img.image),
            ]
        ))

    b.create_style_layout(
        ttk_style, Element('Checkbutton.padding', sticky="nsew").children(
            [
                Element(f'{ttk_style}.indicator', side="left", sticky=""),
                Element(f'{ttk_style}.spacer', side="left"),
                Element('Checkbutton.label', side="left", sticky="nsew")
            ])
    )

    b.configure_style(ttk_style, font="body")
    b.map_style(ttk_style, background=[('', background)], foreground=[('disabled', foreground_disabled), ('', foreground)])
