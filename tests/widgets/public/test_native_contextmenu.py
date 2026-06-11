"""Structural tests for the native (macOS) ContextMenu backend.

`_NativeContextMenu` only runs on Aqua via `ContextMenu`'s dispatch, but it
builds a plain `tk.Menu`, so its structure is verifiable on any OS. These
guard the MenuManager retirement (the standalone MenuManager + create_menu are
gone) while confirming the backend still renders icons (context menus are app
content — icons kept) with its own slim icon/recolor path. One module-scoped App.
"""
from __future__ import annotations

import pytest

from bootstack.widgets._impl.composites.contextmenu import _NativeContextMenu

pytestmark = pytest.mark.gui


@pytest.fixture(scope="module")
def app():
    import bootstack as bs

    app = bs.App()
    app._tk_root.withdraw()
    try:
        yield app
    finally:
        try:
            app._tk_root.destroy()
        except Exception:
            pass


def test_backend_has_no_menu_manager(app):
    cm = _NativeContextMenu(master=app._tk_root)
    assert not hasattr(cm, "_mgr")
    cm.destroy()


def test_renders_icon_on_command(app):
    cm = _NativeContextMenu(master=app._tk_root)
    cm.add_command(text="Open", icon="folder2-open", shortcut="Mod+O", command=lambda: None)
    cm.add_separator()
    cm.add_command(text="Quit", command=lambda: None)
    assert len(cm.keys()) == 3
    # Context menus keep icons (app content): the icon'd entry has an image,
    # the plain one does not.
    assert cm._menu.entrycget(0, "image") not in ("", None)
    assert cm._menu.entrycget(2, "image") in ("", None)
    # And the PhotoImage is retained so Tk doesn't GC it.
    assert cm._icon_refs
    cm.destroy()


def test_accelerator_is_word_form(app):
    cm = _NativeContextMenu(master=app._tk_root)
    cm.add_command(text="Save", shortcut="Mod+S", command=lambda: None)
    acc = cm._menu.entrycget(0, "accelerator")
    # Word form so Tk-Aqua renders ⌘ AND the key (not a pre-symbolized glyph).
    assert acc == "Command+S"
    cm.destroy()


def test_label_translation_passthrough(app):
    cm = _NativeContextMenu(master=app._tk_root)
    cm.add_command(text="Plain Label", command=lambda: None)
    assert cm._menu.entrycget(0, "label") == "Plain Label"
    cm.destroy()


def test_rebuild_after_insert(app):
    cm = _NativeContextMenu(master=app._tk_root)
    cm.add_command(text="A", command=lambda: None)
    cm.add_command(text="B", command=lambda: None)
    cm.insert_item(0, "command", text="Z", command=lambda: None)  # triggers rebuild
    assert cm._menu.entrycget(0, "label") == "Z"
    cm.destroy()