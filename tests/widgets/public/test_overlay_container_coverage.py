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


def test_propagate_skips_nested_toplevels(app):
    import bootstack as bs
    from bootstack._runtime.utility import propagate_target_bindings

    # A ContextMenu parented to the card creates its own Toplevel under it; the
    # walk must not tag the popup's own widgets.
    card, _label = _build_card_with_children(bs)
    menu = bs.ContextMenu(target=card, trigger="manual")
    menu.add_item("Edit")
    propagate_target_bindings(card.tk)

    tag = str(card.tk)
    popup = menu._internal._impl._toplevel
    frame = popup.winfo_children()[0]
    assert tag not in frame.bindtags()
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
