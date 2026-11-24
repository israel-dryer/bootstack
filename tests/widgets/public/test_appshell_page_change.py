"""AppShell.on_page_change hears only the shell's own navigation (#555).

The shell is the root window, and a root binding also receives every
descendant's events — so a PageStack inside a page reached the shell handler,
and each navigate() fired it twice (once from the shell's own content stack).
"""

from __future__ import annotations

import pytest

import bootstack as bs

pytestmark = pytest.mark.isolated


def test_page_change_fires_once_per_shell_navigation_only():
    with bs.AppShell(title="PageChange", size=(600, 400)) as shell:
        heard = []
        shell.on_page_change(heard.append)
        with shell.page_nav() as nav:
            with nav.add_page("viewer", text="Viewer"):
                inner = bs.PageStack()
                with inner.add("p1"):
                    bs.Label("p1")
                with inner.add("p2"):
                    bs.Label("p2")
            with nav.add_page("log", text="Log"):
                bs.Label("log")
    root = shell._internal
    try:
        inner_heard = []
        inner.on_page_change(inner_heard.append)
        root.update()
        heard.clear()

        shell.navigate("log")
        root.update()
        assert [(e.page, e.prev_page) for e in heard] == [("log", "viewer")]

        heard.clear()
        inner.navigate("p2")
        root.update()
        assert [e.page for e in inner_heard] == ["p2"]  # the inner event was delivered
        assert heard == []
    finally:
        root.destroy()
