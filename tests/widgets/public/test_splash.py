"""bs.Splash — registration, dismiss model, and app-reveal deferral (#310).

The splash registers on the ambient app, shows itself, and the app defers its
own reveal until the splash dismisses. These exercise the public surface
(construction, guards, `until` modes, `min_duration` floor, `skippable`,
`dismiss()`, `on_dismiss`) against the shared session root.
"""
from __future__ import annotations

import time

import pytest

import bootstack as bs
from bootstack.errors import BootstackError
from bootstack.events import Subscription


def _internal(app):
    return app._tk_root


def _pump(app, ms: int) -> None:
    """Drive the event loop for `ms` milliseconds so `after()` callbacks run."""
    end = ms / 1000.0
    elapsed = 0.0
    while elapsed < end:
        app._tk_root.update()
        time.sleep(0.01)
        elapsed += 0.01


@pytest.fixture
def splash_app(app):
    """The session app, with any lingering splash registration cleared after."""
    yield app
    sp = getattr(_internal(app), "_splash", None)
    if sp is not None:
        try:
            sp._tk_toplevel.destroy()
        except Exception:
            pass
        _internal(app)._splash = None


# --- construction & registration -------------------------------------------

def test_construction_registers_and_shows(splash_app):
    sp = bs.Splash(until="manual")
    with sp:
        bs.Label("Hello")
    assert sp.is_showing is True
    assert _internal(splash_app)._splash is sp


def test_second_splash_raises(splash_app):
    sp = bs.Splash(until="manual")
    with sp:
        bs.Label("first")
    with pytest.raises(BootstackError):
        bs.Splash(until="manual")


def test_no_app_raises(splash_app, monkeypatch):
    import bootstack._runtime.app as appmod

    def _no_app():
        raise RuntimeError("no app")

    monkeypatch.setattr(appmod, "get_current_app", _no_app)
    with pytest.raises(BootstackError):
        bs.Splash(until="manual")


@pytest.mark.parametrize("bad", [True, False, "soon", "later"])
def test_invalid_until_raises(splash_app, bad):
    with pytest.raises(BootstackError):
        bs.Splash(until=bad)


# --- dismiss model ----------------------------------------------------------

def test_until_manual_does_not_dismiss_on_ready(splash_app):
    revealed = []
    sp = bs.Splash(until="manual")
    with sp:
        bs.Label("x")
    sp._notify_app_ready(lambda: revealed.append(True))
    _pump(splash_app, 100)
    assert revealed == []          # app stays hidden under a manual splash
    assert sp.is_showing is True


def test_until_ready_dismisses_and_reveals(splash_app):
    revealed, reasons = [], []
    sp = bs.Splash(until="ready", fade=False)
    sp.on_dismiss(lambda e: reasons.append(e.reason))
    with sp:
        bs.Label("x")
    sp._notify_app_ready(lambda: revealed.append(True))
    _pump(splash_app, 100)
    assert reasons == ["ready"]
    assert revealed == [True]
    assert sp.is_showing is False
    assert _internal(splash_app)._splash is None


def test_dismiss_method_fires_manual_and_reveals(splash_app):
    revealed, reasons = [], []
    sp = bs.Splash(until="manual", fade=False)
    sp.on_dismiss(lambda e: reasons.append(e.reason))
    with sp:
        bs.Label("x")
    sp._notify_app_ready(lambda: revealed.append(True))
    sp.dismiss()
    _pump(splash_app, 100)
    assert reasons == ["manual"]
    assert revealed == [True]
    assert sp.is_showing is False


def test_timer_mode_dismisses_after_delay(splash_app):
    reasons = []
    sp = bs.Splash(until=0.2, fade=False)
    sp.on_dismiss(lambda e: reasons.append(e.reason))
    with sp:
        bs.Label("x")
    _pump(splash_app, 100)
    assert reasons == []           # before the timer
    _pump(splash_app, 250)
    assert reasons == ["timer"]    # after the timer


def test_min_duration_floors_early_dismiss(splash_app):
    reasons = []
    sp = bs.Splash(until="manual", min_duration=0.3, fade=False)
    sp.on_dismiss(lambda e: reasons.append(e.reason))
    with sp:
        bs.Label("x")
    sp.dismiss()                   # requested immediately
    _pump(splash_app, 150)
    assert reasons == []           # held below the floor
    _pump(splash_app, 250)
    assert reasons == ["manual"]   # released once the floor passes


def test_skippable_escape_dismisses(splash_app):
    reasons = []
    sp = bs.Splash(until="manual", skippable=True, fade=False)
    sp.on_dismiss(lambda e: reasons.append(e.reason))
    with sp:
        bs.Label("x")
    sp._tk_toplevel.focus_force()   # key events route to the focused window
    _pump(splash_app, 30)
    sp._tk_toplevel.event_generate("<Escape>", when="now")
    _pump(splash_app, 50)
    assert reasons == ["skip"]


# --- events surface ---------------------------------------------------------

def test_on_dismiss_returns_subscription_and_stream(splash_app):
    sp = bs.Splash(until="manual")
    with sp:
        bs.Label("x")
    sub = sp.on_dismiss(lambda e: None)
    assert isinstance(sub, Subscription)
    from bootstack.streams import Stream
    assert isinstance(sp.on_dismiss(), Stream)
