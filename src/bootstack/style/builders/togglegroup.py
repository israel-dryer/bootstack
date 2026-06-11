"""ToggleGroup widget style builders.

Duplicated from the ButtonGroup builder so selection widgets (ToggleGroup) can
diverge from action widgets (ButtonGroup) — they need different normal states.
The baked nine-patch shapes are shared (the `button_group_*` image keys); only
the colors/state mappings differ.
"""

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


@BootstyleBuilderTTk.register_builder('solid', 'ToggleGroup')
@BootstyleBuilderTTk.register_builder('default', 'ToggleGroup')
def build_toggle_group_style(b: BootstyleBuilderTTk, ttk_style: str, accent: Optional[str] = None, **options):
    """
    Configure the toggle group style.

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
    accent_color = b.elevate(surface, 2) if accent is None else b.color(accent)

    # background colors
    bg_normal = b.elevate(surface, 1)
    bg_selected = accent_color
    bg_disabled = b.disabled()

    # foreground colors
    fg_normal = b.muted_foreground(bg_normal)
    fg_selected = b.on_color(bg_selected)
    fg_disabled = b.disabled('text', bg_disabled)

    # border colors
    bd_normal = b.border(bg_normal)
    bd_selected = b.border(bg_selected)
    bd_disabled = b.border(bg_disabled)

    normal_img = recolor_element_image(image_key, bg_normal, bd_normal, surface, surface)
    selected_img = recolor_element_image(image_key, bg_selected, bd_selected, surface, surface)
    disabled_img = recolor_element_image(image_key, bg_disabled, bd_disabled, surface, surface)

    if active_state:
        b.create_style_element_image(
            ElementImage(
                f'{ttk_style}.border', normal_img.image, sticky="nsew", border=normal_img.meta.border).state_specs(
                [
                    ('disabled', disabled_img.image),
                    ('selected', selected_img.image),
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
            ('selected', fg_selected),
            ('', fg_normal)],
    )

    state_spec = apply_icon_mapping(b, options, state_spec, icon_size(icon_only, density))
    b.map_style(ttk_style, **state_spec)


@BootstyleBuilderTTk.register_builder('outline', 'ToggleGroup')
def build_outline_toggle_group_style(b: BootstyleBuilderTTk, ttk_style: str, accent: Optional[str] = None, **options):
    """
    Configure the outline toggle group style.

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

    # foreground colors
    fg_normal = b.muted_foreground(bg_normal) if accent is None else accent_color
    fg_selected = b.on_color(bg_selected)
    fg_disabled = b.disabled('text', bg_disabled)


    # border colors
    bd_normal = b.border(bg_normal) if accent is None else accent_color
    bd_selected = b.border(bg_selected)
    bd_disabled = b.border(bg_disabled)


    normal_img = recolor_element_image(image_key, surface, bd_normal, surface, surface)
    selected_img = recolor_element_image(image_key, bg_selected, bd_selected, surface, surface)
    disabled_img = recolor_element_image(image_key, bg_disabled, bd_disabled, surface, surface)

    if active_state:
        b.create_style_element_image(
            ElementImage(
                f'{ttk_style}.border', normal_img.image, sticky="nsew", border=normal_img.meta.border).state_specs(
                [
                    ('disabled', disabled_img.image),
                    ('selected', selected_img.image),
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
        foreground=fg_normal,
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
                ('', fg_normal)],
        )
    else:
        state_spec = dict(
            foreground=[
                ('disabled', fg_disabled),
                ('selected', fg_selected),
                ('', fg_normal)],
        )

    state_spec = apply_icon_mapping(b, options, state_spec, icon_size(icon_only, density))
    b.map_style(ttk_style, **state_spec)


@BootstyleBuilderTTk.register_builder('ghost', 'ToggleGroup')
def build_ghost_toggle_group_style(b: BootstyleBuilderTTk, ttk_style: str, accent: Optional[str] = None, **options):
    """
    Configure the ghost toggle group style.

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
    image_key = f'button_group_{orient}_{position}_{density}'

    surface = b.color(surface_token)
    accent_color = b.elevate(surface, 1) if accent is None else b.color(accent)

    # background colors
    bg_normal = surface
    bg_selected = b.elevate(surface, 2) if accent is None else b.subtle(accent, surface)
    bg_disabled = b.disabled()

    # foreground colors
    fg_normal = b.muted_foreground(bg_normal)
    fg_selected = b.on_color(bg_selected) if accent is None else accent_color
    fg_disabled = b.disabled('text', bg_disabled)

    # border colors
    bd_normal = b.border(surface)
    bd_selected = b.border(bg_selected)

    # button images
    normal_img = recolor_element_image(image_key, bg_normal, bd_normal, surface, surface)
    selected_img = recolor_element_image(image_key, bg_selected, bd_selected, surface, surface)
    disabled_img = recolor_element_image(image_key, surface, bg_normal, surface, surface)

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
            ('selected !disabled', fg_selected),
            ('', fg_normal)
        ]
    )

    state_spec = apply_icon_mapping(b, options, state_spec, icon_size(icon_only, density))
    b.map_style(ttk_style, **state_spec)
