"""Toolbutton widget style builders.

This module contains style builders for ttk.Checkbutton and Radiobutton toolbutton variants.
"""

from __future__ import annotations

from typing import Optional

from bootstack.style.bootstyle_builder_ttk import BootstyleBuilderTTk
from bootstack.style.element import ElementImage
from bootstack.style.utility import recolor_element_image
from bootstack.style.builders.utils import (
    apply_icon_mapping,
    button_font,
    button_padding,
    icon_size,
    normalize_button_density,
    toolbutton_layout,
)


# The active styles are intentionally limited on toolbuttons to improve interaction
# and limit the number of images created for each style.


@BootstyleBuilderTTk.register_builder('default', 'Toolbutton')
@BootstyleBuilderTTk.register_builder('solid', 'Toolbutton')
def build_solid_toolbutton_style(b: BootstyleBuilderTTk, ttk_style: str, accent: Optional[str] = None, **options):
    """
    Configure the solid toolbutton style.

    Style options include:
        * anchor
        * icon
        * icon_only
        * density
    """
    accent = b.default(accent)
    anchor = options.get('anchor', 'center')
    surface_token = options.get('surface', 'content')
    density = options.get('density', 'default')
    surface = b.color(surface_token)
    accent_color = b.elevate(surface, 1) if accent is None else b.color(accent)
    icon_only = options.get('icon_only', False)
    image_key = f'button_{normalize_button_density(density)}'

    bg_normal = b.elevate(surface, 1)

    # background colors
    bg_active = b.active(accent_color)
    bg_selected = accent_color if accent is not None else b.elevate(surface, 2)
    bg_disabled = b.disabled()

    # foreground colors
    fg_normal = b.muted_foreground(bg_normal)
    fg_selected = b.on_color(bg_selected)
    fg_disabled = b.disabled('text', bg_disabled)

    # border colors
    bd_normal = b.border(bg_normal)
    bd_active = b.border(bg_active)
    bd_selected = b.border(bg_selected)
    bd_disabled = b.border(bg_disabled)

    # focus
    accent_focus = b.focus(accent_color)
    focus_ring = b.focus_ring(accent_focus, surface)

    normal_img = recolor_element_image(image_key, bg_normal, bd_normal, surface, surface)
    normal_focus_img = recolor_element_image(image_key, bg_normal, bd_normal, focus_ring, surface)
    active_img = recolor_element_image(image_key, bg_active, bd_active, surface, surface)
    selected_img = recolor_element_image(image_key, bg_selected, bd_selected, surface, surface)
    selected_focus_img = recolor_element_image(image_key, bg_selected, bd_selected, focus_ring, surface)
    disabled_img = recolor_element_image(image_key, bg_disabled, bd_disabled, surface, surface)

    b.create_style_element_image(
        ElementImage(
            f'{ttk_style}.border', normal_img.image, sticky="nsew",
            border=normal_img.meta.border, padding=normal_img.meta.border
        ).state_specs([
            ('disabled', disabled_img.image),
            ('background pressed focus selected', selected_focus_img.image),
            ('background focus selected', selected_focus_img.image),
            ('selected', selected_img.image),
            ('background focus !selected', normal_focus_img.image),
            ('background active !focus', active_img.image),
            ('', normal_img.image)
        ]))

    b.create_style_layout(ttk_style, toolbutton_layout(ttk_style))

    b.configure_style(
        ttk_style,
        background=surface,
        foreground=fg_normal,
        stipple="gray12",
        relief='flat',
        padding=button_padding(b, icon_only, density),
        anchor=anchor,
        font=button_font(density)
    )

    state_spec = dict(
        foreground=[
            ('disabled', fg_disabled),
            ('selected', fg_selected),
            ('', fg_normal)
        ]
    )
    state_spec = apply_icon_mapping(b, options, state_spec, icon_size(icon_only, density))
    b.map_style(ttk_style, **state_spec)


@BootstyleBuilderTTk.register_builder('outline', 'Toolbutton')
def build_outline_toolbutton_style(b: BootstyleBuilderTTk, ttk_style: str, accent: Optional[str] = None, **options):
    """
    Configure the outline toolbutton style.

    Style options include:
        * anchor
        * icon
        * icon_only
        * density
    """
    accent = b.default(accent)
    anchor = options.get('anchor', 'center')
    surface_token = options.get('surface', 'content')
    density = options.get('density', 'default')
    icon_only = options.get('icon_only', False)
    image_key = f'button_{normalize_button_density(density)}'

    surface = b.color(surface_token)
    accent_color = b.elevate(surface, 1) if accent is None else b.color(accent)

    # background colors
    bg_normal = surface
    bg_selected = accent_color
    bg_disabled = b.disabled()

    # foreground colors
    fg_normal = b.on_color(bg_normal) if accent is None else accent_color
    fg_selected = b.on_color(bg_selected)
    fg_disabled = b.disabled('text', bg_disabled)

    # border colors
    bd_normal = b.border(bg_normal) if accent is None else accent_color
    bd_selected = b.border(bg_selected)
    bd_disabled = b.border(bg_disabled)

    # focus
    accent_focus = b.focus(accent_color)
    focus_ring = b.focus_ring(accent_focus, surface)

    normal_img = recolor_element_image(image_key, surface, bd_normal, surface, surface)
    normal_focus_img = recolor_element_image(image_key, surface, bd_normal, focus_ring, surface)
    selected_img = recolor_element_image(image_key, bg_selected, bd_selected, surface, surface)
    selected_focus_img = recolor_element_image(image_key, bg_selected, bd_selected, focus_ring, surface)
    disabled_img = recolor_element_image(image_key, bg_disabled, bd_disabled, surface, surface)

    b.create_style_element_image(
        ElementImage(
            f'{ttk_style}.border', normal_img.image, sticky="nsew",
            border=normal_img.meta.border, padding=normal_img.meta.border
        ).state_specs([
            ('disabled', disabled_img.image),
            ('background pressed selected focus', selected_focus_img.image),
            ('pressed', selected_img.image),
            ('background selected focus', selected_focus_img.image),
            ('selected', selected_img.image),
            ('background focus !selected', normal_focus_img.image),
            ('', normal_img.image)
        ]))

    b.create_style_layout(ttk_style, toolbutton_layout(ttk_style))

    b.configure_style(
        ttk_style,
        background=surface,
        foreground=fg_normal,
        stipple="gray12",
        relief='flat',
        padding=button_padding(b, icon_only, density),
        anchor=anchor,
        font=button_font(density)
    )

    state_spec = dict(
        foreground=[
            ('disabled', fg_disabled),
            ('selected !disabled', fg_selected),
            ('pressed !disabled', fg_selected),
            ('', fg_normal)
        ]
    )
    state_spec = apply_icon_mapping(b, options, state_spec, icon_size(icon_only, density))
    b.map_style(ttk_style, **state_spec)


@BootstyleBuilderTTk.register_builder('ghost', 'Toolbutton')
def build_ghost_toolbutton_style(b: BootstyleBuilderTTk, ttk_style: str, accent: Optional[str] = None, **options):
    """
    Configure the ghost toolbutton style.

    Style options include:
        * anchor
        * icon
        * icon_only
        * density
    """
    accent = b.default(accent)
    anchor = options.get('anchor', 'center')
    surface_token = options.get('surface', 'content')
    density = options.get('density', 'default')
    icon_only = options.get('icon_only', False)
    image_key = f'button_{normalize_button_density(density)}'

    surface = b.color(surface_token)
    accent_color = b.elevate(surface, 1) if accent is None else b.color(accent)

    # background colors
    bg_normal = surface
    bg_selected = b.elevate(surface, 2) if accent is None else b.subtle(accent, surface)
    bg_disabled = b.disabled()

    # foreground colors
    fg_normal = b.muted_foreground(bg_normal)
    fg_selected = b.on_color(bg_selected) if accent is None else b.color(accent)
    fg_disabled = b.disabled('text', bg_disabled)

    # focus
    accent_focus = b.focus(accent_color)
    focus_ring = b.focus_ring(accent_focus, surface)

    normal_img = recolor_element_image(image_key, bg_normal, bg_normal, surface, surface)
    normal_focus_img = recolor_element_image(image_key, bg_normal, accent_color, focus_ring, surface)
    selected_img = recolor_element_image(image_key, bg_selected, bg_selected, surface, surface)
    selected_focus_img = recolor_element_image(image_key, bg_selected, accent_focus, focus_ring, surface)
    disabled_img = recolor_element_image(image_key, bg_disabled, bg_disabled, surface, surface)

    b.create_style_element_image(
        ElementImage(
            f'{ttk_style}.border', normal_img.image, sticky="nsew",
            border=normal_img.meta.border, padding=normal_img.meta.border
        ).state_specs([
            ('disabled', disabled_img.image),
            ('background pressed selected focus', selected_focus_img.image),
            ('background selected focus', selected_focus_img.image),
            ('selected', selected_img.image),
            ('background focus !selected', normal_focus_img.image),
            ('', normal_img.image)
        ]))

    b.create_style_layout(ttk_style, toolbutton_layout(ttk_style))

    b.configure_style(
        ttk_style,
        background=surface,
        foreground=fg_normal,
        stipple="gray12",
        relief='flat',
        padding=button_padding(b, icon_only, density),
        anchor=anchor,
        font=button_font(density)
    )

    state_spec = dict(
        foreground=[
            ('disabled', fg_disabled),
            ('selected', fg_selected),
            ('', fg_normal)
        ]
    )
    state_spec = apply_icon_mapping(b, options, state_spec, icon_size(icon_only, density))
    b.map_style(ttk_style, **state_spec)