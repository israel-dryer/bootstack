"""CodeEditor review fixes (feat/codeeditor-review).

The public `insert()` bypassed the core's read-only-aware `insert()` and poked
the Tk text widget directly, so a programmatic `insert()` silently no-op'd when
`read_only=True` (a disabled Tk text drops insert/delete) — the same read-only
desync class fixed in TextArea. And the public `read_only` setter duplicated the
core's flag/state sync by hand instead of routing through the core property.

Fixes verified here:
1. `insert()` applies even when read-only, leaving the editor read-only.
2. `read_only` set via the property keeps programmatic `value=`/`insert()` working
   and reads back correctly (parity with constructor `read_only=True`).
3. Undo/redo stay bound to the native `<<Undo>>`/`<<Redo>>` virtual events.
4. Tab inserts indentation (kept intentionally — CodeEditor is not a form field,
   so it does NOT adopt TextArea's Tab-moves-focus behavior).
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


# ----- read-only state management -----

def test_insert_applies_when_read_only_via_constructor(app):
    ed = bs.CodeEditor(value="abc", read_only=True)
    ed.insert("end", "XYZ")
    assert ed.value == "abcXYZ"
    assert ed.read_only is True  # still read-only after the programmatic insert


def test_insert_applies_when_read_only_via_property(app):
    ed = bs.CodeEditor(value="abc")
    ed.read_only = True
    ed.insert("end", "XYZ")
    assert ed.value == "abcXYZ"
    assert ed.read_only is True


def test_read_only_via_property_still_allows_programmatic_value(app):
    ed = bs.CodeEditor(value="test")
    ed.read_only = True
    assert ed.read_only is True
    ed.value = "new"
    assert ed.value == "new"  # programmatic write applies despite read-only


def test_read_only_via_constructor_allows_programmatic_value(app):
    ed = bs.CodeEditor(value="test", read_only=True)
    ed.value = "new"
    assert ed.value == "new"


def test_read_only_toggle_round_trip(app):
    ed = bs.CodeEditor(value="a")
    ed.read_only = True
    ed.read_only = False
    assert ed.read_only is False
    ed.value = "editable"
    assert ed.value == "editable"


# ----- cursor position (1-indexed line/col) -----

def test_cursor_position_start(app):
    ed = bs.CodeEditor(value="line1\nline2\nthird")
    ed._internal._core.text.mark_set("insert", "1.0")
    assert ed.cursor_position == (1, 1)


def test_cursor_position_mid(app):
    ed = bs.CodeEditor(value="line1\nline2\nthird")
    ed._internal._core.text.mark_set("insert", "3.5")
    assert ed.cursor_position == (3, 6)  # column is 1-indexed for display


def test_cursor_position_tracks_goto_line(app):
    ed = bs.CodeEditor(value="a\nb\nc")
    ed.goto_line(2)
    assert ed.cursor_position == (2, 1)


# ----- undo/redo bound to native virtual events -----

def test_undo_redo_use_native_virtual_events(app):
    # Drive the custom UndoManager from Tk's platform-aware <<Undo>>/<<Redo>>
    # events so the OS-native shortcut applies (Ctrl+Z / Ctrl+Y on Windows),
    # rather than hardcoding keys.
    ed = bs.CodeEditor(value="x")
    tw = ed._internal._core.text
    assert tw.bind("<<Undo>>")  # bound
    assert tw.bind("<<Redo>>")  # bound


# ----- Tab is kept as indent (not focus traversal) -----

def test_tab_inserts_indent(app):
    # CodeEditor keeps Tab-as-indent (unlike TextArea, which moves focus): the
    # SmartIndent handler inserts spaces to the next tab stop.
    ed = bs.CodeEditor(value="code")
    tw = ed._internal._core.text
    tw.mark_set("insert", "1.0")
    ed._internal._smart_indent._on_tab(None)
    assert ed.value == "    code"  # four spaces to the first tab stop


def test_return_replicates_indentation(app):
    ed = bs.CodeEditor(value="    indented")
    tw = ed._internal._core.text
    tw.mark_set("insert", "end-1c")
    ed._internal._smart_indent._on_return(None)
    tw.insert("insert", "X")
    assert ed.value == "    indented\n    X"
