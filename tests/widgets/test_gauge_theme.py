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
    m = g._internal
    canvas = m._canvas
    # The test window is withdrawn, so the gauge is never "viewable"; force it so
    # the on-screen repaint path runs (off-screen would correctly defer).
    m.winfo_viewable = lambda: True
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
    # the app); the Frame base hook marks it pending and repaints once on <Map>.
    import bootstack as bs

    g = bs.Gauge(value=50)
    app._tk_root.update_idletasks()
    m = g._internal

    calls = {"n": 0}
    m._theme_repaint = lambda: calls.__setitem__("n", calls["n"] + 1)

    # Off-screen: defer (no repaint), mark pending.
    m.winfo_viewable = lambda: False
    m._theme_repaint_pending = False
    m._on_theme_notify()
    assert m._theme_repaint_pending is True
    assert calls["n"] == 0  # expensive redraw skipped while hidden

    # Viewable: repaint immediately, clear pending.
    m.winfo_viewable = lambda: True
    m._on_theme_notify()
    assert m._theme_repaint_pending is False
    assert calls["n"] == 1


def test_supersample_scale_capped_on_hidpi(app):
    # The supersample is downscaled to the gauge's logical size, so the DPI
    # multiplier b.scale() adds is wasted; it must be capped at the base factor
    # so a HiDPI display does not balloon the redraw.
    import bootstack as bs
    from bootstack.style.style import get_style
    from bootstack.widgets._impl.composites import meter as meter_mod

    g = bs.Gauge(value=50)
    m = g._internal
    b = get_style().style_builder
    orig = b.scale
    b.scale = lambda v: v * 3  # pretend a 3x HiDPI display
    try:
        m._resolve_meter_styles()
        assert m._image_scale == meter_mod.DEFAULT_IMAGE_SCALE  # capped, not 18
    finally:
        b.scale = orig


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