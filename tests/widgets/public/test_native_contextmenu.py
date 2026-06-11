"""Structural tests for the de-iconed native (macOS) ContextMenu backend.

`_NativeContextMenu` only runs on Aqua via `ContextMenu`'s dispatch, but it
builds a plain `tk.Menu`, so its structure is verifiable on any OS. These
guard the MenuManager retirement: the backend no longer tracks icons and an
`icon=` argument is accepted but ignored. One module-scoped App.
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


def test_builds_with_icon_arg_ignored_no_crash(app):
    cm = _NativeContextMenu(master=app._tk_root)
    # icon= is accepted for cross-backend parity but not rendered.
    cm.add_command(text="Open", icon="folder2-open", shortcut="Mod+O", command=lambda: None)
    cm.add_separator()
    cm.add_command(text="Quit", command=lambda: None)
    keys = cm.keys()
    assert len(keys) == 3
    # No image option was set on the icon'd entry.
    assert cm._menu.entrycget(0, "image") in ("", None)
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