"""A shell sidebar hidden across a theme change repaints when shown (#511).

The theme walk skips widgets that are not viewable, so a collapsed sidebar missed
the change; re-showing it must repaint it. The observable is the nav pane's
canvas, which paints its own background rather than following the ttk style.
"""

from __future__ import annotations

import pytest

import bootstack as bs

pytestmark = pytest.mark.isolated


def _pump(root):
    for _ in range(6):
        root.update()


def test_sidebar_hidden_across_a_theme_change_repaints_when_shown():
    bs.set_theme("bootstrap-light")
    shell = bs.Workbench(title="511", size=(730, 550))
    with shell:
        with shell.add_workspace("settings", text="Settings", icon="gear") as ws:
            with ws.page_nav() as nav:
                with nav.add_page("general", text="General", icon="sliders"):
                    bs.Label("Settings")
    root = shell._internal
    try:
        root.deiconify()
        _pump(root)
        # The walk skips an unmapped tree, so an unmapped shell would pass for
        # the wrong reason.
        assert root._sidebar.winfo_viewable()
        panes = [w for w in _subtree(root._sidebar) if _paints(w) and w.winfo_viewable()]
        assert len(panes) == 1
        pane = panes[0]
        light = pane.cget("background")

        shell.hide_sidebar()
        _pump(root)
        assert not pane.winfo_viewable()
        bs.set_theme("bootstrap-dark")
        _pump(root)
        shell.show_sidebar()
        _pump(root)

        assert pane.cget("background") != light
    finally:
        root.destroy()


def _subtree(widget):
    out, stack = [], [widget]
    while stack:
        cur = stack.pop()
        out.append(cur)
        stack.extend(cur.winfo_children())
    return out


def _paints(widget):
    try:
        widget.cget("background")
    except Exception:
        return False
    return True
