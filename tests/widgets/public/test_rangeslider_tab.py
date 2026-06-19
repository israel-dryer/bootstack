"""RangeSlider keyboard model tests (issue #211).

The slider is a single tab stop: it binds no ``<Tab>``, so Tk's normal focus
traversal moves focus in and straight out — never trapped. The cross-axis arrow
keys switch which handle is active (``_select_handle``), and the active handle
shows a focus ring while the widget holds keyboard focus. These assert the state
transitions directly (no event-loop pumping needed).
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


def test_no_tab_binding_means_single_tab_stop(app):
    """No instance <Tab> / <<PrevWindow>> binding → Tk traverses focus straight
    through; the widget can never trap focus."""
    rs = bs.RangeSlider(20, 80, min_value=0, max_value=100)
    bound = rs._internal.bind()
    assert "<Tab>" not in bound
    assert "<<PrevWindow>>" not in bound


def test_select_handle_switches_active_handle(app):
    rs = bs.RangeSlider(20, 80, min_value=0, max_value=100)
    inner = rs._internal
    inner._focus_handle = "lo"

    assert inner._select_handle("hi") == "break"
    assert inner._focus_handle == "hi"

    assert inner._select_handle("lo") == "break"
    assert inner._focus_handle == "lo"


def test_select_handle_noop_when_disabled(app):
    rs = bs.RangeSlider(20, 80, min_value=0, max_value=100, disabled=True)
    inner = rs._internal
    inner._focus_handle = "lo"
    inner._select_handle("hi")
    assert inner._focus_handle == "lo"   # disabled → no switch


def test_keyboard_focus_toggles_ring_state(app):
    rs = bs.RangeSlider(20, 80, min_value=0, max_value=100)
    inner = rs._internal
    assert inner._kbd_focused is False

    inner._mouse_pressed = False
    inner._on_focus_in(None)
    assert inner._kbd_focused is True

    inner._on_focus_out(None)
    assert inner._kbd_focused is False


def test_mouse_focus_does_not_set_keyboard_ring(app):
    """A click focuses the widget but should not raise the keyboard focus ring."""
    rs = bs.RangeSlider(20, 80, min_value=0, max_value=100)
    inner = rs._internal
    inner._mouse_pressed = True       # set by the click path
    inner._on_focus_in(None)
    assert inner._kbd_focused is False
