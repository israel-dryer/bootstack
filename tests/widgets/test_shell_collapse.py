"""Step 7 — sidebar collapse mechanics (single-tier static). One App/process.

Verifies the hidden/compact/expanded axis wired to the view: toggle/show/hide
visibility, `compact` rendering the static sidebar icon-only at the rail width
(gated to the standalone case), the `sidebar_mode` property, and Ctrl-B toggling.
"""

from __future__ import annotations

from bootstack.widgets._impl.composites.shell import Shell


def test_sidebar_collapse_single_tier():
    shell = Shell(title="Collapse", size=(800, 540))
    try:
        shell.add_page("home", text="Home", icon="house")
        shell.add_header("Docs")
        shell.add_page("files", text="Files", icon="folder")

        nav = shell.nav
        # Starts expanded + visible.
        assert shell.sidebar_mode == "expanded"
        assert shell.sidebar_visible is True
        assert nav.compact is False

        # Hamburger/toggle hides; show restores the prior non-hidden mode.
        shell.toggle_sidebar()
        assert shell.sidebar_visible is False
        assert shell.sidebar_mode == "hidden"
        shell.show_sidebar()
        assert shell.sidebar_visible is True
        assert shell.sidebar_mode == "expanded"

        # Compact (static + standalone, no rail) -> icon-only at the rail width.
        shell.sidebar_mode = "compact"
        assert shell.sidebar_visible is True
        assert nav.compact is True
        shell.update_idletasks()
        assert int(shell.sidebar.cget("width")) == shell._rail_width

        # Expanded -> labels return, width restored to the expanded token.
        shell.sidebar_mode = "expanded"
        assert nav.compact is False
        shell.update_idletasks()
        assert int(shell.sidebar.cget("width")) == shell._sidebar_width

        # The explicit verbs are pure visibility.
        shell.hide_sidebar()
        assert shell.sidebar_visible is False
        shell.show_sidebar()
        assert shell.sidebar_visible is True

        # Ctrl-B on a standalone static sidebar collapses to/from compact (it is
        # the only nav, so the shortcut never fully hides it).
        shell.sidebar_mode = "expanded"
        shell._on_toggle_shortcut()
        assert shell.sidebar_mode == "compact"
        assert nav.compact is True
        shell._on_toggle_shortcut()
        assert shell.sidebar_mode == "expanded"
        assert nav.compact is False

        # The standalone static workspace supports compaction.
        assert shell.workspace.supports_compact is True
        assert shell._can_compact_active() is True
    finally:
        shell.destroy()


def test_data_bound_providers_not_compactable():
    from bootstack.widgets._impl.composites.shell import (
        ListNavProvider,
        TreeNavProvider,
    )

    # A label-less data list / icon-only hierarchy is meaningless: hidden-or-shown.
    assert ListNavProvider.supports_compact is False
    assert TreeNavProvider.supports_compact is False
