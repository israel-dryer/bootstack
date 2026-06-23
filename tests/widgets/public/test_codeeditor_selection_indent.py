"""CodeEditor selection API (#296) and block indent/dedent (#297).

These two PRs added public surface that shipped without tests. Coordinates are
1-indexed ``(line, col)`` throughout, matching ``cursor_position`` / ``goto()``.
"""
import pytest

import bootstack as bs

pytestmark = pytest.mark.gui


# ----- selection API (#296) -----

def test_selection_none_when_empty(app):
    ed = bs.CodeEditor(value="abc")
    assert ed.selection is None
    assert ed.selected_text == ""


def test_selection_set_read_and_text(app):
    ed = bs.CodeEditor(value="line one\nline two\nline three")
    ed.selection = ((1, 1), (2, 5))
    assert ed.selection == ((1, 1), (2, 5))
    assert ed.selected_text == "line one\nline"


def test_selection_round_trips_coordinates(app):
    ed = bs.CodeEditor(value="hello\nworld")
    ed.selection = ((1, 2), (2, 4))
    assert ed.selection == ((1, 2), (2, 4))


def test_selection_clear(app):
    ed = bs.CodeEditor(value="abc def")
    ed.selection = ((1, 1), (1, 4))
    assert ed.selected_text == "abc"
    ed.selection = None
    assert ed.selection is None
    assert ed.selected_text == ""


# ----- block indent / dedent (#297) -----

def test_indent_no_selection_inserts_tab_stop(app):
    ed = bs.CodeEditor(value="code")
    ed.goto(1, 1)
    ed.indent()
    assert ed.value == "    code"


def test_indent_selected_lines(app):
    ed = bs.CodeEditor(value="a\nb\nc")
    ed.selection = ((1, 1), (3, 2))  # spans lines 1-3
    ed.indent()
    assert ed.value == "    a\n    b\n    c"


def test_indent_keeps_affected_lines_selected(app):
    ed = bs.CodeEditor(value="a\nb")
    ed.selection = ((1, 1), (2, 2))
    ed.indent()
    sel = ed.selection
    assert sel is not None
    assert sel[0][0] == 1 and sel[1][0] == 2  # lines 1-2 still selected


def test_dedent_selected_lines(app):
    ed = bs.CodeEditor(value="    a\n    b\n    c")
    ed.selection = ((1, 1), (3, 6))
    ed.dedent()
    assert ed.value == "a\nb\nc"


def test_dedent_partial_indent_removes_only_what_exists(app):
    # 2 leading spaces, tab_width 4 -> loses just the 2 it has (no underflow).
    ed = bs.CodeEditor(value="  a")
    ed.goto(1, 1)
    ed.dedent()
    assert ed.value == "a"


def test_dedent_no_leading_whitespace_is_noop(app):
    ed = bs.CodeEditor(value="abc")
    ed.goto(1, 1)
    ed.dedent()
    assert ed.value == "abc"


def test_indent_dedent_round_trip(app):
    ed = bs.CodeEditor(value="a\nb\nc")
    ed.selection = ((1, 1), (3, 2))
    ed.indent()
    ed.dedent()
    assert ed.value == "a\nb\nc"


def test_indent_works_when_auto_indent_disabled(app):
    # The indent()/dedent() methods are independent of the auto_indent setting
    # (only the Tab/Shift+Tab key bindings depend on it).
    ed = bs.CodeEditor(value="a\nb", auto_indent=False)
    ed.selection = ((1, 1), (2, 2))
    ed.indent()
    assert ed.value == "    a\n    b"
