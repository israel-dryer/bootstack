"""ThemeToggle — a button whose icon follows the theme; clicking flips it.

It is stateless (a Button), so the only thing kept in sync is the sun/moon icon,
which updates on a click *or* a programmatic theme change elsewhere.
"""
from __future__ import annotations

import pytest

import bootstack as bs
from bootstack.style import get_theme

SUN = "sun-fill"
MOON = "moon-stars-fill"


def _flush(app):
    app._tk_root.update()


def test_icon_reflects_initial_theme(app):
    bs.set_theme("bootstrap-light"); _flush(app)
    tt = bs.ThemeToggle(); _flush(app)
    assert tt.icon == SUN


def test_click_toggles_theme_and_icon(app):
    bs.set_theme("bootstrap-light"); _flush(app)
    tt = bs.ThemeToggle(); _flush(app)

    tt._internal.invoke(); _flush(app)            # real click
    assert get_theme() == "bootstrap-dark"
    assert tt.icon == MOON

    tt._internal.invoke(); _flush(app)
    assert get_theme() == "bootstrap-light"
    assert tt.icon == SUN


def test_programmatic_theme_change_syncs_icon(app):
    bs.set_theme("bootstrap-light"); _flush(app)
    tt = bs.ThemeToggle(); _flush(app)
    assert tt.icon == SUN

    bs.set_theme("bootstrap-dark"); _flush(app)   # changed elsewhere, no click
    assert tt.icon == MOON


def test_custom_icons_variant_density(app):
    bs.set_theme("bootstrap-light"); _flush(app)
    tt = bs.ThemeToggle(
        light_icon="brightness-high", dark_icon="moon",
        variant="outline", density="compact",
    )
    _flush(app)
    assert tt.icon == "brightness-high"
