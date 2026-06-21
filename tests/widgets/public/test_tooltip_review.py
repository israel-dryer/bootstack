"""Tooltip review fixes (feat/tooltip-review).

Three issues closed:

1. `destroy()` crashed when the target widget had already been destroyed — it
   unbound handlers off a dead widget path (`TclError: bad window path name`).
   Now guarded, and a `<Destroy>` binding releases the timer/popup proactively
   when the target dies.
2. The enter/leave/motion/press handlers were bound without `add="+"` and
   unbound by sequence, which could replace or clobber the target's own
   handlers. Now bound with `add="+"` and removed by their captured bind id.
3. No live `text` — a tooltip's text was fixed at construction. Added a `text`
   get/set property (a visible popup updates immediately).
"""
import tkinter

import pytest

import bootstack as bs


@pytest.fixture(scope="module")
def app():
    a = bs.App()
    a.__enter__()
    a._tk_root.deiconify()
    a._tk_root.update_idletasks()
    try:
        yield a
    finally:
        try:
            a.__exit__(None, None, None)
        except Exception:
            pass
        try:
            a._tk_root.destroy()
        except Exception:
            pass


# ----- destroy is safe when the target is already gone -----

def test_destroy_after_target_destroyed_does_not_crash(app):
    btn = bs.Button("x")
    tip = bs.Tooltip(btn, "hi", delay=5000)
    tip._internal._schedule()  # a timer is pending
    btn.destroy()
    app._tk_root.update_idletasks()
    tip.destroy()  # must not raise TclError


def test_target_destroy_cancels_pending_timer(app):
    btn = bs.Button("y")
    tip = bs.Tooltip(btn, "hi", delay=5000)
    tip._internal._schedule()
    assert tip._internal._id is not None
    btn.destroy()
    app._tk_root.update_idletasks()
    assert tip._internal._id is None  # released by the <Destroy> handler


def test_destroy_target_handler_ignores_descendant_destroy(app):
    # The target's bindtag rides on descendants, so a child <Destroy> reaches
    # the handler; it must only act when the target itself is destroyed.
    with bs.Column() as col:
        child = bs.Label("c")
    tip = bs.Tooltip(col, "container tip", delay=5000)
    tip._internal._schedule()
    child.destroy()
    app._tk_root.update_idletasks()
    assert tip._internal._id is not None  # a child dying must not cancel the timer


# ----- live text -----

def test_text_get_set(app):
    tip = bs.Tooltip(bs.Button("z"), "old")
    assert tip.text == "old"
    tip.text = "new"
    assert tip.text == "new"
    assert tip._internal._text == "new"


# ----- bindings do not clobber the target's own handlers -----

def test_user_enter_handler_survives_tooltip_destroy(app):
    btn = bs.Button("q")
    fired = []
    btn.tk.bind("<Enter>", lambda e: fired.append(1), add="+")
    tip = bs.Tooltip(btn, "tip")
    tip.destroy()
    app._tk_root.update_idletasks()
    btn.tk.event_generate("<Enter>", when="now")
    app._tk_root.update_idletasks()
    assert fired == [1]  # the tooltip removed only its own binding


# ----- normal lifecycle -----

def test_construct_and_destroy(app):
    tip = bs.Tooltip(bs.Button("ok"), "help")
    tip.destroy()  # clean, no error
