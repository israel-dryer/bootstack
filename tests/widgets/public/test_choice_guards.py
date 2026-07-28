"""Construction-time checking of keyword arguments with a closed value set.

A behavior-mode argument (`selection_mode`, `sorting_mode`, `scrollbars`) is
read by comparing against one literal, so a near-miss spelling used to take the
other branch silently: `selection_mode='multiple'` turned multi-select off and
reported nothing. Issue #381 — the failure cost real debugging time because it
looked like a broken widget rather than a typo.

Two layers are covered: the helper itself (no Tk root needed) and every public
widget that accepts one of these arguments.
"""
from __future__ import annotations

import pytest

import bootstack as bs
from bootstack.errors import BootstackError, InvalidChoiceError
from bootstack.widgets._core.choices import SELECTION_MODES, validate_choice


# ---------------------------------------------------------------------------
# The helper
# ---------------------------------------------------------------------------

def test_valid_value_passes_through_unchanged():
    assert validate_choice("multi", SELECTION_MODES, param="selection_mode", widget="Tree") == "multi"


def test_message_names_the_value_the_argument_and_the_valid_set():
    with pytest.raises(InvalidChoiceError) as excinfo:
        validate_choice("multiple", SELECTION_MODES, param="selection_mode", widget="DataTable")
    message = str(excinfo.value)
    assert "DataTable" in message
    assert "'multiple'" in message          # what they wrote
    assert "selection_mode" in message      # which argument
    for mode in SELECTION_MODES:            # what they could have written
        assert repr(mode) in message


def test_catchable_as_either_bootstack_error_or_value_error():
    # BootstackError is the framework's error surface; ValueError is what Python
    # convention leads a caller to write for a bad value. Both must work.
    with pytest.raises(BootstackError):
        validate_choice("x", ("a",), param="p", widget="W")
    with pytest.raises(ValueError):
        validate_choice("x", ("a",), param="p", widget="W")


def test_none_is_rejected_like_any_other_value_outside_the_set():
    with pytest.raises(InvalidChoiceError):
        validate_choice(None, ("a", "b"), param="p", widget="W")


def test_selection_modes_tracks_the_type_alias():
    # The tuple is derived from the SelectionMode alias, so the check cannot
    # drift from the documented type.
    from typing import get_args

    from bootstack.widgets.types import SelectionMode

    assert SELECTION_MODES == get_args(SelectionMode)


# ---------------------------------------------------------------------------
# The widgets
# ---------------------------------------------------------------------------

# (label, factory taking no args, the argument expected in the message)
BAD = [
    ("DataTable.selection_mode", lambda: bs.DataTable(rows=[{"id": 1}], selection_mode="multiple"), "selection_mode"),
    ("DataTable.sorting_mode", lambda: bs.DataTable(rows=[{"id": 1}], sorting_mode="multi"), "sorting_mode"),
    ("DataTable.paging_mode", lambda: bs.DataTable(rows=[{"id": 1}], paging_mode="paged"), "paging_mode"),
    ("ListView.selection_mode", lambda: bs.ListView(items=[{"id": 1}], selection_mode="multiple"), "selection_mode"),
    ("Tree.selection_mode", lambda: bs.Tree(selection_mode="multiple"), "selection_mode"),
    ("Gallery.selection_mode", lambda: bs.Gallery(selection_mode="multiple"), "selection_mode"),
    ("Calendar.selection_mode", lambda: bs.Calendar(selection_mode="multi"), "selection_mode"),
    ("DateField.selection_mode", lambda: bs.DateField(selection_mode="multi"), "selection_mode"),
    ("ToggleGroup.mode", lambda: bs.ToggleGroup(mode="multiple"), "mode"),
    ("PathField.mode", lambda: bs.PathField(mode="folder"), "mode"),
    ("ScrollView.scroll_direction", lambda: bs.ScrollView(scroll_direction="down"), "scroll_direction"),
    ("ScrollView.scrollbar_visibility", lambda: bs.ScrollView(scrollbar_visibility="sometimes"), "scrollbar_visibility"),
    ("TextArea.scrollbars", lambda: bs.TextArea(scrollbars="vertikal"), "scrollbars"),
    ("CodeEditor.scrollbars", lambda: bs.CodeEditor(scrollbars="vertikal"), "scrollbars"),
]


@pytest.mark.parametrize("label,make,param", BAD, ids=[b[0] for b in BAD])
def test_invalid_mode_raises_naming_the_argument(app, label, make, param):
    with pytest.raises(InvalidChoiceError) as excinfo:
        make()
    assert param in str(excinfo.value)


# Every valid value must still construct — the guard must not narrow what works.
GOOD = [
    ("DataTable", lambda m: bs.DataTable(rows=[{"id": 1}], selection_mode=m), SELECTION_MODES),
    ("ListView", lambda m: bs.ListView(items=[{"id": 1}], selection_mode=m), SELECTION_MODES),
    ("Tree", lambda m: bs.Tree(selection_mode=m), SELECTION_MODES),
    ("Gallery", lambda m: bs.Gallery(selection_mode=m), SELECTION_MODES),
    ("Calendar", lambda m: bs.Calendar(selection_mode=m), ("single", "range")),
    ("ToggleGroup", lambda m: bs.ToggleGroup(mode=m), ("single", "multi")),
    ("PathField", lambda m: bs.PathField(mode=m), ("open", "open_multiple", "save", "directory")),
    ("TextArea", lambda m: bs.TextArea(scrollbars=m), ("auto", "vertical", "both", "none")),
]


@pytest.mark.parametrize("label,make,values", GOOD, ids=[g[0] for g in GOOD])
def test_every_documented_value_still_constructs(app, label, make, values):
    for value in values:
        assert make(value) is not None


def test_bad_value_is_reported_before_parent_resolution():
    # No `app` fixture, so no container is on the stack. Resolving a parent here
    # raises its own BootstackError about being created outside a container --
    # which would bury the actual mistake. The value is checked first, so the
    # message names the typo.
    with pytest.raises(InvalidChoiceError) as excinfo:
        bs.DataTable(rows=[{"id": 1}], selection_mode="multiple")
    assert "selection_mode" in str(excinfo.value)


def test_multi_still_enables_multi_select(app):
    # The guard's whole point is that the working value keeps working — a typo
    # is now rejected instead of quietly landing here.
    table = bs.DataTable(rows=[{"id": 1}, {"id": 2}], selection_mode="multi")
    assert table._selection_mode == "multi"