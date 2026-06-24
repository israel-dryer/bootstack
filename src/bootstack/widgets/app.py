from __future__ import annotations

import sys
from typing import TYPE_CHECKING, Any, Callable, Literal, Sequence

from bootstack._runtime.app import App as _InternalApp, LocalizeMode

if TYPE_CHECKING:
    from bootstack.images import AppIcon, Image
from bootstack.widgets._impl.primitives.flexframe import FlexFrame
from bootstack.widgets._core.app_config import AppConfigMixin, APP_CONFIG_KWARGS
from bootstack.widgets._core.container import FlexContainer
from bootstack.widgets._core.window_controls import WindowControlsMixin
from bootstack.widgets._core.window_menu import ChromeHostMixin
from bootstack.widgets.types import (
    Padding, HAlign, VArrange, SurfaceToken, WindowStyle,
)


class App(AppConfigMixin, WindowControlsMixin, ChromeHostMixin, FlexContainer):
    """The application window. Behaves as an implicit Column from the user's
    perspective: accepts `padding`, `gap`, `horizontal_items`, `vertical_items`,
    and `grow_items` and applies them to its internal content frame.

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
        undecorated: Remove the OS title bar and border (borderless window).
            Ignored on macOS. The app gets a built-in draggable title bar with
            min/max/close so it stays movable and closeable; add your own with
            `add_toolbar(show_window_controls=True)` to take over the chrome.
        padding: Inner padding applied to the content frame.
        gap: Spacing between stacked children. Default `0`.
        horizontal_items: Horizontal alignment of children — `'left'`,
            `'center'`, `'right'`, or `'stretch'` (fill the width). Default
            `'center'`.
        vertical_items: How children are arranged top to bottom — `'top'`,
            `'center'`, `'bottom'`, or a `'space-*'` mode. Default `'top'`.
        grow_items: When `True`, children grow equally to fill the height.
            Default `False`.
        surface: Background surface for the content frame.
    """

    _auto_place = False  # no parent
    _dev_supports_inprocess = True  # supports in-process hot reload (bootstack dev)

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
        undecorated: bool = False,
        # Child-guidance (applied to the internal content frame)
        padding: Padding | None = None,
        gap: int = 0,
        horizontal_items: HAlign = "center",
        vertical_items: VArrange = "top",
        grow_items: bool = False,
        surface: SurfaceToken | str | None = None,
        # Extra kwargs forwarded to the internal App (icon, position, etc.)
        **app_kwargs: Any,
    ) -> None:
        self._parent = None
        self._dev_body = None  # set in __enter__ under `bootstack dev`

        # Under `bootstack dev`, persist window geometry by default so a
        # process-restart reload re-opens the window where it was. Honors an
        # explicit choice; uses a dev-scoped state file so it never clobbers the
        # app's real saved state.
        from bootstack.dev._env import DEV_MIN_SIZE, is_dev_mode

        if is_dev_mode():
            if not remember_window_state and state_path is None:
                from bootstack._core.paths import app_config_file

                remember_window_state = True
                state_path = str(app_config_file("dev_window_state.json", title or "bootstack"))
            # A usable floor so a reload window starts/stays a sensible size.
            if min_size is None:
                min_size = DEV_MIN_SIZE

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
            "override_redirect": undecorated,
        }
        # overrideredirect has no effect on macOS — so the borderless treatment
        # (custom border + title bar) is Windows/Linux only.
        self._undecorated = undecorated and sys.platform != "darwin"
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
            "horizontal_items": horizontal_items,
            "vertical_items": vertical_items,
            "grow_items": grow_items,
        }
        if padding is not None:
            frame_kwargs["padding"] = padding
        if surface is not None:
            frame_kwargs["surface"] = surface

        # In undecorated mode the OS border is gone; a 1px themed border frame
        # substitutes it and hosts both the chrome stack and the content.
        if self._undecorated:
            from bootstack.widgets._impl.primitives.frame import Frame

            self._region_root = Frame(self._tk_root, show_border=True, padding=1)
            self._region_root.pack(fill="both", expand=True)
        else:
            self._region_root = self._tk_root

        # Stash the content-frame config so dev hot reload can rebuild a fresh
        # content frame with identical guidance after tearing the old one down.
        self._dev_frame_kwargs = dict(frame_kwargs)
        self._content_frame = FlexFrame(self._region_root, **frame_kwargs)
        self._content_frame.pack(fill="both", expand=True)

        self._internal = self._tk_root

    def _toolbar_stack_parent(self) -> Any:
        # The chrome stack lives inside the (bordered) region root, above content.
        return getattr(self, "_region_root", self._tk_root)

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

    @property
    def _flex_frame(self):
        """Children flow into the content frame, not the Tk root."""
        return self._content_frame

    def run(self) -> None:
        """Show the window and start the event loop."""
        self._ensure_default_titlebar()
        from bootstack.dev._env import is_dev_mode

        if is_dev_mode():
            from bootstack.dev._reloader import install_reloader

            install_reloader(self)
        # Let the internal mainloop center and *then* show the window — it
        # flushes layout and applies the window style while still withdrawn, so
        # the window is fully drawn and positioned before it becomes visible.
        # (Deiconifying here first would map it uncentered, then jump on center.)
        self._tk_root.mainloop()

    def __enter__(self) -> "App":
        result = super().__enter__()
        # Under `bootstack dev`, capture where this `with` body lives so a save
        # can re-exec it. No-op (and zero cost) outside dev mode.
        from bootstack.dev._env import is_dev_mode

        if is_dev_mode() and self._dev_body is None:
            import sys as _sys
            from bootstack.dev._capture import capture_from_frame

            try:
                self._dev_body = capture_from_frame(_sys._getframe(1))
            except Exception:
                self._dev_body = None
        return result

    def __exit__(self, exc_type, exc, tb) -> None:
        super().__exit__(exc_type, exc, tb)
        try:
            self._tk_root.update_idletasks()
        except Exception:
            pass
        return None

    # ----- dev hot-reload hooks ----------------------------------------------
    # Used only under `bootstack dev`; see bootstack.dev. AppShell/Workbench
    # override the route hooks to preserve the selected page across a reload.

    def _dev_reset_region(self) -> None:
        """Tear down the chrome + content the `with` body built, keep the root."""
        stack = getattr(self, "_toolbar_stack", None)
        if stack is not None:
            try:
                stack.destroy()
            except Exception:
                pass
        self._toolbar_stack = None
        self._chrome_toolbars = []
        self._native_menu_renderer = None
        self._native_menu_pending = None
        # Clear the native menu bar (macOS) so a rebuild doesn't double it.
        try:
            root = self._menu_root()
            if root is not None:
                root["menu"] = ""
        except Exception:
            pass
        # Replace the content frame wholesale — destroying the subtree fires
        # <Destroy> on every descendant (the normal teardown path) and avoids
        # carrying stale flex bookkeeping into the rebuild.
        old = getattr(self, "_content_frame", None)
        if old is not None:
            try:
                old.destroy()
            except Exception:
                pass
        self._content_frame = FlexFrame(self._region_root, **self._dev_frame_kwargs)
        self._content_frame.pack(fill="both", expand=True)
        try:
            from bootstack.dev import _registry

            _registry.reset_mounts()
        except Exception:
            pass

    def _dev_after_rebuild(self) -> None:
        """Re-apply window chrome that lives outside the body, then flush.

        Grows the window to fit if the rebuilt layout needs more room than the
        current geometry, but never shrinks it — so a reload that adds content
        doesn't clip it, without the jarring shrink when content is removed.
        """
        self._ensure_default_titlebar()
        try:
            root = self._tk_root
            root.update_idletasks()
            cur_w, cur_h = root.winfo_width(), root.winfo_height()
            new_w = max(cur_w, root.winfo_reqwidth())
            new_h = max(cur_h, root.winfo_reqheight())
            if new_w > cur_w or new_h > cur_h:
                root.geometry(f"{new_w}x{new_h}+{root.winfo_x()}+{root.winfo_y()}")
        except Exception:
            pass

    def _dev_capture_route(self) -> Any:
        """Route to restore after a reload. Plain App has none."""
        return None

    def _dev_restore_route(self, route: Any) -> None:
        """Restore a route captured before a reload. No-op for plain App."""
        return None
