"""The backend-agnostic menu probe reads both `ContextMenu` backends (#379).

`ContextMenu` picks its implementation from the windowing system — an
overrideredirect Toplevel of themed widgets everywhere, a real `tk.Menu` on
macOS — and the two share no internals. Several tests reached straight into the
themed backend's `_items` / `_toplevel`, so they passed on Windows and Linux and
errored out on macOS, leaving the native path untested while looking covered.
`menu_probe` (in `tests/conftest.py`) is what those tests read through instead.

The probe is therefore load-bearing on a platform most contributors cannot run.
These tests drive **both** backend classes directly rather than whichever one
this platform selects, so the macOS branch is exercised everywhere — including
in CI on Linux. A `tk.Menu` is real on every platform; only which backend
`ContextMenu` *chooses* is platform-specific.
"""
from __future__ import annotations

import pytest

import bootstack as bs
from bootstack.widgets._impl.composites.contextmenu import (
    _NativeContextMenu,
    _ToplevelContextMenu,
)

pytestmark = pytest.mark.gui

BACKENDS = [("themed", _ToplevelContextMenu), ("native", _NativeContextMenu)]


def _build(backend_cls, app):
    """A menu of Small / Medium (disabled) / Large on the given backend."""
    impl = backend_cls(master=app._tk_root, target=bs.Label("target").tk)
    impl.add_item("command", text="Small")
    impl.add_item("command", text="Medium", disabled=True)
    impl.add_item("command", text="Large")
    return impl


@pytest.mark.parametrize("name,backend_cls", BACKENDS, ids=[b[0] for b in BACKENDS])
def test_is_native_identifies_the_backend(app, menu_probe, name, backend_cls):
    impl = _build(backend_cls, app)
    assert menu_probe.is_native(impl) is (name == "native")


@pytest.mark.parametrize("name,backend_cls", BACKENDS, ids=[b[0] for b in BACKENDS])
def test_item_count_agrees_across_backends(app, menu_probe, name, backend_cls):
    impl = _build(backend_cls, app)
    assert menu_probe.item_count(impl) == 3


@pytest.mark.parametrize("name,backend_cls", BACKENDS, ids=[b[0] for b in BACKENDS])
def test_item_disabled_agrees_across_backends(app, menu_probe, name, backend_cls):
    impl = _build(backend_cls, app)
    # Both must report the same thing, or the tests reading through the probe
    # would assert something different depending on the platform.
    assert menu_probe.item_disabled(impl, 1) is True
    assert menu_probe.item_disabled(impl, 0) is False
    assert menu_probe.item_disabled(impl, 2) is False


def test_popup_toplevel_is_the_themed_backends_window(app, menu_probe):
    impl = _build(_ToplevelContextMenu, app)
    popup = menu_probe.popup_toplevel(impl)
    assert popup is not None
    assert popup.winfo_children(), "the themed popup owns a widget tree to skip"


def test_popup_toplevel_is_none_on_the_native_backend(app, menu_probe):
    # The native menu is drawn by the window server, so there is no widget tree
    # for a bindtag walk to reach. Tests must branch on None, not assume a window.
    impl = _build(_NativeContextMenu, app)
    assert menu_probe.popup_toplevel(impl) is None


def test_empty_menu_counts_zero_on_both_backends(app, menu_probe):
    # `tk.Menu.index('end')` returns None when empty rather than -1; the probe
    # has to translate that, and getting it wrong would report 1 for an empty
    # native menu.
    for backend_cls in (_ToplevelContextMenu, _NativeContextMenu):
        impl = backend_cls(master=app._tk_root)
        assert menu_probe.item_count(impl) == 0


def test_platform_flag_matches_the_backend_contextmenu_picks(
    app, menu_probe, menus_are_native
):
    # Ties the two fixtures together: whichever backend this platform selects
    # must be the one `menus_are_native` describes.
    menu = bs.ContextMenu(target=bs.Label("t"), trigger="manual")
    menu.add_item("Edit")
    try:
        assert menu_probe.is_native(menu._internal._impl) is menus_are_native
    finally:
        menu.destroy()