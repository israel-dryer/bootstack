from __future__ import annotations

from typing import Optional

from bootstack.style.bootstyle_builder_ttk import BootstyleBuilderTTk
from bootstack.style.element import Element, ElementImage
from bootstack.style.utility import recolor_element_image
from bootstack.style.builders.utils import (
    normalize_button_density,
    button_font,
    apply_icon_mapping,
)


def _selection_wash(b: BootstyleBuilderTTk, accent: str, background: str, options: dict) -> str:
    """Row selection background — NEUTRAL by default; accent only when opted in.

    Governs the row's background wash only. The selection control's glyph still
    follows the accent (it reads as the accent indicator regardless). `wash=False`
    drops the wash entirely (selection shown via the control); `accent_selection`
    requests the old accent-tinted wash.
    """
    if not options.get('wash', True):
        return background
    if options.get('accent_selection', False):
        return b.subtle(accent or 'primary', background)
    return b.active(background)


@BootstyleBuilderTTk.register_builder('container', 'ListView.TFrame')
def build_list_container_style(b: BootstyleBuilderTTk, ttk_style: str, accent: str = None, **options):
    """List container frame style - no hover state (only items should have hover)."""
    surface_token = options.get('surface', 'content')
    background = b.color(surface_token)
    b.configure_style(ttk_style, background=background, relief='flat')


@BootstyleBuilderTTk.register_builder('list', 'ListView.TFrame')
def build_list_frame_style(b: BootstyleBuilderTTk, ttk_style: str, accent: str = None, **options):
    """List internal frame style - has state mapping to sync with parent ListItem."""
    hoverable = options.get('hoverable', True)
    accent_token = accent or 'primary'
    surface_token = options.get('surface', 'content')
    base_token = surface_token.split('[')[0]
    background = b.color(surface_token)
    pressed = b.pressed(background)
    selected = _selection_wash(b, accent, background, options)
    b.configure_style(ttk_style, background=background, relief='flat')

    # No hover wash and no 'focus' wash: rows show selection only (keyboard focus
    # rides the row image's bar). Row hover was removed — it competed with the
    # stripe and selection washes (several subtle colors at once) and is gone in
    # DataTable too, so this keeps the data widgets consistent.
    background_state_map = [
        ('selected', selected),
        ('', background)
    ]

    b.map_style(ttk_style, background=[x for x in background_state_map if x is not None])


@BootstyleBuilderTTk.register_builder('item', 'ListView.TFrame')
def build_list_item_default_style(b: BootstyleBuilderTTk, ttk_style: str, accent: str = None, **options):
    build_list_item_style(b, ttk_style, accent, 'list-item', **options)


@BootstyleBuilderTTk.register_builder('separated_item', 'ListView.TFrame')
def build_list_item_separated_style(b: BootstyleBuilderTTk, ttk_style: str, accent: str = None, **options):
    build_list_item_style(b, ttk_style, accent, 'list-item-separated', **options)


def build_list_item_style(
        b: BootstyleBuilderTTk,
        ttk_style: str,
        accent: Optional[str] = None,
        variant: str = 'item',
        **options
):
    # TODO add density option

    hoverable = options.get('hoverable', True)
    surface_token = options.get('surface', 'content')
    base_token = surface_token.split('[')[0]
    accent_token = accent or 'primary'

    background = b.color(surface_token)
    pressed = b.pressed(background)
    selected = _selection_wash(b, accent, background, options)

    # Use separated image for separated variant, otherwise use standard list_item
    is_separated = 'separated' in variant
    image_key = 'listrow_default'
    # An explicit `separator` color overrides the derived border — used to draw
    # the divider in the stripe color so striped+separated rows read as one tone.
    separator = options.get('separator')
    if is_separated:
        border_normal = b.color(separator) if separator else b.border(background)
    else:
        border_normal = background

    def _bd(fill):
        # Separated rows draw a real bottom separator (border_normal); otherwise
        # the border tracks the fill so it stays invisible in every state. Without
        # this, hover/selected rows showed a stray 1px frame (the border channel
        # kept the base background while the fill changed).
        return border_normal if is_separated else fill

    # The magenta channel of the row image is the focus ring; paint it the
    # foreground color but ONLY on the 'background focus' state (keyboard focus
    # via visual_focus — see _runtime/visual_focus.py). Mouse focus has 'focus'
    # but not 'background', so it shows no ring. Other (non-focus) images paint
    # the ring channel = fill so it stays invisible.
    focus_ring = b.color('foreground')

    normal_img = recolor_element_image(image_key, background, _bd(background), background, None, border_normal)
    # No left selection bar: the indicator channels match the selected fill so it
    # stays invisible (selection reads via the row wash + accent checkbox, aligned
    # with DataTable).
    selected_img = recolor_element_image(image_key, selected, _bd(selected), selected, None, selected)

    # Keyboard-focus bar images (bar on the current fill). Row hover was removed
    # (it competed with stripe/selection washes), so there is no hover variant —
    # the bar only needs a normal and a selected fill.
    focus_ring_img = recolor_element_image(image_key, background, _bd(background), focus_ring, None, border_normal)
    selected_focus_img = recolor_element_image(image_key, selected, _bd(selected), focus_ring, None, selected)

    image_state_specs = [
        ('selected background focus', selected_focus_img.image),
        ('selected', selected_img.image),
        ('background focus', focus_ring_img.image),
        ('', normal_img.image),
    ]

    b.create_style_element_image(
        ElementImage(f'{ttk_style}.border', normal_img.image, sticky='nsew', border=normal_img.meta.border).state_specs(
            [x for x in image_state_specs if x is not None]
        )
    )

    b.create_style_layout(
        ttk_style,
        Element(f'{ttk_style}.border', sticky='nsew').children(
            [
                Element(f'{ttk_style}.padding', sticky='')
            ]
        )
    )
    b.configure_style(ttk_style, background=background, relief='flat')


@BootstyleBuilderTTk.register_builder('list', 'ListView.TButton')
def build_list_item_button_style(b: BootstyleBuilderTTk, ttk_style: str, accent: str = None, **options):
    hoverable = options.get('hoverable', True)
    surface_token = options.get('surface', 'content')
    base_token = surface_token.split('[')[0]
    density = normalize_button_density(options.get('density', 'default'))

    background = b.color(surface_token)
    pressed = b.pressed(background)
    selected = _selection_wash(b, accent, background, options)

    b.create_style_layout(
        ttk_style,
        Element('Label.border', sticky='nsew').children([
            Element('Label.padding', sticky='nsew').children([
                Element('Label.label', sticky='nsew')
            ])
        ])
    )

    # Selection + momentary press only — NO hover and NO plain-'focus' highlight.
    # 'selected' keeps the button fill matching a selected row; 'pressed' gives a
    # brief click feedback on the chevron. Row hover was removed (it competed with
    # the stripe/selection washes and never cleared cleanly across recycling).
    background_state_spec = [
        ('selected', selected),
        ('pressed', pressed),
    ]

    b.configure_style(ttk_style, background=background, padding=0, relief='flat', stipple='gray12', font=button_font(density))
    b.map_style(
        ttk_style,
        foreground=[],
        background=[x for x in background_state_spec if x is not None]
    )


@BootstyleBuilderTTk.register_builder('radio', 'ListView.TLabel')
def build_list_item_radio_label(b: BootstyleBuilderTTk, ttk_style: str, accent: str = None, **options):
    build_list_item_label(b, ttk_style, accent, 'list-radio', **options)


@BootstyleBuilderTTk.register_builder('check', 'ListView.TLabel')
def build_list_item_check_label(b: BootstyleBuilderTTk, ttk_style: str, accent: str = None, **options):
    build_list_item_label(b, ttk_style, accent, 'list-checkbox', **options)


@BootstyleBuilderTTk.register_builder('list', 'ListView.TLabel')
def build_list_item_default_label(b: BootstyleBuilderTTk, ttk_style: str, accent: str = None, **options):
    build_list_item_label(b, ttk_style, accent, 'list', **options)


def _list_icon_size(b: BootstyleBuilderTTk, density: str) -> int:
    """Get icon size for list items based on density.

    Args:
        b: The bootstyle builder instance.
        density: The density ('default' or 'compact').

    Returns:
        Scaled icon size in pixels.
    """
    return 16 if density == 'compact' else 18


@BootstyleBuilderTTk.register_builder('icon', 'ListView.TButton')
@BootstyleBuilderTTk.register_builder('icon', 'ListView.TLabel')
def build_list_icon(b: BootstyleBuilderTTk, ttk_style: str, accent: str = None, **options):
    hoverable = options.get('hoverable', True)
    surface_token = options.get('surface', 'content')
    base_token = surface_token.split('[')[0]
    density = normalize_button_density(options.get('density', 'default'))

    background = b.color(surface_token)
    pressed = b.pressed(background)
    selected = _selection_wash(b, accent, background, options)
    on_background = b.on_color(background)
    on_selected = b.on_color(selected)
    on_disabled = b.disabled('text', background)

    # Create layout (remove focus border)
    b.create_style_layout(
        ttk_style,
        Element('Label.border', sticky='nsew').children([
            Element('Label.padding', sticky='nsew').children([
                Element('Label.label', sticky='nsew')
            ])
        ])
    )

    # Configure style
    b.configure_style(
        ttk_style,
        background=background,
        foreground=on_background,
        padding=0,
        relief='flat',
        stipple='gray12',
        font=button_font(density),
    )

    foreground_state_spec = [
        ('disabled', on_disabled),
        ('selected pressed', on_selected),
        ('selected', on_selected),
        ('', on_background)
    ]

    # Selection only — no hover, no 'focus' wash. Row hover was removed (it
    # competed with the stripe/selection washes); the icon/chevron fill just
    # tracks the row's selected state so it stays consistent.
    background_state_spec = [
        ('selected', selected),
    ]

    # Prepare state spec
    state_spec = dict(
        foreground=[x for x in foreground_state_spec if x is not None],
        background=[x for x in background_state_spec if x is not None]
    )

    # Apply icon mapping if icon is provided - use density-aware icon size
    icon_size = _list_icon_size(b, density)
    state_spec = apply_icon_mapping(b, options, state_spec, icon_size)
    b.map_style(ttk_style, **state_spec)


@BootstyleBuilderTTk.register_builder('selection', 'ListView.TLabel')
def build_list_selection_icon(b: BootstyleBuilderTTk, ttk_style: str, accent: str = None, **options):
    """Selection checkbox/radio icon for list rows.

    Mirrors the DataTable selection markers: the glyph is a muted outline when
    unchecked and accent-filled when checked, so selection reads the same across
    both data-bound widgets (unlike a generic row icon, which stays foreground).
    """
    hoverable = options.get('hoverable', True)
    surface_token = options.get('surface', 'content')
    base_token = surface_token.split('[')[0]
    density = normalize_button_density(options.get('density', 'default'))

    background = b.color(surface_token)
    pressed = b.pressed(background)
    # Neutral row wash by default; the GLYPH foreground below stays accent so the
    # checked control is the accent indicator regardless of the wash.
    selected = _selection_wash(b, accent, background, options)
    accent_color = b.color(accent or 'primary')
    muted = b.color('muted')
    on_disabled = b.disabled('text', background)

    b.create_style_layout(
        ttk_style,
        Element('Label.border', sticky='nsew').children([
            Element('Label.padding', sticky='nsew').children([
                Element('Label.label', sticky='nsew')
            ])
        ])
    )

    b.configure_style(
        ttk_style,
        background=background,
        foreground=muted,
        padding=0,
        relief='flat',
        stipple='gray12',
        font=button_font(density),
    )

    foreground_state_spec = [
        ('disabled', on_disabled),
        ('selected', accent_color),   # accent-filled when checked
        ('alternate', accent_color),  # partially-selected parent (mixed) -> accent dash
        ('', muted),                  # muted outline when unchecked
    ]
    # Selection only — no hover, no 'focus' wash (row hover was removed).
    background_state_spec = [
        ('selected', selected),
    ]
    state_spec = dict(
        foreground=[x for x in foreground_state_spec if x is not None],
        background=[x for x in background_state_spec if x is not None],
    )
    # Fixed crisp size across densities so the control doesn't shrink/pixelate
    # in compact mode (used by both ListView and Tree selection markers).
    state_spec = apply_icon_mapping(b, options, state_spec, 18)
    b.map_style(ttk_style, **state_spec)


def build_list_item_label(b: BootstyleBuilderTTk, ttk_style: str, accent: str = None, variant: str = None, **options):
    """

    Style Options
    * surface
    * hoverable
    * foreground
    """
    hoverable = options.get('hoverable', True)
    surface_token = options.get('surface', 'content')
    base_token = surface_token.split('[')[0]
    foreground_token = options.get('foreground', None)

    background = b.color(surface_token)
    pressed = b.pressed(background)
    selected = _selection_wash(b, accent, background, options)
    on_background = b.color(foreground_token) if foreground_token else b.on_color(background)
    on_selected = b.on_color(selected)

    # Selection only — no hover wash, no 'focus' wash (keyboard focus = row bar).
    # Row hover was removed (competed with stripe/selection washes).
    background_state_spec = [
        ('selected', selected),
    ]

    b.configure_style(ttk_style, background=background, foreground=on_background)
    b.map_style(
        ttk_style,
        background=[x for x in background_state_spec if x is not None],
        foreground=[('selected', on_selected)]
    )
