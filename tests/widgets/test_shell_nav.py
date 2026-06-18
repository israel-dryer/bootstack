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
        shell._workspace_select(shell.current_workspace, "home")
        assert shell.current_page == "home"
        assert shell.pages.current()[0] == "home"

        # Unknown page raises.
        import pytest
        with pytest.raises(KeyError):
            shell.navigate("nope")
        with pytest.raises(ValueError):
            shell.add_page("home")             # duplicate

        # Static nav extras: headers, separators, footer pages.
        shell.add_header("Documents")
        shell.add_divider()
        shell.add_page("files", text="Files", icon="folder")
        shell.add_footer_page("settings", text="Settings", icon="gear")
        assert "files" in shell.nav.item_keys()
        assert "settings" in shell.nav.item_keys()
        shell.navigate("settings")             # footer item is navigable
        assert shell.current_page == "settings"
        assert shell.pages.current()[0] == "settings"

        # detail() is rejected on a static (non-data-bound) provider.
        with pytest.raises(RuntimeError):
            shell.detail(lambda record: None)
        # add_page already claimed a static provider -> list_nav is rejected.
        with pytest.raises(RuntimeError):
            shell.list_nav(source=object())
    finally:
        shell.destroy()


def test_static_provider_satisfies_protocol():
    from bootstack.widgets._impl.composites.shell import NavProvider, StaticProvider

    provider = StaticProvider()
    assert isinstance(provider, NavProvider)   # runtime-checkable Protocol
    assert provider.supports_compact is True
