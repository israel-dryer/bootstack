"""Auto-injected title bar for undecorated windows (#162).

An undecorated App/Window with no author-supplied chrome gets a built-in,
draggable title bar (min/max/close) so a borderless window is never stranded.
`window_controls=False` (Window only) opts out. Structural — drives
`ChromeHostMixin._ensure_default_titlebar` directly (no mainloop). One
module-scoped root; Windows are Toplevels under it.
"""
from __future__ import annotations

import sys

import pytest

pytestmark = [pytest.mark.gui, pytest.mark.isolated]

_NOT_MAC = sys.platform != "darwin"
_skip_mac = pytest.mark.skipif(not _NOT_MAC, reason="overrideredirect disabled on macOS")


@pytest.fixture(scope="module")
def app():
    import bootstack as bs

    app = bs.App(title="t", undecorated=True)
    app._tk_root.withdraw()
    try:
        yield app
    finally:
        try:
            app._tk_root.destroy()
        except Exception:
            pass


def _has_controls(host) -> bool:
    return any(
        tb._internal.show_window_controls
        for tb, _ in (getattr(host, "_chrome_toolbars", None) or [])
    )


def _reset_chrome(host) -> None:
    for tb, _ in (getattr(host, "_chrome_toolbars", None) or []):
        try:
            tb._internal.destroy()
        except Exception:
            pass
    host._chrome_toolbars = []


@_skip_mac
def test_app_undecorated_sets_override_redirect(app):
    assert app._undecorated is True
    assert bool(app._tk_root.overrideredirect())


@_skip_mac
def test_app_undecorated_draws_border(app):
    # Undecorated => a 1px border frame wraps the content (not the bare root).
    assert app._region_root is not app._tk_root


@_skip_mac
def test_injects_titlebar_when_undecorated_and_no_chrome(app):
    _reset_chrome(app)
    app._undecorated = True
    app._ensure_default_titlebar()
    assert _has_controls(app)


def test_no_titlebar_when_decorated(app):
    _reset_chrome(app)
    app._undecorated = False
    app._ensure_default_titlebar()
    assert not _has_controls(app)
    app._undecorated = True  # restore module default


@_skip_mac
def test_skips_when_author_added_own_toolbar(app):
    # The author owns the chrome — no auto bar is layered on top.
    _reset_chrome(app)
    app._undecorated = True
    app.add_toolbar()  # author chrome, no window controls
    app._ensure_default_titlebar()
    assert not _has_controls(app)


@_skip_mac
def test_idempotent(app):
    _reset_chrome(app)
    app._undecorated = True
    app._ensure_default_titlebar()
    n = len(app._chrome_toolbars)
    app._ensure_default_titlebar()  # a second show/run is a no-op
    assert len(app._chrome_toolbars) == n


@_skip_mac
def test_window_default_injects_and_borders(app):
    import bootstack as bs

    win = bs.Window(title="w", undecorated=True, parent=app)
    try:
        win._ensure_default_titlebar()
        assert _has_controls(win)
        assert win._region_root is not win._tk_toplevel  # bordered
    finally:
        try:
            win._tk_toplevel.destroy()
        except Exception:
            pass


@_skip_mac
def test_window_controls_false_is_chromeless(app):
    import bootstack as bs

    # window_controls=False => fully chromeless: no title bar AND no border.
    win = bs.Window(title="w2", undecorated=True, window_controls=False, parent=app)
    try:
        win._ensure_default_titlebar()
        assert not _has_controls(win)
        assert win._region_root is win._tk_toplevel  # no border wrapper
    finally:
        try:
            win._tk_toplevel.destroy()
        except Exception:
            pass