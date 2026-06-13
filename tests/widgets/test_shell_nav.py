"""Smoke test for single-tier shell navigation (step 3).

Verifies the NavModel <-> region wiring: add_page registers a page + nav item,
the first page auto-selects, selecting drives the content swap, and navigate()
plus the <<PageChange>> re-emit work. One App per process.
"""

from __future__ import annotations

from bootstack.widgets._impl.composites.shell import Shell


def test_single_tier_navigation_cascade():
    shell = Shell(title="Nav")
    try:
        # First page auto-selects.
        shell.add_page("home", text="Home", icon="house")
        assert shell.current_page == "home"
        assert shell.model.active_page() == "home"
        assert shell.nav.selected == "home"
        assert shell.pages.current()[0] == "home"

        # Second page does not steal selection.
        shell.add_page("inbox", text="Inbox", icon="inbox")
        assert shell.current_page == "home"

        # Rail stays hidden in single-tier (one implicit workspace).
        assert shell.rail_visible is False
        assert shell.model.rail_visible is False

        # navigate() swaps the active page + nav selection + content.
        changes: list = []
        shell.bind("<<PageChange>>", lambda e: changes.append(e), add="+")
        shell.navigate("inbox")
        assert shell.current_page == "inbox"
        assert shell.nav.selected == "inbox"
        assert shell.pages.current()[0] == "inbox"
        shell.update()                         # flush queued (when="tail") events
        assert len(changes) >= 1               # <<PageChange>> re-emitted on the shell

        # Selecting via the nav panel routes through the model.
        shell._on_nav_select("home")
        assert shell.current_page == "home"
        assert shell.pages.current()[0] == "home"

        # Unknown page raises.
        import pytest
        with pytest.raises(KeyError):
            shell.navigate("nope")
        with pytest.raises(ValueError):
            shell.add_page("home")             # duplicate
    finally:
        shell.destroy()
