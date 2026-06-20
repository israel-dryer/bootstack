"""Button review fixes (feat/button-review).

Three correctness fixes from the formal Button review:

1. `disabled` getter reads the ttk state *flag* (`instate`), not a `cget('state')`
   string compare — so a flag-set disabled state (e.g. via composite state
   propagation) is reported correctly.
2. `text` get/set route through the bound textvariable when a `textsignal` owns
   the text (ttk's `text` option no longer tracks the display in that mode).
3. `on_click()` resolves to the activation path (the `<<Click>>` event emitted by
   the command dispatcher), so it fires on mouse/keyboard/`click()` activation,
   honors disabled state, and is consistent with the `on_click=` callback. Both
   the handler and Stream forms compose on the same event.
"""
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


# ----- disabled getter -----

def test_disabled_setter_roundtrips(app):
    b = bs.Button("x")
    assert b.disabled is False
    b.disabled = True
    assert b.disabled is True
    b.disabled = False
    assert b.disabled is False


def test_disabled_getter_reads_state_flag(app):
    # A disabled flag set directly (as composite state propagation does) must be
    # reported — the old cget('state') compare missed this.
    b = bs.Button("x")
    b._internal.state(("disabled",))
    assert b.disabled is True


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
    b._internal.invoke()
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
