"""Tab overflow handling (issue #168).

When tab headers exceed the strip length, they are hosted in a scrollbar-less
scrolling strip with a trailing chevron that lists the off-screen tabs (the
plain non-scrolling strip is used only for `tab_width='stretch'`, which always
fits). These assert the structural behavior — the scrollable
wiring, overflow detection, the off-screen set, and scroll-into-view — for both
orientations. Visual polish is verified by hand. One shown, module-scoped App
(child widgets only map under a shown App; multiple Apps per process crash Tk).
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
    root.geometry("380x260")
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


def _build(app, *, orient, count, label, **kw):
    tabs = bs.Tabs(orient=orient, grow=True, **kw)
    for i in range(count):
        with tabs.add(f"k{i}", label=label.format(i=i)):
            bs.Label(f"body {i}")
    _pump(app)
    inner = tabs._internal._tabs
    inner._update_overflow()
    _pump(app)
    return tabs, inner


def test_scrolling_enabled_by_default(shown_app):
    tabs, inner = _build(shown_app, orient="horizontal", count=2, label="Tab {i}")
    assert inner._scrollable is True
    assert inner._scroll is not None
    tabs.destroy()


def test_stretch_uses_plain_strip(shown_app):
    # Stretched tabs always fit, so they use the plain non-scrolling strip.
    tabs, inner = _build(
        shown_app, orient="horizontal", count=2, label="Tab {i}", tab_width="stretch"
    )
    assert inner._scrollable is False
    assert inner._scroll is None
    tabs.destroy()


def test_horizontal_overflow_shows_button_and_lists_offscreen(shown_app):
    tabs, inner = _build(
        shown_app, orient="horizontal", count=12, label="Document number {i}"
    )
    assert inner._axis == "x"
    assert inner._content_size() > inner._viewport_size()
    assert inner._content_overflows() is True
    assert inner._overflow_visible is True
    assert inner._overflow_button is not None
    # Most tabs are off-screen; the first remains visible.
    offscreen = inner._offscreen_tab_keys()
    assert "k0" not in offscreen
    assert len(offscreen) >= 8
    tabs.destroy()


def test_scroll_into_view_moves_the_strip(shown_app):
    tabs, inner = _build(
        shown_app, orient="horizontal", count=12, label="Document number {i}"
    )
    before = inner._view_first()
    inner._scroll_into_view("k11")
    _pump(shown_app)
    after = inner._view_first()
    assert after > before  # scrolled right to reveal the last tab
    # And the revealed tab is no longer reported off-screen.
    assert "k11" not in inner._offscreen_tab_keys()
    tabs.destroy()


def test_add_then_select_reveals_new_tab(shown_app):
    # Regression: add+select must scroll the new (rightmost) tab into view, not
    # snap to the left because the new tab's geometry wasn't yet computed.
    tabs, inner = _build(
        shown_app, orient="horizontal", count=12, label="source-file-{i}.py"
    )
    inner._scroll_into_view("k6")  # scroll to the middle first
    _pump(shown_app)
    with tabs.add("knew", label="source-file-new.py"):
        bs.Label("new")
    tabs.select("knew")
    _pump(shown_app)
    # The newly selected tab is fully visible.
    assert "knew" not in inner._offscreen_tab_keys()
    assert inner._view_first() > 0.5  # scrolled toward the right end
    tabs.destroy()


def test_remove_middle_tab_preserves_order(shown_app):
    # With gap=0 the strip no longer full-repacks on removal (no flash); the
    # remaining tabs keep their order.
    tabs, inner = _build(shown_app, orient="horizontal", count=6, label="T{i}")
    tabs.forget_tab("k2")
    _pump(shown_app)
    assert inner._tab_order == ["k0", "k1", "k3", "k4", "k5"]
    tabs.destroy()


def test_no_overflow_when_few_tabs(shown_app):
    tabs, inner = _build(shown_app, orient="horizontal", count=2, label="T{i}")
    assert inner._content_overflows() is False
    assert inner._overflow_visible is False
    tabs.destroy()


def test_max_tabs_disables_add_button(shown_app):
    tabs = bs.Tabs(allow_add=True, max_tabs=4, grow=True)
    inner = tabs._internal._tabs
    for i in range(3):
        with tabs.add(f"k{i}", label=f"T{i}"):
            bs.Label("x")
    _pump(shown_app)
    assert inner._add_button.instate(["!disabled"])  # 3 < 4 → enabled
    with tabs.add("k3", label="T3"):
        bs.Label("x")
    _pump(shown_app)
    assert inner._add_button.instate(["disabled"])  # 4 == max → disabled
    tabs.forget_tab("k3")
    _pump(shown_app)
    assert inner._add_button.instate(["!disabled"])  # back under the limit
    tabs.destroy()


def test_overflow_menu_tracks_tab_icons(shown_app):
    tabs, inner = _build(
        shown_app, orient="horizontal", count=6, label="File {i}", allow_close="hover"
    )
    # rebuild with explicit icons
    tabs.destroy()
    tabs = bs.Tabs(orient="horizontal", grow=True)
    inner = tabs._internal._tabs
    for i in range(6):
        with tabs.add(f"k{i}", label=f"File {i}", icon="file-earmark-code"):
            bs.Label("x")
    _pump(shown_app)
    assert inner._tab_icons["k0"] == "file-earmark-code"
    assert len(inner._tab_icons) == 6
    tabs.destroy()


def test_vertical_overflow_and_scroll(shown_app):
    tabs, inner = _build(shown_app, orient="vertical", count=18, label="Section {i}")
    assert inner._axis == "y"
    assert inner._content_overflows() is True
    assert inner._overflow_visible is True
    before = inner._view_first()
    inner._scroll_into_view("k17")
    _pump(shown_app)
    assert inner._view_first() > before
    tabs.destroy()
