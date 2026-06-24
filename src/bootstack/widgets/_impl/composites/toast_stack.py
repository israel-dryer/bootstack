"""Positioning and stacking for the toast family.

The public `toast()` / `Notification` / `Snackbar` facades share one process-wide
manager that owns *where* a transient window lands and how several of them stack:

- **Corner stacks** (toast, notification) float in a corner of the monitor the
  app window currently sits on, newest nearest the corner, older ones offset
  away. The stack re-flows when any member dismisses.
- **Snackbar** anchors to the app window's own bottom edge, aligned left,
  center, or right. Only one snackbar shows at a time; a new one replaces it.

Geometry is computed by hand (no reliance on the engine's default placement) and
applied through the engine's `place=` hook, so positioning happens while the
window is still off-screen — no reposition flash.
"""
from __future__ import annotations

import tkinter
from typing import Literal

from bootstack._runtime.app import get_default_root
from bootstack._runtime.window_utilities import WindowPositioning

Corner = Literal["top-left", "top-right", "bottom-left", "bottom-right"]
Align = Literal["left", "center", "right"]

CORNERS: tuple[Corner, ...] = ("top-left", "top-right", "bottom-left", "bottom-right")

_MARGIN = 24  # px gap from the monitor / window edge
_GAP = 12     # px gap between stacked windows


def _alive(top: tkinter.Toplevel) -> bool:
    """Whether a toast Toplevel still exists."""
    try:
        return bool(top.winfo_exists())
    except tkinter.TclError:
        return False


def _monitor_rect() -> tuple[int, int, int, int]:
    """`(x, y, w, h)` usable work area of the monitor the app window is on.

    On macOS this is the visible frame (menu bar + Dock excluded) so a corner
    toast never lands under the Dock; elsewhere it is the full monitor bounds.
    Falls back to the full screen, then a fixed default.
    """
    root = get_default_root()
    if root is not None:
        try:
            root.update_idletasks()
            cx = root.winfo_rootx() + root.winfo_width() // 2
            cy = root.winfo_rooty() + root.winfo_height() // 2
            rect = WindowPositioning._get_monitor_at_point(cx, cy)
            if rect is None:
                rect = (0, 0, root.winfo_screenwidth(), root.winfo_screenheight())
            return WindowPositioning.get_work_area(root, rect)
        except tkinter.TclError:
            pass
    return (0, 0, 1920, 1080)


class _ToastManager:
    """Process-wide owner of corner stacks and the single active snackbar."""

    def __init__(self) -> None:
        self._corners: dict[Corner, list[tkinter.Toplevel]] = {c: [] for c in CORNERS}
        self._snackbar: tkinter.Toplevel | None = None

    # ----- corner stacks (toast / notification) --------------------------

    def corner_placer(self, corner: Corner):
        """Return a `place(top)` hook that slots `top` into `corner`'s stack."""
        def _place(top: tkinter.Toplevel) -> None:
            self._corners[corner].insert(0, top)  # newest nearest the corner
            self._reflow(corner)
        return _place

    def remove(self, corner: Corner, top: tkinter.Toplevel) -> None:
        """Drop `top` from its stack (on dismiss) and re-flow the rest."""
        stack = self._corners.get(corner)
        if stack is None:
            return
        self._corners[corner] = [t for t in stack if t is not top]
        self._reflow(corner)

    def _reflow(self, corner: Corner) -> None:
        """Re-position every live window in a corner stack, in order."""
        mx, my, mw, mh = _monitor_rect()
        at_top = "top" in corner
        at_right = "right" in corner
        offset = _MARGIN
        live: list[tkinter.Toplevel] = []
        for top in self._corners[corner]:
            if not _alive(top):
                continue
            live.append(top)
            try:
                top.update_idletasks()
                w, h = top.winfo_width(), top.winfo_height()
                x = (mx + mw - w - _MARGIN) if at_right else (mx + _MARGIN)
                y = (my + offset) if at_top else (my + mh - h - offset)
                top.geometry(f"+{int(x)}+{int(y)}")
                offset += h + _GAP
            except tkinter.TclError:
                pass
        self._corners[corner] = live

    # ----- snackbar (single, app-window bottom edge) ---------------------

    def snackbar_placer(self, align: Align):
        """Return a `place(top)` hook that anchors `top` to the window bottom."""
        def _place(top: tkinter.Toplevel) -> None:
            if self._snackbar is not None and _alive(self._snackbar) and self._snackbar is not top:
                try:
                    self._snackbar.destroy()
                except tkinter.TclError:
                    pass
            self._snackbar = top
            self._position_snackbar(top, align)
        return _place

    def clear_snackbar(self, top: tkinter.Toplevel) -> None:
        """Forget the active snackbar if it is `top` (on dismiss)."""
        if self._snackbar is top:
            self._snackbar = None

    def _position_snackbar(self, top: tkinter.Toplevel, align: Align) -> None:
        root = get_default_root()
        if root is None:
            return
        try:
            root.update_idletasks()
            top.update_idletasks()
            rx, ry = root.winfo_rootx(), root.winfo_rooty()
            rw, rh = root.winfo_width(), root.winfo_height()
            w, h = top.winfo_width(), top.winfo_height()
            y = ry + rh - h - _MARGIN
            if align == "left":
                x = rx + _MARGIN
            elif align == "right":
                x = rx + rw - w - _MARGIN
            else:  # center
                x = rx + (rw - w) // 2
            top.geometry(f"+{int(x)}+{int(y)}")
        except tkinter.TclError:
            pass


# One manager for the whole process — toasts are app-global.
_manager = _ToastManager()


def get_toast_manager() -> _ToastManager:
    """Return the process-wide toast manager."""
    return _manager
