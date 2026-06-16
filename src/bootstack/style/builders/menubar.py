"""Menubutton widget style builders.

This module contains style builders for ttk.Menubutton widgets and variants.
"""

from __future__ import annotations

from bootstack.style.style_builder_ttk import StyleBuilderTtk
from bootstack.style.element import Element, ElementImage
from bootstack.style.utility import recolor_element_image
from bootstack.style.builders.utils import (
    button_font,
    button_height,
    button_padding,
    normalize_button_density,
)


@StyleBuilderTtk.register_builder('menubar-item', 'TMenubutton')
@StyleBuilderTtk.register_builder('menubar-item', 'TButton')
def build_menubar_item(b: StyleBuilderTtk, ttk_style: str, color: str = None, **options):
    # Default to the base content surface (so a menu trigger blends into a
    # content-surfaced toolbar). The window menu bar passes surface='chrome'
    # explicitly, so the chrome strip is unaffected. Note `'content'` is dropped
    # before it reaches here, so a content toolbar arrives with no surface option
    # and lands on this default.
    surface_token = options.get('surface', 'content')
    # Follow the host toolbar's density (sizing the trigger image, padding, and
    # font like a button of the same density) so menu triggers match the buttons
    # beside them — rather than being locked to a single compact size.
    density = options.get('density', 'default')
    icon_only = options.get('icon_only', False)

    surface = b.color(surface_token)
    active = b.active(surface)
    pressed = b.pressed(surface)

    foreground_normal = b.on_color(surface)
    foreground_disabled = b.disabled('text', surface)

    # The menu-bar look is a flat button — the normal state paints the surface on
    # all four channels (no visible border); hover / pressed reveal the wash.
    image_key = f'button_{normalize_button_density(density)}'
    normal_img = recolor_element_image(image_key, surface, surface, surface, surface)
    pressed_img = recolor_element_image(image_key, pressed, pressed, surface, surface)
    active_img = recolor_element_image(image_key, active, active, surface, surface)

    # button element
    b.create_style_element_image(
        ElementImage(f'{ttk_style}.Button.border', normal_img.image, sticky="nsew",
                     border=normal_img.meta.border, padding=normal_img.meta.border,
                     height=button_height(b, density)).state_specs([
            ('background focus pressed', pressed_img.image),
            ('background focus hover', active_img.image),
            ('background focus', pressed_img.image),
            ('pressed', pressed_img.image),
            ('hover', active_img.image)
        ]))

    b.create_style_layout(
        ttk_style, Element(f"{ttk_style}.Button.border", sticky="nsew").children([
            Element("Button.padding", sticky="nsew").children([
                Element("Button.label", sticky="nsew")
            ])
        ]))

    b.configure_style(ttk_style, font=button_font(density), background=surface,
                      foreground=foreground_normal,
                      padding=button_padding(b, icon_only, density))

    state_spec = dict(
        foreground=[
            ('disabled', foreground_disabled),
            ('background focus', foreground_normal),
            ('', foreground_normal)
        ]
    )

    state_spec = _apply_icon_mapping(b, options, state_spec)
    b.map_style(ttk_style, **state_spec)


def _apply_icon_mapping(b: StyleBuilderTtk, options: dict, state_spec: dict) -> dict:
    """Apply icon mapping if an icon is provided in options."""
    icon = options.get('icon')
    if icon is None:
        return state_spec

    icon = b.normalize_icon_spec(icon, 20)
    state_spec['image'] = b.map_stateful_icons(icon, state_spec['foreground'])
    return state_spec
