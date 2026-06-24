"""Enhanced TTK Style class with builder registry and theme management."""

from __future__ import annotations

import tkinter
from tkinter.ttk import Style as ttkStyle
from typing import Dict, Optional, Set

from bootstack._runtime.app import get_app_settings
from bootstack.style.style_builder_ttk import StyleBuilderTtk
from bootstack.style.theme_provider import ThemeProvider, use_theme
from bootstack.widgets.types import Master

_style_instance: Style | None = None


class Style(ttkStyle):
    """Enhanced TTK Style with builder registry and theme management.

    This class extends ttk.Style to provide:

    - Singleton pattern (one instance per Tkinter master)
    - Integration with StyleBuilder registry
    - Theme management via ThemeProvider
    - Automatic style rebuilding on theme changes
    - Custom style options support

    The Style class maintains registries to track:

    - All created styles (for theme change rebuilds)
    - Which styles exist in each theme (for caching)
    - Custom options per style (for recreating with same options)
    """

    def __new__(cls, *args, **kwargs):
        """Ensure Style() always returns the global singleton instance.

        If an instance already exists, return it. Otherwise, create it.
        """
        global _style_instance
        if _style_instance is None:
            _style_instance = super().__new__(cls)
        return _style_instance

    def __init__(self, master: Master = None, theme: str = "light"):
        """Initialize the Style instance.

        Args:
            master: Tkinter master widget (None for default)
            theme: Initial theme name (default: "light")
        """
        # Prevent reinitialization on subsequent Style() calls
        if getattr(self, "_initialized", False):
            # Optionally honor a theme argument after initialization
            try:
                if theme and theme != self._current_theme:
                    self.theme_use(theme)
            except Exception:
                pass
            return

        super().__init__(master)

        self._theme_provider = use_theme(theme)
        self._style_builder = StyleBuilderTtk(theme_provider=self._theme_provider, style_instance=None)
        self._style_builder.set_style_instance(self)

        # Style registries
        self._style_registry: Set[str] = set()
        self._style_accents: Dict[str, Optional[str]] = {}
        self._style_variants: Dict[str, str] = {}
        self._style_options: Dict[str, dict] = {}
        self._style_widget_classes: Dict[str, str] = {}

        # Current theme tracking
        self._current_theme: Optional[str] = theme

        # Incremented on every theme change so a widget can detect a restyle it
        # missed while off-screen (stamped on `_bs_theme_version`; see
        # apply_theme_walk).
        self._theme_version: int = 0

        # Cached Tk builder — lazily initialized, reused across all widget creations
        self._cached_tk_builder = None

        self.theme_use(theme)
        self._initialized = True

    @property
    def style_builder(self) -> StyleBuilderTtk:
        """Get the builder manager instance.

        Returns:
            StyleBuilder instance
        """
        return self._style_builder

    @property
    def theme_provider(self) -> ThemeProvider:
        """Get the theme provider instance.

        Returns:
            ThemeProvider instance
        """
        return self._theme_provider

    # ----- Theme metadata helpers -------------------------------------------------

    def list_themes(self) -> list[dict[str, str]]:
        """Return available themes as [{'name', 'display_name'}, ...].

        This delegates to the underlying ThemeProvider. Themes are always
        loaded from both the v2 and legacy theme packages.

        Returns:
            List of theme dictionaries with 'name' and 'display_name' keys.
        """
        return self._theme_provider.list_themes()

    @property
    def current_theme(self) -> Optional[str]:
        """Get the current theme name.

        Returns:
            Current theme name or None
        """
        return self._current_theme

    @property
    def colors(self) -> dict[str, str]:
        """Get colors for the current theme.

        Returns:
            Colors dictionary from ThemeProvider
        """
        return self._theme_provider.colors

    def style_exists(self, style: str) -> bool:
        """Check if a style exists (basic check).

        Args:
            style: TTK style name

        Returns:
            True if style has any configuration
        """
        return bool(self.configure(style))

    def register_style(self, ttk_style: str, options: Optional[dict] = None):
        """Register a style in the current theme.

        This adds the style to registries so it can be:

        - Cached (not recreated if already exists)
        - Rebuilt when theme changes
        - Recreated with same options

        Args:
            ttk_style: Full TTK style name
            options: Optional custom style options
        """
        # Add to global registry
        self._style_registry.add(ttk_style)

        # Store a copy of custom options if provided (to prevent mutation issues)
        if options:
            self._style_options[ttk_style] = options.copy()

    def create_style(
            self,
            widget_class: str,
            variant: str,
            ttk_style: str,
            accent: Optional[str] = None,
            options: Optional[dict] = None) -> None:
        """Create a new style if it doesn't exist in current theme.

        Args:
            widget_class: TTK widget class (e.g., "TButton")
            variant: Variant name (e.g., "outline")
            ttk_style: Full TTK style name (e.g., "success.Outline.TButton")
            accent: Optional accent token (e.g., "success", "blue[100]")
            options: Optional custom style options
        """
        # Fast path: Python-side set lookup before crossing into Tcl
        if ttk_style in self._style_registry:
            return
        # Fallback for styles known to Tcl but not our registry (e.g. external theme changes)
        if self.style_exists(ttk_style):
            self.register_style(ttk_style, options)
            return

        # Call builder with widget class, variant, and parsed accent
        self._style_builder.call_builder(
            widget_class=widget_class,
            variant=variant,
            ttk_style=ttk_style,
            accent=accent,
            **(options or {})
        )

        # Store the accent, variant, and widget_class so we can rebuild with the same values
        self._style_accents[ttk_style] = accent
        self._style_variants[ttk_style] = variant
        self._style_widget_classes[ttk_style] = widget_class

        # Register it
        self.register_style(ttk_style, options)

    def theme_use(self, name: str = None) -> str | None:
        """Switch to a different theme and rebuild all styles.

        Applies theme change to the global Style instance, rebuilds all
        TTK styles and registered Tk widgets, and publishes a legacy
        theme-change event for subscribers.

        Args:
            name: Theme name to switch to. If None, returns the current theme.

        Returns:
            The current theme name, or None if no theme is set.
        """
        if name is None:
            return super().theme_use()

        # Only call use() if theme is changing to avoid redundant build_theme_colors()
        if name != self._theme_provider.name:
            self._theme_provider.use(name)
        self._current_theme = name

        if name not in self.theme_names():
            self.theme_create(name, 'clam', {})

        super().theme_use(name)

        # Initialize all default widget styles before rebuilding custom styles
        # self._style_builder.initialize_all_default_styles()

        self._rebuild_all_styles()

        # Bump version so off-screen widgets know they missed this theme change
        # (they recolor when their container next shows them — see apply_theme_walk).
        self._theme_version += 1

        # Fire the bootstack theme-change event after full rebuild so handlers
        # can safely read new colors. Uses get_default_root lazily to avoid
        # importing app at module level.
        try:
            from bootstack._runtime.app import get_default_root
            root = get_default_root()
            # Unified theme walk: recolor every visible tree widget now; off-screen
            # ones are left stale and recovered when their page/tab/section is next
            # shown. Non-tree reactors (the Image handle, OS window chrome, the
            # app-level on_theme_change callback) listen on <<BsThemeChanged>> below.
            if root is not None:
                self.apply_theme_walk(root, only_stale=False)
            root.event_generate(
                "<<BsThemeChanged>>",
                data={"theme": name, "mode": self._theme_provider.mode},
                when="tail",
            )
        except Exception:
            pass

        return self._current_theme

    def _rebuild_all_styles(self):
        """Recreate all registered styles when theme changes.

        This iterates through all styles that have been created and
        rebuilds them using the new theme's colors, preserving any
        custom options.
        """
        for style in self._style_registry:
            # Get stored options, accent, and variant
            options = self._style_options.get(style, {})
            accent = self._style_accents.get(style)
            variant = self._style_variants.get(style)

            # Use stored widget_class if available (preserves composite classes like 'Menubar.TField')
            # Fall back to parsing from style name for backwards compatibility
            widget_class = self._style_widget_classes.get(style)
            if not widget_class:
                parsed = self._parse_style_name(style)
                if not parsed:
                    continue
                widget_class = parsed['widget_class']
                # Only use parsed variant if we don't have a stored one
                if variant is None:
                    variant = parsed['variant']

            if variant is None:
                from bootstack.style.style_builder_ttk import StyleBuilderTtk
                variant = StyleBuilderTtk.get_default_variant(widget_class)

            self._style_builder.call_builder(
                widget_class=widget_class,
                variant=variant,
                ttk_style=style,
                accent=accent,
                **options
            )

    def _get_tk_builder(self):
        """Return the cached Tk builder, creating it on first call."""
        if self._cached_tk_builder is None:
            from bootstack.style.style_builder_tk import StyleBuilderTk
            self._cached_tk_builder = StyleBuilderTk(
                theme_provider=self._theme_provider,
                style_instance=self,
            )
        return self._cached_tk_builder

    # ------------------------------------------------------------------ Unified theme walk
    #
    # The single mechanism for recoloring *tree widgets* on a theme change. A
    # widget that needs theming exposes one method, ``_bs_apply_theme()``, doing
    # all of its work (background + any canvas repaint). Two triggers drive it,
    # and neither relies on ``<Map>``:
    #   * a theme change walks from the root and applies every *visible* widget;
    #   * a container showing a page/tab walks that subtree and applies the
    #     *stale* ones (those that missed the change while hidden).
    # Visibility is resolved at apply time, so nothing is deferred to a hoped-for
    # event. Non-tree reactors (the Image handle, OS window chrome, the app-level
    # on_theme_change callback) stay on the root ``<<BsThemeChanged>>`` binding.

    def _apply_theme_to_widget(self, widget) -> None:
        """Apply the current theme to one widget and stamp its version.

        Re-applies the surface background for an autostyled Tk widget, then runs
        the widget's ``_bs_apply_theme`` hook if it defines one (canvas painters
        redraw there). Both are best-effort; a failure on one widget never aborts
        the walk.
        """
        surface = getattr(widget, '_surface', None)
        if surface is not None:
            try:
                self._get_tk_builder().call_builder(widget, surface=surface)
            except Exception:
                pass
        hook = getattr(widget, '_bs_apply_theme', None)
        if hook is not None:
            try:
                hook()
            except Exception:
                pass
        widget._bs_theme_version = self._theme_version

    def apply_theme_walk(self, root_widget, *, only_stale: bool) -> None:
        """Walk ``root_widget``'s subtree and theme each on-screen widget.

        Args:
            root_widget: Subtree root — the application root on a theme change, or
                a freshly-shown page/tab on a container-show.
            only_stale: When True (container-show), apply every widget in the
                subtree that missed the current theme version — regardless of
                ``winfo_viewable()``, which is unreliable for a widget embedded in
                a scrollable page's canvas; the container is showing it now. When
                False (theme change), apply every *visible* widget and leave the
                off-screen ones stale for their next container-show.
        """
        version = self._theme_version
        stack = [root_widget]
        while stack:
            w = stack.pop()
            # A PageStack keeps inactive pages mapped (so re-showing one doesn't
            # blank-flash on macOS) but flags them hidden; prune the whole subtree
            # so a theme change repaints only the visible page. A hidden page's
            # widgets stay stale and are repainted on its next show (only_stale).
            if getattr(w, '_bs_nav_hidden', False):
                continue
            try:
                stack.extend(w.winfo_children())
            except Exception:
                pass
            themed = hasattr(w, '_bs_apply_theme') or getattr(w, '_surface', None) is not None
            if not themed:
                continue
            if only_stale:
                if getattr(w, '_bs_theme_version', -1) == version:
                    continue
            else:
                try:
                    if not w.winfo_viewable():
                        continue
                except Exception:
                    continue
            self._apply_theme_to_widget(w)

    @staticmethod
    def _parse_style_name(ttk_style: str) -> Optional[dict]:
        """Parse TTK style name to extract widget class and variant.

        Args:
            ttk_style: Full TTK style name

        Returns:
            Dict with 'widget_class' and 'variant', or None

        Examples:
            >>> Style._parse_style_name("success.TButton")
            {'widget_class': 'TButton', 'variant': 'solid'}
            >>> Style._parse_style_name("info.Thin.TProgressbar")
            {'widget_class': 'TProgressbar', 'variant': 'thin'}
        """
        # Split into parts
        parts = ttk_style.split('.')

        if not parts:
            return None

        # Extract widget class (e.g., "TButton")
        # Widget class is always the LAST part starting with 'T'
        widget_class = None
        for part in parts:
            if part.startswith('T'):
                widget_class = part

        if not widget_class:
            return None

        # Determine variant using registered builders for this widget
        from bootstack.style.style_builder_ttk import StyleBuilderTtk
        builder_variants = set(v.lower() for v in StyleBuilderTtk.get_registered_builders(widget_class))

        variant = None
        accent = None
        for part in parts:
            # Skip the widget class itself (e.g., 'TCheckbutton')
            if part == widget_class:
                continue
            token = part.lower()
            # Identify variant by registry match
            if token in builder_variants and variant is None:
                variant = token
                continue
            # First non-variant token becomes accent
            if accent is None:
                accent = part

        if variant is None:
            variant = StyleBuilderTtk.get_default_variant(widget_class)

        return {
            'widget_class': widget_class,
            'variant': variant
        }

    def get_style_builder(self) -> StyleBuilderTtk:
        """Get the style builder instance.

        Returns:
            StyleBuilder instance
        """
        return self._style_builder

    def __repr__(self) -> str:
        """String representation of Style instance."""
        return f"<Style theme={self._current_theme} styles={len(self._style_registry)}>"


def get_style(master: Master = None) -> Style:
    """Return the global Style singleton instance.

    Convenience helper function that ensures a single Style instance
    is used across the application.

    Args:
        master: Optional master for initial construction; ignored thereafter.

    Returns:
        Global Style instance.

    Examples:
        >>> style = get_style()
        >>> style.theme_use("nord-dark")
    """
    if _style_instance:
        return _style_instance
    else:
        return Style(master)


def reset_style() -> None:
    """Drop the process-wide Style singleton.

    The Style singleton is a `ttk.Style` bound to the Tk root that created it.
    Once that root is destroyed its interpreter is gone, so the singleton can no
    longer be used — a fresh App must rebuild Style against the new root. Call
    this after destroying the root (App.destroy does) so the next
    `get_style()`/`Style()` constructs cleanly instead of reusing a dead
    instance (whose `theme_use` would fail, e.g. "named font body does not
    already exist").
    """
    global _style_instance
    _style_instance = None


def get_style_builder() -> StyleBuilderTtk:
    """Return the style builder for the currently active theme.

    Returns:
        The StyleBuilderTtk instance for the active theme.

    Examples:
        >>> builder = get_style_builder()
        >>> primary_color = builder.color("primary")
    """
    style = get_style()
    return style.style_builder


# --- Global Utilities ---

def set_theme(name: str) -> None:
    """Set the active application theme.

    Args:
        name: Theme name to activate (e.g., "bootstrap-light", "nord-dark").

    Examples:
        >>> set_theme("nord-dark")
    """
    style = get_style()
    style.theme_use(name)


def toggle_theme() -> None:
    """Toggle the active application theme between light and dark mode.

    Uses the light and dark themes specified in app settings, or defaults
    to bootstrap-light and bootstrap-dark.

    Examples:
        >>> toggle_theme()
    """
    settings = get_app_settings()
    light = settings.light_theme
    dark = settings.dark_theme
    theme = get_theme()
    if theme == light or theme == "light":
        set_theme(dark)
    else:
        set_theme(light)


def get_theme() -> str:
    """Return the name of the currently active theme.

    Returns:
        Name of the active theme.

    Examples:
        >>> theme = get_theme()
        >>> print(theme)  # "bootstrap-dark"
    """
    style = get_style()
    return style.theme_use()


def get_themes() -> list[dict[str, str]]:
    """Return the list of all registered themes.

    Returns:
        List of dictionaries containing `name` and `display_name` for each theme.

    Examples:
        >>> themes = get_themes()
        >>> print([theme["name"] for theme in themes])
    """
    style = get_style()
    return style.list_themes()


def get_theme_provider() -> ThemeProvider:
    """Get the theme provider instance for the active theme.

    Returns:
        ThemeProvider instance.

    Examples:
        >>> provider = get_theme_provider()
        >>> colors = provider.get_colors()
    """
    style = get_style()
    return style.theme_provider


def get_theme_color(token: str) -> str:
    """Get a hex color value from a color token based on the active theme.

    Args:
        token: Color token name (e.g., "primary", "background").

    Returns:
        Hex color string (e.g., "#007bff").

    Raises:
        ValueError: If the color token is invalid.

    Examples:
        >>> primary = get_theme_color("primary")
        >>> print(primary)  # "#007bff"
    """
    builder = get_style_builder()
    try:
        return builder.color(token)
    except Exception:
        raise ValueError(f"Invalid color token: {token}")
