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

Emitting stock Tkinter's script shape fixes cancellation. It also makes handler
return values significant, which is NOT wanted on the public surface — see
`test_a_handler_return_value_cannot_suppress_the_others`.

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


# --- Subscribing again in the same turn as a cancellation ---------------
#
# Deferring the cleanup means a handler's name outlives the handler itself for a
# moment. Tkinter builds that name from the address of a bound method created for
# that registration alone, and cancelling releases the last reference to it — so
# the next registration is handed the very same address, and with it the same
# name. The pending deletion would then remove a binding made after it, silently.
# `_unique_name` is what keeps the two apart.


def test_a_cancelled_handlers_name_is_never_reused(app):
    # The deterministic guard for the three tests below. Whether a reused name
    # actually swallows a handler depends on when the allocator hands the same
    # address back, which varies with whatever else the process is doing — so
    # the behavioral tests can pass on a broken build by luck. This one cannot:
    # it asserts the invariant that makes the failure impossible in the first
    # place. Measured on the stock naming scheme, 498 of 499 consecutive cycles
    # reused the name.
    button = bs.Button("go")
    names = []
    for _ in range(50):
        sub = button.on_click(lambda e: None)
        names.append(sub._bind_id)
        sub.cancel()
    app._tk_root.update_idletasks()

    assert len(set(names)) == len(names), "a handler name was reused after cancel"


def test_subscribing_again_right_after_a_cancel_keeps_the_new_handlers(app):
    # Swapping a handler — cancel, then register the replacement — is the whole
    # point of holding a subscription, and it happens well inside one turn of
    # the event loop. There must be no idle point between the two here: that gap
    # is exactly what this is guarding against needing.
    #
    # This is the user-visible contract, but it is a best-effort detector: it
    # only fails on a broken build when the allocator happens to hand back the
    # cancelled handler's address. `test_a_cancelled_handlers_name_is_never_reused`
    # is the guard that always fails.
    root = app._tk_root
    button = bs.Button("go")
    calls = {"a": 0, "b": 0, "c": 0}

    sub_a = button.on_click(lambda e: calls.__setitem__("a", calls["a"] + 1))
    root.update_idletasks()
    _fire(app, button)
    assert calls == {"a": 1, "b": 0, "c": 0}, "precondition: the first handler is live"

    calls.update(a=0)
    sub_a.cancel()
    button.on_click(lambda e: calls.__setitem__("b", calls["b"] + 1))
    button.on_click(lambda e: calls.__setitem__("c", calls["c"] + 1))
    root.update_idletasks()  # the deferred cleanup lands here

    _fire(app, button)

    assert calls == {"a": 0, "b": 1, "c": 1}


def test_subscribing_again_right_after_a_cancel_is_quiet(app):
    # The companion failure has no return value to inspect: reusing a name the
    # pending cleanup still refers to leaves a binding pointing at a deleted
    # command, which Tk reports on its background-error channel and nowhere
    # Python can see. Read that channel directly.
    root = app._tk_root
    seen: list = []
    root.tk.createcommand("bgerror", lambda *a: seen.append(a[0] if a else ""))
    try:
        button = bs.Button("go")
        sub = button.on_click(lambda e: None)
        root.update_idletasks()

        sub.cancel()
        button.on_click(lambda e: None)
        root.update_idletasks()
        _fire(app, button)

        assert seen == []
    finally:
        root.deletecommand("bgerror")


def test_a_real_event_survives_a_cancel_and_resubscribe_too(app):
    # Real events (`hover` is `<Enter>`) take the stock binding path, but they
    # are removed by the same patched `unbind`, so they need the same protection.
    # The virtual-event tests above bind a different wrapper and would not cover
    # this one.
    #
    # PASSES PRE-FIX ON PURPOSE — measured: the address reuse that breaks the
    # virtual path did not happen to land here. Not a dud; it is the only
    # coverage of the real-event wrapper, and it fails if that path regresses
    # outright.
    root = app._tk_root
    button = bs.Button("go")
    calls = {"a": 0, "b": 0}

    sub_a = button.on("hover", lambda e: calls.__setitem__("a", calls["a"] + 1))
    root.update_idletasks()
    button.emit("hover")
    root.update()
    assert calls == {"a": 1, "b": 0}, "precondition: the first handler is live"

    calls.update(a=0)
    sub_a.cancel()
    button.on("hover", lambda e: calls.__setitem__("b", calls["b"] + 1))
    root.update_idletasks()

    button.emit("hover")
    root.update()

    assert calls == {"a": 0, "b": 1}


def test_a_handler_that_destroys_its_own_widget_is_quiet(app):
    # A payload event caches its data and clears the entry once every handler
    # has run. That cleanup is deferred, so it must be owned by something that
    # outlives the widget — a handler destroying its own widget (a dialog
    # dismissing itself, a page tearing down) is ordinary, and getting it wrong
    # leaves a pending callback on a command destroy() already swept.
    #
    # Invisible to Python, like the teardown case above: read the background
    # channel.
    root = app._tk_root
    seen: list = []
    root.tk.createcommand("bgerror", lambda *a: seen.append(a[0] if a else ""))
    try:
        button = bs.Button("go")
        button.on_click(lambda e: button.destroy())
        root.update_idletasks()

        button.emit("click", data={"payload": 1})
        root.update()
        root.update_idletasks()

        assert seen == []
    finally:
        root.deletecommand("bgerror")


# --- A handler's return value must stay inert ---------------------------

def test_a_handler_return_value_cannot_suppress_the_others(app):
    # Matching the toolkit's script shape made handler return values
    # significant, where they had been discarded before. One particular string
    # means "stop the remaining handlers", so a handler that merely computed it
    # by accident would silently drop its siblings.
    #
    # `adapt_handler` discards public handlers' return values so that cannot
    # happen. Suppressing later handlers is a feature to design deliberately,
    # not to inherit from the toolkit — see the docstring there.
    button = bs.Button("go")
    calls = {"a": 0, "b": 0}

    def returns_break(event):
        calls["a"] += 1
        return "break"

    button.on_click(returns_break)
    button.on_click(lambda e: calls.__setitem__("b", calls["b"] + 1))
    app._tk_root.update_idletasks()

    _fire(app, button)

    assert calls == {"a": 1, "b": 1}


def test_a_return_value_is_inert_on_the_payload_path_too(shown_app):
    # `adapt_handler` has two arms — payload events and curated native events.
    # The test above covers the native arm; this one covers the payload arm.
    #
    # A widget whose `on()` and `emit()` agree on their target is required here:
    # on the field wrappers they do not, so `field.emit(...)` never reaches a
    # handler registered by `field.on_change(...)` and this would pass
    # vacuously (#396). `shown_app`, not `app`, because a generated event is not
    # delivered to this composite while its window is unmapped.
    slider = bs.Slider(value=5, min_value=0, max_value=10)
    calls = {"a": 0, "b": 0}

    def returns_break(event):
        calls["a"] += 1
        return "break"

    slider.on_change(returns_break)
    slider.on_change(lambda e: calls.__setitem__("b", calls["b"] + 1))
    shown_app._tk_root.update()

    slider.emit("change", data=bs.events.SliderEvent(value=7.0))
    shown_app._tk_root.update()

    assert calls == {"a": 1, "b": 1}