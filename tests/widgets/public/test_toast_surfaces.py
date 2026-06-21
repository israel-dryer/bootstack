"""The three transient message surfaces: toast / Notification / Snackbar.

Covers the public surface, corner stacking + reflow, the persistent
notification handle, the single-replace snackbar, the neutral snackbar
surface, the positional Notification title, and icon opt-in.
"""
import pytest

import bootstack as bs
from tkinter import ttk

from bootstack.widgets._impl.composites.toast import Toast as _InternalToast
from bootstack.widgets._impl.composites.toast_stack import get_toast_manager


@pytest.fixture(autouse=True)
def _clear(app):
    """Reset the process-wide toast manager around each test."""
    mgr = get_toast_manager()

    def reset():
        for corner in list(mgr._corners):
            for top in list(mgr._corners[corner]):
                try:
                    top.destroy()
                except Exception:
                    pass
            mgr._corners[corner] = []
        if mgr._snackbar is not None:
            try:
                mgr._snackbar.destroy()
            except Exception:
                pass
            mgr._snackbar = None
        app._tk_root.update()

    reset()
    yield
    reset()


pytestmark = pytest.mark.gui


# ----- public surface ----------------------------------------------------

def test_public_surface(app):
    assert not hasattr(bs, "Toast")          # the kitchen-sink class is gone
    assert callable(bs.toast)
    assert callable(bs.snackbar)
    assert hasattr(bs, "Notification")
    assert hasattr(bs, "Snackbar")


def test_type_aliases_exported():
    from bootstack.types import ToastCorner, SnackbarAlign  # noqa: F401


# ----- corner stacking ---------------------------------------------------

def test_toast_stacks_in_corner(app):
    mgr = get_toast_manager()
    for i in range(3):
        bs.toast(f"Message {i}", corner="bottom-right", duration=99999)
    app._tk_root.update()
    stack = mgr._corners["bottom-right"]
    assert len(stack) == 3
    # newest nearest the corner: for a bottom corner, larger y is nearer the edge
    ys = [t.winfo_y() for t in stack]
    assert ys[0] > ys[1] > ys[2]


def test_stack_reflows_on_dismiss(app):
    mgr = get_toast_manager()
    for i in range(3):
        bs.toast(f"Message {i}", corner="top-right", duration=99999)
    app._tk_root.update()
    middle = mgr._corners["top-right"][1]
    mgr.remove("top-right", middle)
    try:
        middle.destroy()
    except Exception:
        pass
    app._tk_root.update()
    assert len(mgr._corners["top-right"]) == 2


# ----- notification ------------------------------------------------------

def test_notification_persists_and_dismisses(app):
    mgr = get_toast_manager()
    note = bs.Notification("Done", message="Finished.", corner="top-right").show()
    app._tk_root.update()
    assert len(mgr._corners["top-right"]) == 1
    note.dismiss()
    app._tk_root.update()
    assert len(mgr._corners["top-right"]) == 0


def test_notification_positional_title(app):
    note = bs.Notification("Update available", message="v2.1 ready").show()
    app._tk_root.update()
    assert note._engine._title == "Update available"


# ----- snackbar ----------------------------------------------------------

def test_snackbar_replaces_single(app):
    mgr = get_toast_manager()
    bs.Snackbar("First", action="Undo").show()
    app._tk_root.update()
    first = mgr._snackbar
    assert first is not None
    bs.Snackbar("Second").show()
    app._tk_root.update()
    assert mgr._snackbar is not None and mgr._snackbar is not first
    assert not first.winfo_exists()


def test_snackbar_surface_is_neutral(app):
    """accent tints only the action — the snackbar surface stays neutral."""
    style = ttk.Style()

    def surface_bg(top):
        cont = top.winfo_children()[0]
        return style.lookup(cont.cget("style"), "background")

    plain = bs.Snackbar("No accent").show()
    plain_bg = surface_bg(plain._engine._toplevel)
    plain.dismiss()
    app._tk_root.update()

    accented = bs.Snackbar("Danger accent", action="Retry", accent="danger").show()
    accented_bg = surface_bg(accented._engine._toplevel)
    assert accented_bg == plain_bg  # accent did not tint the surface


# ----- icon opt-in -------------------------------------------------------

def test_icon_is_opt_in(app):
    def header_labels(top):
        hdr = [c for c in top.winfo_children()[0].winfo_children()
               if c.winfo_class() == "TFrame"][0]
        return [c for c in hdr.winfo_children() if c.winfo_class() == "TLabel"]

    plain = _InternalToast(message="Hello", show_close_button=False, duration=99999)
    plain.show()
    app._tk_root.update()
    iconed = _InternalToast(message="Hello", icon="check-circle",
                            show_close_button=False, duration=99999)
    iconed.show()
    app._tk_root.update()
    assert len(header_labels(plain._toplevel)) == 1    # message only, no icon
    assert len(header_labels(iconed._toplevel)) == 2   # icon + message
    plain.destroy()
    iconed.destroy()
