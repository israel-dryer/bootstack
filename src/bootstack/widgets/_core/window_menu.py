"""The stacked-toolbar chrome host for top-level windows.

`ChromeHostMixin` gives `App` / `Window` / `AppShell` an `add_toolbar()` factory:
the window's top region is a vertical stack of `Toolbar`s, each holding buttons,
labels, widgets, and menus (`toolbar.add_menu(...)`). A menu is just a toolbar
item — it renders as an in-window dropdown on Windows/Linux and bridges to the
native global menu bar on macOS (aggregated across every bridged chrome toolbar).
"""
from __future__ import annotations

from typing import Any


class _ToolbarStackContainer:
    """Public-container shim so an `add_toolbar()` toolbar packs into the host's
    vertical chrome stack (full-width, top-to-bottom in creation order)."""

    _auto_place = True

    def __init__(self, frame: Any) -> None:
        self._frame = frame

    def _child_master(self) -> Any:
        return self._frame

    def guide_layout(self, child: Any, **layout_kw: Any) -> None:
        # Toolbars stack full-width in creation order; the stack owns the layout.
        child._internal.pack(side="top", fill="x")


class ChromeHostMixin:
    """`add_toolbar()` — the window's top region is a stack of toolbars.

    Each `add_toolbar()` appends a full-width `Toolbar` band; menus live on the
    toolbars (`toolbar.add_menu(...)`). On macOS the bridged toolbars' menus are
    aggregated into the native global menu bar; on Windows/Linux they render as
    in-window dropdowns. `AppShell` overrides `_ensure_toolbar_stack()` to mount
    the stack into its own region layout.
    """

    def _menu_root(self) -> Any:
        """Tk root/toplevel for the native menubar (`['menu']`) + shortcuts."""
        return getattr(self, "_internal", None)

    # ----- toolbar stack -----

    def add_toolbar(
        self, *, divider: bool = False, use_macos_menus: bool = True, **toolbar_kwargs: Any
    ) -> Any:
        """Append a `Toolbar` to the window's top chrome stack and return it.

        Toolbars stack full-width, top-to-bottom, in the order added — fill each
        with buttons, labels, widgets, and menus (`toolbar.add_menu(...)`). The
        returned `Toolbar` is a context manager, so the natural form reads::

            with window.add_toolbar() as tb:
                tb.add_menu("File")
                tb.add_spacer()
                tb.add_theme_toggle()

        Args:
            divider: Draw a hairline beneath this toolbar (default `False`).
            use_macos_menus: On macOS, bridge this toolbar's menus to the native
                global menu bar (in-window dropdowns hide). Default `True`; set
                `False` to keep its menus in-window even on macOS. No effect on
                Windows/Linux.
            **toolbar_kwargs: Forwarded to `Toolbar` — e.g. `surface`, `density`,
                `button_variant`, `show_window_controls`, `draggable`. Defaults
                `surface='chrome'` (this is window chrome); a
                `show_window_controls=True` toolbar (a title bar) also defaults to
                `density='compact'`.

        Returns:
            The `Toolbar` for this layer.
        """
        from bootstack.widgets._impl.primitives import Separator
        from bootstack.widgets.toolbar import Toolbar

        stack = self._ensure_toolbar_stack()
        toolbar_kwargs.setdefault("surface", "chrome")
        # A window-controls toolbar is a title bar — default it to a thin compact
        # strip (overridable) so it reads tight rather than a tall command bar.
        if toolbar_kwargs.get("show_window_controls"):
            toolbar_kwargs.setdefault("density", "compact")
        tb = Toolbar(parent=_ToolbarStackContainer(stack), **toolbar_kwargs)
        if divider:
            # A bare full-width hairline — no margin. The bar above provides any
            # spacing through its own (chrome) padding, so nothing of the stack
            # surface leaks below the line when this is the last band before the
            # content (the window's content surface starts right after the line).
            Separator(
                stack, orient="horizontal", surface=toolbar_kwargs["surface"]
            ).pack(side="top", fill="x")
        self._register_chrome_toolbar(tb, use_macos_menus)
        return tb

    def _ensure_toolbar_stack(self) -> Any:
        stack = getattr(self, "_toolbar_stack", None)
        if stack is not None:
            return stack
        from bootstack.widgets._impl.primitives.packframe import PackFrame

        # The stack carries the chrome surface so any gap between stacked bars
        # (e.g. a divider's margin) reads as chrome rather than the window's
        # content surface. Chrome-surfaced toolbars sit seamlessly on it.
        stack = PackFrame(self._toolbar_stack_parent(), direction="vertical", surface="chrome")
        self._mount_toolbar_stack(stack)
        self._toolbar_stack = stack
        return stack

    def _toolbar_stack_parent(self) -> Any:
        """Widget the chrome stack is built under (overridable by the host)."""
        return self._menu_root()

    def _mount_toolbar_stack(self, stack: Any) -> None:
        """Pack the chrome stack at the top of the window, above the content."""
        content = getattr(self, "_content_frame", None)
        pack_kw: dict[str, Any] = {"side": "top", "fill": "x"}
        if content is not None:
            pack_kw["before"] = content
        stack.pack(**pack_kw)

    # ----- macOS native menu bridge -----

    def _register_chrome_toolbar(self, tb: Any, use_macos_menus: bool) -> None:
        """Track a chrome toolbar and, on macOS, wire its menus into the native
        global menu bar (aggregated across all bridged toolbars)."""
        toolbars = getattr(self, "_chrome_toolbars", None)
        if toolbars is None:
            toolbars = self._chrome_toolbars = []
        toolbars.append((tb, use_macos_menus))
        if use_macos_menus and self._menus_are_native():
            tb._internal._on_menu_change = self._schedule_native_menu_rebuild
            self._schedule_native_menu_rebuild()

    def _menus_are_native(self) -> bool:
        """Whether menus render in the native global bar (macOS / aqua)."""
        root = self._menu_root()
        try:
            return root.tk.call("tk", "windowingsystem") == "aqua"
        except Exception:
            return False

    def _aggregate_native_menu_model(self) -> Any:
        """Build one `MenuModel` from every bridged chrome toolbar's menus, in
        stack order then left-to-right within each toolbar. Also hides the
        in-window triggers for bridged toolbars (the native bar shows them)."""
        from bootstack.widgets._impl.composites.menu.model import MenuModel

        agg = MenuModel()
        for tb, bridge in getattr(self, "_chrome_toolbars", []):
            if not bridge:
                continue
            model = tb._internal.menu_model
            if model is None:
                continue
            agg.groups.extend(model.groups)
            for trigger in tb._internal._menu_triggers.values():
                try:
                    trigger.pack_forget()
                except Exception:
                    pass
        return agg

    def _schedule_native_menu_rebuild(self) -> None:
        root = self._menu_root()
        pending = getattr(self, "_native_menu_pending", None)
        if root is None:
            self._rebuild_native_menu()
            return
        if pending is not None:
            try:
                root.after_cancel(pending)
            except Exception:
                pass
        try:
            self._native_menu_pending = root.after_idle(self._rebuild_native_menu)
        except Exception:
            self._rebuild_native_menu()

    def _rebuild_native_menu(self) -> None:
        from bootstack.widgets._impl.composites.menu.render_native import NativeMenuBar

        self._native_menu_pending = None
        model = self._aggregate_native_menu_model()
        renderer = getattr(self, "_native_menu_renderer", None)
        if renderer is None:
            self._native_menu_renderer = NativeMenuBar(self._menu_root(), model)
        else:
            renderer.set_model(model)
