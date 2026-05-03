"""Public style-related API surface."""

from __future__ import annotations

from ttkbootstrap_icons_bs import BootstrapIcon

from bootstack.style.style import (Style, get_style, get_style_builder, get_theme, get_theme_color,
                                      get_theme_provider, set_theme, toggle_theme, get_themes)
from bootstack.style.typography import Font

__all__ = [
    "BootstrapIcon",
    "Font",
    "Style",
    "get_style",
    "get_style_builder",
    "get_theme",
    "set_theme",
    "toggle_theme",
    "get_theme_provider",
    "get_theme_color",
    "get_themes",
]
