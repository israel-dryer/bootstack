"""Radio Button widget style builders.

This module contains style builders for ttk.Radiobutton widgets and variants.
"""

from __future__ import annotations

from bootstack.style.bootstyle_builder_ttk import BootstyleBuilderTTk
from bootstack.style.element import Element, ElementImage
from bootstack.style.utility import create_transparent_image, recolor_element_image
from bootstack.style.builders.utils import resolve_icon_spec

# Label-area custom state icons act as the state indicator, so they read a touch
# larger than a text accent icon.
_STATE_ICON_SIZE = 22


@BootstyleBuilderTTk.register_builder('default', 'TRadiobutton')
def build_radiobutton_style(b: BootstyleBuilderTTk, ttk_style: str, accent: str = 'primary', **options):
    accent_token = accent or 'primary'
    surface_token = options.get('surface', 'content')

    background = b.color(surface_token)
    foreground = b.on_color(background)
    foreground_disabled = b.disabled('text', background)

    normal = b.color(accent_token)
    border = b.muted_foreground(background)
    focus = b.focus(normal)
    focus_ring = b.color('foreground')

    show_indicator = options.get('show_indicator', True)

    if show_indicator:
        spacer_img = create_transparent_image(6, 1)
        b.create_style_element_image(ElementImage(f'{ttk_style}.spacer', spacer_img, sticky="ew"))

        normal_selected_img = recolor_element_image('radiobutton', normal, normal, background, background)
        normal_unselected_img = recolor_element_image('radiobutton', background, border, background, background)

        focus_selected_img = recolor_element_image('radiobutton', focus, focus, focus_ring, background)
        focus_unselected_img = recolor_element_image('radiobutton', background, focus, focus_ring, background)

        disabled_selected_img = recolor_element_image('radiobutton', foreground_disabled, foreground_disabled, background, background)
        disabled_unselected_img = recolor_element_image('radiobutton', background, foreground_disabled, background, background)

        b.create_style_element_image(
            ElementImage(f'{ttk_style}.indicator', normal_unselected_img.image, sticky="ns", padding=b.scale(4)).state_specs(
                [
                    # Disabled states
                    ('disabled selected', disabled_selected_img.image),
                    ('disabled !selected !alternate', disabled_unselected_img.image),

                    # Focused states
                    ('background focus selected', focus_selected_img.image),
                    ('background focus !selected !alternate', focus_unselected_img.image),

                    # Normal base states
                    ('selected', normal_selected_img.image),
                    ('!selected !alternate', normal_unselected_img.image),
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
    layout_children.append(Element('Radiobutton.label', side="left", sticky="nsew"))

    b.create_style_layout(
        ttk_style, Element('Radiobutton.padding', sticky="nsew").children(layout_children)
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