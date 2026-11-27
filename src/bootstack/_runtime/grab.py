"""Modal grab capture and restore, shared by the dialog and window paths.

Tk releases a grab when the window holding it is destroyed, but does not
restore the grab that window displaced. Anything that takes a modal grab has to
hand back what it found, or the window underneath stays on screen, blocking its
caller and holding nothing.

These live here rather than beside the dialogs because the import direction runs
dialogs -> _runtime: `dialogs/_impl/dialog.py` imports `Toplevel` from this
package, so `_runtime` reaching back the other way would be a cycle.
"""
from __future__ import annotations

import tkinter
from typing import Any

def capture_grab(widget: Any) -> tuple[Any, str | None] | None:
    """Record who holds the modal grab and how, for `restore_grab` to hand back.

    Returns `None` when nothing holds the grab — the outermost case, which needs
    no restore. Otherwise returns the holder paired with its grab kind.

    Call this before taking the grab: once another window grabs, the previous
    holder's `grab_status()` reads `None`, so a kind read afterwards is wrong.

    The kind matters because Tk has two: `bs.Window(modal="app")` takes a global
    grab, and restoring it as a local one narrows the window's modality. The
    kind is read back from Tk rather than assumed, so no platform branch is
    needed.

    A holder this cannot address reads as no holder at all. The lookup raises
    for a window the toolkit created on its own (a posted combobox popdown), and
    this runs on the setup path, so it degrades to `None` and logs.
    """
    try:
        holder = widget.grab_current()
    except (AttributeError, KeyError, tkinter.TclError):
        _log_grab_failure("could not identify the current grab holder")
        return None
    if holder is None:
        return None
    try:
        kind = holder.grab_status()
    except (AttributeError, tkinter.TclError):
        # Fall back to the narrower grab rather than guessing global.
        kind = "local"
    return (holder, kind)


def restore_grab(previous: tuple[Any, str | None] | None) -> None:
    """Hand the modal grab back to whatever held it before the caller took it.

    A modal opened from inside another modal — `bs.alert()` from a dialog
    button, or a modal `bs.Window` opened from a dialog — would otherwise leave
    the outer window on screen, blocking its caller but holding no grab.

    Pass the token `capture_grab()` returned. `None` means nothing held the
    grab, which is the outermost case and needs no restore.

    Failures are swallowed but logged: this runs on a teardown path, where the
    previous holder may already be destroyed or the interpreter going down.

    A global restore can fail where a local one cannot (Tk's viewability rule,
    or losing to another X11 client), so a failed global restore degrades to
    local rather than to nothing.
    """
    if previous is None:
        return
    holder, kind = previous
    try:
        if not holder.winfo_exists():
            return
        if kind == "global":
            try:
                holder.grab_set_global()
            except tkinter.TclError:
                _log_grab_failure("could not restore a global grab; falling back to local")
                holder.grab_set()
        else:
            holder.grab_set()
    except (AttributeError, tkinter.TclError):
        _log_grab_failure("could not restore the previous grab holder")


def _log_grab_failure(message: str) -> None:
    """Report a grab failure without ever raising from a teardown path."""
    from bootstack._runtime.utility import debug_log_exception

    debug_log_exception(message)
