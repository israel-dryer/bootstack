"""Regression test for `on_visibility_alpha` never unbinding itself (#398).

The handler documents that it unbinds "after first use". It stored the funcid
that `bind` returned, then passed that funcid where a *sequence* was expected:

    widget.unbind(widget.alpha_bind)     # sequence=<a funcid>

With no `funcid` argument that means "remove every handler for this sequence",
and the sequence is an unparseable pattern — so it matched nothing, raised
nothing, and the binding survived.

X11-only in practice (alpha must be applied after the window is visible, which
is the X11 path), but the no-op itself is platform-independent and testable
anywhere.
"""
from __future__ import annotations

import tkinter

import pytest


def test_on_visibility_alpha_removes_its_own_binding(app):
    from bootstack._runtime.base_window import on_visibility_alpha

    top = tkinter.Toplevel(app._tk_root)
    try:
        top.alpha = 0.9
        top.alpha_bind = top.bind("<Visibility>", lambda e: None, "+")
        app._tk_root.update_idletasks()
        assert top.bind("<Visibility>").strip(), "precondition: the binding exists"

        on_visibility_alpha(type("E", (), {"widget": top})())

        assert not top.bind("<Visibility>").strip()
        assert top.alpha_bind is None
    finally:
        top.destroy()


def test_alpha_is_applied_before_the_binding_is_released(app):
    """Releasing the binding makes this genuinely one-shot, so ordering matters.

    While the unbind was a no-op the handler stayed bound and got as many
    attempts as there were visibility changes. Now there is exactly one, and it
    has to count: if the alpha request fails, the binding must still be there
    for the next visibility change to try again.
    """
    from bootstack._runtime.base_window import on_visibility_alpha

    top = tkinter.Toplevel(app._tk_root)
    try:
        top.alpha = 0.9
        top.alpha_bind = top.bind("<Visibility>", lambda e: None, "+")
        app._tk_root.update_idletasks()

        def _failing_attributes(*args):
            raise tkinter.TclError("alpha unavailable")

        top.attributes = _failing_attributes

        with pytest.raises(tkinter.TclError):
            on_visibility_alpha(type("E", (), {"widget": top})())

        assert top.alpha_bind is not None, "the retry was thrown away"
        assert top.bind("<Visibility>").strip(), "the binding must survive"
    finally:
        top.destroy()
