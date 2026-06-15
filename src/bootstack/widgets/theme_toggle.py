"""ThemeToggle — a sun/moon icon button that flips the application theme."""
from __future__ import annotations

from typing import Any

from bootstack.style import toggle_theme
from bootstack.widgets.button import Button
from bootstack.widgets.types import AccentToken, ButtonVariant, WidgetDensity


def _theme_is_dark() -> bool:
    """Return whether the active theme's mode is dark."""
    from bootstack.style.theme_provider import use_theme

    try:
        return use_theme().mode == "dark"
    except Exception:
        return False


class ThemeToggle(Button):
    """An icon button that switches between the light and dark theme.

    Shows the `light_icon` (a sun) in light mode and the `dark_icon` (a moon) in
    dark mode. Clicking it calls `toggle_theme()`; its icon follows the active
    theme, so it stays correct when the theme is changed elsewhere too.

    It is a plain button — a stateless action whose icon merely reflects the
    current theme — so there is no checked state to keep in sync and no risk of
    looping. Supports the button `variant` and `density`.

    Args:
        light_icon: Bootstrap Icons name shown in light mode. Default `'sun-fill'`.
        dark_icon: Bootstrap Icons name shown in dark mode. Default
            `'moon-stars-fill'`.
        variant: Button style variant — `'default'`, `'solid'`, `'outline'`, or
            `'ghost'`. Default `'ghost'`.
        density: Padding density — `'default'` or `'compact'`.
        accent: Accent token applied to the icon. Defaults to the foreground.
        parent: Explicit parent widget. If omitted, the current context-stack
            container is used.
        **kwargs: Layout placement options applied by the parent container —
            `fill`, `expand`, `anchor`, `margin`, `row`, `column`, `sticky`.
            See :doc:`/tasks/layout`.
    """

    def __init__(
        self,
        *,
        light_icon: str = "sun-fill",
        dark_icon: str = "moon-stars-fill",
        variant: ButtonVariant = "ghost",
        density: WidgetDensity = "default",
        accent: AccentToken | str | None = None,
        parent: Any = None,
        **kwargs: Any,
    ) -> None:
        self._light_icon = light_icon
        self._dark_icon = dark_icon
        super().__init__(
            on_click=toggle_theme,
            icon=self._theme_icon(),
            variant=variant,
            density=density,
            accent=accent,
            parent=parent,
            **kwargs,
        )

        # Keep the icon matching the active theme — clicking this button (or any
        # other theme change) refreshes it. Setting the icon never fires a click,
        # so there is no cycle.
        self._theme_toplevel = self._internal.winfo_toplevel()
        self._theme_bind = self._theme_toplevel.bind(
            "<<BsThemeChanged>>", self._sync_icon, add="+"
        )
        self.on_destroy(self._cleanup_theme_toggle)

    def _theme_icon(self) -> str:
        return self._dark_icon if _theme_is_dark() else self._light_icon

    def _sync_icon(self, _event: Any = None) -> None:
        self.icon = self._theme_icon()

    def _cleanup_theme_toggle(self, _event: Any = None) -> None:
        try:
            self._theme_toplevel.unbind("<<BsThemeChanged>>", self._theme_bind)
        except Exception:
            pass


__all__ = ["ThemeToggle"]
