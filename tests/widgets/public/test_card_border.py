"""Regression guard for #188 — an accented Card derives its border from the
card's own (accent-tinted) surface, not the full-strength base accent. The stroke
should be a soft, surface-harmonious color: distinct from the raw accent (the old
behavior) and visibly different from the fill.
"""
import tkinter.ttk as ttk

import pytest

import bootstack as bs
from bootstack.style import get_theme_color


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


def _style_color(card, option):
    return ttk.Style().lookup(card._internal.cget("style"), option).lower()


@pytest.mark.parametrize("accent", ["primary", "danger", "success", "warning", "info", "secondary"])
def test_accented_card_border_is_surface_derived(app, accent):
    card = bs.Card(accent=accent)
    app._tk_root.update_idletasks()

    border = _style_color(card, "bordercolor")
    fill = _style_color(card, "background")

    # Not the raw accent (the pre-#188 behavior).
    assert border != get_theme_color(accent).lower()
    # A real, visible stroke — distinct from the card fill.
    assert border != fill