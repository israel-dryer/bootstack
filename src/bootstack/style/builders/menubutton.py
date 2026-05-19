"""Menubutton widget style builders.

This module contains style builders for ttk.Menubutton widgets and variants.
"""

from __future__ import annotations

from ttkbootstrap_icons_bs import BootstrapIcon
from bootstack.style.bootstyle_builder_ttk import BootstyleBuilderTTk
from bootstack.style.element import Element, ElementImage
from bootstack.style.utility import create_transparent_image, recolor_element_image
from bootstack.style.builders.utils import (
    apply_icon_mapping,
    button_font,
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
                Element(f"{ttk_style}.spacer", side="right", sticky=""),
            ]
        )

    return Element(f"{ttk_style}.border", sticky="nsew").children(
        [Element("Menubutton.padding", sticky="nsew").children(children)]
    )


def _chevron_size(density: str) -> int:
    """Get chevron icon size based on density."""
    return 14 if density == "compact" else 18


def _create_chevron_images(
    b: BootstyleBuilderTTk,
    ttk_style: str,
    foreground: str,
    disabled: str,
    active: str = None,
    icon_name: str = "caret-down-fill",
    density: str = "default",
):
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
    normal_chevron = BootstrapIcon(icon_name, size=size, color=foreground).image
    disabled_chevron = BootstrapIcon(icon_name, size=size, color=disabled).image

    state_specs = [("disabled", disabled_chevron)]

    if active:
        active_chevron = BootstrapIcon(icon_name, size=size, color=active).image
        state_specs.extend(
            [
                ("focus !disabled", active_chevron),
                ("hover !disabled", active_chevron),
                ("pressed !disabled", active_chevron),
            ]
        )

    state_specs.append(("", normal_chevron))

    b.create_style_element_image(
        ElementImage(f"{ttk_style}.chevron", normal_chevron).state_specs(state_specs)
    )


def _create_spacer(b: BootstyleBuilderTTk, ttk_style: str, density: str = "default"):
    """Create a small spacer element."""
    width = 6 if density == "compact" else 8
    spacer_img = create_transparent_image(width, 1)
    b.create_style_element_image(
        ElementImage(f"{ttk_style}.spacer", spacer_img, sticky="ew", width=width)
    )


def _menubutton_padding(
    b: BootstyleBuilderTTk, icon_only: bool, density: str
) -> int | tuple[int, ...]:
    """Calculate menubutton padding based on options."""
    if icon_only:
        return 0
    if density == "compact":
        return b.scale((6, 0, 3, 0))
    return b.scale((8, 0, 4, 0))


@BootstyleBuilderTTk.register_builder("solid", "TMenubutton")
@BootstyleBuilderTTk.register_builder("default", "TMenubutton")
def build_solid_menubutton_style(
    b: BootstyleBuilderTTk, ttk_style: str, accent: str = None, **options
):
    """Configure the solid menubutton style.

    Style options include:
        * show_dropdown_button: Show/hide the dropdown chevron (default: True)
        * dropdown_button_icon: Icon name for the dropdown indicator (default: 'caret-down-fill')
        * icon: Optional icon specification for the button content
        * icon_only: Whether the button shows only an icon
        * density: Button density ('default' or 'compact')
    """
    accent_token = accent or "primary"
    surface_token = options.get("surface", "content")
    density = options.get("density", "default")
    show_dropdown = options.get("show_dropdown_button", True)
    dropdown_icon = options.get("dropdown_button_icon", "caret-down-fill")
    icon_only = options.get("icon_only", False)
    image_key = f"button_{normalize_button_density(density)}"

    surface = b.color(surface_token)
    normal = b.color(accent_token)
    foreground = b.on_color(normal)
    pressed = b.pressed(normal)
    hovered = b.active(normal)
    focused = b.focus(normal)
    disabled = b.disabled()
    foreground_disabled = b.disabled("text", disabled)

    normal_img = recolor_element_image(image_key, normal, normal, normal)
    hovered_img = recolor_element_image(image_key, hovered, hovered, hovered)
    focused_img = recolor_element_image(image_key, surface, focused, focused)
    pressed_img = recolor_element_image(image_key, surface, pressed, pressed)
    disabled_img = recolor_element_image(image_key, disabled, disabled, disabled)

    if show_dropdown:
        _create_spacer(b, ttk_style, density)
        _create_chevron_images(
            b, ttk_style, foreground, foreground_disabled,
            icon_name=dropdown_icon, density=density,
        )

    b.create_style_element_image(
        ElementImage(
            f"{ttk_style}.border",
            normal_img.image,
            sticky="nsew",
            border=normal_img.meta.border,
            padding=normal_img.meta.border,
        ).state_specs(
            [
                ("disabled", disabled_img.image),
                ("focus pressed", pressed_img.image),
                ("focus", focused_img.image),
                ("active", hovered_img.image),
            ]
        )
    )

    b.create_style_layout(ttk_style, _menubutton_layout(ttk_style, show_dropdown))

    b.configure_style(
        ttk_style,
        background=surface,
        foreground=foreground,
        stipple="gray12",
        relief="flat",
        font=button_font(density),
        takefocus=True,
        padding=_menubutton_padding(b, icon_only, density),
        anchor="center" if icon_only else "w",
    )

    state_spec = dict(
        foreground=[("disabled", foreground_disabled), ("", foreground)],
        background=[("disabled", disabled)],
    )

    state_spec = apply_icon_mapping(b, options, state_spec, icon_size(icon_only, density))
    b.map_style(ttk_style, **state_spec)


@BootstyleBuilderTTk.register_builder("outline", "TMenubutton")
def build_outline_menubutton_style(
    b: BootstyleBuilderTTk, ttk_style: str, accent: str = None, **options
):
    """Configure the outline menubutton style.

    Style options include:
        * show_dropdown_button: Show/hide the dropdown chevron (default: True)
        * dropdown_button_icon: Icon name for the dropdown indicator (default: 'caret-down-fill')
        * icon: Optional icon specification for the button content
        * icon_only: Whether the button shows only an icon
        * density: Button density ('default' or 'compact')
    """
    accent_token = accent or "primary"
    surface_token = options.get("surface", "content")
    density = options.get("density", "default")
    show_dropdown = options.get("show_dropdown_button", True)
    dropdown_icon = options.get("dropdown_button_icon", "caret-down-fill")
    icon_only = options.get("icon_only", False)
    image_key = f"button_{normalize_button_density(density)}"

    surface = b.color(surface_token)
    foreground_normal = b.color(accent_token)
    foreground_disabled = b.disabled("text", surface)
    foreground_active = b.on_color(foreground_normal)

    disabled = foreground_disabled
    pressed = b.pressed(foreground_normal)
    focused = b.focus(foreground_normal)
    active = b.active(foreground_normal)

    normal_img = recolor_element_image(image_key, surface, foreground_normal, surface)
    hovered_img = recolor_element_image(image_key, active, active, active)
    focused_img = recolor_element_image(image_key, surface, focused, focused)
    pressed_img = recolor_element_image(image_key, surface, pressed, pressed)
    disabled_img = recolor_element_image(image_key, surface, disabled, surface, surface)

    if show_dropdown:
        _create_spacer(b, ttk_style, density)
        _create_chevron_images(
            b, ttk_style, foreground_normal, disabled, foreground_active,
            dropdown_icon, density,
        )

    b.create_style_element_image(
        ElementImage(
            f"{ttk_style}.border",
            normal_img.image,
            sticky="nsew",
            border=normal_img.meta.border,
            padding=normal_img.meta.border,
        ).state_specs(
            [
                ("disabled", disabled_img.image),
                ("pressed", pressed_img.image),
                ("focus", focused_img.image),
                ("hover", hovered_img.image),
            ]
        )
    )

    b.create_style_layout(ttk_style, _menubutton_layout(ttk_style, show_dropdown))

    b.configure_style(
        ttk_style,
        background=surface,
        foreground=foreground_normal,
        relief="flat",
        stipple="gray12",
        font=button_font(density),
        takefocus=True,
        padding=_menubutton_padding(b, icon_only, density),
        anchor="center" if icon_only else "w",
    )

    state_spec = dict(
        foreground=[
            ("disabled", foreground_disabled),
            ("focus", foreground_active),
            ("active", foreground_active),
            ("", foreground_normal),
        ],
        background=[("disabled", surface)],
    )

    state_spec = apply_icon_mapping(b, options, state_spec, icon_size(icon_only, density))
    b.map_style(ttk_style, **state_spec)


@BootstyleBuilderTTk.register_builder("ghost", "TMenubutton")
def build_ghost_menubutton_style(
    b: BootstyleBuilderTTk, ttk_style: str, accent: str = None, **options
):
    """Configure the ghost menubutton style.

    Style options include:
        * show_dropdown_button: Show/hide the dropdown chevron (default: True)
        * dropdown_button_icon: Icon name for the dropdown indicator (default: 'caret-down-fill')
        * icon: Optional icon specification for the button content
        * icon_only: Whether the button shows only an icon
        * density: Button density ('default' or 'compact')
    """
    accent_token = accent or "secondary"
    surface_token = options.get("surface", "content")
    density = options.get("density", "default")
    show_dropdown = options.get("show_dropdown_button", True)
    dropdown_icon = options.get("dropdown_button_icon", "caret-down-fill")
    icon_only = options.get("icon_only", False)
    image_key = f"button_{normalize_button_density(density)}"

    surface = b.color(surface_token)
    accent_color = b.color(accent_token)
    hovered = b.subtle(accent_token, surface)
    focused = b.focus(hovered)
    pressed = b.pressed(hovered)

    foreground_normal = accent_color
    foreground_disabled = b.disabled("text", surface)

    normal_img = recolor_element_image(image_key, surface, surface, surface)
    hovered_img = recolor_element_image(image_key, hovered, hovered, hovered)
    focused_img = recolor_element_image(image_key, surface, accent_color, focused)
    pressed_img = recolor_element_image(image_key, surface, accent_color, pressed, surface)
    disabled_img = recolor_element_image(image_key, surface, surface, surface, surface)

    if show_dropdown:
        _create_spacer(b, ttk_style, density)
        _create_chevron_images(
            b, ttk_style, foreground_normal, foreground_disabled,
            icon_name=dropdown_icon, density=density,
        )

    b.create_style_element_image(
        ElementImage(
            f"{ttk_style}.border",
            normal_img.image,
            sticky="nsew",
            border=normal_img.meta.border,
            padding=normal_img.meta.border,
        ).state_specs(
            [
                ("disabled", disabled_img.image),
                ("pressed", pressed_img.image),
                ("focus", focused_img.image),
                ("hover", hovered_img.image),
            ]
        )
    )

    b.create_style_layout(ttk_style, _menubutton_layout(ttk_style, show_dropdown))

    b.configure_style(
        ttk_style,
        background=surface,
        foreground=foreground_normal,
        relief="flat",
        stipple="gray12",
        font=button_font(density),
        takefocus=True,
        padding=_menubutton_padding(b, icon_only, density),
        anchor="center" if icon_only else "w",
    )

    state_spec = dict(
        foreground=[("disabled", foreground_disabled), ("", foreground_normal)],
        background=[("disabled", surface)],
    )

    state_spec = apply_icon_mapping(b, options, state_spec, icon_size(icon_only, density))
    b.map_style(ttk_style, **state_spec)