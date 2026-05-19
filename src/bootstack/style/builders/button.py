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


@BootstyleBuilderTTk.register_builder("solid", "TButton")
@BootstyleBuilderTTk.register_builder("default", "TButton")
def build_solid_button_style(
    b: BootstyleBuilderTTk, ttk_style: str, accent: str = None, **options
):
    """
    Configure the button style.

    Style options include:
        * icon
        * icon_only
        * anchor
    """
    anchor = options.get("anchor", "center")
    accent_token = accent or "primary"
    surface_token = options.get("surface", "content")
    density = options.get("density", "default")

    surface = b.color(surface_token)
    normal = b.color(accent_token)
    foreground = b.on_color(normal)
    pressed = b.pressed(normal)
    hovered = b.active(normal)
    focused = b.focus(normal)
    disabled = b.disabled()
    foreground_disabled = b.disabled("text", disabled)

    icon_only = options.get("icon_only", False)
    image_key = f"button_{normalize_button_density(density)}"

    normal_img = recolor_element_image(image_key, normal, normal, normal)
    hovered_img = recolor_element_image(image_key, hovered, hovered, hovered)
    focused_img = recolor_element_image(image_key, surface, focused, focused)
    pressed_img = recolor_element_image(image_key, surface, pressed, pressed)
    disabled_img = recolor_element_image(image_key, disabled, disabled, disabled)

    b.create_style_element_image(
        ElementImage(
            f"{ttk_style}.Button.border",
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

    b.create_style_layout(
        ttk_style,
        button_layout(ttk_style),
    )

    b.configure_style(
        ttk_style,
        background=surface,
        foreground=foreground,
        stipple="gray12",
        relief="flat",
        padding=button_padding(b, icon_only, density),
        anchor=anchor,
        font=button_font(density),
    )

    state_spec = dict(
        foreground=[("disabled", foreground_disabled), ("", foreground)],
        background=[("disabled", disabled)],
    )
    state_spec = apply_icon_mapping(
        b, options, state_spec, icon_size(icon_only, density)
    )

    b.map_style(ttk_style, **state_spec)


@BootstyleBuilderTTk.register_builder("outline", "TButton")
def build_outline_button_style(
    b: BootstyleBuilderTTk, ttk_style: str, accent: str = None, **options
):
    """
    Configure the outline button style.

    Style options include:
        * icon
        * icon_only
        * anchor
    """
    anchor = options.get("anchor", "center")
    accent_token = accent or "primary"
    surface_token = options.get("surface", "content")
    density = options.get("density", "default")
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

    # button element images
    normal_img = recolor_element_image(image_key, surface, foreground_normal, surface)
    hovered_img = recolor_element_image(image_key, active, active, active)
    focused_img = recolor_element_image(image_key, surface, focused, focused)
    pressed_img = recolor_element_image(image_key, surface, pressed, pressed)
    disabled_img = recolor_element_image(image_key, surface, disabled, surface, surface)

    b.create_style_element_image(
        ElementImage(
            f"{ttk_style}.Button.border",
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

    b.create_style_layout(
        ttk_style,
        button_layout(ttk_style),
    )

    padding = button_padding(b, icon_only, density)

    b.configure_style(
        ttk_style,
        background=surface,
        foreground=foreground_normal,
        relief="flat",
        stipple="gray12",
        anchor=anchor,
        padding=padding,
        font=button_font(density),
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

    state_spec = apply_icon_mapping(
        b, options, state_spec, icon_size(icon_only, density)
    )

    b.map_style(ttk_style, **state_spec)


@BootstyleBuilderTTk.register_builder("link", "TButton")
def build_link_button_style(
    b: BootstyleBuilderTTk, ttk_style: str, accent: str = None, **options
):
    """
    Configure the link button style.

    Style options include:
        * icon
        * icon_only
        * anchor
    """
    anchor = options.get("anchor", "center")
    accent_token = accent or "primary"
    surface_token = options.get("surface", "content")
    density = options.get("density", "default")
    icon_only = options.get("icon_only", False)
    image_key = f"button_{normalize_button_density(density)}"

    surface = b.color(surface_token)
    foreground_normal = b.color(accent_token)
    foreground_disabled = b.disabled("text", surface)

    # button element images - all transparent for link style
    normal_img = recolor_element_image(image_key, surface, surface, surface, surface)
    focused_img = recolor_element_image(image_key, surface, surface, surface, surface)
    disabled_img = recolor_element_image(image_key, surface, surface, surface, surface)

    b.create_style_element_image(
        ElementImage(
            f"{ttk_style}.Button.border",
            normal_img.image,
            sticky="nsew",
            border=normal_img.meta.border,
            padding=normal_img.meta.border,
        ).state_specs(
            [
                ("disabled", disabled_img.image),
                ("focus", focused_img.image),
            ]
        )
    )

    b.create_style_layout(
        ttk_style,
        button_layout(ttk_style),
    )

    b.configure_style(
        ttk_style,
        background=surface,
        foreground=foreground_normal,
        relief="flat",
        stipple="gray12",
        padding=button_padding(b, icon_only, density),
        anchor=anchor,
        font=button_font(density),
    )

    state_spec = dict(
        font=[
            ("active !disabled", "hyperlink"),
            ("background focus !disabled", "hyperlink"),
            ("", button_font(density)),
        ],
        cursor=[("", "hand2")],
        foreground=[("disabled", foreground_disabled), ("", foreground_normal)],
        background=[("disabled", surface)],
    )

    state_spec = apply_icon_mapping(
        b, options, state_spec, icon_size(icon_only, density)
    )

    b.map_style(ttk_style, **state_spec)


@BootstyleBuilderTTk.register_builder("ghost", "TButton")
def build_ghost_button_style(
    b: BootstyleBuilderTTk, ttk_style: str, accent: str = None, **options
):
    """
    Configure the ghost button style.

    Style options include:
        * icon
        * icon_only
        * anchor
    """
    anchor = options.get("anchor", "center")
    accent_token = accent or "secondary"
    surface_token = options.get("surface", "content")
    density = options.get("density", "default")
    icon_only = options.get("icon_only", False)
    image_key = f"button_{normalize_button_density(density)}"

    surface = b.color(surface_token)

    accent_color = b.color(accent_token)
    hovered = b.subtle(accent_token, surface)
    focused = b.focus(hovered)
    pressed = b.pressed(hovered)

    foreground_normal = accent_color if accent else b.on_color(surface)
    foreground_disabled = b.disabled("text", surface)

    # button element images
    normal_img = recolor_element_image(image_key, surface, surface, surface)
    hovered_img = recolor_element_image(image_key, hovered, hovered, hovered)
    focused_img = recolor_element_image(image_key, surface, accent_color, focused)
    pressed_img = recolor_element_image(
        image_key, surface, accent_color, pressed, surface
    )
    disabled_img = recolor_element_image(image_key, surface, surface, surface, surface)

    b.create_style_element_image(
        ElementImage(
            f"{ttk_style}.Button.border",
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

    b.create_style_layout(
        ttk_style,
        button_layout(ttk_style),
    )

    b.configure_style(
        ttk_style,
        background=surface,
        foreground=foreground_normal,
        relief="flat",
        stipple="gray12",
        padding=button_padding(b, icon_only, density),
        anchor=anchor,
        font=button_font(density),
    )

    state_spec = dict(
        foreground=[("disabled", foreground_disabled), ("", foreground_normal)],
        background=[("disabled", surface)],
    )

    state_spec = apply_icon_mapping(
        b, options, state_spec, icon_size(icon_only, density)
    )

    b.map_style(ttk_style, **state_spec)


@BootstyleBuilderTTk.register_builder("selectbox_item", "TButton")
def build_selectbox_item_button_style(
    b: BootstyleBuilderTTk, ttk_style: str, accent: str = None, **options
):
    """Configure the style for selectbox dropdown items with selected state support.

    Style options include:
        * icon
        * icon_only
        * anchor
        * density
    """
    anchor = options.get("anchor", "w")
    accent_token = accent or "primary"
    surface_token = options.get("surface", "content")
    density = options.get("density", "default")

    surface = b.color(surface_token)
    on_surface = b.on_color(surface)
    on_disabled = b.disabled("text", surface)

    active = b.elevate(surface, 1)
    selected = b.color(accent_token)
    on_selected = b.on_color(selected)

    padding = (16, 3) if density != "compact" else (10, 2)

    b.configure_style(
        ttk_style,
        background=surface,
        foreground=on_surface,
        relief="flat",
        stipple="gray12",
        padding=padding,
        anchor=anchor,
        font=button_font(density),
        focuscolor="",
    )

    state_spec = dict(
        foreground=[
            ("disabled", on_disabled),
            ("selected !disabled", on_selected),
            ("pressed", on_selected),
            ("", on_surface),
        ],
        background=[
            ("selected !disabled", selected),
            ("pressed !disabled", selected),
            ("active !disabled", active),
            ("", surface),
        ],
    )

    b.map_style(ttk_style, **state_spec)
