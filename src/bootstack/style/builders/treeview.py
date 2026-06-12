"""Treeview widget style builders."""
import tkinter as tk
from tkinter import font

from bootstack._core.images import _ImageService
from bootstack.style.bootstyle_builder_ttk import BootstyleBuilderTTk
from bootstack.style.element import Element, ElementImage
from bootstack.style.utility import create_transparent_image
from bootstack.style.builders.utils import normalize_button_density, _snap_even


def _tk_version_at_least(major: int, minor: int, patch: int) -> bool:
    """Check if the current Tk version is at least the specified version.

    This is used to work around a regression in Tk 8.6.13+ where user1/user2
    states don't work properly with custom image elements for treeview indicators.
    See: https://core.tcl-lang.org/tk/timeline?r=rfe-d632d28ba4
    """
    try:
        version_str = tk._default_root.tk.call('info', 'patchlevel')
        parts = version_str.split('.')
        current = (int(parts[0]), int(parts[1]), int(parts[2]))
        return current >= (major, minor, patch)
    except Exception:
        # If we can't determine version, assume newer Tk (safer fallback)
        return True


def _treeview_font(density: str) -> str:
    """Get font token based on density."""
    return 'caption' if density == 'compact' else 'body'


def _treeview_row_height(density: str) -> float:
    """Get row height multiplier based on density."""
    return 1.6 if density == 'compact' else 1.75


def _treeview_indicator_size(density: str) -> int:
    """Get indicator size based on density."""
    return 10 if density == 'compact' else 12


def _treeview_icon_size(density: str) -> int:
    """Get custom icon size based on density."""
    return 12 if density == 'compact' else 16


def _treeview_item_padding(density: str) -> tuple[int, int]:
    """Get item padding based on density."""
    return (4, 0) if density == 'compact' else (6, 0)


def _treeview_heading_padding(density: str) -> tuple[int, int]:
    """Get heading padding based on density."""
    return (4, 4) if density == 'compact' else (8, 10)


def _treeview_cell_padding(density: str) -> tuple[int, int]:
    """Get cell padding based on density."""
    return (2, 0) if density == 'compact' else (6, 0)


@BootstyleBuilderTTk.register_builder('default', 'Treeview')
@BootstyleBuilderTTk.register_builder('tree', 'Treeview')
def build_tree_style(b: BootstyleBuilderTTk, ttk_style: str, **options):
    """
    Create treeview style.

    Available options via `style_options`:
        * border_color
        * show_border
        * open_icon
        * close_icon
        * select_background
        * header_background
        * density ('default' or 'compact')
    """
    surface_token: str = options.get('surface', 'content')
    border_token: str = options.get('border_color', surface_token)
    header_bg_token: str | None = options.get('header_background')
    show_border = options.get('show_border', True)
    density = normalize_button_density(options.get('density', 'default'))
    surface = b.color(surface_token)

    if show_border:
        if border_token is not None:
            border_color = b.color(border_token)
        else:
            border_color = b.border(surface)
    else:
        border_color = surface

    if header_bg_token is not None:
        heading_color = b.color(header_bg_token)
        heading_hover = b.active(heading_color)
    else:
        heading_color = b.elevate(surface, 3)
        heading_hover = b.active(heading_color)

    on_heading = b.on_color(heading_color)
    on_surface = b.on_color(surface)
    on_surface_disabled = b.disabled('text', surface)
    hover = b.active(surface)

    select_background_token = options.get('select_background', 'primary')
    # Subtle accent wash so striping shows through and text/icons keep one color.
    select_background = b.subtle(select_background_token)
    select_hover = b.active(select_background)
    on_select = on_surface  # selected rows keep normal text on the soft wash

    # Density-based sizing
    body_font = _treeview_font(density)
    row_multiplier = _treeview_row_height(density)
    item_padding = _treeview_item_padding(density)
    heading_padding = _treeview_heading_padding(density)
    cell_padding = _treeview_cell_padding(density)

    # Calculate row height - use TkDefaultFont for metrics when using font spec
    metrics_font = 'TkDefaultFont' if body_font.startswith('-') else body_font
    f = font.nametofont(metrics_font)
    row_height = int(f.metrics()['linespace'] * row_multiplier)

    # Transparent gap between the leading icon (checkbox / group chevron) and the
    # text, so a group label doesn't butt up against its chevron. Harmless for
    # rows whose icon slot has no adjacent text (e.g. checkbox-only cells).
    gap_width = 8 if density == 'compact' else 10
    gap = create_transparent_image(b.scale(gap_width), 1)
    b.create_style_element_image(
        ElementImage(f'{ttk_style}.iconspacer', gap, sticky='', width=b.scale(gap_width))
    )

    b.create_style_layout(
        f'{ttk_style}.Item',
        Element('Treeitem.padding').children(
            [
                Element('Treeitem.image', side='left', sticky=''),
                Element(f'{ttk_style}.iconspacer', side='left', sticky=''),
                Element('Treeitem.text', side='left', sticky='w')
            ])
    )

    b.configure_style(f'{ttk_style}.Item', padding=b.scale(item_padding))

    # configure header
    heading_font = 'caption' if density == 'compact' else 'label'
    b.configure_style(
        f'{ttk_style}.Heading',
        font=heading_font,
        background=heading_color,
        foreground=on_heading,
        padding=b.scale(heading_padding)
    )
    b.map_style(
        f'{ttk_style}.Heading',
        foreground=[('disabled', on_surface_disabled), ('', on_heading)],
        background=[('active !disabled', heading_hover), ('', heading_color)]
    )

    # configure tree body
    show_border = options.get('show_border', True)
    b.configure_style(
        ttk_style,
        font=body_font,
        background=surface,
        fieldbackground=surface,
        foreground=on_surface,
        borderwidth=1 if show_border else 0,
        bordercolor=border_color,
        darkcolor=surface,
        lightcolor=surface,
        padding=0,
        rowheight=row_height,
        relief='solid' if show_border else 'flat'
    )

    b.map_style(
        ttk_style,
        background=[
            ('active !disabled', hover),
            ('selected active !disabled', select_hover),
            ('selected !disabled', select_background)
            # do not set fallback or it will override tag formats
        ],
        foreground=[
            ('disabled', on_surface_disabled),
            ('selected !disabled', on_select)
            # do not set fallback or it will override tag formats
        ]
    )

    # configure cell
    b.configure_style(f"{ttk_style}.Cell", font=body_font, padding=b.scale(cell_padding))
