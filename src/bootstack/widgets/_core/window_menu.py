"""The `menu` facade for top-level windows.

`MenuHostMixin` gives `App` / `Window` / `AppShell` a lazy `.menu` property
returning a `WindowMenu`. The facade owns a platform-neutral `MenuModel`,
renders it per platform (themed in-window strip on Windows/Linux; native global
menu bar on macOS — added in a later step), and binds the model's shortcuts to
the host window. Re-renders are coalesced to idle so the natural build pattern
(`with win.menu.add_menu("File") as file: ...`) renders once, after all items
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

    def _host_root(self) -> Any:
        return getattr(self._host, "_internal", None)

    def _host_content(self) -> Any:
        return getattr(self._host, "_content_frame", None)

    def _is_aqua(self) -> bool:
        root = self._host_root()
        try:
            return root.tk.call("tk", "windowingsystem") == "aqua"
        except Exception:
            return False

    def _schedule_rebuild(self) -> None:
        """Coalesce re-renders onto the idle queue (a single rebuild per turn)."""
        root = self._host_root()
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
        root = self._host_root()
        if root is not None:
            self._model.bind_shortcuts(root)

    def _rebuild_themed(self) -> None:
        from bootstack.widgets._impl.composites.menu.render_themed import ThemedMenuBar

        root = self._host_root()
        if root is None:
            return

        # Empty model — tear down any existing strip and stop.
        if len(self._model) == 0:
            if self._renderer is not None:
                try:
                    self._renderer.destroy()
                except Exception:
                    pass
                self._renderer = None
            return

        if self._renderer is None:
            self._renderer = ThemedMenuBar(root, self._model)
            content = self._host_content()
            pack_kw: dict[str, Any] = {"side": "top", "fill": "x"}
            if content is not None:
                pack_kw["before"] = content
            self._renderer.pack(**pack_kw)
        else:
            self._renderer.rebuild()

    def _rebuild_native(self) -> None:
        from bootstack.widgets._impl.composites.menu.render_native import NativeMenuBar

        root = self._host_root()
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


class MenuHostMixin:
    """Adds a lazy `.menu` property returning a `WindowMenu`.

    Mixed into the top-level window classes (`App`, `Window`, `AppShell`). The
    host must expose `_internal` (its Tk toplevel) and, for the themed strip,
    `_content_frame` (the strip packs above it).
    """

    @property
    def menu(self) -> WindowMenu:
        """The window's menu bar (menus only). Lazily created on first access."""
        wm = getattr(self, "_window_menu", None)
        if wm is None:
            wm = WindowMenu(self)
            self._window_menu = wm
        return wm