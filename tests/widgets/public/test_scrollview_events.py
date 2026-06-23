"""ScrollView scroll events, position, and keyboard scrolling (#298).

This surface shipped without tests. `on_scroll` and `scroll_position` work
headless; keyboard scrolling needs a mapped, focused canvas (`shown_app`), so
the wiring is asserted deterministically and the behavior is checked when focus
can be taken.
"""
import pytest

import bootstack as bs
from bootstack.events import ScrollEvent
from bootstack.streams import Stream

pytestmark = pytest.mark.gui


def _tall(parent_app, **kw):
    sv = bs.ScrollView(height=100, width=200, **kw)
    with sv:
        for i in range(60):
            bs.Label(f"row {i}")
    parent_app._tk_root.update_idletasks()
    return sv


# ----- scroll_position -----

def test_scroll_position_starts_at_top(app):
    sv = _tall(app)
    assert sv.scroll_position == (0.0, 0.0)


def test_scroll_position_reflects_programmatic_scroll(app):
    sv = _tall(app)
    sv.yview_moveto(0.5)
    app._tk_root.update_idletasks()
    assert sv.scroll_position[0] == pytest.approx(0.5, abs=0.05)


def test_scroll_position_stays_below_one_while_filled(app):
    # The position is the fraction above the viewport top, so it tops out below
    # 1.0 while content still fills the viewport (the docstring's contract).
    sv = _tall(app)
    sv.scroll_to_bottom()
    app._tk_root.update_idletasks()
    assert 0.0 < sv.scroll_position[0] < 1.0


# ----- on_scroll -----

def test_on_scroll_fires_with_scroll_event(app):
    sv = _tall(app)
    events = []
    sv.on_scroll(lambda e: events.append(e))
    sv.yview_moveto(0.5)
    app._tk_root.update_idletasks()
    assert events, "on_scroll did not fire"
    assert isinstance(events[-1], ScrollEvent)
    assert 0.0 <= events[-1].y <= 1.0


def test_on_scroll_without_handler_returns_stream(app):
    sv = _tall(app)
    assert isinstance(sv.on_scroll(), Stream)


# ----- keyboard scrolling -----

def test_keyboard_bindings_registered(app):
    sv = _tall(app)
    canvas = sv._internal.canvas
    for key in ("<Up>", "<Down>", "<Prior>", "<Next>",
                "<Home>", "<End>", "<Left>", "<Right>"):
        assert canvas.bind(key), f"{key} is not bound"


def test_keyboard_end_jumps_to_bottom(shown_app):
    sv = _tall(shown_app)
    canvas = sv._internal.canvas
    canvas.focus_force()
    shown_app._tk_root.update()
    if shown_app._tk_root.focus_get() is not canvas:
        pytest.skip("canvas could not take keyboard focus in this environment")
    canvas.yview_moveto(0.0)
    shown_app._tk_root.update()
    canvas.event_generate("<End>", when="now")
    shown_app._tk_root.update()
    assert canvas.yview()[0] > 0.0  # End jumped toward the bottom
