"""`nav_variant='solid'` — the standalone primary nav's filled-accent selection.

`solid` fills the selected nav item with the accent (+ on-accent text) for a
higher-emphasis look than the default `'ghost'` wash. It is the **standalone**
(no-rail, single-tier `add_page`) nav's treatment ONLY — a named workspace's nav
sits under the rail as quiet rows and always uses the wash, regardless of
`nav_variant`. With no accent, `solid` falls back to the neutral wash.

`nav_variant` is the public AppShell kwarg; it maps to the internal selection
chain (`nav_variant` is taken internally for the pill/quiet tier).

One App/process (an AppShell owns its own root window).
"""

from __future__ import annotations

import bootstack as bs
from bootstack.style.builders.sidenav import _selection_colors
from bootstack.style.style_builder_ttk import StyleBuilderTtk


def test_solid_selection_colors_differ_from_ghost():
    """At the builder level, solid is a filled accent; ghost is a subtle wash."""
    app = bs.App(title="Solid")
    app.__enter__()
    try:
        bs.Label("hi")
        app._tk_root.update_idletasks()
        b = StyleBuilderTtk()
        opts = {"surface": "raised"}
        ghost_bg, ghost_fg = _selection_colors(b, "primary", {**opts, "selection_style": "ghost"})
        solid_bg, solid_fg = _selection_colors(b, "primary", {**opts, "selection_style": "solid"})
        # Solid fills with the accent itself; ghost is a tinted wash off the surface.
        assert solid_bg.lower() == b.color("primary").lower()
        assert solid_bg.lower() != ghost_bg.lower()
        # Solid uses on-accent (white) text; ghost keeps full-strength surface text.
        assert solid_fg.lower() != ghost_fg.lower()
        # No accent -> solid falls back to the neutral wash (no filled accent).
        none_bg, _ = _selection_colors(b, None, {**opts, "selection_style": "solid"})
        assert none_bg.lower() != b.color("primary").lower()
    finally:
        app.__exit__(None, None, None)


def test_solid_applies_to_standalone_nav():
    """add_page (no rail) -> nav-pill -> the item carries the solid selection."""
    shell = bs.AppShell(title="Standalone", size=(800, 540),
                        nav_accent="primary", nav_variant="solid")
    shell.__enter__()
    try:
        with shell.add_page("home", text="Home", icon="house"):
            bs.Label("hi")
        shell.navigate("home")
        shell._internal.update_idletasks()
        nav = shell._internal.nav
        assert nav._variant == "nav-pill"
        assert nav._selection == "solid"
    finally:
        shell.__exit__(None, None, None)


def test_solid_does_not_leak_to_workspace_nav():
    """A named workspace's under-rail nav stays ghost even with nav_variant='solid'."""
    shell = bs.AppShell(title="Workspace", size=(800, 540),
                        nav_accent="primary", nav_variant="solid")
    shell.__enter__()
    try:
        ws = shell.add_workspace("a", text="A", icon="house")
        with ws.add_page("p1", text="P1", icon="file"):
            bs.Label("p")
        shell._internal.update_idletasks()
        nav = shell._internal.nav
        assert nav._variant == "nav-quiet"
        # The solid request does NOT reach the under-rail workspace nav.
        assert nav._selection == "ghost"
    finally:
        shell.__exit__(None, None, None)