"""StyleRegistry — manages named styles and their Tk tag configurations.

Styles are defined once with semantic tokens (theme colors, font tokens).
On <<ThemeChanged>>, all configured tags are reconfigured automatically.
Each (layer, style) pair gets its own Tk tag: `bs::{layer}::{style}`.
"""
from __future__ import annotations

import tkinter as tk
from typing import Any, TYPE_CHECKING

if TYPE_CHECKING:
    from bootstack.widgets._impl.composites.textarea.core import _MultilineCore


class StyleRegistry:
    """Manages named styles and applies them as Tk text tags.

    Styles are defined with semantic attributes (theme tokens, font tokens).
    The registry resolves tokens to concrete colors/fonts at configure time
    and reconfigures on `<<ThemeChanged>>`.
    """

    def __init__(self, core: _MultilineCore) -> None:
        self._core = core
        self._text = core.text
        # style_name -> raw attribute dict (may contain tokens)
        self._styles: dict[str, dict[str, Any]] = {}
        # set of "layer::style" tag names already configured on the Text widget
        self._configured: set[str] = set()

        self._text.bind("<<ThemeChanged>>", self._on_theme_changed, add="+")

    # ── public API ────────────────────────────────────────────────────────

    def define_style(
        self,
        name: str,
        *,
        foreground: str | None = None,
        background: str | None = None,
        font: str | None = None,
        underline: bool = False,
        underline_color: str | None = None,
        spacing1: int | None = None,
        spacing3: int | None = None,
        cursor: str | None = None,
    ) -> None:
        """Define or update a named style.

        Args:
            name: Style identifier used in decoration objects.
            foreground: Text color — a theme token (e.g. `'primary'`) or
                literal color string. `None` leaves foreground unchanged.
            background: Background color — token or literal. `None` leaves
                background unchanged.
            font: Font token (e.g. `'code[bold]'`) or font name. `None`
                leaves font unchanged.
            underline: If True, underline text in this style.
            underline_color: Color for the underline (Tk 8.7+).
            spacing1: Extra space above lines.
            spacing3: Extra space below lines.
            cursor: Cursor name when hovering over this style.
        """
        self._styles[name] = {
            k: v for k, v in {
                'foreground': foreground,
                'background': background,
                'font': font,
                'underline': underline,
                'underline_color': underline_color,
                'spacing1': spacing1,
                'spacing3': spacing3,
                'cursor': cursor,
            }.items() if v is not None and v is not False
        }
        # If any Tk tags already exist for this style, re-apply immediately so
        # that callers who redefine a style (e.g. swapping syntax highlighters)
        # see the new color without having to trigger a full redecoration.
        suffix = f"::{name}"
        attrs = self._resolve(self._styles[name])
        if attrs:
            for tag in self._configured:
                if tag.endswith(suffix):
                    try:
                        self._text.tag_configure(tag, **attrs)
                    except tk.TclError:
                        pass

    def configure_tag(self, layer: str, style: str) -> None:
        """Create and configure the Tk tag for a (layer, style) pair."""
        tag = _tag_name(layer, style)
        attrs = self._resolve(self._styles.get(style, {}))
        if attrs:
            self._text.tag_configure(tag, **attrs)
        self._configured.add(tag)

    def tag_name(self, layer: str, style: str) -> str:
        """Return the Tk tag name for a (layer, style) pair."""
        return _tag_name(layer, style)

    def is_configured(self, layer: str, style: str) -> bool:
        """Return True if the Tk tag for this pair has been configured."""
        return _tag_name(layer, style) in self._configured

    # ── theme integration ─────────────────────────────────────────────────

    def _on_theme_changed(self, _event=None) -> None:
        """Reconfigure all registered tags when the theme changes."""
        for tag in self._configured:
            parts = tag.replace("bs::", "", 1).split("::", 1)
            if len(parts) == 2:
                _, style = parts
                attrs = self._resolve(self._styles.get(style, {}))
                if attrs:
                    try:
                        self._text.tag_configure(tag, **attrs)
                    except tk.TclError:
                        pass

    def _resolve(self, raw: dict[str, Any]) -> dict[str, Any]:
        """Resolve token values to concrete colors/fonts."""
        out: dict[str, Any] = {}
        for key, value in raw.items():
            if key in ('foreground', 'background') and isinstance(value, str):
                out[key] = self._resolve_color(value)
            elif key == 'font' and isinstance(value, str):
                out[key] = self._resolve_font(value)
            else:
                out[key] = value
        return out

    def _resolve_color(self, token: str) -> str:
        """Resolve a theme color token to a hex color, or return as-is."""
        try:
            from bootstack.style.style import get_theme_provider
            colors = get_theme_provider().colors
            if token in colors:
                return colors[token]
        except Exception:
            pass
        return token

    def _resolve_font(self, token: str) -> Any:
        """Resolve a font token to a Tk font name, or return as-is."""
        try:
            import tkinter.font as tkfont
            if tkfont.nametofont(token):
                return token
        except Exception:
            pass
        return token


def _tag_name(layer: str, style: str) -> str:
    return f"bs::{layer}::{style}"
