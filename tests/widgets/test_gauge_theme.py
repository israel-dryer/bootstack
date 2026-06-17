"""Gauge repaints its canvas on theme change (#167).

The Gauge (internal Meter) paints its face / track / arc / text imperatively,
outside the ttk style loop, so it re-resolves its colors via the STD publisher
channel — which fires *after* the theme rebuild (the old ttk `<<ThemeChanged>>`
binding fired before and raced it, leaving stale colors). Structural; one App
per process.
"""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.gui


@pytest.fixture(scope="module")
def app():
    import bootstack as bs

    app = bs.App(theme="bootstrap-light")
    app._tk_root.withdraw()
    try:
        yield app
    finally:
        try:
            app._tk_root.destroy()
        except Exception:
            pass


def test_gauge_canvas_repaints_on_theme_change(app):
    import bootstack as bs

    g = bs.Gauge(value=50)
    app._tk_root.update_idletasks()
    canvas = g._internal._canvas
    light_bg = canvas.cget("background")

    bs.set_theme("bootstrap-dark")
    app._tk_root.update()
    app._tk_root.update_idletasks()
    dark_bg = canvas.cget("background")

    assert dark_bg != light_bg, "gauge canvas kept the light-theme background"

    bs.set_theme("bootstrap-light")
    app._tk_root.update()
    app._tk_root.update_idletasks()
    assert canvas.cget("background") == light_bg


def test_offscreen_theme_change_defers_expensive_redraw(app):
    # A theme change while the gauge is off-screen must NOT run the expensive
    # supersampled redraw (so toggling the theme doesn't repaint every gauge in
    # the app); it marks the repaint pending and runs once when next viewable.
    import bootstack as bs

    g = bs.Gauge(value=50)
    app._tk_root.update_idletasks()
    m = g._internal

    calls = {"n": 0}
    m._draw_base_meter_images = lambda: calls.__setitem__("n", calls["n"] + 1)

    # Off-screen: defer.
    m.winfo_viewable = lambda: False
    m._theme_update_pending = False
    m._apply_theme_update()
    assert m._theme_update_pending is True
    assert calls["n"] == 0  # expensive redraw skipped while hidden

    # Viewable: repaint now, clear pending.
    m.winfo_viewable = lambda: True
    m._apply_theme_update()
    assert m._theme_update_pending is False
    assert calls["n"] == 1


def test_gauge_subscribes_and_releases(app):
    import bootstack as bs
    from bootstack._core.publisher import Publisher

    base = Publisher.subscriber_count()
    g = bs.Gauge(value=10)
    app._tk_root.update_idletasks()
    assert Publisher.subscriber_count() == base + 1

    g._internal.destroy()
    app._tk_root.update()
    app._tk_root.update_idletasks()
    assert Publisher.subscriber_count() == base