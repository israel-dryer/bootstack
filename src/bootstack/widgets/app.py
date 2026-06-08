from __future__ import annotations

from typing import Any, Sequence

from bootstack._runtime.app import App as _InternalApp, LocalizeMode
from bootstack.widgets._impl.primitives.packframe import PackFrame
from bootstack.widgets._core.app_config import AppConfigMixin, APP_CONFIG_KWARGS
from bootstack.widgets._core.container import PublicContainer, PACK_KEYS, normalize_fill


class App(AppConfigMixin, PublicContainer):
    """The application window. Behaves as an implicit VStack from the user's
    perspective: accepts `padding`, `gap`, `fill_items`, `expand_items`, and
    `anchor_items` and applies them to its internal content frame.

    Configuration is a single flat path: pass options as constructor kwargs and
    read or change them through matching `app.*` properties (e.g. `app.theme`,
    `app.locale`). Setting `app.theme` or `app.locale` takes effect live.

    Args:
        title: Window title bar text and the app's display name.
        size: Initial window size as `(width, height)`.
        theme: Theme name to apply on startup (e.g. `'bootstrap-dark'`).
        app_author: Application author. Reserved for config-path use.
        app_version: Application version string.
        light_theme: Theme used for the light end of system-appearance
            tracking and `toggle_theme`.
        dark_theme: Theme used for the dark end of system-appearance
            tracking and `toggle_theme`.
        follow_system_appearance: If True, switch between `light_theme` and
            `dark_theme` to match the OS (currently effective on macOS).
        available_themes: Theme names to expose to theme pickers. Empty means
            all registered themes.
        inherit_surface_color: If True, child widgets inherit the parent's
            surface color for consistent backgrounds.
        locale: Locale identifier (e.g. `'en_US'`, `'de_DE'`). Auto-detected
            from the system when not given.
        localize_mode: Localization behavior — `'auto'`, `True`, or `False`.
        window_style: Windows-only window effect (`'mica'`, `'acrylic'`,
            `'aero'`, `'transparent'`, `'win7'`) or None to disable.
        macos_quit_behavior: macOS close / Cmd+Q behavior — `'native'` or
            `'classic'`. No-op on Win/Linux.
        remember_window_state: If True, window geometry is saved on close and
            restored on next launch.
        state_path: Optional override for the persisted window-state file.

    `app.tk` returns the underlying `tk.Tk` root window.
    """

    _auto_place = False  # no parent

    def __init__(
        self,
        *,
        title: str | None = None,
        size: tuple[int, int] | None = None,
        theme: str | None = None,
        # application identity
        app_author: str | None = None,
        app_version: str | None = None,
        # theme
        light_theme: str = "bootstrap-light",
        dark_theme: str = "bootstrap-dark",
        follow_system_appearance: bool = False,
        available_themes: Sequence[str] = (),
        inherit_surface_color: bool = True,
        # localization
        locale: str | None = None,
        localize_mode: LocalizeMode = "auto",
        # platform / window-state persistence
        window_style: str | None = "mica",
        macos_quit_behavior: str = "native",
        remember_window_state: bool = False,
        state_path: str | None = None,
        # Child-guidance (applied to the internal content frame)
        padding: Any = None,
        gap: int = 0,
        fill_items: str | None = None,
        expand_items: bool | None = None,
        anchor_items: str | None = None,
        surface: str | None = None,
        # Extra kwargs forwarded to the internal App (icon, position, etc.)
        **app_kwargs: Any,
    ) -> None:
        self._parent = None

        init_kwargs: dict[str, Any] = {
            "app_author": app_author,
            "app_version": app_version,
            "light_theme": light_theme,
            "dark_theme": dark_theme,
            "follow_system_appearance": follow_system_appearance,
            "available_themes": available_themes,
            "inherit_surface_color": inherit_surface_color,
            "locale": locale,
            "localize_mode": localize_mode,
            "window_style": window_style,
            "macos_quit_behavior": macos_quit_behavior,
            "remember_window_state": remember_window_state,
            "state_path": state_path,
        }
        if title is not None:
            init_kwargs["title"] = title
        if size is not None:
            init_kwargs["size"] = size
        if theme is not None:
            init_kwargs["theme"] = theme
        init_kwargs.update(app_kwargs)

        self._tk_root = _InternalApp(**init_kwargs)

        frame_kwargs: dict[str, Any] = {
            "direction": "vertical",
            "gap": gap,
            "fill_items": normalize_fill(fill_items),
            "expand_items": expand_items,
            "anchor_items": anchor_items,
        }
        if padding is not None:
            frame_kwargs["padding"] = padding
        if surface is not None:
            frame_kwargs["surface"] = surface

        self._content_frame = PackFrame(self._tk_root, **frame_kwargs)
        self._content_frame.pack(fill="both", expand=True)

        self._internal = self._tk_root

    @classmethod
    def from_store(cls, store: Any, **overrides: Any) -> "App":
        """Construct an `App` from a persisted `Store` (or plain dict).

        Reads configuration from `store` and applies it as constructor kwargs,
        tolerantly ignoring any keys that are not valid `App` configuration —
        so a settings file written by an older or newer version (with renamed
        or removed keys) still restores cleanly instead of raising. Explicit
        keyword `overrides` win over stored values.

        Args:
            store: A `Store` (anything with `as_dict()`) or a mapping of
                configuration values.
            **overrides: Configuration kwargs that take precedence over the
                stored values.

        Returns:
            A new `App` configured from the store.

        Example:
            ```python
            from bootstack.store import Store

            store = Store("settings")
            app = bs.App.from_store(store)
            app.on_theme_change(lambda t: store.update(theme=t))
            ```
        """
        data = store.as_dict() if hasattr(store, "as_dict") else dict(store)
        kwargs = {k: v for k, v in data.items() if k in APP_CONFIG_KWARGS}
        kwargs.update(overrides)
        return cls(**kwargs)

    def _config_app(self) -> Any:
        return self._tk_root

    def _child_master(self):
        """Children pack into the content frame, not the Tk root."""
        return self._content_frame

    def _default_layout_method(self) -> str:
        return "pack"

    def _merge_layout_options(self, child: Any, layout_kw: dict) -> tuple[str, dict]:
        options = {k: v for k, v in layout_kw.items() if k in PACK_KEYS}
        return ("pack", options)

    def run(self) -> None:
        """Show the window and start the event loop."""
        self._tk_root.deiconify()
        self._tk_root.mainloop()

    mainloop = run

    def __exit__(self, exc_type, exc, tb) -> None:
        super().__exit__(exc_type, exc, tb)
        try:
            self._tk_root.update_idletasks()
        except Exception:
            pass
        return None
