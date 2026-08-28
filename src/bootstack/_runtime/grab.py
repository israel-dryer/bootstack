"""Modal grab capture and restore, shared by the dialog and window paths.

Tk releases a grab when the window holding it is destroyed, but it does NOT
restore the grab that window displaced. Anything that takes a modal grab has to
hand back what it found, or the window underneath is left on screen, still
blocking its caller, holding nothing (#440 for dialogs, #444 for windows).

These live here rather than beside the dialogs because the import direction runs
dialogs -> _runtime: `dialogs/_impl/dialog.py` imports `Toplevel` from this
package, so `_runtime` reaching back the other way would be a cycle.
"""
from __future__ import annotations

import tkinter
from typing import Any

def capture_grab(widget: Any) -> tuple[Any, str | None] | None:
    """Record who holds the modal grab and HOW, for `restore_grab` to hand back.

    Returns `None` when nothing holds the grab — the outermost case, which needs
    no restore. Otherwise returns the holder paired with its grab KIND.

    ⚠ Call this BEFORE taking the grab. Once another window grabs, the previous
    holder's `grab_status()` reads `None`, so a kind read afterwards is always
    wrong — measured, and the reason this pairing exists as one function rather
    than two steps a caller has to sequence correctly.

    The kind matters because Tk has two: `bs.Window(modal="app")` takes a GLOBAL
    grab, and restoring that as a local one silently narrows the window's
    modality (it would block only this application). Reading the kind back from
    Tk rather than assuming it keeps this correct on every window system without
    a platform branch — whatever Tk reported, we hand back.

    A holder this cannot ADDRESS reads the same as no holder at all. Resolving
    who holds the grab goes through a name lookup that raises for a window the
    toolkit created on its own — a posted combobox popdown is one — and there is
    nothing to hand back to a window we cannot name. This runs on the SETUP path,
    where a raise would escape into the application, so it degrades to `None` and
    logs rather than propagating.
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

    Tk releases a grab when the window holding it is destroyed, but it does NOT
    restore the grab that window displaced. So a modal opened from inside
    another modal — `bs.alert()` from a dialog button command, or a
    `bs.Window(modal=True)` opened from a dialog's "Advanced..." button — took
    the grab over and then dropped it on the floor when it closed. The OUTER
    window was left on screen and still blocking its caller, yet holding no
    grab at all: the user could click straight back into the main window and
    drive the app underneath it, against something that was modal in appearance
    only (issue #440 for dialogs, #444 for windows).

    Pass the token `capture_grab()` returned. `None` means nothing held the
    grab, which is the outermost case and needs no restore.

    A failure here is deliberately swallowed. This runs on a teardown path,
    where the previous holder may itself have been destroyed while the inner
    window was up, or the whole interpreter may be going down — and something
    that has already closed must not raise on its way out. It is LOGGED rather
    than passed over in silence, because a failed restore is the very defect
    this function exists to prevent: the outer window stays on screen holding
    nothing.

    ⚠ A global restore can fail where a local one cannot — `grab set -global`
    is the call Tk's viewability rule guards, and on X11 it can also lose to
    another client. That is the one way this is riskier than always restoring
    a local grab, so a failed global restore DEGRADES TO LOCAL rather than to
    nothing: modal within the application is imperfect, but it is not the #440
    symptom.
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
