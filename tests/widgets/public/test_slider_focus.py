"""Slider keyboard-focus halo tests.

The single Slider uses the same per-handle focus halo as RangeSlider (instead of
a whole-widget frame ring): hidden at rest, shown on keyboard focus, hidden on
blur, and never raised by a mouse-driven focus.
"""
from __future__ import annotations

import pytest

import bootstack as bs


@pytest.fixture(scope="module")
def app():
    a = bs.App()
    a.__enter__()
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


def _ring_state(slider) -> str:
    inner = slider._internal
    return inner._canvas.itemcget(inner._focus_ring_item, "state")


def test_halo_hidden_at_rest(app):
    s = bs.Slider(50, min_value=0, max_value=100)
    assert _ring_state(s) == "hidden"


def test_halo_shows_on_keyboard_focus(app):
    s = bs.Slider(50, min_value=0, max_value=100)
    inner = s._internal
    inner._mouse_pressed = False
    inner._on_focus_in(None)
    assert inner._kbd_focused is True
    assert _ring_state(s) == "normal"
    inner._on_focus_out(None)
    assert _ring_state(s) == "hidden"


def test_mouse_focus_does_not_show_halo(app):
    s = bs.Slider(50, min_value=0, max_value=100)
    inner = s._internal
    inner._mouse_pressed = True       # set by the click path
    inner._on_focus_in(None)
    assert inner._kbd_focused is False
    assert _ring_state(s) == "hidden"
