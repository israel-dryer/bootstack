"""Scrollbar style builders.

This module contains style builders for ttk.Scrollbar widget variants.
"""
from typing import Optional

from bootstack.style.bootstyle_builder_ttk import BootstyleBuilderTTk
from bootstack.style.element import Element, ElementImage
from bootstack.style.utility import recolor_element_image


def build_horizontal_scrollbar(b: BootstyleBuilderTTk, ttk_style: str, accent: Optional[str] = None, **options):
    surface_token = options.get('surface', 'content')
    surface = b.color(surface_token)
    border_color = b.border(surface)

    thumb_normal = b.color(accent) if accent is not None else border_color
    thumb_active = b.active(thumb_normal)
    thumb_pressed = b.pressed(thumb_normal)

    b.create_style_layout(
        ttk_style,
        Element('Horizontal.Scrollbar.trough', sticky="we").children([
            Element(f'{ttk_style}.thumb', sticky="ew"),
        ])
    )

    b.configure_style(
        ttk_style,
        background=thumb_normal,
        troughcolor=surface,
        padding=0,
        bordercolor=surface,
        darkcolor=thumb_normal,
        lightcolor=thumb_normal,
        gripcount=0,
        relief='flat',
        arrowsize=0,
    )
    b.map_style(
        ttk_style,
        background=[('pressed', thumb_pressed), ('active', thumb_active)],
        darkcolor=[('pressed', thumb_pressed), ('active', thumb_active)],
        lightcolor=[('pressed', thumb_pressed), ('active', thumb_active)],
    )


def build_vertical_scrollbar(b: BootstyleBuilderTTk, ttk_style: str, accent: Optional[str] = None, **options):
    surface_token = options.get('surface', 'content')
    surface = b.color(surface_token)
    border_color = b.border(surface)

    thumb_normal = b.color(accent) if accent is not None else border_color
    thumb_active = b.active(thumb_normal)
    thumb_pressed = b.pressed(thumb_normal)

    b.create_style_layout(
        ttk_style,
        Element('Vertical.Scrollbar.trough', sticky="ns").children([
            Element(f'{ttk_style}.thumb', sticky="ns"),
        ]),
    )

    b.configure_style(
        ttk_style,
        background=thumb_normal,
        troughcolor=surface,
        padding=0,
        bordercolor=surface,
        darkcolor=thumb_normal,
        lightcolor=thumb_normal,
        gripcount=0,
        relief='flat',
        arrowsize=0,
    )
    b.map_style(
        ttk_style,
        background=[('pressed', thumb_pressed), ('active', thumb_active)],
        darkcolor=[('pressed', thumb_pressed), ('active', thumb_active)],
        lightcolor=[('pressed', thumb_pressed), ('active', thumb_active)],
    )


@BootstyleBuilderTTk.register_builder('default', 'TScrollbar')
def build_rounded_scrollbar_style(b: BootstyleBuilderTTk, ttk_style: str, accent: str = None, **options):
    if options.get('orient', 'vertical') == 'vertical':
        _build_rounded_vertical_scrollbar(b, ttk_style, accent, **options)
    else:
        _build_rounded_horizontal_scrollbar(b, ttk_style, accent, **options)


def _build_rounded_vertical_scrollbar(b: BootstyleBuilderTTk, ttk_style: str, accent: Optional[str] = None, **options):
    surface_token = options.get('surface', 'content')
    surface = b.color(surface_token)
    border_color = b.border(surface)

    thumb_normal = b.color(accent) if accent is not None else border_color
    thumb_active = b.active(thumb_normal)
    thumb_pressed = b.pressed(thumb_normal)

    thumb_normal_img = recolor_element_image('scrollbar_vertical', thumb_normal, thumb_active, surface, surface)
    thumb_active_img = recolor_element_image('scrollbar_vertical', thumb_active, thumb_active, surface, surface)
    thumb_pressed_img = recolor_element_image('scrollbar_vertical', thumb_pressed, thumb_pressed, surface, surface)

    b.create_style_element_image(
        ElementImage(
            f'{ttk_style}.thumb', thumb_normal_img.image,
            padding=thumb_normal_img.meta.border, border=thumb_normal_img.meta.border,
            width=thumb_normal_img.meta.width, height=thumb_normal_img.meta.height).state_specs(
            [
                ('pressed', thumb_pressed_img.image),
                ('active', thumb_active_img.image),
                ('', thumb_normal_img.image),
            ]),
    )

    b.create_style_layout(
        ttk_style,
        Element('Vertical.Scrollbar.trough', sticky="ns").children([
            Element(f'{ttk_style}.thumb', sticky="ns"),
        ]),
    )

    b.configure_style(
        ttk_style,
        troughcolor=surface,
        bordercolor=surface,
        relief='flat',
        arrowsize=0,
    )


def _build_rounded_horizontal_scrollbar(b: BootstyleBuilderTTk, ttk_style: str, accent: Optional[str] = None, **options):
    surface_token = options.get('surface', 'content')
    surface = b.color(surface_token)
    border_color = b.border(surface)

    thumb_normal = b.color(accent) if accent is not None else border_color
    thumb_active = b.active(thumb_normal)
    thumb_pressed = b.pressed(thumb_normal)

    thumb_normal_img = recolor_element_image('scrollbar_horizontal', thumb_normal, thumb_active, surface, surface)
    thumb_active_img = recolor_element_image('scrollbar_horizontal', thumb_active, thumb_active, surface, surface)
    thumb_pressed_img = recolor_element_image('scrollbar_horizontal', thumb_pressed, thumb_pressed, surface, surface)

    b.create_style_element_image(
        ElementImage(
            f'{ttk_style}.thumb', thumb_normal_img.image,
            padding=thumb_normal_img.meta.border, border=thumb_normal_img.meta.border,
            width=thumb_normal_img.meta.width, height=thumb_normal_img.meta.height).state_specs(
            [
                ('pressed', thumb_pressed_img.image),
                ('active', thumb_active_img.image),
                ('', thumb_normal_img.image),
            ]),
    )

    b.create_style_layout(
        ttk_style,
        Element('Horizontal.Scrollbar.trough', sticky="we").children([
            Element(f'{ttk_style}.thumb', sticky="ew"),
        ])
    )

    b.configure_style(
        ttk_style,
        troughcolor=surface,
        bordercolor=surface,
        relief='flat',
        arrowsize=0,
    )
