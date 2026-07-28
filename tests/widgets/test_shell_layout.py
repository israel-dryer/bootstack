"""Structural smoke test for the shell region layout (Layer 1).

Asserts that regions construct and that show/hide toggles their geometry
management — no visual inspection. One `App` per process: a single test owns
the window and tears it down.
"""

from __future__ import annotations

from bootstack.widgets._impl.composites.shell import ShellLayout


def test_region_layout_construction_and_toggles():
    shell = ShellLayout(title="Smoke")
    try:
        # Regions exist.
        for name in ("toolbar_stack", "statusbar", "rail", "sidebar", "content", "dock"):
            assert getattr(shell, name) is not None

        # Guard: internal attributes must not shadow tkinter's `Misc._root()`
        # method (doing so breaks event dispatch in the mainloop).
        assert shell._root() is shell
        shell.update_idletasks()

        # Default visibility: content + sidebar shown; status/rail/dock hidden.
        # The toolbar_stack region is always packed (empty until add_toolbar).
        assert shell.content.winfo_manager() == "pack"
        assert shell.sidebar.winfo_manager() == "pack"
        assert shell.toolbar_stack.winfo_manager() == "pack"
        for hidden in (shell.statusbar, shell.rail, shell.dock):
            assert hidden.winfo_manager() == ""

        # Reflected in the visibility properties.
        assert shell.sidebar_visible is True
        assert shell.rail_visible is False
        assert shell.statusbar_visible is False
        assert shell.dock_visible is False

        # Toggle each slot on.
        shell.rail_visible = True
        shell.statusbar_visible = True
        shell.dock_visible = True
        assert shell.rail.winfo_manager() == "pack"
        assert shell.statusbar.winfo_manager() == "pack"
        assert shell.dock.winfo_manager() == "pack"

        # Hide the sidebar; content stays.
        shell.sidebar_visible = False
        assert shell.sidebar.winfo_manager() == ""
        assert shell.content.winfo_manager() == "pack"

        # Assigning the value it already holds is a no-op, not an error.
        shell.rail_visible = True
        assert shell.rail_visible is True

        # Width setters apply to the slot frames.
        shell.set_sidebar_width(300)
        assert int(shell.sidebar.cget("width")) == 300
        shell.set_rail_width(64)
        assert int(shell.rail.cget("width")) == 64
    finally:
        shell.destroy()
