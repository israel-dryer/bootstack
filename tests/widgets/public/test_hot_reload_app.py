"""GUI integration: in-process hot reload of a plain App.

Isolated — builds its own Tk root (one per process). Drives the real reloader
through its ``_handle`` entry point (the watcher's main-thread callback) so the
happy path, the error banner, and recovery are all exercised end to end.
"""
from __future__ import annotations

import runpy

import pytest

pytestmark = pytest.mark.isolated


_V1 = """\
import bootstack as bs
count = bs.Signal(0)
with bs.App(title='T') as app:
    with app.add_toolbar() as tb:
        tb.add_button('File')
    bs.Label('V1')
"""

_V2 = """\
import bootstack as bs
count = bs.Signal(0)
with bs.App(title='T') as app:
    with app.add_toolbar() as tb:
        tb.add_button('File')
    bs.Label('V2')
    bs.Label('EXTRA')
"""

_BAD = """\
import bootstack as bs
count = bs.Signal(0)
with bs.App(title='T') as app:
    bs.Label(undefined_name)
"""

_FIXED = """\
import bootstack as bs
count = bs.Signal(0)
with bs.App(title='T') as app:
    bs.Label('RECOVERED')
"""


def test_app_hot_reload(tmp_path, monkeypatch):
    monkeypatch.setenv("BOOTSTACK_DEV", "1")
    monkeypatch.setenv("BOOTSTACK_DEV_MODE", "inprocess")
    from bootstack.dev._reloader import _InProcessReloader

    appfile = tmp_path / "app.py"
    appfile.write_text(_V1, encoding="utf-8")
    ns = runpy.run_path(str(appfile), run_name="__main__")
    app = ns["app"]
    count = ns["count"]
    count.set(7)

    def labels():
        return [
            w.cget("text")
            for w in app._content_frame.winfo_children()
            if "text" in w.keys()
        ]

    # The real App must advertise in-process support (the bug that shipped).
    assert app._dev_supports_inprocess is True
    assert app._dev_body is not None and app._dev_body.is_capturable
    assert "V1" in labels()
    assert len(app._chrome_toolbars) == 1

    reloader = _InProcessReloader(app, app._dev_body)

    # 1) Happy reload: text changes, a widget is added, state + chrome intact.
    appfile.write_text(_V2, encoding="utf-8")
    reloader._handle({str(appfile)})
    assert "V2" in labels() and "EXTRA" in labels()
    assert count() == 7                    # module-level signal survives
    assert len(app._chrome_toolbars) == 1  # chrome rebuilt, not doubled
    assert reloader._error_banner is None

    # 2) Bad reload: an error banner renders and the process stays alive.
    appfile.write_text(_BAD, encoding="utf-8")
    reloader._handle({str(appfile)})
    assert reloader._error_banner is not None

    # 3) Recovery: the next valid save clears the banner and rebuilds.
    appfile.write_text(_FIXED, encoding="utf-8")
    reloader._handle({str(appfile)})
    assert reloader._error_banner is None
    assert "RECOVERED" in labels()

    app._internal.destroy()
