"""Step 8 — 1-level collapsible groups in the static provider. One App/process.

A collapsible header toggles the run of items that follow it (up to the next
header or separator). Compact flattens the group (items reappear as icons),
preserving and restoring the collapse state on expand.
"""

from __future__ import annotations

from bootstack.widgets._impl.composites.shell import Shell


def test_collapsible_group_single_tier():
    shell = Shell(title="Groups")
    try:
        shell.add_page("home", text="Home", icon="house")
        docs = shell.add_header("Documents", collapsible=True)
        shell.add_page("files", text="Files", icon="folder")
        shell.add_page("photos", text="Photos", icon="image")
        shell.add_separator()
        shell.add_page("trash", text="Trash", icon="trash")

        nav = shell.nav
        shell.update_idletasks()

        # Group starts expanded.
        assert docs.collapsible is True
        assert docs.collapsed is False
        assert nav._items["files"].winfo_manager() == "pack"

        # Collapse hides the run (files, photos) only.
        nav._toggle_group(docs)
        shell.update_idletasks()
        assert docs.collapsed is True
        assert nav._items["files"].winfo_manager() == ""
        assert nav._items["photos"].winfo_manager() == ""
        assert nav._items["home"].winfo_manager() == "pack"   # before the group
        assert nav._items["trash"].winfo_manager() == "pack"  # after the separator

        # Expand restores.
        nav._toggle_group(docs)
        shell.update_idletasks()
        assert nav._items["files"].winfo_manager() == "pack"

        # Compact flattens: collapse, then compact -> grouped items reappear as
        # icons and the header hides.
        nav._toggle_group(docs)                # collapse again
        shell.sidebar_mode = "compact"
        shell.update_idletasks()
        assert nav.compact is True
        assert nav._items["files"].winfo_manager() == "pack"
        assert docs.winfo_manager() == ""      # header hidden in compact

        # Expand -> collapse state is preserved (files hidden again).
        shell.sidebar_mode = "expanded"
        shell.update_idletasks()
        assert docs.collapsed is True
        assert nav._items["files"].winfo_manager() == ""

        # A non-collapsible header is a plain label (no chevron, no toggle).
        plain = shell.add_header("Other")
        assert plain.collapsible is False

        # expand_all / collapse_all drive every collapsible group at once.
        lib = shell.add_header("Library", collapsible=True)
        shell.add_page("books", text="Books", icon="book")
        shell.expand_all()
        shell.update_idletasks()
        assert docs.collapsed is False and lib.collapsed is False
        assert nav._items["files"].winfo_manager() == "pack"

        shell.collapse_all()
        shell.update_idletasks()
        assert docs.collapsed is True and lib.collapsed is True
        assert nav._items["files"].winfo_manager() == ""
        assert nav._items["books"].winfo_manager() == ""
        # Non-grouped items are unaffected.
        assert nav._items["home"].winfo_manager() == "pack"
    finally:
        shell.destroy()
