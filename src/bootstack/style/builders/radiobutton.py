"""Radio Button widget style builders.

This module contains style builders for ttk.Radiobutton widgets and variants.
"""

from __future__ import annotations

from bootstack.style.bootstyle_builder_ttk import BootstyleBuilderTTk
from bootstack.style.element import Element, ElementImage
from bootstack.style.utility import create_transparent_image, recolor_element_image
from bootstack.style.builders.utils import icon_size, resolve_icon_spec


@BootstyleBuilderTTk.register_builder('default', 'TRadiobutton')
def build_radiobutton_style(b: BootstyleBuilderTTk, ttk_style: str, accent: str = 'primary', **options):
    accent_token = accent or 'primary'
    surface_token = options.get('surface', 'content')

    background = b.color(surface_token)
    background_hover = b.active(background)
    foreground = b.on_color(background)
    foreground_disabled = b.disabled('text', background)

    normal = b.color(accent_token)
    hovered = b.active(normal)
    border = b.border(background)
    focus = hovered
    focus_ring = b.focus_ring(normal, background)

    show_indicator = options.get('show_indicator', True)

    if show_indicator:
        spacer_img = create_transparent_image(6, 1)
        b.create_style_element_image(ElementImage(f'{ttk_style}.spacer', spacer_img, sticky="ew"))

        normal_checked_img = recolor_element_image('radio_selected', background, normal, background)
        normal_unchecked_img = recolor_element_image('radio_unselected', background, border, background)

        focus_checked_img = recolor_element_image('radio_selected', background, focus, focus_ring)
        focus_unchecked_img = recolor_element_image('radio_unselected', background_hover, focus, focus_ring)

        disabled_checked_img = recolor_element_image('radio_selected', background, foreground_disabled, background)
        disabled_unchecked_img = recolor_element_image('radio_unselected', background, foreground_disabled, background)

        b.create_style_element_image(
            ElementImage(f'{ttk_style}.indicator', normal_unchecked_img.image, sticky="ns", padding=b.scale(4)).state_specs(
                [
                    # Disabled states
                    ('disabled selected', disabled_checked_img.image),
                    ('disabled !selected !alternate', disabled_unchecked_img.image),

                    # Focused states
                    ('focus selected', focus_checked_img.image),
                    ('focus !selected !alternate', focus_unchecked_img.image),

                    # Normal base states
                    ('selected', normal_checked_img.image),
                    ('!selected !alternate', normal_unchecked_img.image),
                ]
            ))

    # Label-area icon: stateful, independent of show_indicator.
    # Accent color when selected, foreground when unselected.
    icon_images = []
    icon_spec_raw = resolve_icon_spec(options)
    if icon_spec_raw is not None:
        icon_spec = b.normalize_icon_spec(icon_spec_raw, icon_size(False, 'default'))
        fg_spec = [
            ('disabled', foreground_disabled),
            ('selected !disabled', normal),
            ('', foreground),
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