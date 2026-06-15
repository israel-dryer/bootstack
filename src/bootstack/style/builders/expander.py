"""Style builders for the Expander widget."""
from typing import Optional

from bootstack.style.style_builder_ttk import StyleBuilderTtk
from bootstack.style.builders.utils import apply_icon_mapping


@StyleBuilderTtk.register_builder('solid', 'Expander.TFrame')
def build_solid_expander_header_style(b: StyleBuilderTtk, ttk_style: str, accent: Optional[str] = None, **options):
    # use a subtle background with foreground if normal, otherwise subtle accent with accent foreground

    accent = b.default(accent or 'primary')
    surface_token = options.get('surface', 'content')
    surface = b.color(surface_token)
    selected = b.color(accent)
    b.configure_style(ttk_style, background=surface, borderwidth=1, relief='raised')

    b.map_style(
        ttk_style,
        background=[
            ('selected', selected),
            ('', surface)
        ],
        darkcolor=[
            ('selected', selected),
            ('', surface)
        ],
        lightcolor=[
            ('selected', selected),
            ('', surface)
        ],
        bordercolor=[
            ('background focus', b.color('foreground')),
            ('selected', selected),
            ('', surface)
        ]
    )


@StyleBuilderTtk.register_builder('solid', 'Expander.TLabel')
def build_solid_expander_header_label_style(b: StyleBuilderTtk, ttk_style: str, accent: Optional[str] = None, **options):
    """Expander header label style with state-aware foreground."""
    accent = b.default(accent or 'primary')
    surface_token = options.get('surface', 'content')
    background = b.color(surface_token)
    selected = b.color(accent)
    on_background = b.on_color(background)
    on_selected = b.on_color(selected)
    disabled = b.disabled('text', background)

    b.configure_style(
        ttk_style,
        background=background,
        foreground=on_background,
        relief='flat',
        font='body'
    )

    foreground_state_map = [
        ('disabled', disabled),
        ('selected', on_selected),
        ('', on_background)
    ]

    background_state_map = [
        ('selected', selected),
        ('', background)
    ]

    state_spec = dict(foreground=foreground_state_map, background=background_state_map)
    state_spec = apply_icon_mapping(b, options, state_spec)

    b.map_style(ttk_style, **state_spec)


@StyleBuilderTtk.register_builder('default', 'Expander.TFrame')
def build_ghost_expander_header_style(b: StyleBuilderTtk, ttk_style: str, accent: str = None, **options):
    accent_token = accent or 'foreground'
    surface_token = options.get('surface', 'content')

    surface = b.color(surface_token)
    accent_color = b.color(accent_token)
    selected = b.subtle(accent_color, surface)

    focused_border = b.focus_border(accent_color) if accent_token != 'foreground' else b.focus_border(b.color('primary'))

    b.configure_style(ttk_style, background=surface, borderwidth=1, relief='raised')
    b.map_style(
        ttk_style,
        background=[("selected", selected), ("", surface)],
        darkcolor=[
            ("background focus", focused_border),
            ("selected", selected),
            ("", surface),
        ],
        lightcolor=[
            ("background focus", focused_border),
            ("selected", selected),
            ("", surface),
        ],
        bordercolor=[
            ("background focus", focused_border),
            ("selected", selected),
            ("", surface),
        ],
    )


@StyleBuilderTtk.register_builder('default', 'Expander.TLabel')
def build_ghost_expander_header_label_style(b: StyleBuilderTtk, ttk_style: str, accent: str = None, **options):
    """Expander header label style with state-aware foreground."""
    accent_token = accent or 'foreground'
    surface_token = options.get('surface', 'content')

    surface = b.color(surface_token)
    accent_color = b.color(accent_token)

    selected = b.subtle(accent_color, surface)

    on_surface = b.on_color(surface)
    on_disabled = b.disabled('text', accent_color)

    b.configure_style(
        ttk_style,
        background=surface,
        foreground=on_surface,
        relief='flat',
        font='body'
    )

    foreground_state_map = [
        ('disabled', on_disabled),
        # Selected uses the plain foreground (not the accent) so the header text
        # reads well over the subtle accent wash — same as the sidenav subtle nav.
        ('selected', on_surface),
        ('', on_surface)
    ]

    background_state_map = [
        ('selected', selected),
        ('disabled', surface),
        ('', surface)
    ]

    state_spec = dict(foreground=foreground_state_map, background=background_state_map)
    state_spec = apply_icon_mapping(b, options, state_spec)

    b.map_style(ttk_style, **state_spec)