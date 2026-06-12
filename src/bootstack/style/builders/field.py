"""Field widget style builders.

This module contains style builders for ttk.Frame widget and field variants used to build
the Entry containers.
"""

from __future__ import annotations

from typing import Optional

from bootstack._core.images import _ImageService

from bootstack.style.bootstyle_builder_ttk import BootstyleBuilderTTk
from bootstack.style.element import Element, ElementImage
from bootstack.style.utility import recolor_element_image
from bootstack.style.builders.utils import (
    normalize_button_density,
    entry_font,
    entry_padding,
    field_height,
    entry_icon_size,
    entry_image_key,
    spinner_arrow_height,
    spinner_arrow_width,
)


@BootstyleBuilderTTk.register_builder('default', 'TField')
def build_field_style(b: BootstyleBuilderTTk, ttk_style: str, accent: str = None, **options):
    surface_token = options.get('surface', 'content')
    fill_token = options.get('input_background') or 'background'
    density = normalize_button_density(options.get('density', 'default'))

    fill = b.color(fill_token)
    container_surface = b.color(surface_token)
    accent_color = b.color(accent or 'primary')
    normal = fill
    border = b.border(fill)
    disabled = b.disabled('text')
    focused_border = b.focus_border(accent_color)
    focused_ring = b.focus_ring(accent_color, container_surface)

    # input element images - use density-aware images from manifest
    img_key = entry_image_key('input', density)
    normal_img = recolor_element_image(img_key, normal, border, container_surface, container_surface)
    focused_img = recolor_element_image(img_key, normal, focused_border, focused_ring, container_surface)
    disabled_img = recolor_element_image(img_key, normal, disabled, container_surface, container_surface)

    # input element
    b.create_style_element_image(
        ElementImage(f'{ttk_style}.border', normal_img.image, sticky="nsew", border=normal_img.meta.border).state_specs(
            [
                ('disabled', disabled_img.image),
                ('focus', focused_img.image),
            ]
        )
    )
    b.create_style_layout(
        ttk_style, Element(f'{ttk_style}.border', sticky="nsew").children(
            [
                Element(f'{ttk_style}.padding', sticky="nsew")
            ]))
    b.configure_style(ttk_style, background=fill)


@BootstyleBuilderTTk.register_builder('input', 'TField')
def build_field_input_style(b: BootstyleBuilderTTk, ttk_style: str, accent: str = None, **options):
    surface_token = options.get('surface', 'content')
    fill_token = options.get('input_background') or 'background'
    density = normalize_button_density(options.get('density', 'default'))

    fill = b.color(fill_token)
    disabled_bg = b.disabled('background')
    disabled_fg = b.disabled('text')
    foreground = b.on_color(fill)

    # Inner field is a white fill that gets recolored; height controls density
    field_img = recolor_element_image('field', fill)
    height = field_height(b, density)

    b.create_style_element_image(ElementImage(f'{ttk_style}.field', field_img.image, sticky="nsew", height=height))
    b.create_style_layout(
        ttk_style, Element(f'{ttk_style}.field').children(
            [
                Element('Entry.padding', sticky="ew").children(
                    [
                        Element('Entry.textarea', sticky="nsew")
                    ])
            ]))

    b.configure_style(
        ttk_style,
        relief='flat',
        foreground=foreground,
        background=fill,
        fieldbackground=fill,
        selectborderwidth=0,
        bordercolor=fill,
        darkcolor=fill,
        lightcolor=fill,
        insertcolor=foreground,
        padding=entry_padding(b, density),
        font=entry_font(density),
        selectforeground=b.on_color(b.color('primary')),
        selectbackground=b.color('primary')
    )

    b.map_style(
        ttk_style,
        background=[('disabled', disabled_bg), ('readonly', disabled_bg)],
        fieldbackground=[('disabled', disabled_bg), ('readonly', disabled_bg)],
        selectforeground=[],
        selectbackground=[],
        bordercolor=[('disabled', disabled_bg), ('readonly', disabled_bg)],
        darkcolor=[('disabled', disabled_bg), ('readonly', disabled_bg)],
        lightcolor=[('disabled', disabled_bg), ('readonly', disabled_bg)],
        foreground=[('disabled', disabled_fg), ('', foreground)],
    )


@BootstyleBuilderTTk.register_builder('spinner', 'TField')
def build_spinner_input_style(b: BootstyleBuilderTTk, ttk_style: str, accent: str = None, **options):
    surface_token = options.get('surface', 'content')
    fill_token = options.get('input_background') or 'background'
    density = normalize_button_density(options.get('density', 'default'))

    fill = b.color(fill_token)
    disabled_bg = b.disabled('background')
    disabled_fg = b.disabled('text')
    foreground = b.on_color(fill)

    # Inner field is a white fill that gets recolored; height controls density
    field_img = recolor_element_image('field', fill)
    height = field_height(b, density)

    b.create_style_element_image(ElementImage(f'{ttk_style}.field', field_img.image, sticky="nsew", height=height))

    # add arrow images - use density-aware icon size
    icon_size = entry_icon_size(b, density)
    arrow_up_normal_img = _ImageService.get_icon('caret-up-fill', icon_size, foreground)
    arrow_up_disabled_img = _ImageService.get_icon('caret-up-fill', icon_size, disabled_fg)
    arrow_down_normal_img = _ImageService.get_icon('caret-down-fill', icon_size, foreground)
    arrow_down_disabled_img = _ImageService.get_icon('caret-down-fill', icon_size, disabled_fg)

    # Arrow element images
    arrow_height = spinner_arrow_height(b, density)
    arrow_width = spinner_arrow_width(b)

    b.create_style_element_image(
        ElementImage(f'{ttk_style}.uparrow', arrow_up_normal_img, sticky='', width=arrow_width, height=arrow_height).state_specs([
            ('disabled', arrow_up_disabled_img),
            ('', arrow_up_normal_img),
        ])
    )

    b.create_style_element_image(
        ElementImage(f'{ttk_style}.downarrow', arrow_down_normal_img, sticky='', width=arrow_width, height=arrow_height).state_specs([
            ('disabled', arrow_down_disabled_img),
            ('', arrow_down_normal_img),
        ])
    )

    # layout - arrows stacked vertically
    b.create_style_layout(
        ttk_style,
        Element(f'{ttk_style}.field', sticky="nsew").children(
            [
                Element('null', side='right', sticky='').children(
                    [
                        Element(f'{ttk_style}.uparrow', side='top', sticky=''),
                        Element(f'{ttk_style}.downarrow', side='top', sticky=''),
                    ]),
                Element('Spinbox.padding', sticky='nsew').children(
                    [
                        Element('Spinbox.textarea', sticky='nsew'),
                    ])
            ]),
    )

    # Add extra right padding for spinner arrows
    base_padding = entry_padding(b, density)
    spinner_padding = (base_padding[0], base_padding[1], base_padding[0] + b.scale(3), base_padding[1])

    b.configure_style(
        ttk_style,
        relief='flat',
        foreground=foreground,
        background=fill,
        fieldbackground=fill,
        selectborderwidth=0,
        bordercolor=fill,
        darkcolor=fill,
        lightcolor=fill,
        insertcolor=foreground,
        padding=spinner_padding,
        font=entry_font(density),
        selectforeground=b.on_color(b.color('primary')),
        selectbackground=b.color('primary')
    )

    b.map_style(
        ttk_style,
        background=[('disabled', disabled_bg), ('readonly', disabled_bg)],
        fieldbackground=[('disabled', disabled_bg), ('readonly', disabled_bg)],
        selectforeground=[],
        selectbackground=[],
        bordercolor=[('disabled', disabled_bg), ('readonly', disabled_bg)],
        darkcolor=[('disabled', disabled_bg), ('readonly', disabled_bg)],
        lightcolor=[('disabled', disabled_bg), ('readonly', disabled_bg)],
        foreground=[('disabled', disabled_fg), ('', foreground)],
    )


@BootstyleBuilderTTk.register_builder('prefix', 'TField')
def build_field_prefix_style(b: BootstyleBuilderTTk, ttk_style: str, accent: Optional[str] = None, **options):
    build_field_addon_style(b, ttk_style, accent, **options)


@BootstyleBuilderTTk.register_builder('suffix', 'TField')
def build_field_suffix_style(b: BootstyleBuilderTTk, ttk_style: str, accent: Optional[str] = None, **options):
    build_field_addon_style(b, ttk_style, accent, **options)


def build_field_addon_style(b: BootstyleBuilderTTk, ttk_style: str, accent: Optional[str] = None, **options):
    """Build prefix/suffix addon styles for entry fields.

    Args:
        b: The bootstyle builder instance.
        ttk_style: The TTK style name.
        accent: Accent color of the button, if provided.
        **options: Style options including 'density', 'surface', 'icon', 'icon_only'.
    """

    surface_token = options.get('surface', 'content')
    fill_token = options.get('input_background') or 'background'
    density = normalize_button_density(options.get('density', 'default'))
    img_key = entry_image_key('input_addon', density)
    icon_only = options.get('icon_only', False)

    # background colors
    input_background= b.color(fill_token)

    # if not icon only, then must show button, otherwise accent will decide whether button is shown.
    show_button = (accent is None and not icon_only) or accent is not None

    if not show_button:
        bg_normal = input_background
    elif accent is not None:
        bg_normal = b.color(accent)
    else:
        bg_normal = b.elevate(input_background, 1)
    bg_active = b.active(bg_normal)
    bg_pressed = b.pressed(bg_normal)

    # foreground colors
    fg_normal = b.on_color(bg_normal)
    fg_disabled = b.disabled('text')

    if show_button:
        bg_disabled = b.disabled('background', input_background)
        bd_normal = b.border(bg_normal)
        bd_pressed = b.border(bg_pressed) if show_button else bg_pressed
        bd_active = b.border(bg_active) if show_button else bg_active
        bd_disabled = b.border(bg_disabled)
    else:
        bg_disabled = bg_normal
        bd_normal = bg_normal
        bd_active = bg_active
        bd_pressed = bg_pressed
        bd_disabled = bg_disabled


    normal_img = recolor_element_image(img_key, bg_normal, bd_normal, input_background, input_background)
    active_img = recolor_element_image(img_key, bg_active, bd_active, input_background, input_background)
    pressed_img = recolor_element_image(img_key, bg_pressed, bd_pressed, input_background, input_background)
    disabled_img = recolor_element_image(img_key, bg_disabled, bd_disabled, input_background, input_background)
    selected_img = active_img


    # addon element - set explicit height to match field height
    height = field_height(b, density)
    b.create_style_element_image(
        ElementImage(f'{ttk_style}.border', normal_img.image, border=normal_img.meta.border, height=height, padding=0).state_specs([
            ('disabled', disabled_img.image),
            ('selected !disabled', selected_img.image),
            ('pressed !disabled', pressed_img.image),
            ('active', active_img.image),
            ('', normal_img.image)
        ]))

    b.create_style_layout(
        ttk_style, Element(f"{ttk_style}.border", sticky="nsew").children(
            [
                Element("Button.padding", sticky="nsew").children(
                    [
                        Element("Button.label", sticky="nsew")
                    ])
            ]))

    # Add horizontal padding - less for icon-only buttons
    if icon_only:
        addon_padding = b.scale((5, 0)) if density == 'compact' else b.scale((4, 0))
    else:
        addon_padding = b.scale((12, 0))
    b.configure_style(
        ttk_style,
        background=bg_normal,
        foreground=fg_normal,
        relief='flat',
        stipple="gray12",
        padding=addon_padding,
        anchor='center',
    )

    # map icon if available
    icon = options.get('icon')

    state_spec = dict(
        foreground=[
            ('disabled', fg_disabled),
            ('selected !disabled', fg_normal),
            ('pressed !disabled', fg_normal),
            ('hover !disabled', fg_normal),
            ('', fg_normal)
        ])

    if icon is not None:
        icon = b.normalize_icon_spec(icon)
        # Use density-aware icon size for addon icons (kept a touch smaller than
        # a standalone icon-only button, since addons sit inside the field).
        addon_icon_size = b.scale(16) if density == 'compact' else b.scale(18)
        icon['size'] = addon_icon_size
        state_spec['image'] = b.map_stateful_icons(icon, state_spec['foreground'])

    b.map_style(ttk_style, **state_spec)
