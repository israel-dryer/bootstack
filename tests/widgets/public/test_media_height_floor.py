"""Gallery/Carousel keep a height floor in non-expanding parents (issue #160).

Gallery and Carousel are fill-driven and request ~0 height on their own, so in a
container that hands children their requested size — a ScrollView, an auto-fit
window — they used to collapse to a sliver and drag the surrounding group down
with them. PR #161 gave each a requested-height floor (a true minimum: `grow`/
`expand` still grow past it). These guard that the floor exists, is honored inside
a ScrollView, reflects the sizing knobs, and does not freeze growth.

One shown, module-scoped App (children only map under a shown App; multiple Apps
per process crash Tk).
"""
from __future__ import annotations

import pytest

import bootstack as bs

pytestmark = pytest.mark.gui


@pytest.fixture(scope="module")
def shown_app():
    app = bs.App()
    app.__enter__()
    root = app._tk_root
    root.geometry("440x640")
    root.deiconify()
    root.update_idletasks()
    try:
        yield app
    finally:
        try:
            app.__exit__(None, None, None)
        except Exception:
            pass
        try:
            root.destroy()
        except Exception:
            pass


def _pump(app):
    app._tk_root.update_idletasks()
    app._tk_root.update()


# ----- The floor exists (requested height is non-zero) -----------------------


def test_gallery_requests_a_height_floor(shown_app):
    g = bs.Gallery(grow=True)
    _pump(shown_app)
    # Default rows=2, tile 160, ring pad 2x6, gap 8 -> 2 * 180 = 360.
    assert g._internal.winfo_reqheight() == 360
    g.destroy()


def test_carousel_requests_a_height_floor(shown_app):
    c = bs.Carousel(grow=True)
    _pump(shown_app)
    # Default aspect_ratio 1.5 -> round(400 / 1.5) = 267.
    assert c._internal.winfo_reqheight() == 267
    c.destroy()


# ----- The issue's literal case: non-zero height inside a ScrollView ----------


def test_gallery_in_scrollview_does_not_collapse(shown_app):
    with bs.ScrollView(scroll_direction="vertical", height=240, grow=True) as sv:
        g = bs.Gallery(grow=True)
    _pump(shown_app)
    assert g._internal.winfo_reqheight() > 1
    assert g._internal.winfo_height() > 1  # actually rendered, not a sliver
    sv.destroy()  # also destroys the gallery inside


def test_carousel_in_scrollview_does_not_collapse(shown_app):
    with bs.ScrollView(scroll_direction="vertical", height=240, grow=True) as sv:
        c = bs.Carousel(grow=True)
    _pump(shown_app)
    assert c._internal.winfo_reqheight() > 1
    assert c._internal.winfo_height() > 1
    sv.destroy()


# ----- The floor is a minimum, not a freeze ----------------------------------


def test_floor_is_a_minimum_not_a_fixed_size(shown_app):
    # The floor must be a requested MINIMUM the parent can grow past, not a hard
    # freeze. The public wrappers achieve this by freezing the frame at the floor
    # while packing the inner canvas with expand, so a larger allocation flows
    # into the canvas. Assert that growth path so a future change that re-breaks
    # it is caught. (Actual grow-past-floor allocation is exercised in the demo.)
    g = bs.Gallery(grow=True)
    c = bs.Carousel(grow=True)
    _pump(shown_app)
    assert g._internal._container.pack_info().get("expand") in (1, "1", True)
    assert c._internal._stage.pack_info().get("expand") in (1, "1", True)
    g.destroy()
    c.destroy()


# ----- The sizing knobs move the floor ---------------------------------------


def test_gallery_rows_scale_the_floor(shown_app):
    g2 = bs.Gallery(rows=2, grow=True)
    g4 = bs.Gallery(rows=4, grow=True)
    _pump(shown_app)
    assert g4._internal.winfo_reqheight() > g2._internal.winfo_reqheight()
    g2.destroy()
    g4.destroy()


def test_carousel_height_overrides_aspect_ratio(shown_app):
    c = bs.Carousel(height=200, grow=True)
    _pump(shown_app)
    assert c._internal.winfo_reqheight() == 200
    c.destroy()


def test_carousel_lower_aspect_ratio_is_taller(shown_app):
    wide = bs.Carousel(aspect_ratio=2.0, grow=True)   # shorter floor
    tall = bs.Carousel(aspect_ratio=1.0, grow=True)   # taller floor
    _pump(shown_app)
    assert tall._internal.winfo_reqheight() > wide._internal.winfo_reqheight()
    wide.destroy()
    tall.destroy()
