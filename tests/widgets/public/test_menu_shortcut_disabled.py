"""A disabled menu item's shortcut does not run its on_click (#556).

Isolated: it delivers a real key event, which the shared-root suite must not.
"""

from __future__ import annotations

import pytest

import bootstack as bs
from bootstack.shortcuts import get_shortcuts

pytestmark = pytest.mark.isolated


def _press(root, pattern):
    binding = next(s.binding for s in get_shortcuts().all().values() if s.pattern == pattern)
    root.focus_force()
    root.update()
    root.event_generate(binding, when="tail")
    root.update()


def test_disabled_item_shortcut_does_not_fire():
    ran = []
    with bs.AppShell(title="Shortcut", size=(500, 300)) as shell:
        with shell.add_toolbar() as bar:
            with bar.add_menu("File") as menu:
                menu.add_action("Load", shortcut="Mod+L", disabled=True,
                                on_click=lambda: ran.append("load"))
                menu.add_action("Keep", shortcut="Mod+K",
                                on_click=lambda: ran.append("keep"))
        with shell.page_nav() as nav:
            with nav.add_page("a", text="A"):
                bs.Label("a")
    root = shell.tk
    try:
        _press(root, "Mod+K")
        assert ran == ["keep"]  # the same key path reaches an enabled item

        ran.clear()
        _press(root, "Mod+L")
        assert ran == []
    finally:
        root.destroy()
