"""Flat configuration properties shared by `App` and `AppShell`.

The public app surface exposes configuration as flat `app.*` properties, so
that what goes in through the constructor comes back out symmetrically:
`App(theme=...)` in, `app.theme` out. Settable knobs reflect live where the
machinery supports a runtime change (theme, locale, title); locale-derived
formats are read-only.

`AppConfigMixin` delegates to the internal runtime `App` returned by
`_config_app()`, which each public class implements.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any, Callable, Sequence, overload

from bootstack.events import Subscription

if TYPE_CHECKING:
    from bootstack.streams import Stream
    from bootstack.widgets.types import WindowStyle


class AppConfigMixin:
    """Mixin providing flat configuration properties for the public app.

    Subclasses must implement `_config_app()` to return the internal runtime
    `App` (a `tkinter.Tk` subclass) whose `settings` holds the resolved
    configuration.
    """

    def _config_app(self) -> Any:
        """Return the internal runtime `App` backing this public app."""
        raise NotImplementedError

    @property
    def _settings(self) -> Any:
        return self._config_app().settings

    # ----- identity -----

    @property
    def title(self) -> str:
        """The window title bar text (also the app's display name)."""
        return self._config_app().title()

    @title.setter
    def title(self, value: str) -> None:
        app = self._config_app()
        app.title(value)
        app.settings.app_name = value

    # The app name (config-directory / taskbar identity) is set via `title=`
    # (which writes both the title bar and `app_name`); there is no separate
    # public `name` property — it was redundant with `title`.

    # ----- theme -----

    @property
    def theme(self) -> str:
        """The active theme name. Setting it switches the theme live."""
        from bootstack.style.style import get_theme
        return get_theme()

    @theme.setter
    def theme(self, value: str) -> None:
        from bootstack.style.style import set_theme
        set_theme(value)
        self._settings.theme = value

    @property
    def light_theme(self) -> str:
        """Theme used for the light end of system-appearance / `toggle_theme`."""
        return self._settings.light_theme

    @light_theme.setter
    def light_theme(self, value: str) -> None:
        self._settings.light_theme = value

    @property
    def dark_theme(self) -> str:
        """Theme used for the dark end of system-appearance / `toggle_theme`."""
        return self._settings.dark_theme

    @dark_theme.setter
    def dark_theme(self, value: str) -> None:
        self._settings.dark_theme = value

    @property
    def follow_system_appearance(self) -> bool:
        """Whether the app tracks the OS light/dark appearance (macOS)."""
        return self._settings.follow_system_appearance

    @follow_system_appearance.setter
    def follow_system_appearance(self, value: bool) -> None:
        self._settings.follow_system_appearance = value

    # `available_themes` is intentionally construction-only (no runtime property):
    # `App(available_themes=...)` reads as an input ("offer these themes"), but a
    # getter would collide with `get_themes()` (the actual theme-list query) and
    # return `()` by default. Read the exposed list via `get_themes()`.

    # ----- localization -----

    @property
    def locale(self) -> str | None:
        """The active locale (e.g. `'en_US'`). Setting it switches locale live."""
        return self._settings.locale

    @locale.setter
    def locale(self, value: str) -> None:
        from bootstack.i18n.msgcat import MessageCatalog
        MessageCatalog.locale(value)
        self._settings.locale = value

    # `localize_mode` is construction-only (no runtime property): changing it
    # would only affect widgets created afterward, not the existing UI, so a
    # live setter would be misleading. Pass it to the constructor.

    @property
    def locale_language(self) -> str | None:
        """Base language code derived from the locale (e.g. `'en'`). Read-only."""
        from bootstack._runtime.app import _language_from_locale
        loc = self._settings.locale
        return _language_from_locale(loc) if loc else None

    @property
    def locale_date_format(self) -> str | None:
        """Short date pattern for the active locale (e.g. `'M/d/yy'`). Read-only."""
        from bootstack._runtime.app import _safe_date_format
        loc = self._settings.locale
        return _safe_date_format(loc) if loc else None

    @property
    def locale_time_format(self) -> str | None:
        """Short time pattern for the active locale, e.g. h:mm a. Read-only."""
        from bootstack._runtime.app import _safe_time_format
        loc = self._settings.locale
        return _safe_time_format(loc) if loc else None

    @property
    def locale_decimal(self) -> str | None:
        """Decimal separator for the active locale (e.g. `'.'`). Read-only."""
        from bootstack._runtime.app import _safe_decimal_symbol
        loc = self._settings.locale
        return _safe_decimal_symbol(loc) if loc else None

    @property
    def locale_thousands(self) -> str | None:
        """Thousands separator for the active locale (e.g. `','`). Read-only."""
        from bootstack._runtime.app import _safe_group_symbol
        loc = self._settings.locale
        return _safe_group_symbol(loc) if loc else None

    # ----- platform / window state -----

    @property
    def window_style(self) -> WindowStyle | str | None:
        """Windows-only window effect, or None to disable."""
        return self._settings.window_style

    @window_style.setter
    def window_style(self, value: WindowStyle | str | None) -> None:
        app = self._config_app()
        app.settings.window_style = value
        # Best-effort live re-apply (Windows / pywinstyles only).
        try:
            app._window_style = value
            app._window_style_applied = False
            app._apply_window_style()
        except Exception:
            pass

    # `macos_quit_behavior` and `state_path` are construction-only (no runtime
    # properties): both are set-once startup configuration that a user would not
    # change while the app runs. Pass them to the constructor.

    @property
    def remember_window_state(self) -> bool:
        """Whether window geometry is saved on close and restored on launch."""
        return self._settings.remember_window_state

    @remember_window_state.setter
    def remember_window_state(self, value: bool) -> None:
        self._settings.remember_window_state = value

    # ----- configuration-change events -----

    def _bind_value_event(
        self,
        sequence: str,
        key: str,
        handler: Callable[[Any], Any] | None,
    ) -> "Stream | Subscription":
        app = self._config_app()

        def _decode(h: Callable[[Any], Any]) -> Callable[[Any], Any]:
            def _wrapped(raw: Any) -> Any:
                data = getattr(raw, "data", None)
                value = data.get(key) if isinstance(data, dict) else data
                return h(value)
            return _wrapped

        if handler is None:
            from bootstack.streams import Stream

            def _source(h: Callable[[Any], Any]) -> Subscription:
                bid = app.bind(sequence, _decode(h), add="+")
                return Subscription(app, sequence, bid)

            return Stream(app, _source=_source)
        bid = app.bind(sequence, _decode(handler), add="+")
        return Subscription(app, sequence, bid)

    @overload
    def on_theme_change(self) -> "Stream": ...
    @overload
    def on_theme_change(self, handler: Callable[[str], Any]) -> Subscription: ...
    def on_theme_change(
        self, handler: Callable[[str], Any] | None = None
    ) -> "Stream | Subscription":
        """React to theme changes; the handler receives the new theme name.

        Fired after the theme is fully rebuilt, so handlers can safely read new
        colors. Useful for persisting the choice, e.g.
        `app.on_theme_change(lambda t: store.update(theme=t))`.

        Returns:
            `Subscription` (with handler) or `Stream` (without handler).
        """
        return self._bind_value_event("<<BsThemeChanged>>", "theme", handler)

    @overload
    def on_locale_change(self) -> "Stream": ...
    @overload
    def on_locale_change(self, handler: Callable[[str], Any]) -> Subscription: ...
    def on_locale_change(
        self, handler: Callable[[str], Any] | None = None
    ) -> "Stream | Subscription":
        """React to locale changes; the handler receives the new locale code.

        Returns:
            `Subscription` (with handler) or `Stream` (without handler).
        """
        return self._bind_value_event("<<LocaleChanged>>", "locale", handler)


# The set of App() constructor kwargs that map to configuration. Used by
# App.from_store() to tolerantly filter a persisted dict (version skew).
APP_CONFIG_KWARGS: frozenset[str] = frozenset({
    "title",
    "theme",
    "light_theme",
    "dark_theme",
    "follow_system_appearance",
    "available_themes",
    "locale",
    "localize_mode",
    "window_style",
    "macos_quit_behavior",
    "remember_window_state",
    "state_path",
})


__all__ = ["AppConfigMixin", "APP_CONFIG_KWARGS"]
