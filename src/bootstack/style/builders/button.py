"""Button widget style builders.

This module contains style builders for ttk.Button widgets and variants.
"""

from __future__ import annotations

from bootstack.style.bootstyle_builder_ttk import BootstyleBuilderTTk
from bootstack.style.element import ElementImage
from bootstack.style.utility import recolor_element_image
from bootstack.style.builders.utils import (
    apply_icon_mapping,
    button_font,
    button_layout,
    button_padding,
    icon_size,
    normalize_button_density,
)


@BootstyleBuilderTTk.register_builder('solid', 'TButton')
@BootstyleBuilderTTk.register_builder('default', 'TButton')
def build_solid_button_style(b: BootstyleBuilderTTk, ttk_style: str, accent: str = None, **options):
    """
    Configure the button style.

    Style options include:
        * icon
        * icon_only
        * anchor
    """
    anchor = options.get('anchor', 'center')
    accent_token = accent or 'primary'
    surface_token = options.get('surface', 'content')
    density = options.get('density', 'default')

    surface = b.color(surface_token)
    normal = b.color(accent_token)
    foreground = b.on_color(normal)
    pressed = b.pressed(normal)
    hovered = focused = b.active(normal)
    disabled = b.disabled()
    focused_ring = b.color('foreground')
    foreground_disabled = b.disabled('text', disabled)

    icon_only = options.get('icon_only', False)
    image_key = f'button_{normalize_button_density(density)}'

    normal_img = recolor_element_image(image_key, normal, normal, surface, surface)
    pressed_img = recolor_element_image(image_key, pressed, pressed, surface, surface)
    hovered_img = recolor_element_image(image_key, hovered, hovered, surface, surface)
    focused_img = recolor_element_image(image_key, focused, focused, focused_ring, surface)
    focused_hovered_img = recolor_element_image(image_key, hovered, focused, focused_ring, surface)
    focused_pressed_img = recolor_element_image(image_key, pressed, focused, focused_ring, surface)
    disabled_img = recolor_element_image(image_key, disabled, disabled, surface, surface)


    b.create_style_element_image(
        ElementImage(
            f'{ttk_style}.Button.border',
            normal_img.image,
            sticky="nsew",
            border=normal_img.meta.border,
            padding=normal_img.meta.border
        ).state_specs(
            [
                ('disabled', disabled_img.image),
                ('background focus pressed', focused_pressed_img.image),
                ('background focus hover', focused_hovered_img.image),
                ('background focus', focused_img.image),
                ('pressed', pressed_img.image),
                ('hover', hovered_img.image),
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
        foreground=[('disabled', foreground_disabled), ('', foreground)],
        background=[('disabled', disabled), ('', surface)]
    )
    state_spec = apply_icon_mapping(b, options, state_spec, icon_size(icon_only, density))

    b.map_style(ttk_style, **state_spec)


@BootstyleBuilderTTk.register_builder('outline', 'TButton')
def build_outline_button_style(b: BootstyleBuilderTTk, ttk_style: str, accent: str = None, **options):
    """
    Configure the outline button style.

    Style options include:
        * icon
        * icon_only
        * anchor
    """
    anchor = options.get('anchor', 'center')
    accent_token = accent or 'primary'
    surface_token = options.get('surface', 'content')
    density = options.get('density', 'default')
    icon_only = options.get('icon_only', False)
    image_key = f'button_{normalize_button_density(density)}'

    surface = b.color(surface_token)

    foreground_normal = b.color(accent_token)
    foreground_disabled = b.disabled('text', surface)
    foreground_active = b.on_color(foreground_normal)

    disabled = foreground_disabled
    normal = surface
    active = foreground_normal
    pressed = b.active(foreground_normal)
    focused = b.focus(foreground_normal)
    focused_ring = b.color('foreground')



    # button element images
    normal_img = recolor_element_image(image_key, normal, foreground_normal, surface, surface)
    pressed_img = recolor_element_image(image_key, pressed, pressed, surface, surface)
    active_img = recolor_element_image(image_key, active, active, surface, surface)
    focused_img = recolor_element_image(image_key, focused, focused, focused_ring, surface)
    focused_active_img = recolor_element_image(image_key, active, active, focused_ring, surface)
    focused_pressed_img = recolor_element_image(image_key, pressed, pressed, focused_ring, surface)
    disabled_img = recolor_element_image(image_key, surface, disabled, surface, surface)

    b.create_style_element_image(
        ElementImage(
            f'{ttk_style}.Button.border',
            normal_img.image,
            sticky="nsew",
            border=normal_img.meta.border,
            padding=normal_img.meta.border
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
            ('disabled', foreground_disabled),
            ('background focus', foreground_active),
            ('hover', foreground_active),
            ('', foreground_normal)
        ], background=[('disabled', surface), ('', surface)]
    )

    state_spec = apply_icon_mapping(b, options, state_spec, icon_size(icon_only, density))

    b.map_style(ttk_style, **state_spec)


@BootstyleBuilderTTk.register_builder('link', 'TButton')
def build_link_button_style(b: BootstyleBuilderTTk, ttk_style: str, accent: str = None, **options):
    """
    Configure the link button style.

    Style options include:
        * icon
        * icon_only
        * anchor
    """
    anchor = options.get('anchor', 'center')
    accent_token = accent or 'primary'
    surface_token = options.get('surface', 'content')
    density = options.get('density', 'default')
    icon_only = options.get('icon_only', False)
    image_key = f'button_{normalize_button_density(density)}'

    surface = b.color(surface_token)
    focus_ring = b.color('foreground')
    foreground_normal = b.color(accent_token)
    foreground_active = b.active(foreground_normal)
    foreground_pressed = b.pressed(foreground_normal)
    foreground_disabled = b.disabled('text', surface)

    # button element images - all transparent for link style
    normal_img = recolor_element_image(image_key, surface, surface, surface, surface)
    focused_img = recolor_element_image(image_key, surface, surface, focus_ring, surface)
    disabled_img = recolor_element_image(image_key, surface, surface, surface, surface)

    b.create_style_element_image(
        ElementImage(
            f'{ttk_style}.Button.border', normal_img.image, sticky="nsew",
            border=normal_img.meta.border, padding=normal_img.meta.border).state_specs(
            [
                ('disabled', disabled_img.image),
                ('background focus', focused_img.image),
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
        font=[
            ("active !disabled", "hyperlink"),
            ("background focus !disabled", "hyperlink"),
            ("", button_font(density))],
        cursor=[('', 'hand2')],
        foreground=[
            ('disabled', foreground_disabled),
            ('pressed !disabled', foreground_pressed),
            ('active !disabled', foreground_active),
            ('', foreground_normal)
        ], background=[('disabled', surface), ('', surface)]
    )

    state_spec = apply_icon_mapping(b, options, state_spec, icon_size(icon_only, density))

    b.map_style(ttk_style, **state_spec)


@BootstyleBuilderTTk.register_builder('ghost', 'TButton')
def build_ghost_button_style(b: BootstyleBuilderTTk, ttk_style: str, accent: str = None, **options):
    """
    Configure the ghost button style.

    Style options include:
        * icon
        * icon_only
        * anchor
    """
    anchor = options.get('anchor', 'center')
    accent_token = accent or 'secondary'
    surface_token = options.get('surface', 'content')
    density = options.get('density', 'default')
    icon_only = options.get('icon_only', False)
    image_key = f'button_{normalize_button_density(density)}'

    surface = b.color(surface_token)

    accent_color = b.color(accent_token)
    normal = surface
    active = b.subtle(accent_token, surface)
    focused = b.focus(active)
    pressed = b.pressed(active)
    focused_ring = b.color('foreground')

    foreground_normal = accent_color if accent else b.on_color(surface)
    foreground_disabled = b.disabled('text', surface)

    # button element images
    normal_img = recolor_element_image(image_key, normal, normal, surface, surface)
    pressed_img = recolor_element_image(image_key, pressed, pressed, surface, surface)
    active_img = recolor_element_image(image_key, active, active, surface, surface)
    focused_img = recolor_element_image(image_key, focused, focused, focused_ring, surface)
    focused_active_img = recolor_element_image(image_key, focused, focused, focused_ring, surface)
    focused_pressed_img = recolor_element_image(image_key, pressed, pressed, focused_ring, surface)
    disabled_img = recolor_element_image(image_key, surface, surface, surface, surface)

    b.create_style_element_image(
        ElementImage(
            f'{ttk_style}.Button.border', normal_img.image, sticky="nsew",
            border=normal_img.meta.border, padding=normal_img.meta.border).state_specs(
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
        foreground=[('disabled', foreground_disabled), ('', foreground_normal)],
        background=[('disabled', surface), ('', surface)]
    )

    state_spec = apply_icon_mapping(b, options, state_spec, icon_size(icon_only, density))

    b.map_style(ttk_style, **state_spec)


@BootstyleBuilderTTk.register_builder('selectbox_item', 'TButton')
def build_selectbox_item_button_style(b: BootstyleBuilderTTk, ttk_style: str, accent: str = None, **options):
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
