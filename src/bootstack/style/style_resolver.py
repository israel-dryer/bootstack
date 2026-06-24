"""Style resolution and widget integration for bootstack.

Resolves accent/variant tokens into TTK style names and wires those styles
onto widgets by overriding their constructors.
"""

from __future__ import annotations

from typing import Optional

from bootstack._runtime.app import get_app_settings, has_current_app
from bootstack.style.token_maps import (COLOR_TOKENS, CONTAINER_CLASSES, ORIENT_CLASSES, WIDGET_CLASS_MAP)



def to_pascal_case(s: str) -> str:
    """Convert dash-separated string to PascalCase.

    Examples:
        'context-check' -> 'ContextCheck'
        'outline' -> 'Outline'
        'solid' -> 'Solid'
    """
    return ''.join(part.capitalize() for part in s.split('-'))


def from_pascal_case(s: str) -> str:
    """Convert PascalCase string to dash-separated lowercase.

    Examples:
        'ContextCheck' -> 'context-check'
        'Outline' -> 'outline'
        'Solid' -> 'solid'
    """
    import re
    # Insert dash before uppercase letters (except at start), then lowercase
    return re.sub(r'(?<!^)(?=[A-Z])', '-', s).lower()


def generate_ttk_style_name(
        accent: Optional[str],
        variant: Optional[str],
        widget_class: str,
        custom_prefix: Optional[str] = None,
        orient: Optional[str] = None,
) -> str:
    """Generate TTK style name from parsed components.

    Returns style name in format: [custom_prefix].[accent].[Variant].[Orient].[Widget]
    """
    parts = []

    if custom_prefix:
        parts.append(custom_prefix)
    if accent:
        parts.append(accent)
    if variant:
        parts.append(to_pascal_case(variant))
    if orient:
        parts.append(normalize_orientation(orient))
    parts.append(widget_class)
    return '.'.join(parts)


def normalize_orientation(orient: str):
    """Normalize TTK style orientation."""
    if orient.lower().startswith('v'):
        return 'Vertical'
    else:
        return 'Horizontal'



def extract_orient_from_style(ttk_style: str):
    """Extract orientation from TTK style name."""
    if 'horizontal' in ttk_style.lower():
        return 'Horizontal'
    elif 'vertical' in ttk_style.lower():
        return 'Vertical'
    else:
        return None


def extract_accent_from_style(ttk_style: str, default: str = 'primary') -> str:
    """Extract accent token from TTK style name, including modifiers like [subtle]."""
    parts = ttk_style.split('.')

    # Skip custom prefix if present (e.g., bs[hash] or custom_xyz)
    if parts and (parts[0].startswith('bs[') or parts[0].startswith('custom_')):
        parts = parts[1:]

    for part in parts:
        part_lower = part.lower()
        # Check exact match first
        if part_lower in COLOR_TOKENS:
            return part_lower
        # Check if base accent (before modifier) is an accent token
        # e.g., 'primary[subtle]' -> 'primary'
        if '[' in part_lower:
            base_accent = part_lower.split('[')[0]
            if base_accent in COLOR_TOKENS:
                return part_lower  # Return full token with modifier

    return default


def extract_variant_from_style(ttk_style: str, widget_class: str = None) -> Optional[str]:
    """Extract variant name from TTK style name.

    Args:
        ttk_style: The TTK style name to parse.
        widget_class: Optional widget class from winfo_class() to exclude from parsing.

    Returns:
        Variant name in dash-separated lowercase format (e.g., 'context-check')
    """
    parts = ttk_style.split('.')

    # Skip custom prefix if present (e.g., bs[hash] or custom_xyz)
    if parts and (parts[0].startswith('bs[') or parts[0].startswith('custom_')):
        parts = parts[1:]

    # Build set of class-related parts to skip (e.g., 'Expander', 'TLabel')
    class_parts = set()
    if widget_class:
        class_parts.update(widget_class.split('.'))

    for part in parts:
        part_lower = part.lower()
        # Skip color tokens (including those with modifiers like 'primary[subtle]')
        if part_lower in COLOR_TOKENS:
            continue
        if '[' in part_lower:
            base_color = part_lower.split('[')[0]
            if base_color in COLOR_TOKENS:
                continue
        # Skip known class parts from widget_class
        if part in class_parts:
            continue
        # Skip standard ttk class names (TLabel, TButton, etc.)
        if part.startswith('T'):
            continue
        # Skip orientation parts
        if part in ('Horizontal', 'Vertical'):
            continue
        # Found a variant - convert from PascalCase to dash-separated
        return from_pascal_case(part)

    return None


def extract_widget_class_from_style(ttk_style: str) -> Optional[str]:
    """Extract widget class from TTK style name."""
    parts = ttk_style.split('.')

    for part in parts:
        if part.startswith('T'):
            return part

    return None


class StyleResolver:
    """Widget integration layer for the style system.

    Wires bootstack into tkinter/ttk by overriding widget constructors to
    resolve `accent`/`variant` tokens into TTK style names.
    """

    @staticmethod
    def create_ttk_style(
            widget_class: str,
            style_options: Optional[dict] = None,
            *,
            accent: Optional[str] = None,
            variant: Optional[str] = None,
    ) -> str:
        """Create or get TTK style name for a widget.

        Args:
            widget_class: TTK widget class (e.g., "TButton")
            style_options: Custom style options dict
            accent: Accent token (e.g., "success", "primary[subtle]")
            variant: Variant name (e.g., "outline", "solid")

        Returns:
            Generated TTK style name
        """
        from bootstack.style.style_builder_ttk import StyleBuilderTtk

        # If no accent and no variant, return base widget class
        if not accent and not variant:
            return widget_class

        # Initialize style_options to empty dict if None
        if style_options is None:
            style_options = {}

        surface = style_options.get("surface")

        builder_variant = variant if variant is not None else \
            StyleBuilderTtk.get_default_variant(widget_class)

        custom_prefix = None

        if style_options.keys() or surface != 'background':
            import hashlib
            import json
            options_str = json.dumps(style_options, sort_keys=True)
            options_hash = hashlib.md5(options_str.encode()).hexdigest()[:8]
            custom_prefix = f"bs[{options_hash}]"

        ttk_style = generate_ttk_style_name(
            accent=accent,
            variant=variant,
            widget_class=widget_class,
            custom_prefix=custom_prefix,
            orient=style_options.get('orient'),
        )

        from bootstack.style.style import get_style
        style = get_style()

        style.create_style(
            widget_class=widget_class,
            variant=builder_variant,
            ttk_style=ttk_style,
            accent=accent,
            options=style_options
        )

        return ttk_style

    @staticmethod
    def override_ttk_widget_constructor(func):
        """Override ttk widget __init__ to accept accent and variant parameters."""

        def __init__wrapper(self, *args, **kwargs):

            # Extract accent/variant parameters
            accent = kwargs.pop("accent", None)
            if accent == 'default':
                accent = None
            variant = kwargs.pop("variant", None)

            had_style_kwarg = 'style' in kwargs

            style_options = kwargs.pop("style_options", {})
            inherit_surface = kwargs.pop('inherit_surface', None)
            surface_token = kwargs.pop('surface', None)
            input_bg_token = kwargs.pop('input_background', None)

            # Extract ttk_class for style lookup (doesn't affect widget's actual class_)
            # This allows custom style builders without affecting bindtags
            ttk_class = kwargs.pop('ttk_class', None)

            func(self, *args, **kwargs)  # the actual widget constructor

            # Use ttk_class for style lookup if provided, otherwise use widget's actual class
            widget_class = self.winfo_class()
            style_class = ttk_class or widget_class

            # ===== Surface color inheritance =====

            # Surface inheritance is always on in this framework (the former
            # `inherit_surface_color` app toggle was removed); an explicit
            # per-call `inherit_surface` kwarg can still override locally.
            if inherit_surface is None:
                inherit_surface = True

            if hasattr(self, 'master') and self.master is not None:
                parent_surface_token = getattr(self.master, '_surface', 'content')
            else:
                parent_surface_token = 'content'

            if surface_token:
                effective_surface_token = surface_token
            elif inherit_surface:
                effective_surface_token = parent_surface_token
            else:
                effective_surface_token = 'content'

            # container widgets can take their surface color from the accent param
            # Use style_class so custom ttk_class like 'Field' can opt out of this behavior
            if accent and style_class in CONTAINER_CLASSES and surface_token is None:
                effective_surface_token = accent

            # cache the surface color for child components
            setattr(self, '_surface', effective_surface_token)
            if effective_surface_token != 'content' and effective_surface_token is not None:
                style_options.setdefault('surface', effective_surface_token)

            # ===== Input background inheritance =====

            if hasattr(self, 'master') and self.master is not None:
                parent_input_bg = getattr(self.master, '_input_background', None)
            else:
                parent_input_bg = None

            if input_bg_token:
                effective_input_bg = input_bg_token
            elif inherit_surface and parent_input_bg:
                effective_input_bg = parent_input_bg
            else:
                effective_input_bg = None

            setattr(self, '_input_background', effective_input_bg)
            if effective_input_bg:
                style_options.setdefault('input_background', effective_input_bg)

            # ==== Orientation =====

            # handle widgets with orientation
            if widget_class in ORIENT_CLASSES:
                orient = str(self.cget('orient'))
                style_options.setdefault('orient', orient)

            # ==== Create actual ttk style & assign to widget =====

            if (accent or variant) and style_class:

                ttk_style = StyleResolver.create_ttk_style(
                    widget_class=style_class,
                    style_options=style_options,
                    accent=accent,
                    variant=variant,
                )
                self.configure(style=ttk_style)

            elif style_class and not had_style_kwarg:
                from bootstack.style.style_builder_ttk import StyleBuilderTtk
                from bootstack.style.style import get_style

                default_variant = StyleBuilderTtk.get_default_variant(style_class)

                if StyleBuilderTtk.has_builder(style_class, default_variant):

                    # Build options first so we can decide if a custom bs[...] prefix is needed
                    custom_prefix = None
                    if style_options.keys():
                        import hashlib
                        import json
                        options_str = json.dumps(style_options, sort_keys=True)
                        options_hash = hashlib.md5(options_str.encode()).hexdigest()[:8]
                        custom_prefix = f"bs[{options_hash}]"

                    ttk_style = generate_ttk_style_name(
                        accent=None,
                        variant=default_variant,
                        widget_class=style_class,
                        custom_prefix=custom_prefix,
                    )

                    style_instance = get_style()
                    if style_instance is not None:
                        style_instance.create_style(
                            widget_class=style_class,
                            variant=default_variant,
                            ttk_style=ttk_style,
                            options=style_options,
                        )
                        self.configure(style=ttk_style)
                else:
                    self.configure(style=style_class)

            # Store accent, variant, ttk_class, and style_options for later retrieval
            setattr(self, '_accent', accent)
            setattr(self, '_variant', variant)
            setattr(self, '_ttk_class', ttk_class)
            setattr(self, '_style_options', style_options)

        return __init__wrapper

    @staticmethod
    def override_tk_widget_constructor(func):
        """Override Tk widget __init__ to apply theme background when autostyle=True."""

        def __init__wrapper(self, *args, **kwargs):

            # capture bootstrap arguments
            auto_style = kwargs.pop("autostyle", True)

            # Class-level opt-out: widget manages its own styling
            if auto_style and not getattr(type(self), '_bs_autostyle', True):
                auto_style = False

            # Parent-level opt-out: parent manages styling for its children
            if auto_style:
                master = args[0] if args else kwargs.get('master')
                if master is not None and not getattr(master, '_bs_autostyle', True):
                    auto_style = False

            inherit_surface = kwargs.pop('inherit_surface', None)
            surface_token = kwargs.pop('surface', None)

            # Outside an active App there is no theme/settings context — build
            # the widget as plain Tk (no autostyle) instead of raising.
            if not has_current_app():
                func(self, *args, **kwargs)
                setattr(self, '_surface', surface_token or 'content')
                return

            if inherit_surface is None:
                inherit_surface = True

            func(self, *args, **kwargs)  # the actual constructor

            # ===== Surface color inheritance =====

            if hasattr(self, 'master') and self.master is not None:
                parent_surface_token = getattr(self.master, '_surface', 'content')
            else:
                parent_surface_token = 'content'

            # An explicit `surface=` always wins; otherwise inherit from the
            # parent (the default) or fall back to 'content'. (This mirrors the
            # ttk autostyle path — the Tk path previously let inheritance clobber
            # an explicit surface, freezing e.g. a meter canvas to a resolved hex.)
            if surface_token is None:
                surface_token = parent_surface_token if inherit_surface else 'content'

            setattr(self, '_surface', surface_token)

            if not auto_style:
                return

            # ==== Apply the initial theme background =====
            # `_surface` (the token, set above) is what the unified theme walk
            # later re-resolves on a theme change; `_bs_theme_version` lets the
            # walk tell whether this widget already matches the current theme.

            from bootstack.style.style import get_style
            style = get_style()
            surface = getattr(self, '_surface', 'content')
            style._get_tk_builder().call_builder(self, surface=surface)
            self._bs_theme_version = style._theme_version

        return __init__wrapper


__all__ = [
    'generate_ttk_style_name',
    'extract_accent_from_style',
    'extract_variant_from_style',
    'extract_widget_class_from_style',
    'StyleResolver',
]
