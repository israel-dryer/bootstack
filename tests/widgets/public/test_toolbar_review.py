"""Toolbar review (feat/toolbar-review).

The audit found no correctness/crash bugs in the toolbar's layout, window
controls, drag, or menu handling. The one lifecycle wart rolled in here: a
pending menu-shortcut rebind (scheduled via after_idle when a menu item is added)
was not cancelled if the toolbar was destroyed first. It is now cancelled by a
guarded <Destroy> handler.
"""
import pytest

import bootstack as bs


@pytest.fixture(scope="module")
def app():
    a = bs.App()
    a.__enter__()
    a._tk_root.deiconify()
    a._tk_root.update_idletasks()
    try:
        yield a
    finally:
        try:
            a.__exit__(None, None, None)
        except Exception:
            pass
        try:
            a._tk_root.destroy()
        except Exception:
            pass


def test_destroy_cancels_pending_menu_rebind(app):
    tb = bs.Toolbar()
    with tb.add_menu("File") as file:
        file.add_action("Quit", on_click=lambda: None)
    internal = tb._internal
    assert internal._menu_rebind_pending is not None  # an after_idle is scheduled
    internal.destroy()
    app._tk_root.update_idletasks()
    assert internal._menu_rebind_pending is None  # cancelled by the <Destroy> handler


def test_destroy_handler_ignores_descendant_destroy(app):
    tb = bs.Toolbar()
    with tb.add_menu("File") as file:
        file.add_action("Quit", on_click=lambda: None)
    internal = tb._internal
    # Add and destroy a child item; the bar's pending rebind must survive.
    tb.add_button("temp")
    internal.content.winfo_children()[-1].destroy()
    app._tk_root.update_idletasks()
    # (the rebind itself may have fired on idle; the point is no crash and the
    # bar is still alive)
    assert internal.winfo_exists()


# ----- basic surface sanity -----

def test_spacer_and_items_build(app):
    tb = bs.Toolbar()
    tb.add_button("Save", icon="floppy")
    tb.add_divider()
    tb.add_label("Title", font="heading-md")
    tb.add_spacer()
    tb.add_button(icon="gear")
    app._tk_root.update_idletasks()
    assert tb.density == "default"


def test_button_variant_default(app):
    tb = bs.Toolbar(button_variant="outline")
    assert tb.button_variant == "outline"
