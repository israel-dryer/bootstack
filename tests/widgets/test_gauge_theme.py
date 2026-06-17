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