"""Style engine, theming, and typography for bootstack.

`Style`, `Typography`, and `Font` are internal engine classes — import them from
their modules (`bootstack.style.style`, `bootstack.style.typography`) if you need
them. They are deliberately not part of the public API: `Style` subclasses
`ttk.Style` (a Tkinter leak), and `Typography`/`Font` are internal registries
slated to be replaced by a public font-token API.

The low-level engine accessors `get_style`, `get_style_builder`, and
`get_theme_provider` return those internal objects and are likewise not public —
import them from `bootstack.style.style` if you need them internally.
"""
from bootstack.style.style import (
    get_theme,
    get_theme_color,
    get_themes,
    set_theme,
    toggle_theme,
)
from bootstack.style.theme import Theme, ThemeMode
from bootstack.style.fonts import (
    get_font_families,
    set_font_family,
    update_font_token,
)

__all__ = [
    "Theme",
    "ThemeMode",
    "get_theme",
    "get_theme_color",
    "get_themes",
    "set_theme",
    "toggle_theme",
    "get_font_families",
    "set_font_family",
    "update_font_token",
]