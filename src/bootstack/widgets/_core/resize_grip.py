"""Resize grip for undecorated windows."""

from __future__ import annotations

from tkinter import TclError
from typing import Any


def install_resize_grip(host: Any) -> Any:
    """Pin a resize grip to the bottom-right corner of an undecorated window.

    An undecorated window has no OS border to drag, so the grip is its only
    way to resize by hand. It sits inside the 1px border of `host` (the
    window's bordered region root), takes the surface of whatever is beneath
    the corner (content, a status bar, a dock), is hidden while the window is
    maximized or not resizable, and is kept above its siblings so content
    packed later cannot cover it.

    Args:
        host: The bordered frame that fills the undecorated window.

    Returns:
        The grip widget.
    """
    from bootstack.widgets._impl.primitives.sizegrip import SizeGrip

    grip = SizeGrip(host)
    top = host.winfo_toplevel()
    pending: list[Any] = []

    def corner_surface() -> str | None:
        # Walk this window's own widget tree (never the screen, where another
        # window may cover the corner) to the deepest widget under the point
        # just left of the grip, then take the nearest surface up from it.
        x = host.winfo_width() - 2 - grip.winfo_reqwidth()
        y = host.winfo_height() - 2
        widget = host
        while True:
            hit = None
            for child in widget.winfo_children():
                if child is grip or not child.winfo_manager():
                    continue
                cx, cy = child.winfo_x(), child.winfo_y()
                if cx <= x < cx + child.winfo_width() and cy <= y < cy + child.winfo_height():
                    hit = child  # later siblings stack on top
            if hit is None:
                break
            x, y = x - hit.winfo_x(), y - hit.winfo_y()
            widget = hit
        while widget is not None:
            surface = getattr(widget, "_surface", None)
            if surface:
                return surface
            widget = getattr(widget, "master", None)
        return None

    def sync() -> None:
        pending.clear()
        try:
            resize_x, resize_y = top.resizable()
            if not (resize_x or resize_y) or top.state() == "zoomed":
                grip.place_forget()
                return
            grip.place(in_=host, relx=1.0, rely=1.0, anchor="se")
            grip.lift()
            if host.winfo_width() <= 1:
                return  # not laid out yet; its <Configure> re-syncs
            surface = corner_surface()
            if surface and surface != getattr(grip, "_surface", None):
                grip.configure_style_options(surface=surface)
                grip.rebuild_style()
        except (AttributeError, KeyError, TclError):
            pass  # the window was destroyed before this ran

    def schedule(_event: Any = None) -> None:
        if pending:
            return
        # On the root, never the window: a window destroyed before idle would
        # orphan the job and Tk would report an invalid command.
        try:
            pending.append(host._root().after_idle(sync))
        except (AttributeError, TclError):
            pass

    # Any layout change in the window (a resize, a status bar or dock shown or
    # hidden) can change what sits under the corner.
    top.bind("<Configure>", schedule, add="+")
    sync()
    return grip
