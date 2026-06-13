"""Smoke test for the two-tier rail + the VS Code gesture (step 6).

Verifies: add_workspace reveals the rail, each workspace owns its own provider,
the rail switches workspaces (with per-workspace page memory), and the gesture
(active icon hides the sidebar, different icon switches + shows). One App/process.
"""

from __future__ import annotations

import bootstack as bs
from bootstack.widgets._impl.composites.shell import Shell


def test_two_tier_rail_and_gesture():
    shell = Shell(title="TwoTier", size=(900, 600))
    try:
        # Workspace 1 — static pages.
        ws1 = shell.add_workspace("acquire", text="Acquire", icon="cpu")
        ws1.add_page("sensors", text="Sensors", icon="thermometer-half")
        ws1.add_page("ports", text="Ports", icon="usb-symbol")

        # One workspace: rail still hidden.
        assert shell.rail_visible is False
        assert shell.current_workspace == "acquire"
        assert shell.current_page == "sensors"     # first page auto-selected

        # Workspace 2 — different provider; rail now appears.
        ws2 = shell.add_workspace("library", text="Library", icon="folder")
        ws2.tree_nav(nodes=[{"label": "README.md", "icon": "filetype-md"}])

        @ws2.detail
        def render(record):
            bs.Label(record["text"])

        assert shell.rail_visible is True
        assert shell.model.rail_visible is True
        # The rail REGION must actually be packed into the body (guards the
        # _rail attribute-collision orphan bug).
        shell.update_idletasks()
        assert shell.rail.winfo_manager() == "pack"
        assert set(shell._railnav.keys()) == {"acquire", "library"}

        # Switch within ws1, then to ws2, then back -> per-workspace page memory.
        shell.navigate("acquire", "ports")
        assert shell.current_workspace == "acquire"
        assert shell.current_page == "ports"

        # Rail gesture: click a DIFFERENT workspace -> switch + show.
        shell._rail_select("library")
        assert shell.current_workspace == "library"
        assert shell.sidebar_visible is True
        assert shell._railnav.selected == "library"

        # Back to ws1 remembers "ports".
        shell._rail_select("acquire")
        assert shell.current_workspace == "acquire"
        assert shell.current_page == "ports"

        # Rail gesture: click the ACTIVE workspace -> hide the sidebar.
        shell._rail_select("acquire")
        assert shell.sidebar_visible is False
        assert shell.current_workspace == "acquire"   # still active, just hidden

        # Click it again -> show.
        shell._rail_select("acquire")
        assert shell.sidebar_visible is True

        # Compact is gated OFF under a rail: a tier-2 sidebar stays expanded even
        # when the mode is compact (an icon panel beside the icon rail is noise).
        assert ws1.supports_compact is True            # provider can, in principle
        shell.sidebar_mode = "compact"
        assert shell.sidebar_visible is True
        assert ws1.provider.nav.compact is False       # but not icon-compacted here
        shell.sidebar_mode = "expanded"

        # Under a rail, Ctrl-B hides/shows (the rail stays as nav) — no compact.
        assert shell._can_compact_active() is False
        shell._on_toggle_shortcut()
        assert shell.sidebar_visible is False
        shell._on_toggle_shortcut()
        assert shell.sidebar_visible is True

        # Mixing shell-level pages with workspaces is rejected.
        import pytest
        with pytest.raises(RuntimeError):
            shell.add_page("loose")
    finally:
        shell.destroy()
