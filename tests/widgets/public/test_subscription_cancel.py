"""Regression tests for `Subscription.cancel()` (#392).

Cancelling one subscription used to silence *every other handler* on the same
event, with no Python-level error to show for it.

The runtime patches `bind` so virtual events can carry a data payload, and it
wrote its own Tcl binding script in a bare `<funcid> %d %# ...` shape. Tkinter's
`unbind(sequence, funcid)` removes a single handler by matching the line prefix
`if {"[<funcid> ` that its own `bind` emits — so nothing matched, the binding
survived, and yet the Tcl command behind it was still deleted. The orphan then
errored on every dispatch; because bootstack binds with `add='+'` all handlers
for an event live in ONE concatenated script, so that error aborted every
handler registered after the cancelled one.

Only virtual events (`<<...>>` — every bootstack event) took the custom path;
real events like `<Configure>` go through stock `bind` and were never affected.

Emitting stock Tkinter's script shape fixes cancellation.

Matching the script shape is only half of it. Stock `unbind` also deletes the Tcl
command behind a handler the moment it is asked to, and the copy of the script Tk
is currently running is not the one the removal rewrites — so cancelling *from
inside a handler for the same event* hit the deleted command further down and
aborted the remainder of that dispatch, just as silently. `unbind` is patched to
neutralize the command in place and delete it once the dispatch has finished.
"""
from __future__ import annotations

import bootstack as bs


def _fire(app, widget) -> None:
    widget.emit("click")
    app._tk_root.update()


# --- The reported bug: cancelling one handler killed the others ---------

def test_cancelling_one_subscription_leaves_the_others_working(app):
    # Reported repro: two `on_click` subscriptions, cancel the first, and
    # neither fired afterward.
    button = bs.Button("go")
    calls = {"a": 0, "b": 0}
    sub_a = button.on_click(lambda e: calls.__setitem__("a", calls["a"] + 1))
    button.on_click(lambda e: calls.__setitem__("b", calls["b"] + 1))
    app._tk_root.update_idletasks()

    _fire(app, button)
    assert calls == {"a": 1, "b": 1}, "precondition: both handlers are live"

    sub_a.cancel()
    calls.update(a=0, b=0)
    _fire(app, button)

    assert calls == {"a": 0, "b": 1}


def test_cancelling_a_middle_subscription_spares_both_neighbors(app):
    # The abort took out everything *after* the cancelled handler, so a
    # two-handler test can't tell "later handlers die" from "all die".
    button = bs.Button("go")
    calls = {"a": 0, "b": 0, "c": 0}
    button.on_click(lambda e: calls.__setitem__("a", calls["a"] + 1))
    sub_b = button.on_click(lambda e: calls.__setitem__("b", calls["b"] + 1))
    button.on_click(lambda e: calls.__setitem__("c", calls["c"] + 1))
    app._tk_root.update_idletasks()

    _fire(app, button)
    assert calls == {"a": 1, "b": 1, "c": 1}, "precondition: all three are live"

    sub_b.cancel()
    calls.update(a=0, b=0, c=0)
    _fire(app, button)

    assert calls == {"a": 1, "b": 0, "c": 1}


def test_cancelling_every_subscription_leaves_nothing_bound(app):
    button = bs.Button("go")
    calls = {"a": 0, "b": 0}
    sub_a = button.on_click(lambda e: calls.__setitem__("a", calls["a"] + 1))
    sub_b = button.on_click(lambda e: calls.__setitem__("b", calls["b"] + 1))
    app._tk_root.update_idletasks()

    _fire(app, button)
    assert calls == {"a": 1, "b": 1}, "precondition: both handlers are live"

    sub_a.cancel()
    sub_b.cancel()
    calls.update(a=0, b=0)
    _fire(app, button)

    assert calls == {"a": 0, "b": 0}


def test_cancel_is_idempotent(app):
    button = bs.Button("go")
    calls = {"a": 0, "b": 0}
    sub_a = button.on_click(lambda e: calls.__setitem__("a", calls["a"] + 1))
    button.on_click(lambda e: calls.__setitem__("b", calls["b"] + 1))
    app._tk_root.update_idletasks()

    sub_a.cancel()
    sub_a.cancel()

    _fire(app, button)
    assert calls == {"a": 0, "b": 1}


# --- The data payload must survive the new script shape ----------------

def test_a_surviving_handler_still_receives_its_payload(shown_app):
    # The whole reason for the custom script was the %d data token; a
    # cancellation fix that dropped the payload would be no fix at all.
    #
    # `shown_app`, not `app`: a generated event isn't delivered to this
    # composite while its window is unmapped, and the `app` fixture's root is
    # withdrawn. (Pre-existing and unrelated — it measures the same either
    # side of this fix.)
    slider = bs.Slider(value=5, min_value=0, max_value=10)
    seen: list = []
    sub_first = slider.on_change(lambda e: None)
    slider.on_change(lambda e: seen.append(e.value))
    shown_app._tk_root.update()

    slider.emit("change", data=bs.events.SliderEvent(value=7.0))
    shown_app._tk_root.update()
    assert seen == [7.0], "precondition: the payload arrives while both are live"

    sub_first.cancel()
    seen.clear()
    slider.emit("change", data=bs.events.SliderEvent(value=9.0))
    shown_app._tk_root.update()

    assert seen == [9.0]


# --- Cancelling from inside a handler for the same event ----------------
#
# All handlers for an event share one script, and the copy Tk is running is not
# the one a cancellation rewrites. Removing a handler mid-dispatch therefore has
# to leave something callable behind where it used to be, or the rest of that
# dispatch is skipped with nothing raised to show for it.

def test_cancelling_a_later_handler_from_inside_one_spares_the_rest(app):
    button = bs.Button("go")
    calls = {"a": 0, "b": 0, "c": 0}

    def cancel_b(event):
        calls["a"] += 1
        sub_b.cancel()

    button.on_click(cancel_b)
    sub_b = button.on_click(lambda e: calls.__setitem__("b", calls["b"] + 1))
    button.on_click(lambda e: calls.__setitem__("c", calls["c"] + 1))
    app._tk_root.update_idletasks()

    _fire(app, button)

    # `b` is cancelled before it is reached, so it must not run; `c` is behind
    # it in the same script and must still run.
    assert calls == {"a": 1, "b": 0, "c": 1}


def test_cancelling_the_last_handler_from_inside_one_spares_the_middle(app):
    # Guards the mirror error: a fix that let the whole dispatch continue by
    # skipping the *rest* of the script would pass the test above.
    #
    # PASSES PRE-FIX ON PURPOSE — with nothing bound after the cancelled
    # handler there was nothing left for the aborted dispatch to swallow. Not a
    # dud; it fails if a fix ever over-reaches in the other direction.
    button = bs.Button("go")
    calls = {"a": 0, "b": 0, "c": 0}

    def cancel_c(event):
        calls["a"] += 1
        sub_c.cancel()

    button.on_click(cancel_c)
    button.on_click(lambda e: calls.__setitem__("b", calls["b"] + 1))
    sub_c = button.on_click(lambda e: calls.__setitem__("c", calls["c"] + 1))
    app._tk_root.update_idletasks()

    _fire(app, button)

    assert calls == {"a": 1, "b": 1, "c": 0}


def test_a_handler_can_cancel_its_own_subscription(app):
    # The unsubscribe-on-first-result shape. The handler is mid-flight when its
    # own binding goes away, so this is the case most likely to misbehave.
    #
    # PASSES PRE-FIX ON PURPOSE — a handler's own line has already been
    # evaluated by the time it runs, so this case was never broken. It is here
    # to catch a cancellation fix that breaks it.
    button = bs.Button("go")
    calls = {"a": 0, "b": 0}

    def once(event):
        calls["a"] += 1
        sub_a.cancel()

    sub_a = button.on_click(once)
    button.on_click(lambda e: calls.__setitem__("b", calls["b"] + 1))
    app._tk_root.update_idletasks()

    _fire(app, button)
    assert calls == {"a": 1, "b": 1}, "the handler behind it still runs"

    calls.update(a=0, b=0)
    _fire(app, button)
    assert calls == {"a": 0, "b": 1}, "and it really is unsubscribed"


def test_cancelling_mid_dispatch_does_not_leak_the_binding(app):
    # The deferred cleanup must actually happen, not just be postponed forever.
    #
    # PASSES PRE-FIX ON PURPOSE — the old code deleted the command immediately
    # (which is exactly what caused the abort). This guards the cost of deferring
    # it: postponed must not mean skipped.
    button = bs.Button("go")
    calls = {"a": 0}

    def cancel_self(event):
        calls["a"] += 1
        sub_a.cancel()

    sub_a = button.on_click(cancel_self)
    app._tk_root.update_idletasks()

    _fire(app, button)
    app._tk_root.update_idletasks()
    app._tk_root.update()

    bind_id = sub_a._bind_id
    registered = app._tk_root.tk.call("info", "commands", bind_id)
    assert not registered, f"{bind_id} outlived the dispatch that cancelled it"


def test_unbinding_a_foreign_funcid_leaves_the_real_binding_alone(app):
    # A funcid unbound from the wrong widget used to delete the command behind
    # the still-live binding, orphaning it. Removing nothing must delete nothing.
    button = bs.Button("go")
    other = bs.Button("other")
    calls = {"a": 0}
    sub_a = button.on_click(lambda e: calls.__setitem__("a", calls["a"] + 1))
    app._tk_root.update_idletasks()

    other._internal.unbind(sub_a._sequence, sub_a._bind_id)
    app._tk_root.update_idletasks()
    app._tk_root.update()

    _fire(app, button)
    assert calls == {"a": 1}


def test_cancelling_then_destroying_the_widget_is_quiet(app):
    # Cleaning up the removed handler is deferred to the next idle point, so it
    # must be owned by something that outlives the widget being cleaned up.
    # Cancel-then-destroy is an ordinary teardown order, and getting this wrong
    # leaves a pending callback pointing at an already-swept command.
    #
    # The failure is invisible to Python — it surfaces only as a background
    # error inside the interpreter — so this reads that channel directly. There
    # is no public surface that reports it.
    root = app._tk_root
    seen: list = []
    root.tk.createcommand("bgerror", lambda *a: seen.append(a[0] if a else ""))
    try:
        button = bs.Button("go")
        sub = button.on_click(lambda e: None)
        root.update_idletasks()

        sub.cancel()
        button.destroy()
        root.update_idletasks()
        root.update()

        assert seen == []
    finally:
        root.deletecommand("bgerror")
