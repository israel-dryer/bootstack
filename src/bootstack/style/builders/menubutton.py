"""Menubutton widget style builders.

This module contains style builders for ttk.Menubutton widgets and variants.
"""

from __future__ import annotations

from typing import Optional

from bootstack._core.images import Image as _ImageService
from bootstack.style.bootstyle_builder_ttk import BootstyleBuilderTTk
from bootstack.style.element import Element, ElementImage
from bootstack.style.utility import create_transparent_image, recolor_element_image
from bootstack.style.builders.utils import (
    apply_icon_mapping,
    button_font,
    button_height,
    icon_size,
    normalize_button_density,
)


def _menubutton_layout(ttk_style: str, show_dropdown: bool = True) -> Element:
    """Create the layout for a menubutton."""
    children = [Element("Menubutton.label", sticky="nsew", side="left")]

    if show_dropdown:
        children.extend(
            [
                Element(f"{ttk_style}.chevron", side="right", sticky=""),
                Element(f'{ttk_style}.spacer', side="right", sticky=""),
            ])

    return Element(f"{ttk_style}.border", sticky="nsew").children(
        [
            Element("Menubutton.padding", sticky="nsew").children(children)
        ])


def _chevron_size(density: str) -> int:
    """Get chevron icon size based on density."""
    return 14 if density == 'compact' else 18


def _create_chevron_images(
        b: BootstyleBuilderTTk, ttk_style: str, foreground: str, disabled: str, active: str = None,
        icon_name: str = 'caret-down-fill', density: str = 'default'):
    """Create chevron icon images for dropdown indicator.

    Args:
        b: Style builder instance
        ttk_style: TTK style name
        foreground: Normal foreground color
        disabled: Disabled color
        active: Active/hover color (optional)
        icon_name: Name of the icon to use (default: 'caret-down-fill')
        density: Button density ('default' or 'compact')
    """
    size = _chevron_size(density)
    normal_chevron = _ImageService.get_icon(icon_name, size, foreground)
    disabled_chevron = _ImageService.get_icon(icon_name, size, disabled)

    state_specs = [('disabled', disabled_chevron)]

    if active:
        active_chevron = _ImageService.get_icon(icon_name, size, active)
        state_specs.extend([
            ('background focus !disabled', active_chevron),
            ('hover !disabled', active_chevron),
            ('pressed !disabled', active_chevron),
        ])

    state_specs.append(('', normal_chevron))

    b.create_style_element_image(
        ElementImage(f'{ttk_style}.chevron', normal_chevron).state_specs(state_specs)
    )


def _create_spacer(b: BootstyleBuilderTTk, ttk_style: str, density: str = 'default'):
    """Create a small spacer element."""
    width = 6 if density == 'compact' else 8
    spacer_img = create_transparent_image(width, 1)
    b.create_style_element_image(ElementImage(f'{ttk_style}.spacer', spacer_img, sticky="ew", width=width))


def _menubutton_padding(b: BootstyleBuilderTTk, icon_only: bool, density: str) -> int | tuple[int, ...]:
    """Calculate menubutton padding based on options."""
    if icon_only:
        return 0
    if density == 'compact':
        return b.scale((6, 0, 3, 0))
    return b.scale((8, 0, 4, 0))


@BootstyleBuilderTTk.register_builder('solid', 'TMenubutton')
@BootstyleBuilderTTk.register_builder('default', 'TMenubutton')
def build_solid_menubutton_style(b: BootstyleBuilderTTk, ttk_style: str, accent: Optional[str] = None, **options):
    """Configure the solid menubutton style.

    Style options include:
        * show_dropdown_button: Show/hide the dropdown chevron (default: True)
        * dropdown_button_icon: Icon name for the dropdown indicator (default: 'caret-down-fill')
        * icon: Optional icon specification for the button content
        * icon_only: Whether the button shows only an icon
        * density: Button density ('default' or 'compact')
    """
    accent = b.default(accent)
    density = options.get('density', 'default')
    show_dropdown = options.get('show_dropdown_button', True)
    dropdown_icon = options.get('dropdown_button_icon', 'caret-down-fill')
    icon_only = options.get('icon_only', False)
    image_key = f'button_{normalize_button_density(density)}'

    surface_token = options.get('surface', 'content')
    surface = b.color(surface_token)

    # background colors
    bg_normal = b.elevate(surface, 1) if accent is None else b.color(accent)
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

    normal_img = recolor_element_image(image_key, bg_normal, bd_normal, surface, surface)
    pressed_img = recolor_element_image(image_key, bg_pressed, bd_pressed, surface, surface)
    active_img = recolor_element_image(image_key, bg_active, bd_active, surface, surface)
    focused_img = recolor_element_image(image_key, focused, focused, focused_ring, surface)
    focused_active_img = recolor_element_image(image_key, bd_active, focused, focused_ring, surface)
    focused_pressed_img = recolor_element_image(image_key, bd_pressed, focused, focused_ring, surface)
    disabled_img = recolor_element_image(image_key, bg_disabled, bd_disabled, surface, surface)

    if show_dropdown:
        _create_spacer(b, ttk_style, density)
        _create_chevron_images(b, ttk_style, fg_normal, fg_disabled, icon_name=dropdown_icon, density=density)

    b.create_style_element_image(
        ElementImage(
            f'{ttk_style}.border', normal_img.image, sticky="nsew",
            border=normal_img.meta.border, padding=normal_img.meta.border,
            height=button_height(b, density),
        ).state_specs([
            ('disabled', disabled_img.image),
            ('background focus pressed', focused_pressed_img.image),
            ('background focus hover', focused_active_img.image),
            ('background focus', focused_img.image),
            ('pressed', pressed_img.image),
            ('active', active_img.image),
        ]))

    b.create_style_layout(ttk_style, _menubutton_layout(ttk_style, show_dropdown))

    b.configure_style(
        ttk_style,
        stipple="gray12",
        font=button_font(density),
        takefocus=True,
        padding=_menubutton_padding(b, icon_only, density),
        anchor="center" if icon_only else "w"
    )

    state_spec = dict(
        foreground=[('disabled', fg_disabled), ('', fg_normal)],
        background=[('disabled', bg_disabled), ('', surface)]
    )

    state_spec = apply_icon_mapping(b, options, state_spec, icon_size(icon_only, density))
    b.map_style(ttk_style, **state_spec)


@BootstyleBuilderTTk.register_builder('outline', 'TMenubutton')
def build_outline_menubutton_style(b: BootstyleBuilderTTk, ttk_style: str, accent: Optional[str] = None, **options):
    """Configure the outline menubutton style.

    Style options include:
        * show_dropdown_button: Show/hide the dropdown chevron (default: True)
        * dropdown_button_icon: Icon name for the dropdown indicator (default: 'caret-down-fill')
        * icon: Optional icon specification for the button content
        * icon_only: Whether the button shows only an icon
        * density: Button density ('default' or 'compact')
    """
    accent = b.default(accent)
    density = options.get('density', 'default')
    show_dropdown = options.get('show_dropdown_button', True)
    dropdown_icon = options.get('dropdown_button_icon', 'caret-down-fill')
    icon_only = options.get('icon_only', False)
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
    fg_normal = b.on_color(bg_normal) if accent is None else accent_color
    fg_disabled = b.disabled('text', surface)
    fg_active = b.on_color(bg_normal if accent is None else accent_color)

    # border colors
    bd_normal = b.border(bg_normal) if accent is None else fg_normal
    bd_active = b.border(bg_active)
    bd_pressed = b.border(bg_pressed)

    normal_img = recolor_element_image(image_key, surface, bd_normal, surface, surface)
    pressed_img = recolor_element_image(image_key, bg_pressed, bd_pressed, surface, surface)
    active_img = recolor_element_image(image_key, bg_active, bd_active, surface, surface)
    focused_img = recolor_element_image(image_key, surface, bd_active, bg_focus_ring, surface)
    focused_active_img = recolor_element_image(image_key, bg_active, bd_active, bg_focus_ring, surface)
    focused_pressed_img = recolor_element_image(image_key, bg_pressed, bd_pressed, bg_focus_ring, surface)
    disabled_img = recolor_element_image(image_key, surface, bg_disabled, surface, surface)

    if show_dropdown:
        _create_spacer(b, ttk_style, density)
        _create_chevron_images(b, ttk_style, fg_normal, fg_disabled, fg_active, dropdown_icon, density)

    b.create_style_element_image(
        ElementImage(
            f'{ttk_style}.border', normal_img.image, sticky="nsew",
            border=normal_img.meta.border, padding=normal_img.meta.border,
            height=button_height(b, density),
        ).state_specs([
            ('disabled', disabled_img.image),
            ('background focus pressed', focused_pressed_img.image),
            ('background focus active', focused_active_img.image),
            ('background focus', focused_img.image),
            ('pressed', pressed_img.image),
            ('active', active_img.image),
        ]))

    b.create_style_layout(ttk_style, _menubutton_layout(ttk_style, show_dropdown))

    b.configure_style(
        ttk_style,
        stipple="gray12",
        font=button_font(density),
        takefocus=True,
        padding=_menubutton_padding(b, icon_only, density),
        anchor="center" if icon_only else "w"
    )

    state_spec = dict(
        foreground=[
            ('disabled', fg_disabled),
            ('background focus pressed', fg_active),
            ('background focus active', fg_active),
            ('hover', fg_active),
            ('', fg_normal)
        ],
        background=[('disabled', surface), ('', surface)]
    )

    state_spec = apply_icon_mapping(b, options, state_spec, icon_size(icon_only, density))
    b.map_style(ttk_style, **state_spec)


@BootstyleBuilderTTk.register_builder('ghost', 'TMenubutton')
def build_ghost_menubutton_style(b: BootstyleBuilderTTk, ttk_style: str, accent: Optional[str] = None, **options):
    """Configure the ghost menubutton style.

    Style options include:
        * show_dropdown_button: Show/hide the dropdown chevron (default: True)
        * dropdown_button_icon: Icon name for the dropdown indicator (default: 'caret-down-fill')
        * icon: Optional icon specification for the button content
        * icon_only: Whether the button shows only an icon
        * density: Button density ('default' or 'compact')
    """
    accent = b.default(accent)
    density = options.get('density', 'default')
    show_dropdown = options.get('show_dropdown_button', True)
    dropdown_icon = options.get('dropdown_button_icon', 'caret-down-fill')
    icon_only = options.get('icon_only', False)
    image_key = f'button_{normalize_button_density(density)}'

    surface_token = options.get('surface', 'content')
    surface = b.color(surface_token)

    # background colors
    bg_normal = surface
    bg_active = bg_focused = b.elevate(surface, 1) if accent is None else b.subtle(accent, surface)
    bg_pressed = b.active(bg_active)
    focused_ring = b.color('foreground')

    # foreground colors
    fg_normal = b.on_color(bg_normal) if accent is None else b.color(accent)
    fg_disabled = b.disabled('text', surface)

    normal_img = recolor_element_image(image_key, bg_normal, bg_normal, surface, surface)
    pressed_img = recolor_element_image(image_key, bg_pressed, bg_pressed, surface, surface)
    active_img = recolor_element_image(image_key, bg_active, bg_active, surface, surface)
    focused_img = recolor_element_image(image_key, bg_focused, bg_focused, focused_ring, surface)
    focused_active_img = recolor_element_image(image_key, bg_focused, bg_focused, focused_ring, surface)
    focused_pressed_img = recolor_element_image(image_key, bg_pressed, bg_pressed, focused_ring, surface)
    disabled_img = recolor_element_image(image_key, surface, surface, surface, surface)

    if show_dropdown:
        _create_spacer(b, ttk_style, density)
        _create_chevron_images(b, ttk_style, fg_normal, fg_disabled, icon_name=dropdown_icon, density=density)

    b.create_style_element_image(
        ElementImage(
            f'{ttk_style}.border', normal_img.image, sticky="nsew",
            border=normal_img.meta.border, padding=normal_img.meta.border,
            height=button_height(b, density),
        ).state_specs([
            ('disabled', disabled_img.image),
            ('background focus pressed', focused_pressed_img.image),
            ('background focus active', focused_active_img.image),
            ('background focus', focused_img.image),
            ('pressed !disabled', pressed_img.image),
            ('active !disabled', active_img.image),
        ]))

    b.create_style_layout(ttk_style, _menubutton_layout(ttk_style, show_dropdown))

    b.configure_style(
        ttk_style,
        stipple="gray12",
        font=button_font(density),
        takefocus=True,
        padding=_menubutton_padding(b, icon_only, density),
        anchor="center" if icon_only else "w"
    )

    state_spec = dict(
        foreground=[('disabled', fg_disabled), ('', fg_normal)],
        background=[('disabled', surface), ('', surface)]
    )

    state_spec = apply_icon_mapping(b, options, state_spec, icon_size(icon_only, density))
    b.map_style(ttk_style, **state_spec)