"""Button review fixes (feat/button-review).

Two correctness fixes from the formal Button review, both reachable through the
public surface:

1. `text` setter routes through the bound textvariable when a `textsignal` owns
   the text — `configure(text=)` is a no-op in that mode, so `button.text = ...`
   silently failed. (The getter stays on the public `cget('text')`, which
   reliably reflects the bound variable.)
2. `on_click()` resolves to the activation path (the `<<Click>>` event emitted by
   the command dispatcher), so it fires on mouse/keyboard/`click()` activation,
   honors disabled state, and is consistent with the `on_click=` callback. Both
   the handler and Stream forms compose on the same event.
"""
import pytest

import bootstack as bs


# ----- disabled getter -----

def test_disabled_setter_roundtrips(app):
    b = bs.Button("x")
    assert b.disabled is False
    b.disabled = True
    assert b.disabled is True
    b.disabled = False
    assert b.disabled is False


def test_disabled_via_constructor(app):
    assert bs.Button("x", disabled=True).disabled is True


# ----- text get/set with a bound signal -----

def test_text_get_set_unbound(app):
    b = bs.Button("Plain")
    assert b.text == "Plain"
    b.text = "New"
    assert b.text == "New"


def test_text_get_set_with_textsignal(app):
    sig = bs.Signal("Initial")
    b = bs.Button(textsignal=sig)
    assert b.text == "Initial"

    # Setting .text writes through the bound variable and keeps the signal in sync.
    b.text = "Changed"
    assert b.text == "Changed"
    assert sig() == "Changed"

    # Signal writes flow back to .text.
    sig.set("ViaSignal")
    assert b.text == "ViaSignal"


# ----- on_click activation semantics -----

def test_click_fires_both_callback_and_handler(app):
    seen = {"cmd": 0, "handler": 0}
    b = bs.Button("x", on_click=lambda: seen.__setitem__("cmd", seen["cmd"] + 1))
    b.on_click(lambda e: seen.__setitem__("handler", seen["handler"] + 1))

    b.click()
    assert seen == {"cmd": 1, "handler": 1}


def test_click_is_noop_when_disabled(app):
    seen = {"cmd": 0, "handler": 0}
    b = bs.Button("x", on_click=lambda: seen.__setitem__("cmd", seen["cmd"] + 1))
    b.on_click(lambda e: seen.__setitem__("handler", seen["handler"] + 1))

    b.disabled = True
    b.click()
    assert seen == {"cmd": 0, "handler": 0}


def test_on_click_stream_form(app):
    got = []
    b = bs.Button("y")
    sub = b.on_click().map(lambda e: "clicked").listen(lambda v: got.append(v))

    b.click()
    b.click()
    assert got == ["clicked", "clicked"]

    sub.cancel()
    b.click()
    assert got == ["clicked", "clicked"]


def test_on_click_handler_receives_event(app):
    received = []
    b = bs.Button("z")
    b.on_click(lambda e: received.append(e))
    b.click()
    assert len(received) == 1
    # The activation event carries the widget; pointer/modifier fields are unset
    # for programmatic/keyboard activation, so we only assert delivery here.
    assert received[0] is not None
