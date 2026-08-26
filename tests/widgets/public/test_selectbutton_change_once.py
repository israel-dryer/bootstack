"""`SelectButton` announces a selection exactly once (#476).

`OptionMenu._bind_change_event` subscribes a closure to the internal's
`textsignal` that emits `<<Change>>`, and guards against double-binding by
cancelling `self._bind_id` first. It was called twice per construction while
only one caller stored the return, so the guard had nothing to cancel and two
live subscriptions each emitted their own event: every selection reached an
`on_change` handler twice.
"""
import pytest

import bootstack as bs
from bootstack.widgets._impl.primitives.optionmenu import OptionMenu


DECOUPLED = [("One", "1"), ("Two", "2"), ("Three", "3")]


# --------------------------------------------------------------------------
# The behavior — public paths
# --------------------------------------------------------------------------

def test_a_selection_fires_change_exactly_once(app):
    """The headline: one selection, one announcement."""
    sb = bs.SelectButton(list(DECOUPLED), value="1")
    seen: list = []
    sb.on_change(lambda e: seen.append(e.value))

    sb.value = "2"
    app.tk.update()

    assert seen == ["2"]


def test_plain_string_options_fire_change_exactly_once(app):
    """The other option shape reaches the same subscription."""
    sb = bs.SelectButton(["a", "b", "c"], value="a")
    seen: list = []
    sb.on_change(lambda e: seen.append(e.value))

    sb.value = "b"
    app.tk.update()

    assert seen == ["b"]


def test_repeated_selections_do_not_accumulate(app):
    """Three selections, three events — not six, and not a growing multiple.

    Guards the failure a rebind would introduce: one that re-adds a subscriber
    rather than replacing it would climb with each pass through the rebind
    path, which a single-selection test cannot see.
    """
    sb = bs.SelectButton(list(DECOUPLED), value="1")
    seen: list = []
    sb.on_change(lambda e: seen.append(e.value))

    for v in ("2", "3", "1"):
        sb.value = v
        app.tk.update()

    assert seen == ["2", "3", "1"]


def test_reassigning_options_still_fires_change_once(app):
    """`options=` rebuilds the menu; the rebuild must not add a subscriber."""
    sb = bs.SelectButton(list(DECOUPLED), value="1")
    seen: list = []
    sb.on_change(lambda e: seen.append(e.value))

    sb.options = [("Four", "4"), ("Five", "5")]
    app.tk.update()
    seen.clear()

    sb.value = "4"
    app.tk.update()

    assert seen == ["4"]


# --------------------------------------------------------------------------
# The invariant — structural, and deliberately not a public path
# --------------------------------------------------------------------------

def test_exactly_one_change_subscription_after_construction(app):
    """Assert the subscription count, not just the emission count.

    Breaking the "test public paths" rule on purpose. The behavioral tests
    above pass for any arrangement that happens to emit once, so they would go
    green again the moment some future path emitted once by luck. The real
    invariant is that exactly one subscription exists, and this is the
    assertion that fails deterministically the first time a call path forgets
    to record its handle.
    """
    sb = bs.SelectButton(list(DECOUPLED), value="1")

    assert len(sb._internal._textsignal._subscribers) == 1


def test_rebinding_the_textsignal_replaces_the_subscription(app):
    """The path that caused #476, driven directly.

    `configure(textsignal=…)` re-enters `_bind_change_event` without storing
    its result, which is where the untracked subscription came from. It is
    unreachable from public API since #472 rejects the keyword at the wrapper,
    so this constructs the internal rather than a `bs.SelectButton`.
    """
    menu = OptionMenu(app.tk, options=list(DECOUPLED), value="1")
    previous = menu._textsignal
    assert len(previous._subscribers) == 1

    menu.configure(textsignal=bs.Signal("Two"))

    # Assert on the signal being REPLACED, not the new one. A count of 1 on the
    # new signal reads the same on a broken build, because the discarded
    # subscription stayed behind on the old one: 50 orphans across 50 rebinds
    # before the fix, 0 after.
    assert len(previous._subscribers) == 0
    assert len(menu._textsignal._subscribers) == 1
