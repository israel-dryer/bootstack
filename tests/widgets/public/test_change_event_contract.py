"""Every `ChangeEvent` emitter honors the payload's own contract (#509).

`ChangeEvent` documents itself as *"Fires when a field's value is committed (on
blur or Enter)"* with `prev_value` = *"The value before this change."* Three
widgets emitted it without ever filling `prev_value`, and two of them fired when
nothing had been committed: a `TextArea` announced a change on every blur, and a
`CodeEditor` announced one per keystroke plus a spurious one at construction,
making `on_change` a byte-for-byte duplicate of `on_input`.

The family rule, settled in #482: **`<<Change>>` means the committed value
differs from what it was at focus-in.** `_impl/_parts/textentry_part.py:149-211`
is the reference — snapshot on `<FocusIn>`, emit only on a difference, then
re-snapshot.

⚠ `SelectButton` is the deliberate exception and is asserted as such below. It
emits on a programmatic `w.value = x`, which the 2026-08-26 maintainer
disposition leaves alone ("keep in mind, do not fix"). Only its payload was
wrong, so only its payload is pinned here — the emission count belongs to
`test_selectbutton_change_once.py` and must not be re-litigated from this file.

⚠ THE EDITS DRIVE `text.insert`, NOT SYNTHESIZED KEYS, AND THAT IS MEASURED
RATHER THAN STYLISTIC. The shared root is withdrawn, so `focus_force` is a
silent no-op on an unmapped widget and a generated `<KeyPress>` never reaches the
Text's class bindings — the document simply stays empty and the test passes or
fails for reasons unrelated to the contract. `insert` rides the same
`WidgetRedirector` a keystroke does. The same reasoning is spelled out at
`test_textarea_signal_binding.py:355-362`; focus itself is driven as a real
`<FocusIn>`/`<FocusOut>` event for the same reason.
"""
from __future__ import annotations

import bootstack as bs


# Text and value deliberately differ. A `SelectButton` whose option text equals
# its value cannot tell value-space from text-space, which is exactly how the
# seeded `prev_value` came to be a display label while every later one was a
# value (#461/#476 is this same mismatch).
DECOUPLED = [("Small", "sm"), ("Medium", "md"), ("Large", "lg")]


def _pump(app, times: int = 4) -> None:
    """Drain the queue.

    `<<Changed>>` is queued `when="tail"`, so idle tasks alone do not deliver it
    — only a full `update()` does.
    """
    for _ in range(times):
        app.tk.update()
        app.tk.update_idletasks()


def _core_text(widget):
    """The raw text widget behind a `TextArea` or a `CodeEditor`."""
    inner = widget._internal
    core = inner.core if hasattr(inner, "core") else inner
    return core.text


def _focus_in(app, widget) -> None:
    """Drive a real `<FocusIn>` where the snapshot handler is bound."""
    _core_text(widget).event_generate("<FocusIn>")
    _pump(app)


def _blur(app, widget) -> None:
    """Drive a real `<FocusOut>` where the emit handler is bound."""
    _core_text(widget).event_generate("<FocusOut>")
    _pump(app)


# ---------------------------------------------------------------------------
# TextArea
# ---------------------------------------------------------------------------

def test_textarea_edit_then_blur_reports_the_pre_edit_value_as_the_prior(app):
    """One event, carrying both ends of the change."""
    ta = bs.TextArea(value="before")
    seen: list = []
    ta.on_change(seen.append)
    _pump(app)

    _focus_in(app, ta)
    _core_text(ta).insert("end", " and after")
    _pump(app)
    _blur(app, ta)

    assert len(seen) == 1, "expected exactly one change, got %d" % len(seen)
    assert seen[0].value == "before and after"
    assert seen[0].prev_value == "before", (
        "prev_value did not carry the pre-edit text: %r" % (seen[0].prev_value,)
    )


def test_textarea_focus_round_trip_with_no_edit_is_silent(app):
    """The headline of #509: a blur is not a change.

    Nothing was typed, so nothing was committed. Before the fix this fired on
    every focus-out for the life of the widget.
    """
    ta = bs.TextArea(value="untouched")
    seen: list = []
    ta.on_change(seen.append)
    _pump(app)

    for _ in range(3):
        _focus_in(app, ta)
        _blur(app, ta)

    assert seen == [], "a no-edit focus round trip announced %d change(s)" % len(seen)


def test_textarea_reports_each_edit_against_the_previous_one(app):
    """Two edits chain: the second event's prior is the first event's value.

    A snapshot taken only at construction passes the single-edit test above and
    fails here, which is what makes the re-snapshot after the emit load-bearing
    rather than decorative.
    """
    ta = bs.TextArea(value="one")
    seen: list = []
    ta.on_change(seen.append)
    _pump(app)

    _focus_in(app, ta)
    _core_text(ta).delete("1.0", "end")
    _core_text(ta).insert("end", "two")
    _pump(app)
    _blur(app, ta)

    _focus_in(app, ta)
    _core_text(ta).delete("1.0", "end")
    _core_text(ta).insert("end", "three")
    _pump(app)
    _blur(app, ta)

    assert [e.value for e in seen] == ["two", "three"]
    assert [e.prev_value for e in seen] == ["one", "two"], (
        "the priors did not chain: %r" % ([e.prev_value for e in seen],)
    )


# ---------------------------------------------------------------------------
# SelectButton — payload only
# ---------------------------------------------------------------------------

def test_selectbutton_chains_prev_value_and_reports_the_display_label(app):
    """Both payload defects at once, on options whose text is not their value.

    `text` is documented as the display text behind the value, and the only
    correct source is `_display_text()` — the signal holds the value KEY.
    """
    sb = bs.SelectButton(list(DECOUPLED), value="sm")
    seen: list = []
    sb.on_change(seen.append)

    sb.value = "md"
    _pump(app)
    sb.value = "lg"
    _pump(app)

    assert [e.value for e in seen] == ["md", "lg"]
    assert [e.prev_value for e in seen] == ["sm", "md"], (
        "the priors did not chain in value-space: %r"
        % ([e.prev_value for e in seen],)
    )
    assert [e.text for e in seen] == ["Medium", "Large"], (
        "text carried the value key rather than the display label: %r"
        % ([e.text for e in seen],)
    )


def test_selectbutton_reports_a_falsy_option_value_intact(app):
    """`0` is an ordinary option value, not an absent one.

    Coercing the payload on the truthiness of the resolved value — rather than
    on whether any option is selected — silently reports `None` for `0`, `False`
    and `''`, and disagrees with `get()`, which returns them unchanged.
    """
    sb = bs.SelectButton([("Zero", 0), ("One", 1)], value=1)
    seen: list = []
    sb.on_change(seen.append)

    sb.value = 0
    _pump(app)

    assert [e.value for e in seen] == [0], (
        "a falsy option value was not reported intact: %r"
        % ([e.value for e in seen],)
    )
    assert sb.value == 0
    assert seen[0].prev_value == 1


# ---------------------------------------------------------------------------
# CodeEditor
# ---------------------------------------------------------------------------

def test_codeeditor_seeded_value_announces_no_change(app):
    """Construction is not a user edit.

    `value=` is inserted into the core, which raised the core's `<<Change>>`,
    which re-emitted a public change before the widget had ever been touched.
    """
    seen: list = []
    ce = bs.CodeEditor(language="python", value='print("hello")')
    ce.on_change(seen.append)
    _pump(app)

    assert seen == [], "construction announced %d change(s)" % len(seen)
    assert ce.value.startswith('print("hello")')


def test_codeeditor_edits_are_input_and_only_the_blur_is_a_change(app):
    """The split: `on_input` per edit, `on_change` once on commit.

    The `on_input` arm is not decoration — it is the control. Without it this
    test passes just as well for a build that stopped emitting anything at all,
    which is precisely the shape the fix could have taken by accident.
    """
    # Subscribed AFTER the construction pump on purpose. Seeding `value=` raises
    # the core's `<<Change>>`, which still re-emits `<<BsInput>>` — pre-existing,
    # unchanged by #509, and out of scope here (the input leg was already
    # correct per edit). The change leg's construction-time fire is the half
    # that was a defect, and `test_codeeditor_seeded_value_announces_no_change`
    # subscribes immediately to pin it.
    ce = bs.CodeEditor(language="python", value="x = 1")
    _pump(app)
    changes: list = []
    inputs: list = []
    ce.on_change(changes.append)
    ce.on_input(inputs.append)
    before = ce.value

    _focus_in(app, ce)
    for ch in "abc":
        _core_text(ce).insert("end", ch)
        _pump(app)

    assert len(inputs) == 3, "expected one input per edit, got %d" % len(inputs)
    assert changes == [], "editing announced %d change(s) before the commit" % len(changes)

    _blur(app, ce)

    assert len(changes) == 1, "expected one change on blur, got %d" % len(changes)
    assert changes[0].value == ce.value
    assert changes[0].prev_value == before, (
        "prev_value did not carry the pre-edit document: %r"
        % (changes[0].prev_value,)
    )


def test_codeeditor_focus_round_trip_with_no_edit_is_silent(app):
    """Same rule as `TextArea`, on the widget that reached it by a different route."""
    ce = bs.CodeEditor(language="python", value="x = 1")
    seen: list = []
    ce.on_change(seen.append)
    _pump(app)

    for _ in range(3):
        _focus_in(app, ce)
        _blur(app, ce)

    assert seen == [], "a no-edit focus round trip announced %d change(s)" % len(seen)