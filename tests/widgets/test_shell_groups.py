"""Grouped-static sidebar — `add_header` chunks a flat nav list with plain labels.

There is no built-in collapsible accordion (dropped — a section that hides/reveals
a sub-list is a content concern; compose `bs.Accordion` in a custom `panel()` if
you need one). A header is a quiet, non-interactive label: it groups the items
that follow it and hides while the sidebar is compacted. One App/process.
"""

from __future__ import annotations

import bootstack as bs
from bootstack.widgets._impl.composites.shell import Shell
from bootstack.widgets._impl.composites.sidenav.header import SideNavHeader


def test_grouped_static_sidebar():
    shell = Shell(title="Grouped", size=(800, 540))
    try:
        shell.add_page("home", text="Home", icon="house")
        header = shell.add_header("Documents")
        shell.add_page("files", text="Files", icon="folder")
        shell.add_page("photos", text="Photos", icon="image")
        shell.add_divider()
        shell.add_page("trash", text="Trash", icon="trash")

        nav = shell.nav
        shell.update_idletasks()

        # The header is a plain, non-interactive label — not a collapsible control.
        assert isinstance(header, SideNavHeader)
        assert header.text == "Documents"
        assert not hasattr(header, "collapsed")
        assert not hasattr(header, "collapsible")
        assert not hasattr(header, "set_collapsed")

        # First page auto-selects; every item is mapped (a header groups items but
        # never hides them — the run does not collapse).
        assert shell.current_page == "home"
        for key in ("home", "files", "photos", "trash"):
            assert nav._items[key].winfo_manager() == "pack"
        assert header.winfo_manager() == "pack"

        # Navigation across grouped items works.
        shell.navigate("photos")
        shell.update_idletasks()
        assert shell.current_page == "photos"
        assert nav.selected == "photos"

        # Compaction hides the header + separator (icon-only strip), items stay.
        shell.sidebar_mode = "compact"
        shell.update_idletasks()
        assert nav.compact is True
        assert header.winfo_manager() == ""
        assert nav._items["files"].winfo_manager() == "pack"

        # Expanding restores the header.
        shell.sidebar_mode = "expanded"
        shell.update_idletasks()
        assert header.winfo_manager() == "pack"
    finally:
        shell.destroy()
