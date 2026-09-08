"""A path picked from the dialog reaches `on_change` (#509).

`PathEntry._show_file_chooser` hand-built a `ChangeEvent` and generated it on the
**outer** `PathEntry` frame, while `PathField` routes `on_change` to the **inner
entry** through `_INNER_ENTRY_SEQUENCES` (`textfield.py:19-29`). Virtual events do
not reach a child, so the event landed on a widget nothing was bound to: picking a
file set the value and announced nothing at all.

The emit site was wrong, not the routing. `_show_file_chooser` now sets the value
and re-enters the entry's own `_check_if_changed()`, which emits on the right
widget with a correct `prev_value` for free — the standing preference over
re-emitting an event by hand.

⚠ THE TYPED CONTROL IS NOT DECORATION. A handler that was never wired produces
zero events for the dialog too, so the headline assertion alone passes just as
well for a broken subscription as for a broken emit. The control is what tells the
two apart, and it is why the original defect was diagnosable at all.

⚠ `open_multiple` is deliberately not covered here. Its return contract (a tuple,
empty `()`) is decided but unshipped — see #416 on `0.5.0` — and pinning today's
joined-display-text behavior would fight that change rather than guard this one.
"""
from __future__ import annotations

import pytest

import bootstack as bs
from bootstack.widgets._impl.composites import pathentry as pathentry_mod


PICKED = "/tmp/chosen.txt"
PICKED_AGAIN = "/tmp/second.txt"
SEEDED = "/tmp/seeded.txt"


@pytest.fixture
def pick(monkeypatch):
    """Replace the native 'open' dialog with one returning a path we choose.

    `monkeypatch.setitem` restores the real `filedialog.askopenfilename` on
    teardown; a bare assignment into the module dict would leak a stub into every
    later test in the session, which the shared root makes especially cheap to do
    and expensive to find.
    """
    def _set(path):
        monkeypatch.setitem(pathentry_mod._MODE_TO_DIALOG, "open", lambda **kw: path)

    return _set


def _pump(app, times: int = 4) -> None:
    for _ in range(times):
        app.tk.update()
        app.tk.update_idletasks()


def _browse(app, pf) -> None:
    """Click the browse button the way a user does."""
    pf._internal.dialog_button.invoke()
    _pump(app)


def _type_and_blur(app, pf, text: str) -> None:
    """Drive the other door into the same commit path.

    Focus is generated as real `<FocusIn>`/`<FocusOut>` events rather than driven
    with `focus_set`: the shared root is withdrawn, and Tk's `focus_set` is a
    silent no-op on an unmapped widget.
    """
    entry = pf._entry_widget()
    entry.event_generate("<FocusIn>")
    _pump(app)
    entry.delete(0, "end")
    entry.insert("end", text)
    _pump(app)
    entry.event_generate("<FocusOut>")
    _pump(app)


def test_a_path_picked_from_the_dialog_announces_one_change(app, pick):
    """The headline: the reporter's scenario, driven through public API."""
    pick(PICKED)
    pf = bs.PathField(value=SEEDED)
    seen: list = []
    pf.on_change(seen.append)
    _pump(app)

    _browse(app, pf)

    assert len(seen) == 1, "the dialog pick announced %d change(s)" % len(seen)
    assert seen[0].value == PICKED
    assert seen[0].prev_value == SEEDED, (
        "prev_value did not carry the path the field held before: %r"
        % (seen[0].prev_value,)
    )
    assert pf.value == PICKED


def test_the_same_field_announces_a_typed_edit(app, pick):
    """The control: proves the handler is wired on this widget at all.

    Without this, the test above cannot distinguish "the emit reaches the
    subscriber" from "nothing is subscribed", and the second reads as a pass.
    """
    pick(PICKED)
    pf = bs.PathField(value=SEEDED)
    seen: list = []
    pf.on_change(seen.append)
    _pump(app)

    _type_and_blur(app, pf, PICKED_AGAIN)

    assert len(seen) == 1, "a typed edit announced %d change(s)" % len(seen)
    assert seen[0].value == PICKED_AGAIN
    assert seen[0].prev_value == SEEDED


def test_successive_picks_chain_their_priors(app, pick):
    """Each pick's prior is the previous pick's value.

    The deleted `_prev_value` bookkeeping was only ever updated on the dialog
    path, so it was already stale after any typed edit. Re-entering the entry's
    own routine means one piece of state tracks both doors — this is the
    assertion that fails if a second, dialog-only prior is reintroduced.
    """
    pick(PICKED)
    pf = bs.PathField(value=SEEDED)
    seen: list = []
    pf.on_change(seen.append)
    _pump(app)

    _browse(app, pf)
    pick(PICKED_AGAIN)
    _browse(app, pf)

    assert [e.value for e in seen] == [PICKED, PICKED_AGAIN]
    assert [e.prev_value for e in seen] == [SEEDED, PICKED], (
        "the priors did not chain across two picks: %r"
        % ([e.prev_value for e in seen],)
    )


def test_a_pick_that_repeats_the_current_path_is_not_a_change(app, pick):
    """Choosing the file the field already holds committed nothing."""
    pick(SEEDED)
    pf = bs.PathField(value=SEEDED)
    seen: list = []
    pf.on_change(seen.append)
    _pump(app)

    _browse(app, pf)

    assert seen == [], "re-picking the current path announced %d change(s)" % len(seen)
    assert pf.value == SEEDED


def test_a_cancelled_dialog_changes_nothing(app, pick):
    """A cancelled native dialog returns an empty string, not a path."""
    pick("")
    pf = bs.PathField(value=SEEDED)
    seen: list = []
    pf.on_change(seen.append)
    _pump(app)

    _browse(app, pf)

    assert seen == [], "a cancelled dialog announced %d change(s)" % len(seen)
    assert pf.value == SEEDED, "a cancelled dialog overwrote the value: %r" % (pf.value,)