"""PageStack navigation behavior.

The macOS-specific tests cover the keep-mapped fix for the page-nav white flash
(GitHub #336): on Aqua a remapped page paints blank for one display cycle, so
PageStack keeps every visited page mapped (stacked in one grid cell) and switches
with lift()/lower() instead of pack_forget/pack. Other platforms keep the cheaper
one-page-mapped pack path, so these invariants are gated to Aqua.
"""
from __future__ import annotations

import pytest

import bootstack as bs


def _is_aqua(app) -> bool:
    return app._tk_root.tk.call("tk", "windowingsystem") == "aqua"


def _build_three(app):
    ps = bs.PageStack(grow=True)
    for key in ("a", "b", "c"):
        with ps.add(key):
            bs.Label(f"page {key}")
    return ps, ps._internal._pages


def test_visited_pages_stay_mapped_on_macos(shown_app):
    """macOS: navigating away keeps every visited page mapped (no remap flash)."""
    if not _is_aqua(shown_app):
        pytest.skip("keep-mapped navigation is macOS-only")

    ps, pages = _build_three(shown_app)
    for key in ("a", "b", "c"):
        ps.navigate(key)
        shown_app._tk_root.update()

    # None was unmapped on hide — re-showing any of them never remaps (no flash).
    assert pages["a"].winfo_ismapped()
    assert pages["b"].winfo_ismapped()
    assert pages["c"].winfo_ismapped()


def test_only_active_page_exposed_to_theme_walk_on_macos(shown_app):
    """macOS: hidden-but-mapped pages are flagged so the theme walk skips them."""
    if not _is_aqua(shown_app):
        pytest.skip("keep-mapped navigation is macOS-only")

    ps, pages = _build_three(shown_app)
    ps.navigate("a")
    shown_app._tk_root.update()
    ps.navigate("b")
    shown_app._tk_root.update()

    # The active page is walkable; the one left behind is pruned (stays mapped).
    assert pages["b"]._bs_nav_hidden is False
    assert pages["a"]._bs_nav_hidden is True


def test_return_after_many_visits_does_not_remap_on_macos(shown_app):
    """macOS: returning to an early page after others keeps everything mapped.

    Unbounded keep-mapped — no eviction — so depth of navigation never
    reintroduces the flash for a previously-visited page.
    """
    if not _is_aqua(shown_app):
        pytest.skip("keep-mapped navigation is macOS-only")

    ps, pages = _build_three(shown_app)
    for key in ("a", "b", "c", "b", "a"):
        ps.navigate(key)
        shown_app._tk_root.update()

    assert pages["a"]._bs_nav_hidden is False
    assert pages["a"].winfo_ismapped()
    assert pages["b"].winfo_ismapped()
    assert pages["c"].winfo_ismapped()


def test_navigation_and_history_work_everywhere(app):
    """Cross-platform: navigate/back/forward and current() behave regardless."""
    ps, _pages = _build_three(app)

    ps.navigate("a")
    assert ps._internal.current()[0] == "a"
    ps.navigate("b")
    ps.navigate("c")
    assert ps._internal.can_back() is True

    ps.back()
    assert ps._internal.current()[0] == "b"
    ps.forward()
    assert ps._internal.current()[0] == "c"