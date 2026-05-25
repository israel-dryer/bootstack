"""ButtonGroup widget style builders."""

from __future__ import annotations

from typing import Optional

from bootstack.style.bootstyle_builder_ttk import BootstyleBuilderTTk
from bootstack.style.builders.utils import button_padding, apply_icon_mapping, icon_size, button_font
from bootstack.style.element import Element, ElementImage
from bootstack.style.utility import recolor_element_image


def _toolbutton_layout(ttk_style: str) -> Element:
    return Element(f"{ttk_style}.border", sticky="nsew").children(
        [
            Element("Toolbutton.padding", sticky="nsew").children(
                [
                    Element("Toolbutton.label", sticky="nsew")
                ])
        ])


@BootstyleBuilderTTk.register_builder('solid', 'ButtonGroup')
@BootstyleBuilderTTk.register_builder('default', 'ButtonGroup')
def build_button_group_style(b: BootstyleBuilderTTk, ttk_style: str, accent: Optional[str] = None, **options):
    """
    Configure the button style.

    Style options include:
        * icon_only
        * position
        * orientation
        * active_state
        * density
    """
    accent = b.default(accent)
    surface_token = options.get('surface', 'content')
    orient = options.get('orient', 'horizontal')
    position = options.get('position', 'before')
    density = options.get('density', 'default')
    icon_only = options.get('icon_only', False)
    active_state = options.get('active_state', False)
    image_key = f'button_group_{orient}_{position}_{density}'

    surface = b.color(surface_token)
    accent_color = b.elevate(surface, 1) if accent is None else b.color(accent)

    # background colors
    bg_normal = accent_color
    bg_selected = b.selected(accent_color)
    bg_active = b.active(accent_color)
    bg_pressed = b.pressed(accent_color)
    bg_disabled = b.disabled()

    # foreground colors
    fg_selected = b.on_color(bg_selected)
    fg_normal = b.on_color(accent_color)
    fg_disabled = b.disabled('text', bg_disabled)

    # border colors
    bd_normal = b.border(bg_normal)
    bd_active = b.border(bg_active)
    bd_pressed = b.border(bg_pressed)
    bd_selected = b.border(bg_selected)
    bd_disabled = b.border(bg_disabled)

    normal_img = recolor_element_image(image_key, bg_normal, bd_normal, surface, surface)
    active_img = recolor_element_image(image_key, bg_active, bd_active, surface, surface)
    pressed_img = recolor_element_image(image_key, bg_pressed, bd_pressed, surface, surface)
    selected_img = recolor_element_image(image_key, bg_selected, bd_selected, surface, surface)
    disabled_img = recolor_element_image(image_key, bg_disabled, bd_disabled, surface, bg_disabled)

    if active_state:
        b.create_style_element_image(
            ElementImage(
                f'{ttk_style}.border', normal_img.image, sticky="nsew", border=normal_img.meta.border).state_specs(
                [
                    ('disabled', disabled_img.image),
                    ('pressed !selected', pressed_img.image),
                    ('active', active_img.image),
                    ('selected', selected_img.image),
                    ('', normal_img.image)
                ]))
    else:
        b.create_style_element_image(
            ElementImage(
                f'{ttk_style}.border', normal_img.image, sticky="nsew", border=normal_img.meta.border).state_specs(
                [
                    ('disabled', disabled_img.image),
                    ('pressed !selected', pressed_img.image),
                    ('selected', selected_img.image),
                    ('', normal_img.image)
                ]))

    b.create_style_layout(
        ttk_style,
        _toolbutton_layout(ttk_style),
    )

    b.configure_style(
        ttk_style,
        background=surface,
        foreground=fg_normal,
        stipple="gray12",
        relief='flat',
        padding=button_padding(b, icon_only, density),
        anchor="center",
        font=button_font(density)
    )

    state_spec = dict(
        foreground=[
            ('disabled', fg_disabled),
            ('pressed', fg_normal),
            ('selected', fg_selected),
            ('', fg_normal)],
    )

    state_spec = apply_icon_mapping(b, options, state_spec, icon_size(icon_only, density))
    b.map_style(ttk_style, **state_spec)


@BootstyleBuilderTTk.register_builder('outline', 'ButtonGroup')
def build_outline_button_group_style(b: BootstyleBuilderTTk, ttk_style: str, accent: Optional[str] = None, **options):
    """
    Configure the outline button group style.

    Style options include:
        * icon_only
        * position
        * orientation
        * active_state
        * density
    """
    accent = b.default(accent)
    surface_token = options.get('surface', 'content')
    orient = options.get('orient', 'horizontal')
    position = options.get('position', 'before')
    density = options.get('density', 'default')
    icon_only = options.get('icon_only', False)
    active_state = options.get('active_state', False)
    image_key = f'button_group_{orient}_{position}_{density}'

    surface = b.color(surface_token)
    accent_color = b.elevate(surface, 1) if accent is None else b.color(accent)

    # background colors
    bg_normal = surface
    bg_selected = accent_color
    bg_disabled = b.disabled()
    bg_active = bg_selected
    bg_pressed = b.active(bg_selected)

    # foreground colors
    fg_normal = b.on_color(bg_normal) if accent is None else accent_color
    fg_selected = b.on_color(bg_normal)
    fg_active = b.on_color(bg_active)
    fg_pressed = b.on_color(bg_pressed)
    fg_disabled = b.disabled('text', bg_disabled)


    # border colors
    bd_normal = b.border(bg_normal) if accent is None else accent_color
    bd_selected = b.border(bg_selected)
    bd_active = b.border(bg_active)
    bd_pressed = b.pressed(bg_pressed)
    bd_disabled = b.border(bg_disabled)


    normal_img = recolor_element_image(image_key, surface, bd_normal, surface, surface)
    selected_img = recolor_element_image(image_key, bg_selected, bd_selected, surface, surface)
    active_img = recolor_element_image(image_key, bg_active, bd_active, surface, surface)
    pressed_img = recolor_element_image(image_key, bg_pressed, bd_pressed, surface, surface)
    disabled_img = recolor_element_image(image_key, bg_disabled, bd_disabled, surface, surface)

    if active_state:
        b.create_style_element_image(
            ElementImage(
                f'{ttk_style}.border', normal_img.image, sticky="nsew", border=normal_img.meta.border).state_specs(
                [
                    ('disabled', disabled_img.image),
                    ('selected', selected_img.image),
                    ('pressed', pressed_img.image),
                    ('active', active_img.image),
                    ('', normal_img.image)
                ]))
    else:
        b.create_style_element_image(
            ElementImage(
                f'{ttk_style}.border', normal_img.image, sticky="nsew", border=normal_img.meta.border).state_specs(
                [
                    ('disabled', disabled_img.image),
                    ('selected', selected_img.image),
                    ('', normal_img.image)
                ]))

    b.create_style_layout(
        ttk_style,
        _toolbutton_layout(ttk_style),
    )

    b.configure_style(
        ttk_style,
        background=surface,
        foreground=bg_normal,
        stipple="gray12",
        relief='flat',
        padding=button_padding(b, icon_only, density),
        anchor="center",
        font=button_font(density)
    )

    if active_state:
        state_spec = dict(
            foreground=[
                ('disabled', fg_disabled),
                ('selected', fg_selected),
                ('pressed', fg_pressed),
                ('active', fg_active),
                ('', fg_normal)],
        )
    else:
        state_spec = dict(
            foreground=[
                ('disabled', fg_disabled),
                ('selected', fg_selected),
                ('pressed', fg_normal),
                ('', fg_normal)],
        )

    state_spec = apply_icon_mapping(b, options, state_spec, icon_size(icon_only, density))
    b.map_style(ttk_style, **state_spec)


@BootstyleBuilderTTk.register_builder('ghost', 'ButtonGroup')
def build_ghost_button_group_style(b: BootstyleBuilderTTk, ttk_style: str, accent: Optional[str] = None, **options):
    """
    Configure the ghost button group style.

    Style options include:
        * icon_only
        * position
        * orientation
        * active_state
        * density
    """
    accent = b.default(accent)
    surface_token = options.get('surface', 'content')
    orient = options.get('orient', 'horizontal')
    position = options.get('position', 'before')
    density = options.get('density', 'default')
    icon_only = options.get('icon_only', False)
    active_state = options.get('active_state', False)
    image_key = f'button_group_{orient}_{position}_{density}'

    surface = b.color(surface_token)
    accent_color = b.elevate(surface, 1) if accent is None else b.color(accent)

    # background colors
    bg_normal = surface
    bg_active = b.elevate(surface, 1) if accent is None else b.subtle(accent, surface)
    bg_pressed = b.active(bg_active)
    bg_disabled = b.disabled()

    # foreground colors
    fg_normal = b.on_color(bg_normal) if accent is None else accent_color
    fg_disabled = b.disabled('text', bg_disabled)

    # border colors
    bd_normal = bg_active

    # button images
    normal_img = recolor_element_image(image_key, bg_normal, bd_normal, surface, surface)
    active_img = recolor_element_image(image_key, bg_active, bd_normal, surface, surface)
    pressed_img = recolor_element_image(image_key, bg_pressed, bd_normal, surface, surface)

    disabled_img = recolor_element_image(image_key, surface, bg_normal, surface, surface)

    if active_state:
        b.create_style_element_image(
            ElementImage(
                f'{ttk_style}.border', normal_img.image, sticky="nsew", border=normal_img.meta.border).state_specs(
                [
                    ('disabled', disabled_img.image),
                    ('pressed !selected', pressed_img.image),
                    ('active', active_img.image),
                    ('selected', active_img.image),
                    ('', normal_img.image)
                ]))
    else:
        b.create_style_element_image(
            ElementImage(
                f'{ttk_style}.border', normal_img.image, sticky="nsew", border=normal_img.meta.border).state_specs(
                [
                    ('disabled', disabled_img.image),
                    ('pressed !selected', pressed_img.image),
                    ('selected', active_img.image),
                    ('', normal_img.image)
                ]))

    b.create_style_layout(
        ttk_style,
        _toolbutton_layout(ttk_style),
    )

    b.configure_style(
        ttk_style,
        background=surface,
        foreground=fg_normal,
        stipple="gray12",
        relief='flat',
        padding=button_padding(b, icon_only, density),
        anchor="center",
        font=button_font(density)
    )

    state_spec = dict(
        foreground=[
            ('disabled', fg_disabled),
            ('', fg_normal)
        ]
    )

    state_spec = apply_icon_mapping(b, options, state_spec, icon_size(icon_only, density))
    b.map_style(ttk_style, **state_spec)
