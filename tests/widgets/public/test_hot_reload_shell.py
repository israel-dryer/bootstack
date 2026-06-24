"""GUI integration: in-process hot reload of an AppShell.

Isolated — builds its own Tk root. Verifies that authored navigation rebuilds
on reload and that the selected route survives (even though the rebuilt body
calls ``navigate('home')``, the pre-reload page is restored).
"""
from __future__ import annotations

import runpy

import pytest

pytestmark = pytest.mark.isolated


_V1 = """\
import bootstack as bs
with bs.AppShell(title='S') as shell:
    with shell.add_toolbar() as tb:
        tb.add_button('File')
    with shell.page_nav() as nav:
        with nav.add_page('home', text='Home', icon='house'):
            bs.Label('HOME-V1')
        with nav.add_page('settings', text='Settings', icon='gear'):
            bs.Label('SETTINGS-V1')
    shell.navigate('home')
"""

_V2 = """\
import bootstack as bs
with bs.AppShell(title='S') as shell:
    with shell.add_toolbar() as tb:
        tb.add_button('File')
    with shell.page_nav() as nav:
        with nav.add_page('home', text='Home', icon='house'):
            bs.Label('HOME-V2')
        with nav.add_page('settings', text='Settings', icon='gear'):
            bs.Label('SETTINGS-V2')
        with nav.add_page('reports', text='Reports', icon='bar-chart'):
            bs.Label('REPORTS-NEW')
    shell.navigate('home')
"""


def test_shell_hot_reload(tmp_path, monkeypatch):
    monkeypatch.setenv("BOOTSTACK_DEV", "1")
    monkeypatch.setenv("BOOTSTACK_DEV_MODE", "inprocess")
    from bootstack.dev._reloader import _InProcessReloader

    appfile = tmp_path / "shell.py"
    appfile.write_text(_V1, encoding="utf-8")
    ns = runpy.run_path(str(appfile), run_name="__main__")
    shell = ns["shell"]
    shell.navigate("settings")  # move off the authored default
    shell.sidebar_mode = "compact"  # minimized sidebar must survive a reload

    def pages():
        ws = shell._internal._model.active_workspace
        return sorted(shell._internal._workspaces[ws].keys())

    def active():
        model = shell._internal._model
        return model.active_page(model.active_workspace)

    assert shell._dev_supports_inprocess is True
    assert shell._dev_body is not None and shell._dev_body.is_capturable
    assert pages() == ["home", "settings"]
    assert active() == "settings"
    assert len(shell._chrome_toolbars) == 1

    reloader = _InProcessReloader(shell, shell._dev_body)
    appfile.write_text(_V2, encoding="utf-8")
    reloader._handle({str(appfile)})

    assert pages() == ["home", "reports", "settings"]  # new page picked up
    assert active() == "settings"                       # route preserved
    assert shell._internal._model.sidebar_mode == "compact"  # minimized state kept
    assert len(shell._chrome_toolbars) == 1             # chrome not doubled
    assert reloader._error_banner is None

    shell._internal.destroy()
