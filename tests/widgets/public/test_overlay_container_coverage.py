"""ContextMenu/Tooltip cover a container target's children (issue #166).

Tk events don't bubble, so a gesture bound to a container never fires when the
pointer is over a child. `propagate_target_bindings` adds the container's own
bindtag to its descendants so the gesture/hover triggers anywhere inside it.

Structural only — asserts the child widgets carry the container's bindtag after
attach (no synthetic event delivery, which is flaky headless). One module-scoped
App (creating several Apps crashes Tk).
"""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.gui


def _build_card_with_children(bs):
    """Return (card, [child tk widgets]) — a Card holding a nested Label."""
    with bs.Card() as card:
        with bs.Column():
            label = bs.Label("Right-click me")
    card.tk.update_idletasks()
    return card, label


def test_context_menu_tag_reaches_container_children(app):
    import bootstack as bs
    from bootstack.widgets.contextmenu import _resolve_tk

    card, label = _build_card_with_children(bs)
    menu = bs.ContextMenu(target=card, trigger="right_click")
    menu.add_item("Edit")

    tag = str(_resolve_tk(card))
    assert tag in label.tk.bindtags()
    menu.destroy()


def test_tooltip_tag_reaches_container_children(app):
    import bootstack as bs

    card, label = _build_card_with_children(bs)
    tip = bs.Tooltip(card, "Container tip")

    # Tooltip resolves the target via `.tk`; that is the tag its hover bindings
    # are registered under, and it must reach the nested child.
    tag = str(card.tk)
    assert tag in label.tk.bindtags()
    tip.destroy()


def test_propagate_is_idempotent(app):
    import bootstack as bs
    from bootstack._runtime.utility import propagate_target_bindings

    card, label = _build_card_with_children(bs)
    target = card.tk
    propagate_target_bindings(target)
    propagate_target_bindings(target)

    tag = str(target)
    # The tag appears exactly once, not duplicated per call.
    assert label.tk.bindtags().count(tag) == 1


def _descendants(widget):
    """Every widget under `widget`, itself excluded."""
    for child in widget.winfo_children():
        yield child
        yield from _descendants(child)


def test_propagate_skips_nested_toplevels(app, menu_probe):
    import tkinter as tk

    import bootstack as bs
    from bootstack._runtime.utility import propagate_target_bindings

    # The walk tags the target's own descendants so a gesture fires anywhere
    # inside it, but must stop at a nested Toplevel -- a popup parented under
    # the target is not part of the target.
    card, label = _build_card_with_children(bs)
    menu = bs.ContextMenu(target=card, trigger="manual")
    menu.add_item("Edit")
    propagate_target_bindings(card.tk)

    tag = str(card.tk)

    # The walk actually ran. Without this the checks below pass on a walk that
    # did nothing at all.
    assert tag in label.tk.bindtags()

    # Nothing inside a nested Toplevel was tagged. On the themed backend that
    # Toplevel is the menu popup; on the native backend the menu is drawn by
    # the window server and parents no Toplevel here, so the loop finds none.
    nested = [w for w in _descendants(card.tk) if isinstance(w, tk.Toplevel)]
    for toplevel in nested:
        for widget in [toplevel, *_descendants(toplevel)]:
            assert tag not in widget.bindtags()

    popup = menu_probe.popup_toplevel(menu._internal._impl)
    if popup is not None:
        # Themed backend: the popup parents under the target, so it must be one
        # of the Toplevels checked above. Without this the loop could silently
        # find nothing and the test would assert only that the walk ran.
        assert popup in nested
    menu.destroy()


def test_child_own_pathtag_keeps_precedence(app):
    import bootstack as bs
    from bootstack._runtime.utility import propagate_target_bindings

    card, label = _build_card_with_children(bs)
    propagate_target_bindings(card.tk)

    tags = label.tk.bindtags()
    # The child's own path-name tag still runs before the injected container tag.
    assert tags[0] == str(label.tk)
    assert tags.index(str(label.tk)) < tags.index(str(card.tk))
