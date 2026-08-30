"""`TextArea.insert()` and `append()` write through the placeholder (#491).

Both reached the core text directly, so `_showing_placeholder` stayed `True`
and the text landed *alongside* the placeholder on screen. `value`, `<<Input>>`
and `<<Changed>>` all gate on that flag, so the widget went on reporting itself
empty and stopped announcing edits — durably, not for one cycle. `value = ...`
was always clean, because its setter drops the placeholder first.

`_hide_placeholder()` deletes the whole document, so it may only be called when
a placeholder is actually showing. The last three tests are the control for
that: measured, no single wrong implementation passes the whole file — against
`main` the first four fail, and against a fix that drops the guard the last
three fail, `append()` having become "replace everything".

`CodeEditor` has no placeholder and is not reachable by any of this.
"""
import pytest

import bootstack as bs

PLACEHOLDER = "Type something here"


def _pump(app, times: int = 4) -> None:
    """`<<Input>>` and `<<Changed>>` are queued `when="tail"`, so idle tasks
    alone do not deliver them — only a full `update()` does."""
    for _ in range(times):
        app.tk.update()
        app.tk.update_idletasks()


def _screen(widget) -> str:
    """What the text widget is actually showing.

    Worth reaching past the public surface here: the defect is precisely that
    `value` and the screen disagreed, so asserting `value` alone would pass on
    a widget still displaying the placeholder with the text stuck to it.
    """
    return widget._internal._core.text.get("1.0", "end-1c")


# ----- the defect: writing onto a showing placeholder -----

def test_append_onto_a_placeholder_replaces_it(app):
    ta = bs.TextArea(placeholder=PLACEHOLDER)
    assert ta._internal._showing_placeholder is True, (
        "precondition failed — no placeholder is showing, so nothing was tested"
    )

    ta.append("written by code")

    assert ta.value == "written by code"
    assert _screen(ta) == "written by code"
    assert ta._internal._showing_placeholder is False


def test_insert_onto_a_placeholder_replaces_it(app):
    """The second door — `insert()` was broken the same way and separately."""
    ta = bs.TextArea(placeholder=PLACEHOLDER)
    assert ta._internal._showing_placeholder is True, (
        "precondition failed — no placeholder is showing, so nothing was tested"
    )

    ta.insert("written by code")

    assert ta.value == "written by code"
    assert _screen(ta) == "written by code"
    assert ta._internal._showing_placeholder is False


def test_appending_onto_a_placeholder_announces_the_edit(app):
    """The durable half: the flag gated the events, not just `value`.

    After the append the widget stayed silent for everything typed afterwards,
    so an application watching `on_input` went deaf for the field's whole life.
    """
    ta = bs.TextArea(placeholder=PLACEHOLDER)
    inputs: list = []
    ta.on_input(lambda e: inputs.append(e.text))

    ta.append("written by code")
    _pump(app)

    assert inputs, "on_input never fired for a write onto the placeholder"
    assert inputs[-1] == "written by code"


def test_append_onto_a_placeholder_leaves_a_read_only_field_read_only(app):
    """Dropping the placeholder toggles the underlying state to write; a
    read-only field has to come back out of it read-only."""
    ta = bs.TextArea(placeholder=PLACEHOLDER, read_only=True)

    ta.append("written by code")

    assert ta.value == "written by code"
    assert ta.read_only is True


# ----- the control: `_hide_placeholder()` deletes the document -----

def test_append_keeps_existing_text_when_a_placeholder_was_declared(app):
    """A placeholder that is declared but not showing must not cost the content."""
    ta = bs.TextArea(placeholder=PLACEHOLDER, value="line1")
    assert ta._internal._showing_placeholder is False, (
        "precondition failed — the placeholder is showing, so this is the other case"
    )

    ta.append("line2")

    assert ta.value == "line1line2"


def test_append_keeps_existing_text_with_no_placeholder_at_all(app):
    ta = bs.TextArea(value="line1")

    ta.append("line2")

    assert ta.value == "line1line2"


def test_insert_keeps_existing_text_with_no_placeholder_at_all(app):
    ta = bs.TextArea(value="line1")

    ta.insert("X")

    assert ta.value == "line1X"
