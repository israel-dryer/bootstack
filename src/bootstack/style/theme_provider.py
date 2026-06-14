from __future__ import annotations

from bootstack._runtime.app import get_app_settings
from bootstack._core.exceptions import ThemeError
from bootstack.style.utility import (
    shade_color, tint_color, color_to_hsl, hsl_to_hex, best_foreground
)

_registered_themes = {}
_current_theme = None

# Weights for generating color spectrum tints (toward white) and shades (toward black)
# Each weight represents how much of the original color to retain when mixing
# Full 50-step increments from 50-450 (tints) and 550-950 (shades)
# Tint (toward white) / shade (toward black) weights per 50-step stop. The named
# 100-step stops match Bootstrap 5.3's scale exactly — 100/200/300 = tint
# 80/60/40, 400 = tint 20, 600/700/800/900 = shade 20/40/60/80 — so `[100]`/
# `[200]`/`[800]` equal Bootstrap's bg-subtle/border-subtle/text-emphasis. The
# half-steps (150/250/…) interpolate linearly between the Bootstrap anchors.
TINT_WEIGHTS = {
    50: 0.90,
    100: 0.80,
    150: 0.70,
    200: 0.60,
    250: 0.50,
    300: 0.40,
    350: 0.30,
    400: 0.20,
    450: 0.10,
}
SHADE_WEIGHTS = {
    550: 0.10,
    600: 0.20,
    650: 0.30,
    700: 0.40,
    750: 0.50,
    800: 0.60,
    850: 0.70,
    900: 0.80,
    950: 0.90,
}


def register_theme(name, data):
    """Register a resolved theme schema dict under `name`.

    Args:
        name: Canonical theme name used by `set_theme`.
        data: Resolved theme dict (name, display_name, mode, foreground,
            background, white, black, shades, semantic).
    """
    _registered_themes[name] = data


def get_theme(name):
    """Return a registered theme by name.

    If the theme is not currently registered this will re-run
    `load_system_themes` once to pick up any newly added themes before
    failing.
    """
    if name in _registered_themes:
        return _registered_themes[name]

    # Lazy fallback: configuration (e.g., load_all_themes/include_legacy_themes)
    # may have changed after the provider singleton was first initialized.
    # Re-run the loader once to pick up any additional themes.
    try:
        load_system_themes()
        if name in _registered_themes:
            return _registered_themes[name]
    except Exception:
        # If anything goes wrong here, fall through to the ThemeError.
        pass

    # Build a helpful error message listing available themes
    available = sorted(
        {
            data.get("name")
            for data in _registered_themes.values()
            if isinstance(data, dict) and data.get("name")
        }
    )
    available_str = ", ".join(available) if available else "<none>"
    raise ThemeError(
        f"Theme '{name}' is not registered. "
        f"Registered themes: {available_str}"
    )


def load_system_themes():
    """Register the built-in themes and the `light`/`dark` aliases.

    Built-in themes are plain `Theme` instances (no JSON assets). The themes
    matching the app's configured `light_theme`/`dark_theme` are also registered
    under the `'light'` and `'dark'` aliases. Themes may be registered before an
    App exists (e.g. installing a custom theme with `base=` at module level), so
    this falls back to the default light/dark theme names when there is no app.
    """
    from bootstack.style.themes import install_builtin_themes

    install_builtin_themes()

    try:
        app_settings = get_app_settings()
        dark_theme_name = app_settings.dark_theme
        light_theme_name = app_settings.light_theme
    except Exception:
        dark_theme_name = "bootstrap-dark"
        light_theme_name = "bootstrap-light"

    if dark_theme_name in _registered_themes:
        _registered_themes['dark'] = _registered_themes[dark_theme_name]
    if light_theme_name in _registered_themes:
        _registered_themes['light'] = _registered_themes[light_theme_name]


def color_spectrum(token, value):
    """Generate a color spectrum with 50-step increments from 50-950.

    Creates tints (lighter) and shades (darker) of the base color:
    - 50-450: Tints toward white (50 is lightest)
    - 500: Base color
    - 550-950: Shades toward black (950 is darkest)

    Args:
        token: The color token name (e.g., 'gray', 'blue')
        value: The base hex color value

    Returns:
        Dict mapping spectrum names to hex colors
    """
    result = {}

    # Generate tints (50-450)
    for stop, weight in TINT_WEIGHTS.items():
        result[f'{token}[{stop}]'] = tint_color(value, weight)

    # Base color (500)
    result[f'{token}[500]'] = value

    # Generate shades (550-950)
    for stop, weight in SHADE_WEIGHTS.items():
        result[f'{token}[{stop}]'] = shade_color(value, weight)

    return result


class ThemeProvider:
    """Theme data provider with singleton access and helpers.

    Mirrors the pattern used by Style/use_style():
    - `ThemeProvider()` returns the global instance (singleton)
    - `use_theme(name)` returns/initializes the singleton with optional theme
    - `ThemeProvider.instance(name)` remains for backward compatibility
    """

    # Class-level global singleton instance
    _instance: ThemeProvider | None = None

    def __new__(cls, *args, **kwargs):
        """Ensure ThemeProvider() always returns the global singleton instance."""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self, name: str = "dark"):
        # Prevent reinitialization on subsequent ThemeProvider() calls
        if getattr(self, "_initialized", False):
            if name and name != self.name:
                self.use(name)
            return

        self._theme = {}
        self._colors = {}
        load_system_themes()

        from bootstack.style.typography import Typography
        Typography.initialize()

        self.use(name)
        self._initialized = True

    # ----- Theme metadata helpers -------------------------------------------------

    def list_themes(self) -> list[dict[str, str]]:
        """Return a list of available themes with names and display names.

        The result is a list of dictionaries in the form:

        ```python
        {"name": "bootstrap-light", "display_name": "Bootstrap Light"}
        ```

        Aliases such as `\"light\"` and `\"dark\"` are not included; only the
        canonical theme entries loaded into the provider are returned.
        """
        themes: list[dict[str, str]] = []
        seen: set[str] = set()

        for key, data in _registered_themes.items():
            # Skip alias keys that point at an existing theme object
            name = data.get("name")
            if not name:
                continue
            if key != name and name in _registered_themes:
                # This is an alias like 'light' or 'dark'
                continue
            if name in seen:
                continue
            seen.add(name)
            themes.append(
                {
                    "name": name,
                    "display_name": data.get("display_name", name),
                }
            )

        # If the application has declared a specific set/order of themes
        # to expose, filter and order by that list.
        select_themes = get_app_settings().available_themes
        if select_themes:
            by_name = {t["name"]: t for t in themes}
            ordered: list[dict[str, str]] = []
            for name in select_themes:
                t = by_name.get(name)
                if t is not None:
                    ordered.append(t)
            return ordered

        # Otherwise, sort for stable UI ordering (by display name, then name)
        themes.sort(key=lambda t: (t["display_name"].lower(), t["name"].lower()))
        return themes

    def use(self, name):
        self._theme = get_theme(name)
        self.build_theme_colors()

    @property
    def raw(self):
        """Return the raw source dictionary"""
        return self._theme

    def build_theme_colors(self):
        colors = {}
        colors.update(
            foreground=self.raw.get('foreground'),
            background=self.raw.get('background'),
            white=self.raw.get('white'),
            black=self.raw.get('black'),
            **self._shades,
        )
        # add shaded spectrum
        for color, value in self._shades.items():
            colors.update(**color_spectrum(color, value))

        # semantic tokens
        neutral_tokens = {
            "foreground",
            "muted",
            "muted_alt",
            "subtle",
            "border",
            "border_subtle",
        }
        for token, value in self._semantic.items():
            # Neutral roles are derived elsewhere from the top-level
            # foreground/background and should not be overridden here.
            if token in neutral_tokens:
                continue
            colors[token] = colors[value]

        # Per-semantic subtle / border / emphasis tokens (Bootstrap 5.3 model),
        # sourced from the accent's hue-FAMILY scale stops so they stay vibrant
        # regardless of how dark the semantic solid is. Light: bg-subtle=[100],
        # border-subtle=[200], text-emphasis=[800]; dark uses the dark end.
        # border-subtle + text-emphasis are fixed accent shades (light: [200]/
        # [800]; dark: [700]/[300]). The bg-subtle WASH is NOT precomputed here —
        # it is surface-relative (a blend of the accent anchor into whatever
        # surface it sits on), computed in `BootstyleBuilder.subtle()`.
        import re as _re
        _stop_re = _re.compile(r'^([a-z]+)\[\d+\]$')
        _is_dark = self.mode == 'dark'
        _stops = ('700', '300') if _is_dark else ('200', '800')
        for token, value in self._semantic.items():
            if token in neutral_tokens:
                continue
            m = _stop_re.match(str(value))
            if m is None:
                continue
            family = m.group(1)
            for suffix, stop in zip(('border_subtle', 'emphasis'), _stops):
                colors[f'{token}_{suffix}'] = colors.get(f'{family}[{stop}]')

        # Surface tokens - semantic ramps for container backgrounds
        self._build_surface_tokens(colors)

        # Neutral text tokens — pre-computed for direct use as accent tokens
        from bootstack.style.utility import muted_foreground
        colors['muted'] = muted_foreground(colors['background'])

        self._colors.clear()
        self._colors.update(**colors)

    def _build_surface_tokens(self, colors: dict):
        """Build semantic surface tokens for container backgrounds.

        Surface tokens provide deterministic, theme-defined backgrounds
        that don't rely on "background +1 math" for elevation. The hue
        and saturation are derived from the theme's background color to
        ensure consistent tinting across all surfaces.

        Token families:
        - chrome: UI shell (sidebars, toolbars, navigation)
        - content: Main content area background (= theme background)
        - card: Elevated content (cards, panels)
        - overlay: Floating elements (menus, dialogs, tooltips)
        - input: Form control backgrounds
        """
        from bootstack.style.utility import darken_color, lighten_color
        is_dark = self.mode == 'dark'
        bg = colors['background']
        fg = colors['foreground']

        # Derive surfaces by darkening/lightening the BACKGROUND — this preserves
        # the theme's hue AND saturation at every level (rebuilding at a target
        # lightness with capped saturation washed the tint out and could invert
        # the content/sidebar hierarchy). `content` is always the background;
        # `chrome` is the recessed shell tier (darkest in both modes).
        def dk(amount: float) -> str:
            return darken_color(bg, amount)

        def lt(amount: float) -> str:
            return lighten_color(bg, amount)

        # Helpers for the muted-foreground + hover tokens below (a tinted gray at
        # a target lightness; the main surfaces use dk/lt above).
        hue, sat, bg_lightness = color_to_hsl(bg, model='hex')
        tint_sat = min(sat, 25) if sat >= 5 else 0

        def tinted_surface(lightness: float) -> str:
            if tint_sat == 0:
                return hsl_to_hex(0, 0, lightness)
            return hsl_to_hex(hue, tint_sat, lightness)

        if is_dark:
            # Elevation lightens off the dark bg; chrome darkens (recessed).
            surfaces = {
                'chrome': dk(0.40),
                'content': bg,
                'raised': lt(0.05),
                'card': lt(0.09),
                'card_raised': lt(0.15),
                'overlay': lt(0.12),
                'input': lt(0.03),
            }
            colors['stroke'] = lt(0.22)
            colors['stroke_subtle'] = lt(0.10)
        else:
            # Surfaces darken off the light bg; content stays the lightest.
            surfaces = {
                'chrome': dk(0.10),
                'content': bg,
                'raised': dk(0.025),
                'card': dk(0.05),
                'card_raised': dk(0.085),
                'overlay': dk(0.025),
                'input': bg,
            }
            colors['stroke'] = dk(0.14)
            colors['stroke_subtle'] = dk(0.06)

        # Per-theme surface overrides (escape hatch for cases the derivation
        # can't produce well, e.g. a very-dark or very-light background).
        override = self.raw.get('surfaces') if isinstance(self.raw, dict) else None
        if override:
            for name, value in override.items():
                if name == 'stroke' or name == 'stroke_subtle':
                    colors[name] = value
                else:
                    surfaces[name] = value

        # Add surfaces to colors
        for name, value in surfaces.items():
            colors[name] = value

        # Pre-compute foreground colors for each surface
        candidates = [fg, '#ffffff', '#000000']
        for name, value in surfaces.items():
            colors[f'on_{name}'] = best_foreground(value, candidates)

        # Secondary/muted foreground for each surface (reduced contrast)
        for name, value in surfaces.items():
            # Generate a muted foreground by mixing fg with the surface
            on_color = colors[f'on_{name}']
            if on_color in ('#ffffff', '#FFFFFF'):
                colors[f'on_{name}_secondary'] = tinted_surface(65) if is_dark else tinted_surface(45)
            else:
                colors[f'on_{name}_secondary'] = tinted_surface(35) if is_dark else tinted_surface(55)

        # Hover states for each surface (subtle highlight)
        for name in surfaces.keys():
            if name == 'content':
                # Content hover: slightly elevated
                hover_l = min(bg_lightness + 5, 25) if is_dark else max(bg_lightness - 5, 90)
            else:
                # Other surfaces: shift toward content
                surface_h, surface_s, surface_l = color_to_hsl(colors[name], model='hex')
                hover_l = min(surface_l + 5, 30) if is_dark else max(surface_l - 5, 85)
            colors[f'{name}_hover'] = tinted_surface(hover_l)

    @property
    def name(self):
        """The name of the theme"""
        return self.raw.get('name')

    @property
    def display_name(self):
        """The display name of the theme"""
        return self.raw.get('display_name')

    @property
    def mode(self):
        """Returns the color mode 'light' or 'dark'"""
        return self.raw.get('mode')

    @property
    def colors(self):
        return self._colors

    @property
    def typography(self):
        """Returns the current typography configuration as FontTokens"""
        from bootstack.style.typography import Typography
        return Typography.all()

    @property
    def _shades(self):
        return self.raw.get('shades')

    @property
    def _semantic(self):
        return self.raw.get('semantic')

    def __repr__(self):
        """Return a string representation of the current theme"""
        return f"<Theme name={self.name} mode={self.mode}>"


def use_theme(name: str = None) -> ThemeProvider:
    """Return the global ThemeProvider singleton instance.

    Convenience helper that mirrors `use_style()` so callers can obtain
    the current ThemeProvider without handling singleton state.

    Args:
        name: Optional theme name to switch to, or None to return current instance.

    Returns:
        Global ThemeProvider instance.
    """
    # If instance doesn't exist yet, create it with default theme
    if ThemeProvider._instance is None:
        return ThemeProvider(name or "dark")

    # If name is provided and different, switch themes
    if name is not None and name != ThemeProvider._instance.name:
        ThemeProvider._instance.use(name)

    # Return the singleton
    return ThemeProvider._instance
