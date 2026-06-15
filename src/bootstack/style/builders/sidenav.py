"""Style builders for SideNav widget components.

This module provides navigation-specific styling with selection indicator bars.
"""

from __future__ import annotations

from typing import Optional

from bootstack.style.style_builder_ttk import StyleBuilderTtk
from bootstack.style.element import Element, ElementImage
from bootstack.style.utility import recolor_element_image, create_transparent_image, mix_colors
from bootstack.style.builders.utils import apply_icon_mapping, resolve_icon_spec
from bootstack.style.builders.toolbutton import (
    toolbutton_layout, button_padding, button_font, icon_size, normalize_button_density
)


@StyleBuilderTtk.register_builder('default', 'NavigationView.TFrame')
def build_navigationview_frame_style(b: StyleBuilderTtk, ttk_style: str, accent: Optional[str] = None, **options):
    """Build SideNav frame style for group expanders.

    Uses standard button assets (no selection indicator needed since
    groups don't get selected, only their child items do).
    """
    accent_token = accent or 'primary'
    surface_token = options.get('surface', 'content')
    density = options.get('density', 'default')
    image_key = f'button_{density}'

    surface = b.color(surface_token)
    surface_hover = b.color(f'{surface_token}_hover') if b.colors.get(f'{surface_token}_hover') else b.active(surface)
    surface_pressed = b.pressed(surface_hover)

    disabled = b.disabled()

    normal_img = recolor_element_image(image_key, surface, surface, surface, surface)
    hover_img = recolor_element_image(image_key, surface_hover, surface_hover, surface, surface)
    pressed_img = recolor_element_image(image_key, surface_pressed, surface_pressed, surface, surface)
    disabled_img = recolor_element_image(image_key, disabled, disabled, surface, surface)

    b.create_style_element_image(
        ElementImage(
            f'{ttk_style}.border', normal_img.image, sticky="nsew",
            border=normal_img.meta.border, padding=normal_img.meta.border
        ).state_specs(
            [
                ('disabled', disabled_img.image),
                ('pressed', pressed_img.image),
                ('hover', hover_img.image),
                ('', normal_img.image)
            ]))

    # Create layout to use the image-based border
    b.create_style_layout(
        ttk_style,
        Element(f'{ttk_style}.border', sticky="nsew")
    )

    b.configure_style(
        ttk_style,
        background=surface,
        relief='flat',
    )


@StyleBuilderTtk.register_builder('default', 'NavigationView.TLabel')
def build_navigationview_label_style(b: StyleBuilderTtk, ttk_style: str, accent: str = None, **options):
    """Build SideNav label style with state-aware foreground colors.

    Matches the ghost Toolbutton foreground color behavior.
    """
    accent_token = accent or 'primary'
    surface_token = options.get('surface', 'content')

    surface = b.color(surface_token)
    surface_hover = b.color(f'{surface_token}_hover') if b.colors.get(f'{surface_token}_hover') else b.active(surface)
    surface_pressed = b.pressed(surface_hover)
    on_surface = b.on_color(surface)

    accent_color = b.color(accent_token)
    active = b.subtle(accent_token, surface)

    on_disabled = b.disabled('text', surface)

    b.configure_style(
        ttk_style,
        background=surface,
        foreground=on_surface,
        relief='flat',
        font='body'
    )

    foreground_state_map = [
        ('disabled', on_disabled),
        ('selected', accent_color),
        ('', on_surface)
    ]

    background_state_map = [
        ('selected', active),
        ('disabled', surface),
        ('pressed !selected', surface_pressed),
        ('hover !selected', surface_hover),
        ('', surface)
    ]

    state_spec = dict(foreground=foreground_state_map, background=background_state_map)
    state_spec = apply_icon_mapping(b, options, state_spec)

    b.map_style(ttk_style, **state_spec)


@StyleBuilderTtk.register_builder('navigation', 'Toolbutton')
def build_navigation_toolbutton_style(b: StyleBuilderTtk, ttk_style: str, accent: str = None, **options):
    """Build navigation Toolbutton style with selection indicator.

    Uses nav-button assets with a left-side selection indicator bar
    that shows the accent color when selected.
    """
    accent_token = accent or 'primary'
    surface_token = options.get('surface', 'content')
    density = options.get('density', 'default')
    icon_only = options.get('icon_only', False)
    anchor = options.get('anchor', 'center' if icon_only else 'w')
    image_key = f'navitem_{normalize_button_density(density)}'

    surface = b.color(surface_token)
    surface_hover = b.color(f'{surface_token}_hover') if b.colors.get(f'{surface_token}_hover') else b.active(surface)
    surface_pressed = b.pressed(surface_hover)
    on_surface = b.on_color(surface)

    active = b.subtle(accent_token, surface)
    accent_color = b.color(accent_token)
    accent_pressed = b.pressed(active)

    disabled = b.disabled()
    on_disabled = b.disabled('text', disabled)

    # Normal states: indicator hidden (same color as button background)
    normal_img = recolor_element_image(image_key, surface, surface, surface, surface)
    hover_img = recolor_element_image(image_key, surface_hover, surface_hover, surface_hover, surface)
    pressed_img = recolor_element_image(image_key, surface_pressed, surface_pressed, surface_pressed, surface)

    # Selected states: in compact/icon-only mode the indicator matches the fill so it's invisible
    if icon_only:
        selected_img         = recolor_element_image(image_key, active,         active,         active,         surface)
        selected_hover_img   = recolor_element_image(image_key, active,         active,         active,         surface)
        selected_pressed_img = recolor_element_image(image_key, accent_pressed, accent_pressed, accent_pressed, surface)
    else:
        selected_img         = recolor_element_image(image_key, active,         active,         accent_color,   surface)
        selected_hover_img   = recolor_element_image(image_key, active,         active,         accent_color,   surface)
        selected_pressed_img = recolor_element_image(image_key, accent_pressed, accent_pressed, accent_color,   surface)

    disabled_img = recolor_element_image(image_key, disabled, disabled, disabled, surface)

    b.create_style_element_image(
        ElementImage(
            f'{ttk_style}.border', normal_img.image, sticky="nsew",
            border=normal_img.meta.border, padding=normal_img.meta.border
        ).state_specs(
            [
                ('disabled', disabled_img.image),
                ('selected pressed', selected_pressed_img.image),
                ('selected hover', selected_hover_img.image),
                ('selected', selected_img.image),
                ('pressed', pressed_img.image),
                ('hover', hover_img.image),
                ('', normal_img.image)
            ]))

    b.create_style_layout(
        ttk_style,
        toolbutton_layout(ttk_style),
    )

    b.configure_style(
        ttk_style,
        background=surface,
        foreground=on_surface,
        relief='flat',
        padding=button_padding(b, icon_only, density),
        anchor=anchor,
        font=button_font(density)
    )

    state_spec = dict(
        foreground=[
            ('disabled', on_disabled),
            ('selected', accent_color),
            ('', on_surface)
        ],
    )
    state_spec = apply_icon_mapping(b, options, state_spec, icon_size(icon_only, density))

    b.map_style(ttk_style, **state_spec)


@StyleBuilderTtk.register_builder('rail', 'Toolbutton')
def build_rail_toolbutton_style(b: StyleBuilderTtk, ttk_style: str, accent: str = None, **options):
    """Build the workspace-rail item — the VS Code activity-bar treatment.

    A radio toggle (single-select) rendered icon-only on the chrome surface:
    the glyph is muted when idle and full-strength when selected (or hovered),
    and the `navitem` asset's left indicator bar shows the **foreground** color
    when selected (neutral by default — accent is opt-in, like the buttons). The
    background stays flat in every state (no wash / no fill) — the bar carries the
    selection.
    """
    accent_token = accent  # None -> neutral
    surface_token = options.get('surface', 'chrome')
    density = options.get('density', 'default')
    icon_only = options.get('icon_only', True)
    # Labeled rail: a small caption under the icon (compound='top' on the widget)
    # instead of icon-only + tooltips. Dedicated variant, so we just flip the font.
    labeled = options.get('labeled', False)
    image_key = f'navitem_{normalize_button_density(density)}'

    surface = b.color(surface_token)
    surface_hover = b.color(f'{surface_token}_hover') if b.colors.get(f'{surface_token}_hover') else b.active(surface)
    surface_pressed = b.pressed(surface_hover)
    on_surface = b.on_color(surface)
    muted = b.muted_foreground(surface)
    # Neutral indicator bar by default (the foreground); when an accent is set
    # (`nav_accent`), the bar shows it.
    bar_color = b.color(accent_token) if accent_token else on_surface
    disabled = b.disabled()
    on_disabled = b.disabled('text', disabled)

    # Flat background throughout; the left bar is hidden (== fill) unless selected.
    normal_img  = recolor_element_image(image_key, surface, surface, surface, surface)
    hover_img   = recolor_element_image(image_key, surface_hover, surface_hover, surface_hover, surface)
    pressed_img = recolor_element_image(image_key, surface_pressed, surface_pressed, surface_pressed, surface)
    # Selected: foreground bar visible, background still flat (no wash).
    selected_img         = recolor_element_image(image_key, surface,         surface,         bar_color, surface)
    selected_hover_img   = recolor_element_image(image_key, surface_hover,   surface_hover,   bar_color, surface)
    selected_pressed_img = recolor_element_image(image_key, surface_pressed, surface_pressed, bar_color, surface)
    disabled_img = recolor_element_image(image_key, disabled, disabled, surface, surface)

    b.create_style_element_image(
        ElementImage(
            f'{ttk_style}.border', normal_img.image, sticky="nsew",
            border=normal_img.meta.border, padding=normal_img.meta.border
        ).state_specs(
            [
                ('disabled', disabled_img.image),
                ('selected pressed', selected_pressed_img.image),
                ('selected hover', selected_hover_img.image),
                ('selected', selected_img.image),
                ('pressed', pressed_img.image),
                ('hover', hover_img.image),
                ('', normal_img.image)
            ]))

    b.create_style_layout(ttk_style, toolbutton_layout(ttk_style))

    # Rail items are tall, near-square tap targets (VS Code activity bar), not the
    # icon-height of a normal icon-only toolbutton. Generous vertical padding +
    # anchor center gives the larger hit area and vertical rhythm. Labeled rails
    # use a smaller caption font and a touch more room for the stacked label.
    if labeled:
        rail_font = 'caption'
        rail_padding = options.get('padding') or b.scale((2, 8, 2, 8))
    else:
        rail_font = button_font(density)
        rail_padding = options.get('padding') or b.scale((0, 7, 0, 7))

    b.configure_style(
        ttk_style,
        background=surface,
        foreground=muted,
        relief='flat',
        padding=rail_padding,
        anchor='center',
        font=rail_font,
    )

    state_spec = dict(
        foreground=[
            ('disabled', on_disabled),
            ('selected', on_surface),
            ('hover', on_surface),
            ('', muted),
        ]
    )
    state_spec = apply_icon_mapping(b, options, state_spec, icon_size(icon_only, density))

    b.map_style(ttk_style, **state_spec)


# Sidebar nav item geometry. The icon is its OWN layout element so a real spacer
# can sit between it and the label — ttk gives no control over the compound
# image<->text gap, so the icon must be separated out (like the radio indicator).
_NAV_ICON_SIZE = 20
# Icon-only (compact) buttons read better with a slightly larger glyph and a
# taller, squarer footprint than the labeled rows.
_NAV_COMPACT_ICON_SIZE = 24
_NAV_GAP = 10
# Nine-patch content inset for nav items. Kept well below the asset border (the
# slice) so items don't carry the asset's full built-in padding as dead space
# between buttons.
_NAV_CONTENT_PAD = 4


def _nav_colors(b, accent_token, options):
    surface_token = options.get('surface', 'card')
    surface = b.color(surface_token)
    surface_hover = b.color(f'{surface_token}_hover') if b.colors.get(f'{surface_token}_hover') else b.active(surface)
    surface_pressed = b.pressed(surface_hover)
    on_surface = b.on_color(surface)
    disabled = b.disabled()
    on_disabled = b.disabled('text', disabled)
    return surface, surface_hover, surface_pressed, on_surface, disabled, on_disabled


def _nav_border_element(b, ttk_style, image_key, *, surface, surface_hover, surface_pressed,
                        selected_bg, selected_pressed, disabled):
    """Create a nav item's flat background nine-patch (no indicator bar).

    Channels are `(white=fill, black, magenta, transparent=surface)`. The edge
    channels (black/magenta) must blend correctly per asset:

    - the rounded `button` asset (pill) uses black=border / magenta=focus-ring,
      so both must match the **background** (surface) or the rounded edge fails to
      anti-alias and the pill reads square/haloed;
    - the square `navitem` asset (quiet) uses black as part of the fill and
      magenta as the (here hidden) indicator bar, so both must match the **fill**.

    The 4th channel (surface-behind) is always the surface so rounded corners
    blend into the region.
    """
    rounded = image_key.startswith('button')

    def img(fill):
        edge = surface if rounded else fill
        return recolor_element_image(image_key, fill, edge, edge, surface)

    normal_img   = img(surface)
    hover_img    = img(surface_hover)
    pressed_img  = img(surface_pressed)
    selected_img = img(selected_bg)
    selected_hover_img   = img(selected_bg)
    selected_pressed_img = img(selected_pressed)
    disabled_img = img(disabled)
    # `border` is the nine-patch slice (for the rounded corners); `padding` is the
    # asset's intended content inset (0 for navitem/card — no built-in dead space).
    # The button's height therefore comes from the configure padding only; spacing
    # BETWEEN items is the container's job (NavPanel pack).
    b.create_style_element_image(
        ElementImage(
            f'{ttk_style}.border', normal_img.image, sticky="nsew",
            border=normal_img.meta.border, padding=normal_img.meta.padding
        ).state_specs(
            [
                ('disabled', disabled_img.image),
                ('selected pressed', selected_pressed_img.image),
                ('selected hover', selected_hover_img.image),
                ('selected', selected_img.image),
                ('pressed', pressed_img.image),
                ('hover', hover_img.image),
                ('', normal_img.image)
            ]))


def _build_nav_expanded(b, ttk_style, *, accent_token, options, image_key, selected_bg, selected_fg):
    """Expanded nav item: icon element + spacer + text label (a real icon/text gap)."""
    density = options.get('density', 'default')
    surface, surface_hover, surface_pressed, on_surface, disabled, on_disabled = _nav_colors(b, accent_token, options)
    # Idle items are slightly muted (a light blend toward the surface) so the
    # selected item — and content headings — stay the brightest text. A gentle
    # mute, not the heavy header mute, so idle rows still sit above the section
    # headers in the 3-tier hierarchy (selected > idle > header).
    idle_fg = mix_colors(on_surface, surface, 0.85)
    _nav_border_element(
        b, ttk_style, image_key, surface=surface, surface_hover=surface_hover,
        surface_pressed=surface_pressed, selected_bg=selected_bg,
        selected_pressed=b.pressed(selected_bg), disabled=disabled,
    )

    fg_spec = [('disabled', on_disabled), ('selected', selected_fg), ('', idle_fg)]

    # Icon as its own stateful element (recolored to follow the text foreground).
    icon_spec = resolve_icon_spec(options)
    has_icon = False
    if icon_spec:
        spec = b.normalize_icon_spec(icon_spec, _NAV_ICON_SIZE)
        icon_map = b.map_stateful_icons(spec, fg_spec)
        if icon_map:
            has_icon = True
            b.create_style_element_image(
                ElementImage(f'{ttk_style}.icon', icon_map[-1][1], sticky="").state_specs(icon_map))

    # Spacer between icon and text; collapses to ~0 in icon-only (the 'alternate'
    # state) so the same layout also serves the compacted item.
    gap = create_transparent_image(_NAV_GAP, 1)
    gap0 = create_transparent_image(1, 1)
    b.create_style_element_image(
        ElementImage(f'{ttk_style}.spacer', gap, sticky="").state_specs([('alternate', gap0), ('', gap)]))

    row = []
    if has_icon:
        row.append(Element(f'{ttk_style}.icon', side="left", sticky=""))
        row.append(Element(f'{ttk_style}.spacer', side="left", sticky=""))
    row.append(Element('Toolbutton.label', side="left", sticky="nsew"))
    b.create_style_layout(
        ttk_style,
        Element(f'{ttk_style}.border', sticky="nsew").children(
            [Element('Toolbutton.padding', sticky="nsew").children(row)]))

    b.configure_style(
        ttk_style, background=surface, foreground=idle_fg, relief='flat',
        padding=options.get('padding') or b.scale((10, 8, 10, 8)),
        anchor=options.get('anchor', 'w'), font=button_font(density),
    )
    # Only the text label's foreground here — the icon element carries its own.
    b.map_style(ttk_style, foreground=fg_spec)


def _build_nav_compact(b, ttk_style, *, accent_token, options, image_key, selected_bg, selected_fg):
    """Compact nav item: a single centered icon (icon-only)."""
    density = options.get('density', 'default')
    surface, surface_hover, surface_pressed, on_surface, disabled, on_disabled = _nav_colors(b, accent_token, options)
    idle_fg = mix_colors(on_surface, surface, 0.85)  # slight idle mute (see _build_nav_expanded)
    _nav_border_element(
        b, ttk_style, image_key, surface=surface, surface_hover=surface_hover,
        surface_pressed=surface_pressed, selected_bg=selected_bg,
        selected_pressed=b.pressed(selected_bg), disabled=disabled,
    )
    b.create_style_layout(ttk_style, toolbutton_layout(ttk_style))
    b.configure_style(
        ttk_style, background=surface, foreground=idle_fg, relief='flat',
        # No horizontal padding: the compact sidebar is only the rail width, and
        # the icon centers via anchor; a bit more vertical padding makes the
        # icon-only buttons taller/squarer.
        padding=options.get('padding') or b.scale((0, 10, 0, 10)), anchor='center',
        font=button_font(density),
    )
    state_spec = dict(foreground=[('disabled', on_disabled), ('selected', selected_fg), ('', idle_fg)])
    state_spec = apply_icon_mapping(b, options, state_spec, _NAV_COMPACT_ICON_SIZE)
    b.map_style(ttk_style, **state_spec)


def _selection_colors(b, accent_token, options):
    """Selected nav-item (background, foreground), per accent + selection style.

    Neutral by default (a light active-level wash + neutral fg). With an accent:
    `'ghost'` (default) = a subtle accent wash + **full foreground** text;
    `'solid'` = the solid accent filled + the on-accent (e.g. white) fg — the
    higher-emphasis look. Solid needs an accent; without one falls back to neutral.

    The ghost foreground is the full foreground (bright on dark, dark on light),
    NOT the accent — accent text is too dim for low-luminance hues (blue) to pop
    consistently. The accent identity instead lives in the wash + the indicator
    bar, which read by hue regardless of luminance, so selection pops uniformly
    across every accent. Idle items are muted, so the bright selected text stands
    out (the prominence is luminance, not color).
    """
    surface = b.color(options.get('surface', 'card'))
    if accent_token:
        if options.get('selection_style') == 'solid':
            fill = b.color(accent_token)
            return fill, b.on_color(fill)
        return b.subtle(accent_token, surface), b.on_color(surface)
    return b.active(surface), b.on_color(surface)


def _quiet_colors(b, accent_token, options):
    return _selection_colors(b, accent_token, options)


def _pill_colors(b, accent_token, options):
    return _selection_colors(b, accent_token, options)


@StyleBuilderTtk.register_builder('nav-quiet', 'Toolbutton')
def build_nav_quiet_toolbutton_style(b: StyleBuilderTtk, ttk_style: str, accent: str = None, **options):
    """Quiet sidebar nav item (under a rail): subtle wash, neutral fg, no bar."""
    accent_token = accent  # None -> neutral
    image_key = f'navitem_{normalize_button_density(options.get("density", "default"))}'
    sel_bg, sel_fg = _quiet_colors(b, accent_token, options)
    _build_nav_expanded(b, ttk_style, accent_token=accent_token, options=options,
                        image_key=image_key, selected_bg=sel_bg, selected_fg=sel_fg)


@StyleBuilderTtk.register_builder('nav-quiet-compact', 'Toolbutton')
def build_nav_quiet_compact_toolbutton_style(b: StyleBuilderTtk, ttk_style: str, accent: str = None, **options):
    """Quiet nav item compacted to a centered icon."""
    accent_token = accent  # None -> neutral
    image_key = f'navitem_{normalize_button_density(options.get("density", "default"))}'
    sel_bg, sel_fg = _quiet_colors(b, accent_token, options)
    _build_nav_compact(b, ttk_style, accent_token=accent_token, options=options,
                       image_key=image_key, selected_bg=sel_bg, selected_fg=sel_fg)


@StyleBuilderTtk.register_builder('nav-pill', 'Toolbutton')
def build_nav_pill_toolbutton_style(b: StyleBuilderTtk, ttk_style: str, accent: str = None, **options):
    """Standalone sidebar nav item: a rounded accent pill + accent fg (macOS vibe).

    The primary nav (no rail): the selected row gets a rounded accent-tinted pill
    (the `card` asset — black/white only, no focus-ring band) with accent
    foreground. Distinct from the quiet under-a-rail treatment (square wash +
    neutral fg).
    """
    accent_token = accent  # None -> neutral
    image_key = 'card'
    sel_bg, sel_fg = _pill_colors(b, accent_token, options)
    _build_nav_expanded(b, ttk_style, accent_token=accent_token, options=options,
                        image_key=image_key, selected_bg=sel_bg, selected_fg=sel_fg)


@StyleBuilderTtk.register_builder('nav-pill-compact', 'Toolbutton')
def build_nav_pill_compact_toolbutton_style(b: StyleBuilderTtk, ttk_style: str, accent: str = None, **options):
    """Standalone nav item compacted to a centered icon (rounded pill on select)."""
    accent_token = accent  # None -> neutral
    image_key = 'card'
    sel_bg, sel_fg = _pill_colors(b, accent_token, options)
    _build_nav_compact(b, ttk_style, accent_token=accent_token, options=options,
                       image_key=image_key, selected_bg=sel_bg, selected_fg=sel_fg)


@StyleBuilderTtk.register_builder('default', 'NavigationButton.TFrame')
def build_navigationbutton_frame_style(b: StyleBuilderTtk, ttk_style: str, accent: str = None, **options):
    """Build NavigationButton frame style with selection indicator.

    Uses nav-button assets with a left-side selection indicator bar
    that shows the accent color when selected. This is the container
    frame for the composite navigation button.
    """
    accent_token = accent or 'primary'
    surface_token = options.get('surface', 'content')
    density = options.get('density', 'default')
    icon_only = options.get('icon_only', False)
    image_key = f'navitem_{normalize_button_density(density)}'

    surface = b.color(surface_token)
    surface_hover = b.color(f'{surface_token}_hover') if b.colors.get(f'{surface_token}_hover') else b.active(surface)
    surface_pressed = b.pressed(surface_hover)

    active = b.subtle(accent_token, surface)
    accent_color = b.color(accent_token)
    accent_pressed = b.pressed(active)

    disabled = b.disabled()

    # Normal states: indicator hidden (same color as button background)
    normal_img = recolor_element_image(image_key, surface, surface, surface, surface)
    hover_img = recolor_element_image(image_key, surface_hover, surface_hover, surface_hover, surface)
    pressed_img = recolor_element_image(image_key, surface_pressed, surface_pressed, surface_pressed, surface)

    # Selected states: in compact/icon-only mode the indicator matches the fill so it's invisible
    if icon_only:
        selected_img         = recolor_element_image(image_key, active,         active,         active,         surface)
        selected_hover_img   = recolor_element_image(image_key, active,         active,         active,         surface)
        selected_pressed_img = recolor_element_image(image_key, accent_pressed, accent_pressed, accent_pressed, surface)
    else:
        selected_img         = recolor_element_image(image_key, active,         active,         accent_color,   surface)
        selected_hover_img   = recolor_element_image(image_key, active,         active,         accent_color,   surface)
        selected_pressed_img = recolor_element_image(image_key, accent_pressed, accent_pressed, accent_color,   surface)

    disabled_img = recolor_element_image(image_key, disabled, disabled, disabled, surface)

    b.create_style_element_image(
        ElementImage(
            f'{ttk_style}.border', normal_img.image, sticky="ew",
            border=normal_img.meta.border
        ).state_specs(
            [
                ('disabled', disabled_img.image),
                ('selected pressed', selected_pressed_img.image),
                ('selected hover', selected_hover_img.image),
                ('selected', selected_img.image),
                ('pressed', pressed_img.image),
                ('hover', hover_img.image),
                ('', normal_img.image)
            ]))

    # Create layout to use the image-based border
    b.create_style_layout(
        ttk_style,
        Element(f'{ttk_style}.border', sticky="nsew")
    )

    b.configure_style(
        ttk_style,
        background=surface,
        relief='flat',
    )


@StyleBuilderTtk.register_builder('default', 'NavigationButton.TLabel')
def build_navigationbutton_label_style(b: StyleBuilderTtk, ttk_style: str, accent: str = None, **options):
    """Build NavigationButton label style with state-aware colors.

    Labels inside the navigation button container that respond to
    hover, pressed, and selected states.
    """
    accent_token = accent or 'primary'
    surface_token = options.get('surface', 'content')
    icon_only = options.get('icon_only', False)
    density = options.get('density', 'default')

    surface = b.color(surface_token)
    surface_hover = b.color(f'{surface_token}_hover') if b.colors.get(f'{surface_token}_hover') else b.active(surface)
    surface_pressed = b.pressed(surface_hover)
    on_surface = b.on_color(surface)

    accent_color = b.color(accent_token)
    active = b.subtle(accent_token, surface)
    active_pressed = b.pressed(active)

    on_disabled = b.disabled('text', surface)

    b.configure_style(
        ttk_style,
        background=surface,
        foreground=on_surface,
        relief='flat',
        font='body'
    )

    foreground_state_map = [
        ('disabled', on_disabled),
        ('selected', accent_color),
        ('', on_surface)
    ]

    background_state_map = [
        ('disabled', surface),
        ('selected pressed', active_pressed),
        ('selected', active),
        ('pressed !selected', surface_pressed),
        ('hover !selected', surface_hover),
        ('', surface)
    ]

    state_spec = dict(foreground=foreground_state_map, background=background_state_map)

    # Navigation icons use a smaller size than standalone icon buttons
    # to stay visually consistent with context menu popup icons
    nav_icon_size = 20 if icon_only else icon_size(icon_only, density)
    state_spec = apply_icon_mapping(b, options, state_spec, nav_icon_size)

    b.map_style(ttk_style, **state_spec)