"""The `menubar` / `commandbar` facade for top-level windows.

`ChromeHostMixin` gives `App` / `Window` / `AppShell` a lazy `.menubar` property
returning a `WindowMenu`. The facade owns a platform-neutral `MenuModel`,
renders it per platform (themed in-window strip on Windows/Linux; native global
menu bar on macOS), and binds the model's shortcuts to the host window.
Re-renders are coalesced to idle so the natural build pattern
(`with win.menubar.add_menu("File") as file: ...`) renders once, after all items
are added.
"""
from __future__ import annotations

from typing import Any

from bootstack.widgets._impl.composites.menu.model import MenuGroup, MenuModel


class WindowMenu:
    """The menu bar of a top-level window — menus only.

    Build it imperatively with `add_menu()` or declaratively with `load()`;
    both feed the same model. Placement and platform rendering are handled
    internally — the menu strip sits at the top of the window on Windows/Linux
    and relocates to the native global menu bar on macOS.
    """

    def __init__(self, host: Any) -> None:
        self._host = host
        self._model = MenuModel()
        self._renderer: Any = None
        self._pending: Any = None

    # ----- building -----

    def add_menu(self, text: str, *, key: str | None = None) -> MenuGroup:
        """Append a top-level menu and return it (context-manager capable).

        Args:
            text: The menu's label (e.g. `'File'`).
            key: Optional stable identifier; defaults to `text`.
        """
        group = self._model.add_menu(text, key=key)
        group.on_change = self._schedule_rebuild
        self._schedule_rebuild()
        return group

    def load(self, spec: list[dict]) -> None:
        """Replace the menu bar's contents from a declarative spec.

        Args:
            spec: List of group dicts — see `MenuModel.load`.
        """
        self._model.load(spec)
        for group in self._model:
            group.on_change = self._schedule_rebuild
        self._schedule_rebuild()

    def clear(self) -> None:
        """Remove all menus and release their shortcuts."""
        self._model.clear()
        self._schedule_rebuild()

    def refresh(self) -> None:
        """Force an immediate re-render (normally not needed — changes coalesce)."""
        self._rebuild()

    @property
    def model(self) -> MenuModel:
        """The underlying menu model."""
        return self._model

    # ----- rendering -----

    def _menu_root(self) -> Any:
        """The Tk root/toplevel for the native menubar + shortcut binding."""
        return self._host._menu_root()

    def _is_aqua(self) -> bool:
        root = self._menu_root()
        try:
            return root.tk.call("tk", "windowingsystem") == "aqua"
        except Exception:
            return False

    def _schedule_rebuild(self) -> None:
        """Coalesce re-renders onto the idle queue (a single rebuild per turn)."""
        root = self._menu_root()
        if root is None:
            self._rebuild()
            return
        if self._pending is not None:
            try:
                root.after_cancel(self._pending)
            except Exception:
                pass
        try:
            self._pending = root.after_idle(self._rebuild)
        except Exception:
            # No event loop yet (rare) — render synchronously.
            self._rebuild()

    def _rebuild(self) -> None:
        self._pending = None
        if self._is_aqua():
            self._rebuild_native()
        else:
            self._rebuild_themed()
        # Bind the model's pattern shortcuts to this window so keypresses fire.
        root = self._menu_root()
        if root is not None:
            self._model.bind_shortcuts(root)

    def _rebuild_themed(self) -> None:
        from bootstack.widgets._impl.composites.menu.render_themed import ThemedMenuBar

        parent = self._host._menu_strip_parent()
        if parent is None:
            return

        # Empty model — tear down any existing strip and stop.
        if len(self._model) == 0:
            if self._renderer is not None:
                try:
                    self._renderer.destroy()
                except Exception:
                    pass
                self._renderer = None
                # Clear the host's stale strip reference and re-arrange the
                # chrome (otherwise a later command-bar build packs a dead
                # window — the strip the host still points at was destroyed).
                self._host._place_menu_strip(None)
            return

        if self._renderer is None:
            surface = getattr(self._host, "_chrome_surface", "chrome")
            self._renderer = ThemedMenuBar(parent, self._model, surface=surface)
            self._host._place_menu_strip(self._renderer)
        else:
            self._renderer.rebuild()

    def _rebuild_native(self) -> None:
        from bootstack.widgets._impl.composites.menu.render_native import NativeMenuBar

        root = self._menu_root()
        if root is None:
            return

        # Empty model — detach any existing menubar and stop.
        if len(self._model) == 0:
            if self._renderer is not None:
                try:
                    self._renderer.destroy()
                except Exception:
                    pass
                self._renderer = None
            return

        if self._renderer is None:
            self._renderer = NativeMenuBar(root, self._model)
        else:
            self._renderer.rebuild()


class _ChromeContainer:
    """Minimal public-container shim so a public `CommandBar` parents into the
    host's chrome frame. Defers all packing to the host's arranger."""

    _auto_place = True

    def __init__(self, frame: Any, arrange: Any) -> None:
        self._frame = frame
        self._arrange = arrange

    def _child_master(self) -> Any:
        return self._frame

    def guide_layout(self, child: Any, **layout_kw: Any) -> None:
        # Don't pack here — the host arranger positions the toolbar per layout.
        self._arrange()


class ChromeHostMixin:
    """Lazy `.menubar` + `.commandbar`, laid out as top chrome.

    On `App`/`Window` the menu strip and the command bar share one host-owned
    chrome row, arranged per `menu_layout`: `'fused'` (one row — menus left,
    command bar fills right) or `'stacked'` (menu-strip row, command-bar row
    beneath). `AppShell` overrides the placement hooks (its command bar is
    internal and pre-placed), so it does not use the chrome row.
    """

    # ----- menu placement hooks (consumed by WindowMenu) -----

    def _menu_root(self) -> Any:
        """Tk root/toplevel for the native menubar (`['menu']`) + shortcuts."""
        return getattr(self, "_internal", None)

    def _menu_strip_parent(self) -> Any:
        """Widget the themed menu strip is constructed under."""
        return self._ensure_chrome()

    def _place_menu_strip(self, strip: Any) -> None:
        """Register the menu strip and (re)arrange the chrome row."""
        self._menu_strip = strip
        self._arrange_chrome()

    # ----- chrome row -----

    def _ensure_chrome(self) -> Any:
        chrome = getattr(self, "_chrome", None)
        if chrome is not None:
            return chrome
        from bootstack.widgets._impl.primitives.packframe import PackFrame

        from bootstack.widgets._impl.primitives import Separator

        root = self._menu_root()
        surface = getattr(self, "_chrome_surface", "chrome")
        chrome = PackFrame(root, direction="horizontal", surface=surface)
        content = getattr(self, "_content_frame", None)
        pack_kw: dict[str, Any] = {"side": "top", "fill": "x"}
        if content is not None:
            pack_kw["before"] = content
        chrome.pack(**pack_kw)
        self._chrome = chrome

        # Hairline divider between the chrome row and the content below — the
        # native convention (Windows command bars / macOS toolbars), and it
        # guarantees separation in themes where chrome ≈ content surface.
        # Suppressible via chrome_divider=False (e.g. for a fully seamless blend).
        if getattr(self, "_chrome_divider_enabled", True):
            divider = Separator(root, orient="horizontal")
            div_kw: dict[str, Any] = {"side": "top", "fill": "x"}
            if content is not None:
                div_kw["before"] = content
            divider.pack(**div_kw)
            self._chrome_divider = divider

        return chrome

    def _arrange_chrome(self) -> None:
        """(Re)pack the menu strip + toolbar in the chrome row per `menu_layout`."""
        chrome = getattr(self, "_chrome", None)
        if chrome is None:
            return
        strip = getattr(self, "_menu_strip", None)
        commandbar = getattr(self, "_commandbar_widget", None)
        tb_widget = commandbar._internal if commandbar is not None else None
        layout = getattr(self, "_menu_layout", "fused")

        for widget in (strip, tb_widget):
            if widget is not None:
                try:
                    widget.pack_forget()
                except Exception:
                    pass

        if layout == "stacked":
            if strip is not None:
                strip.pack(side="top", fill="x")
            if tb_widget is not None:
                tb_widget.pack(side="top", fill="x")
        else:  # fused: menus left, toolbar fills the rest (its spacer pushes right)
            if strip is not None:
                strip.pack(side="left")
            if tb_widget is not None:
                tb_widget.pack(side="left", fill="x", expand=True)

    @property
    def menubar(self) -> WindowMenu:
        """The window's menu bar (menus only). Lazily created on first access."""
        wm = getattr(self, "_window_menu", None)
        if wm is None:
            wm = WindowMenu(self)
            self._window_menu = wm
        return wm

    @property
    def commandbar(self) -> Any:
        """The window's command bar — a `CommandBar`. Lazily created on first access.

        Lives in the top chrome row (beside or below the menu bar per
        `menu_layout`). Add buttons/labels/separators and an `add_spacer()` to
        push trailing items (e.g. a theme toggle) to the right.
        """
        tb = getattr(self, "_commandbar_widget", None)
        if tb is None:
            from bootstack.widgets.commandbar import CommandBar

            chrome = self._ensure_chrome()
            shim = _ChromeContainer(chrome, self._arrange_chrome)
            # Compact density so the command bar matches the (compact) menu bar
            # height when fused; surface threaded so its ghost buttons paint the
            # chosen chrome surface (rather than their default).
            surface = getattr(self, "_chrome_surface", "chrome")
            tb = CommandBar(parent=shim, density="compact", surface=surface)
            self._commandbar_widget = tb
            self._arrange_chrome()
        return tb