"""Themed top-level window for secondary application windows."""
from __future__ import annotations

import tkinter
import warnings
from typing import Any, Callable, Literal, Optional, Tuple

from bootstack._core.mixins.widget import WidgetCapabilitiesMixin
from bootstack._runtime.base_window import BaseWindow


class Toplevel(BaseWindow, WidgetCapabilitiesMixin, tkinter.Toplevel):
    """A themed top-level window.

    This class wraps `tkinter.Toplevel` and adds bootstack window conveniences
    (title/geometry helpers, centering, alpha/topmost/toolwindow helpers, etc.).

    The standard widget API (events, scheduling, clipboard, geometry managers,
    winfo, etc.) is available through inheritance and is documented under
    bootstack capabilities.

    For additional information on the underlying Tk/Tkinter behavior, see:
        - Tcl/Tk `toplevel` command documentation
        - Python `tkinter.Toplevel` documentation

    Examples:
        >>> win = Toplevel(title="My Toplevel")
        >>> win.mainloop()
    """

    def __init__(
            self,
            title: str = "bootstack",
            icon: tkinter.PhotoImage | str | None = None,
            size: Optional[Tuple[int, int]] = None,
            position: Optional[Tuple[int, int]] = None,
            minsize: Optional[Tuple[int, int]] = None,
            maxsize: Optional[Tuple[int, int]] = None,
            resizable: Optional[Tuple[bool, bool]] = None,
            transient: Optional[tkinter.Misc] = None,
            overrideredirect: bool = False,
            windowtype: Optional[str] = None,
            topmost: bool = False,
            toolwindow: bool = False,
            alpha: float = 1.0,
            window_style: Optional[str] = None,
            modal: Literal[False, True, "window", "app"] = False,
            center_on_parent: bool = False,
            center_on_screen: bool = False,
            on_close: Optional[Callable[[], bool | None]] = None,
            **kwargs: Any,
    ) -> None:
        """Initialize a top-level window.

        Args:
            title: The title that appears on the window titlebar.
            icon: A PhotoImage used for the titlebar icon. If None, the default bootstack icon is used.
            size: Window size as (width, height). Applied via `geometry`.
            position: Window position as (x, y). Applied via `geometry`. Overrides `center_on_*`.
            minsize: Minimum permissible window size as (width, height).
            maxsize: Maximum permissible window size as (width, height).
            resizable: Whether the user may resize the window as (x, y).
            transient: Mark this window as transient for the given master.
            overrideredirect: If True, instruct the window manager to ignore this window.
            windowtype: Request a native window type, resolved per platform from a
                single switch. Values: `'splash'`, `'tooltip'`, `'dock'`, `'utility'`.
                On X11 it sets `-type`; on macOS it maps to a `MacWindowStyle`; on
                Windows the chromeless types (`'splash'`/`'tooltip'`/`'dock'`) resolve
                to override-redirect (borderless, no taskbar button) and `'utility'`
                resolves to a tool window. The caller does not also need to pass
                `overrideredirect=True` to get a chromeless window on Windows.
            topmost: If True, keep this window above others (`-topmost`).
            toolwindow: On Windows, request a toolwindow style (`-toolwindow`).
            alpha: On Windows, the window alpha transparency (0.0–1.0) via `-alpha`.
            window_style: Windows-only pywinstyles effect. Options include
                'mica', 'acrylic', 'aero', 'transparent', 'win7', etc.
                Defaults to 'mica'. Set to None to disable.
            modal: Modality level. `False` (default) — non-modal. `True` or
                `"window"` — window-level modal: grabs input from parent only.
                `"app"` — app-level modal: grabs input from all windows.
                When modal is truthy and `transient` is not set, a transient
                parent is inferred from `master` or the current app.
            center_on_parent: If True, center this window over its transient
                parent (or master). Ignored when `position` is given. Falls
                back to `center_on_screen` behavior when no parent is found.
                Mutually exclusive with `center_on_screen`.
            center_on_screen: If True, center this window on the screen.
                Ignored when `position` or `center_on_parent` is given.
            on_close: Callback invoked when the user clicks the close button.
                Return `False` to veto the close; return `None` or `True`
                to allow it. Equivalent to calling `add_close_handler(fn)`
                after construction.
            **kwargs: Other keyword arguments passed to `tkinter.Toplevel`.
        """
        # Extract iconify kwarg if present
        iconify = kwargs.pop("iconify", None)

        # Initialize Toplevel
        tkinter.Toplevel.__init__(self, **kwargs)

        # Setup window system info
        self.winsys: str = self.tk.call("tk", "windowingsystem")

        # result storage for block_until_closed() pattern
        self._result: Any = None

        # modal level — stored for use in show()
        self._modal = modal

        # Apply Aqua MacWindowStyle BEFORE any setup that might pump the
        # event loop (icons, geometry, update_idletasks). Tk's docs require
        # the style to be set on a freshly-created, never-mapped window;
        # after the first event-loop trip the call silently has no effect
        # and the window keeps its default chrome. We withdraw immediately
        # so the window is unmapped, set the style, then continue.
        self.withdraw()
        if windowtype is not None and self.winsys == "aqua":
            aqua_style = {
                "tooltip": ("help", "none"),
                "splash": ("plain", "none"),
                "utility": ("utility", "none"),
                "dock": ("plain", "none"),
            }.get(windowtype)
            if aqua_style is not None:
                try:
                    self.tk.call(
                        "::tk::unsupported::MacWindowStyle", "style",
                        self, aqua_style[0], aqua_style[1],
                    )
                except tkinter.TclError:
                    pass

        # Windows has no native window-type attribute, so translate windowtype
        # to the matching primitive: the chromeless types resolve to
        # override-redirect (borderless + no taskbar/Alt-Tab button), and
        # 'utility' resolves to a tool window (minimal chrome). One switch then
        # yields the right native window on all three platforms. (On Aqua the
        # overrideredirect call is a no-op — MacWindowStyle handled it above.)
        _effective_overrideredirect = overrideredirect
        _effective_toolwindow = toolwindow
        if windowtype is not None and self.winsys == "win32":
            if windowtype in ("splash", "tooltip", "dock"):
                _effective_overrideredirect = True
            elif windowtype == "utility":
                _effective_toolwindow = True

        # Setup icon (use default bootstack icon if no icon provided)
        self._setup_icon(icon, default_icon_enabled=True)

        # Resolve the centering parent.  When center_on_parent=True we need a
        # parent widget; prefer the explicit transient, then self.master.
        _center_parent: Optional[tkinter.Misc] = None
        _effective_center_screen = center_on_screen
        if center_on_parent and position is None:
            _center_parent = transient or (self.master if isinstance(self.master, tkinter.Misc) else None)
            if _center_parent is None:
                warnings.warn(
                    "Toplevel center_on_parent=True but no parent window detected; "
                    "centering on screen instead.",
                    stacklevel=2,
                )
                _effective_center_screen = True

        # Auto-promote transient when modal is truthy and no transient given
        _resolved_transient = transient
        if modal and transient is None:
            parent = self.master if isinstance(self.master, tkinter.Misc) else None
            if parent is None:
                try:
                    from bootstack._runtime.app import get_current_app
                    parent = get_current_app()
                except RuntimeError:
                    pass
            if parent is not None:
                _resolved_transient = parent
            else:
                warnings.warn(
                    "Toplevel modal=True but no parent window could be inferred. "
                    "Modality may not work correctly.",
                    stacklevel=2,
                )

        # Setup window using BaseWindow
        self._setup_window(
            title=title,
            size=size,
            position=position,
            minsize=minsize,
            maxsize=maxsize,
            resizable=resizable,
            transient=_resolved_transient,
            overrideredirect=_effective_overrideredirect,
            alpha=alpha,
            window_style=window_style,
            center_on_parent=_center_parent,
            center_on_screen=_effective_center_screen if _center_parent is None else False,
        )

        # Handle iconify
        if iconify:
            self.iconify()

        # X11 -type attribute. The Aqua case was handled before
        # _setup_window above (style must be set pre-map).
        if windowtype is not None and self.winsys == "x11":
            self.attributes("-type", windowtype)

        if topmost:
            self.attributes("-topmost", 1)

        if _effective_toolwindow and self.winsys == "win32":
            self.attributes("-toolwindow", 1)

        # Register on_close handler
        if on_close is not None:
            self.add_close_handler(on_close)

    # -------------------------------------------------------------------------
    # show() override — applies grab when modal
    # -------------------------------------------------------------------------

    def show(self) -> None:
        """Show the window and apply modal grab if configured."""
        super().show()
        if self._modal:
            try:
                if self._modal == "app":
                    self.grab_set_global()
                else:
                    self.grab_set()
                self.focus_set()
            except tkinter.TclError:
                pass

    # -------------------------------------------------------------------------
    # result property + block_until_closed()
    # -------------------------------------------------------------------------

    @property
    def result(self) -> Any:
        """Value set by the window's content before it closes.

        Defaults to `None`. Set this attribute before calling
        `destroy()` to return a value from `block_until_closed()`.

        See [block_until_closed()][bootstack.Toplevel.block_until_closed].
        """
        return self._result

    @result.setter
    def result(self, value: Any) -> None:
        self._result = value

    def block_until_closed(self) -> Any:
        """Show this window and block until it is destroyed.

        Calls `show()` to make the window visible, then enters a nested
        event loop via `wait_window()` that blocks until the window is
        destroyed. Returns `self.result`.

        Set `self.result` (or `self.result = value`) before calling
        `destroy()` to pass a return value back to the caller.

        Returns:
            The value of `self.result` at the time the window was destroyed.

        Note:
            Do not call this from within an existing `block_until_closed()`
            chain unless you understand the implications of nested event loops.
        """
        self.show()
        try:
            self.wait_window(self)
        except tkinter.TclError:
            pass
        return self._result
