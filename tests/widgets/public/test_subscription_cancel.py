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
