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


# ----- container children added after attach (#260) -----

def _covers(target, child) -> bool:
    """True if `child` carries the target's bindtag (the tip reaches it)."""
    return str(target.tk) in child.tk.bindtags()


def test_child_present_at_attach_is_covered(app):
    col = bs.Column(parent=app)
    early = bs.Label("early", parent=col)
    bs.Tooltip(col, "tip")
    assert _covers(col, early)


def test_child_added_after_attach_needs_refresh(app):
    col = bs.Column(parent=app)
    bs.Label("early", parent=col)
    tip = bs.Tooltip(col, "tip")
    late = bs.Label("late", parent=col)  # added after the tooltip was created
    assert not _covers(col, late)  # not auto-covered (the #260 gap)
    tip.refresh_bindings()
    assert _covers(col, late)  # refresh extends coverage to it


def test_refresh_bindings_is_idempotent(app):
    col = bs.Column(parent=app)
    early = bs.Label("early", parent=col)
    tip = bs.Tooltip(col, "tip")
    before = list(early.tk.bindtags())
    tip.refresh_bindings()
    assert list(early.tk.bindtags()) == before  # no duplicate tag


def test_refresh_bindings_safe_after_target_destroyed(app):
    btn = bs.Button("x")
    tip = bs.Tooltip(btn, "tip")
    btn.destroy()
    app._tk_root.update_idletasks()
    tip.refresh_bindings()  # must not raise


# ----- normal lifecycle -----

def test_construct_and_destroy(app):
    tip = bs.Tooltip(bs.Button("ok"), "help")
    tip.destroy()  # clean, no error
