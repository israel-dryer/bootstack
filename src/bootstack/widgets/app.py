from __future__ import annotations

from typing import TYPE_CHECKING, Any, Callable, Literal, Sequence

from bootstack._runtime.app import App as _InternalApp, LocalizeMode

if TYPE_CHECKING:
    from bootstack.images import AppIcon, Image
from bootstack.widgets._impl.primitives.packframe import PackFrame
from bootstack.widgets._core.app_config import AppConfigMixin, APP_CONFIG_KWARGS
from bootstack.widgets._core.container import PublicContainer, PACK_KEYS, normalize_fill
from bootstack.widgets._core.window_controls import WindowControlsMixin
from bootstack.widgets._core.window_menu import ChromeHostMixin
from bootstack.widgets.types import Padding, Fill, Anchor, SurfaceToken, WindowStyle


class App(AppConfigMixin, WindowControlsMixin, ChromeHostMixin, PublicContainer):
    """The application window. Behaves as an implicit VStack from the user's
    perspective: accepts `padding`, `gap`, `fill_items`, `expand_items`, and
    `anchor_items` and applies them to its internal content frame.

    Configuration is a single flat path: pass options as constructor kwargs and
    read or change them through matching `app.*` properties (e.g. `app.theme`,
    `app.locale`). Setting `app.theme` or `app.locale` takes effect live.

    Args:
        title: Window title bar text and the app's display name.
        size: Initial window size as `(width, height)`.
        icon: Title-bar and taskbar icon — an icon file path, an `Image` handle,
            or an `AppIcon`. Defaults to the bootstack icon.
        theme: Theme name to apply on startup (e.g. `'bootstrap-dark'`).
        light_theme: Theme used for the light end of system-appearance
            tracking and `toggle_theme`.
        dark_theme: Theme used for the dark end of system-appearance
            tracking and `toggle_theme`.
        follow_system_appearance: If True, switch between `light_theme` and
            `dark_theme` to match the OS (currently effective on macOS).
        available_themes: Theme names to expose to theme pickers. Empty means
            all registered themes.
        locale: Locale identifier (e.g. `'en_US'`, `'de_DE'`). Auto-detected
            from the system when not given.
        localize_mode: Localization behavior.
        window_style: Windows-only window effect, or None to disable.
        macos_quit_behavior: macOS close / Cmd+Q behavior. No-op on Win/Linux.
        remember_window_state: If True, window geometry is saved on close and
            restored on next launch.
        state_path: Optional override for the persisted window-state file.
        on_close: Handler invoked when the user clicks the window's close button.
            Return `False` to veto the close; return `None` or `True` to allow
            it. Not called by the programmatic `close()`.
        position: Initial window position as `(x, y)`.
        min_size: Minimum window size as `(width, height)`.
        max_size: Maximum window size as `(width, height)`.
        resizable: Whether the window can be resized as `(width, height)`.
        scaling: Explicit UI scaling factor. When None, scaling is automatic.
        hdpi: Enable high-DPI awareness for the application. Default `True`.
        padding: Inner padding applied to the content frame.
        gap: Spacing between stacked children. Default `0`.
        fill_items: Default `fill` for children that don't set their own.
        expand_items: Default `expand` for children that don't set their own.
        anchor_items: Default anchor for children that don't fill their cell.
        surface: Background surface for the content frame.
    """

    _auto_place = False  # no parent

    def __init__(
        self,
        *,
        title: str | None = None,
        size: tuple[int, int] | None = None,
        icon: "str | Image | AppIcon | None" = None,
        theme: str | None = None,
        # theme
        light_theme: str = "bootstrap-light",
        dark_theme: str = "bootstrap-dark",
        follow_system_appearance: bool = False,
        available_themes: Sequence[str] = (),
        # localization
        locale: str | None = None,
        localize_mode: LocalizeMode = "auto",
        # platform / window-state persistence
        window_style: WindowStyle | str | None = "mica",
        macos_quit_behavior: Literal['native', 'classic'] = "native",
        remember_window_state: bool = False,
        state_path: str | None = None,
        on_close: Callable[[], bool | None] | None = None,
        # window placement / display
        position: tuple[int, int] | None = None,
        min_size: tuple[int, int] | None = None,
        max_size: tuple[int, int] | None = None,
        resizable: tuple[bool, bool] | None = None,
        scaling: float | None = None,
        hdpi: bool = True,
        # Child-guidance (applied to the internal content frame)
        padding: Padding | None = None,
        gap: int = 0,
        fill_items: Fill | None = None,
        expand_items: bool | None = None,
        anchor_items: Anchor | None = None,
        surface: SurfaceToken | str | None = None,
        # Extra kwargs forwarded to the internal App (icon, position, etc.)
        **app_kwargs: Any,
    ) -> None:
        self._parent = None

        init_kwargs: dict[str, Any] = {
            "light_theme": light_theme,
            "dark_theme": dark_theme,
            "follow_system_appearance": follow_system_appearance,
            "available_themes": available_themes,
            "locale": locale,
            "localize_mode": localize_mode,
            "window_style": window_style,
            "macos_quit_behavior": macos_quit_behavior,
            "remember_window_state": remember_window_state,
            "state_path": state_path,
            "scaling": scaling,
            "hdpi": hdpi,
        }
        if title is not None:
            init_kwargs["title"] = title
        if size is not None:
            init_kwargs["size"] = size
        if theme is not None:
            init_kwargs["theme"] = theme
        if position is not None:
            init_kwargs["position"] = position
        if min_size is not None:
            init_kwargs["minsize"] = min_size
        if max_size is not None:
            init_kwargs["maxsize"] = max_size
        if resizable is not None:
            init_kwargs["resizable"] = resizable
        if on_close is not None:
            init_kwargs["on_close"] = on_close

        init_kwargs.update(app_kwargs)

        self._tk_root = _InternalApp(**init_kwargs)

        # Resolve the icon AFTER the root exists. An `AppIcon` may resolve theme
        # color tokens (which need the style/root) and a deferred `Image` must be
        # rendered against the root — doing either before the root would spin up
        # a stray default root and bind the icon to the wrong interpreter.
        self._app_icon_photo = None
        if icon is not None:
            from bootstack.widgets._core.image_binding import resolve_window_icon

            icon_path, icon_image = resolve_window_icon(icon)
            if icon_path is not None:
                self._tk_root._setup_icon(icon_path)
            elif icon_image is not None:
                self._app_icon_photo = icon_image._materialize()
                self._tk_root._setup_icon(self._app_icon_photo)

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
            .. code-block:: python

               from bootstack.store import Store

               store = Store("settings")
               app = bs.App.from_store(store)
               app.on_theme_change(lambda t: store.update(theme=t))
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
        # Let the internal mainloop center and *then* show the window — it
        # flushes layout and applies the window style while still withdrawn, so
        # the window is fully drawn and positioned before it becomes visible.
        # (Deiconifying here first would map it uncentered, then jump on center.)
        self._tk_root.mainloop()

    def __exit__(self, exc_type, exc, tb) -> None:
        super().__exit__(exc_type, exc, tb)
        try:
            self._tk_root.update_idletasks()
        except Exception:
            pass
        return None
