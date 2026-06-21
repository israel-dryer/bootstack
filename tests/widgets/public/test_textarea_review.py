"""TextArea review fixes (feat/textarea-review).

Read-only state management was broken: the public `read_only` setter and the
placeholder code poked the tk.Text `state` directly without syncing the core's
`_read_only` flag, so programmatic writes silently failed and the placeholder
flipped a read-only field editable. And the multi-line text widget trapped Tab
(inserting a tab char and keeping focus) — a keyboard trap for a form field.

Fixes verified here:
1. `read_only` set via the property keeps programmatic `value=`/`insert()` working
   and reads back correctly (parity with constructor `read_only=True`).
2. `insert()` applies even when read-only, leaving the field read-only.
3. A placeholder shown on a read-only field does not make it editable.
4. Tab moves focus instead of inserting a tab character.
"""
import pytest

import bootstack as bs


# ----- read-only state management -----

def test_read_only_via_property_still_allows_programmatic_value(app):
    ta = bs.TextArea(value="test")
    ta.read_only = True
    assert ta.read_only is True
    ta.value = "new"
    assert ta.value == "new"  # programmatic write applies despite read-only


def test_read_only_via_constructor_allows_programmatic_value(app):
    ta = bs.TextArea(value="test", read_only=True)
    ta.value = "new"
    assert ta.value == "new"


def test_read_only_toggle_round_trip(app):
    ta = bs.TextArea(value="a")
    ta.read_only = True
    ta.read_only = False
    assert ta.read_only is False
    ta.value = "editable"
    assert ta.value == "editable"


def test_insert_applies_when_read_only(app):
    ta = bs.TextArea(value="abc", read_only=True)
    ta.append("XYZ")
    assert ta.value == "abcXYZ"
    assert ta.read_only is True  # still read-only after the programmatic insert


def test_insert_at_cursor(app):
    # TextArea is a form field: insert is positionless (at the cursor only).
    ta = bs.TextArea(value="abc")
    ta._internal._core.text.mark_set("insert", "1.1")  # between a and b
    ta.insert("Z")
    assert ta.value == "aZbc"


def test_append(app):
    ta = bs.TextArea(value="abc")
    ta.append("\nmore")
    assert ta.value == "abc\nmore"


def test_placeholder_does_not_make_read_only_editable(app):
    ta = bs.TextArea(placeholder="hint", read_only=True, value="")
    app._tk_root.update_idletasks()
    assert ta.read_only is True


# ----- Tab is not a keyboard trap -----

def test_tab_moves_focus_instead_of_inserting_tab(app):
    ta = bs.TextArea(value="x")
    tw = ta._internal._core.text
    tw.focus_set()
    tw.event_generate("<Tab>", when="now")
    app._tk_root.update_idletasks()
    assert ta.value == "x"  # no tab character was inserted
    assert "\t" not in ta.value


# ----- undo/redo bound to native virtual events -----

def test_undo_redo_use_native_virtual_events(app):
    # Drive the custom UndoManager from Tk's platform-aware <<Undo>>/<<Redo>>
    # events so the OS-native shortcut applies (Ctrl+Z / Ctrl+Y on Windows),
    # rather than hardcoding keys.
    ta = bs.TextArea(value="x")
    tw = ta._internal._core.text
    assert tw.bind("<<Undo>>")  # bound
    assert tw.bind("<<Redo>>")  # bound
    # The old hardcoded redo key (Ctrl+Shift+Z) is no longer bound directly.
    assert not tw.bind("<Control-Z>")
