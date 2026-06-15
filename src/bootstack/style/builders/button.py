"""Button widget style builders.

This module contains style builders for ttk.Button widgets and variants.
"""

from __future__ import annotations

from typing import Optional

from bootstack.style.style_builder_ttk import StyleBuilderTtk
from bootstack.style.element import ElementImage
from bootstack.style.utility import recolor_element_image
from bootstack.style.builders.utils import (
    apply_icon_mapping,
    button_font,
    button_height,
    button_layout,
    button_padding,
    icon_size,
    normalize_button_density,
)


@StyleBuilderTtk.register_builder('solid', 'TButton')
@StyleBuilderTtk.register_builder('default', 'TButton')
def build_solid_button_style(b: StyleBuilderTtk, ttk_style: str, accent: Optional[str] = None, **options):
    """
    Configure the button style.

    Style options include:
        * icon
        * icon_only
        * anchor
    """
    accent = b.default(accent)
    anchor = options.get('anchor', 'center')
    density = options.get('density', 'default')

    surface_token = options.get('surface', 'content')
    surface = b.color(surface_token)

    # background colors
    if accent is None:
        bg_normal = b.elevate(surface, 1)
    else:
        bg_normal = b.color(accent)

    bg_pressed = b.pressed(bg_normal)
    bg_active = focused = b.active(bg_normal)
    bg_disabled = b.disabled()

    # foreground colors
    fg_normal = b.on_color(bg_normal)
    fg_disabled = b.disabled('text', bg_disabled)

    # border colors
    bd_normal = b.border(bg_normal)
    bd_pressed = b.border(bg_pressed)
    bd_active = b.border(bg_active)
    bd_disabled = b.border(bg_disabled)

    focused_ring = b.color('foreground')

    icon_only = options.get('icon_only', False)
    image_key = f'button_{normalize_button_density(density)}'

    normal_img = recolor_element_image(image_key, bg_normal, bd_normal, surface, surface)
    pressed_img = recolor_element_image(image_key, bg_pressed, bd_pressed, surface, surface)
    hovered_img = recolor_element_image(image_key, bg_active, bd_active, surface, surface)
    focused_img = recolor_element_image(image_key, focused, focused, focused_ring, surface)
    focused_hovered_img = recolor_element_image(image_key, bd_active, focused, focused_ring, surface)
    focused_pressed_img = recolor_element_image(image_key, bd_pressed, focused, focused_ring, surface)
    disabled_img = recolor_element_image(image_key, bg_disabled, bd_disabled, surface, surface)


    b.create_style_element_image(
        ElementImage(
            f'{ttk_style}.Button.border',
            normal_img.image,
            sticky="nsew",
            border=normal_img.meta.border,
            padding=normal_img.meta.border,
            height=button_height(b, density),
        ).state_specs(
            [
                ('disabled', disabled_img.image),
                ('background focus pressed', focused_pressed_img.image),
                ('background focus hover', focused_hovered_img.image),
                ('background focus', focused_img.image),
                ('pressed', pressed_img.image),
                ('active', hovered_img.image),
            ]))

    b.create_style_layout(
        ttk_style,
        button_layout(ttk_style),
    )

    b.configure_style(
        ttk_style,
        stipple="gray12",
        padding=button_padding(b, icon_only, density),
        anchor=anchor,
        font=button_font(density)
    )

    state_spec = dict(
        foreground=[('disabled', fg_disabled), ('', fg_normal)],
        background=[('disabled', bg_disabled), ('', surface)]
    )
    state_spec = apply_icon_mapping(b, options, state_spec, icon_size(icon_only, density))

    b.map_style(ttk_style, **state_spec)


@StyleBuilderTtk.register_builder('outline', 'TButton')
def build_outline_button_style(b: StyleBuilderTtk, ttk_style: str, accent: str = None, **options):
    """
    Configure the outline button style.

    Style options include:
        * icon
        * icon_only
        * anchor
    """
    accent = b.default(accent)
    anchor = options.get('anchor', 'center')
    icon_only = options.get('icon_only', False)
    density = options.get('density', 'default')
    image_key = f'button_{normalize_button_density(density)}'

    surface_token = options.get('surface', 'content')
    surface = b.color(surface_token)

    accent_color = b.elevate(surface, 1) if accent is None else b.color(accent)

    # background colors
    bg_normal = surface
    bg_active = accent_color
    bg_pressed = b.active(accent_color)
    bg_focus_ring = b.color('foreground')
    bg_disabled = b.disabled('text', surface)

    # foreground colors
    if accent is None:
        fg_normal = b.on_color(bg_normal)
    else:
        fg_normal = accent_color

    fg_disabled = b.disabled('text', surface)
    fg_active = b.on_color(bg_normal if accent is None else accent_color)

    # border colors
    bd_normal = b.border(bg_normal) if accent is None else fg_normal
    bd_active = b.border(bg_active)
    bd_pressed = b.border(bg_pressed)

    # button element images
    normal_img = recolor_element_image(image_key, surface, bd_normal, surface, surface)
    pressed_img = recolor_element_image(image_key, bg_pressed, bd_pressed, surface, surface)
    active_img = recolor_element_image(image_key, bg_active, bd_active, surface, surface)
    focused_img = recolor_element_image(image_key, surface, bd_active, bg_focus_ring, surface)
    focused_active_img = recolor_element_image(image_key, bg_active, bd_active, bg_focus_ring, surface)
    focused_pressed_img = recolor_element_image(image_key, bg_pressed, bd_pressed, bg_focus_ring, surface)
    disabled_img = recolor_element_image(image_key, surface, bg_disabled, surface, surface)

    b.create_style_element_image(
        ElementImage(
            f'{ttk_style}.Button.border',
            normal_img.image,
            sticky="nsew",
            border=normal_img.meta.border,
            padding=normal_img.meta.border,
            height=button_height(b, density),
        ).state_specs(
            [
                ('disabled', disabled_img.image),
                ('background focus pressed', focused_pressed_img.image),
                ('background focus active', focused_active_img.image),
                ('background focus', focused_img.image),
                ('pressed', pressed_img.image),
                ('active', active_img.image),
            ])
    )

    b.create_style_layout(
        ttk_style,
        button_layout(ttk_style),
    )

    padding = button_padding(b, icon_only, density)

    b.configure_style(
        ttk_style,
        stipple="gray12",
        anchor=anchor,
        padding=padding,
        font=button_font(density)
    )

    state_spec = dict(
        foreground=[
            ('disabled', fg_disabled),
            ('background focus pressed', fg_active),
            ('background focus active', fg_active),
            ('hover', fg_active),
            ('', fg_normal)
        ], background=[('disabled', surface), ('', surface)]
    )

    state_spec = apply_icon_mapping(b, options, state_spec, icon_size(icon_only, density))

    b.map_style(ttk_style, **state_spec)


@StyleBuilderTtk.register_builder('ghost', 'TButton')
def build_ghost_button_style(b: StyleBuilderTtk, ttk_style: str, accent: str = None, **options):
    """
    Configure the ghost button style.

    Style options include:
        * icon
        * icon_only
        * anchor
    """
    accent = b.default(accent)
    anchor = options.get('anchor', 'center')
    surface_token = options.get('surface', 'content')
    density = options.get('density', 'default')
    icon_only = options.get('icon_only', False)
    image_key = f'button_{normalize_button_density(density)}'

    surface = b.color(surface_token)

    # background colors
    bg_normal = surface
    bg_active = bg_focused = b.elevate(surface, 1) if accent is None else b.subtle(accent, surface)
    bg_pressed = b.active(bg_active)
    focused_ring = b.color('foreground')

    # foreground colors
    fg_normal = b.on_color(bg_normal) if accent is None else b.color(accent)
    fg_disabled = b.disabled('text', surface)

    # button element images
    normal_img = recolor_element_image(image_key, bg_normal, bg_normal, surface, surface)
    pressed_img = recolor_element_image(image_key, bg_pressed, bg_pressed, surface, surface)
    active_img = recolor_element_image(image_key, bg_active, bg_active, surface, surface)
    focused_img = recolor_element_image(image_key, bg_focused, bg_focused, focused_ring, surface)
    focused_active_img = recolor_element_image(image_key, bg_focused, bg_focused, focused_ring, surface)
    focused_pressed_img = recolor_element_image(image_key, bg_pressed, bg_pressed, focused_ring, surface)
    disabled_img = recolor_element_image(image_key, surface, surface, surface, surface)

    b.create_style_element_image(
        ElementImage(
            f'{ttk_style}.Button.border', normal_img.image, sticky="nsew",
            border=normal_img.meta.border, padding=normal_img.meta.border,
            height=button_height(b, density)).state_specs(
            [
                ('disabled', disabled_img.image),
                ('background focus pressed', focused_pressed_img.image),
                ('background focus hover', focused_active_img.image),
                ('background focus', focused_img.image),
                ('pressed !disabled', pressed_img.image),
                ('active !disabled', active_img.image),
            ])
    )

    b.create_style_layout(
        ttk_style,
        button_layout(ttk_style),
    )

    b.configure_style(
        ttk_style,
        stipple="gray12",
        padding=button_padding(b, icon_only, density),
        anchor=anchor,
        font=button_font(density)
    )

    state_spec = dict(
        foreground=[('disabled', fg_disabled), ('', fg_normal)],
        background=[('disabled', surface), ('', surface)]
    )

    state_spec = apply_icon_mapping(b, options, state_spec, icon_size(icon_only, density))

    b.map_style(ttk_style, **state_spec)


@StyleBuilderTtk.register_builder('selectbox_item', 'TButton')
def build_selectbox_item_button_style(b: StyleBuilderTtk, ttk_style: str, accent: str = None, **options):
    """Configure the style for selectbox dropdown items with selected state support.

    Style options include:
        * icon
        * icon_only
        * anchor
    """
    anchor = options.get('anchor', 'w')
    accent_token = accent or 'primary'
    surface_token = options.get('surface', 'content')

    surface = b.color(surface_token)
    on_surface = b.on_color(surface)
    on_disabled = b.disabled('text', surface)

    active = b.elevate(surface, 1)
    selected = b.color(accent_token)
    on_selected = b.on_color(selected)

    b.configure_style(
        ttk_style,
        background=surface,
        foreground=on_surface,
        relief='flat',
        stipple='gray12',
        padding=(6, 3),
        anchor=anchor,
        font='body',
        focuscolor=''
    )

    state_spec = dict(
        foreground=[
            ('disabled', on_disabled),
            ('selected !disabled', on_selected),
            ('pressed', on_selected),
            ('', on_surface)],
        background=[
            ('selected !disabled', selected),
            ('pressed !disabled', selected),
            ('active !disabled', active),
            ('', surface)
        ]
    )

    b.map_style(ttk_style, **state_spec)
