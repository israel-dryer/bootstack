"""Checkbutton widget style builders.

This module contains style builders for ttk.Checkbutton widgets and variants.
"""

from __future__ import annotations

from bootstack.style.bootstyle_builder_ttk import BootstyleBuilderTTk
from bootstack.style.element import Element, ElementImage
from bootstack.style.utility import create_transparent_image, recolor_element_image
from bootstack.style.builders.utils import resolve_icon_spec

# Label-area custom state icons act as the state indicator, so they read a touch
# larger than a text accent icon.
_STATE_ICON_SIZE = 22


@BootstyleBuilderTTk.register_builder('default', 'TCheckbutton')
def build_checkbutton_style(b: BootstyleBuilderTTk, ttk_style: str, accent: str = 'primary', **options):
    accent_token = accent or 'primary'
    surface_token = options.get('surface', 'content')

    background = b.color(surface_token)
    background_hover = b.active(background)
    foreground = b.on_color(background)
    foreground_disabled = b.disabled('text', background)

    normal = b.color(accent_token)
    border = b.muted_foreground(background)
    focus = b.focus(normal)
    focus_ring = b.color('foreground')
    disabled = b.disabled()

    show_indicator = options.get('show_indicator', True)

    if show_indicator:
        spacer_img = create_transparent_image(6, 1)
        b.create_style_element_image(ElementImage(f'{ttk_style}.spacer', spacer_img, sticky="ew"))

        normal_checked_img = recolor_element_image('checkbox_checked', background, normal, background, background)
        normal_unchecked_img = recolor_element_image('checkbox_unchecked', background, border, background, background)
        normal_indeterminate_img = recolor_element_image('checkbox_indeterminate', background, normal, background, background)

        focus_checked_img = recolor_element_image('checkbox_checked', background, focus, focus_ring, background)
        focus_unchecked_img = recolor_element_image('checkbox_unchecked', background_hover, focus, focus_ring, background)
        focus_indeterminate_img = recolor_element_image('checkbox_indeterminate', background, focus, focus_ring, background)

        disabled_checked_img = recolor_element_image(
            'checkbox_checked', disabled, foreground_disabled, background, background)
        disabled_unchecked_img = recolor_element_image(
            'checkbox_unchecked', foreground_disabled, foreground_disabled, background, background)
        disabled_indeterminate_img = recolor_element_image(
            'checkbox_indeterminate', disabled, foreground_disabled, background, background)

        b.create_style_element_image(
            ElementImage(f'{ttk_style}.indicator', normal_unchecked_img.image, sticky="ns").state_specs(
                [
                    # Disabled states
                    ('disabled alternate !selected', disabled_indeterminate_img.image),
                    ('disabled selected', disabled_checked_img.image),
                    ('disabled !selected !alternate', disabled_unchecked_img.image),

                    # Focused states
                    ('background focus alternate !selected', focus_indeterminate_img.image),
                    ('background focus selected', focus_checked_img.image),
                    ('background focus !selected !alternate', focus_unchecked_img.image),

                    # Normal base states
                    ('alternate !selected', normal_indeterminate_img.image),
                    ('selected', normal_checked_img.image),
                    ('!selected !alternate', normal_unchecked_img.image),
                ]
            ))

    # Label-area icon: stateful, independent of show_indicator.
    # Accent color when selected, foreground when unselected.
    icon_images = []
    icon_spec_raw = resolve_icon_spec(options)
    if icon_spec_raw is not None:
        icon_spec = b.normalize_icon_spec(icon_spec_raw, _STATE_ICON_SIZE)
        fg_spec = [
            ('disabled', foreground_disabled),
            ('selected !disabled', normal),
            ('', border),
        ]
        icon_images = b.map_stateful_icons(icon_spec, fg_spec)

    layout_children = []
    if show_indicator:
        layout_children += [
            Element(f'{ttk_style}.indicator', side="left", sticky=""),
            Element(f'{ttk_style}.spacer', side="left"),
        ]
    layout_children.append(Element('Checkbutton.label', side="left", sticky="nsew"))

    b.create_style_layout(
        ttk_style, Element('Checkbutton.padding', sticky="nsew").children(layout_children)
    )

    b.configure_style(ttk_style, background=background, foreground=foreground, font="body")

    map_kwargs = {
        'background': [],
        'foreground': [('disabled', foreground_disabled), ('', foreground)],
    }
    if icon_images:
        map_kwargs['image'] = icon_images
        if not options.get('icon_only', False):
            map_kwargs['compound'] = 'left'
    b.map_style(ttk_style, **map_kwargs)