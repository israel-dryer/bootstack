"""ButtonGroup review — regression coverage for the group contract.

The review found no correctness bugs; these lock the behaviors that matter for a
group: disabled state propagates to every member (on construction, via the live
property, and to buttons added while disabled), `on_click` reports the clicked
button's key/text/icon and honors disabled, and item management stays consistent
across add/remove.
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


def _member_states(bg):
    return [str(bg.item(k).cget("state")) for k in bg.keys]


# ----- disabled propagation -----

def test_disabled_propagates_from_constructor(app):
    bg = bs.ButtonGroup(disabled=True)
    bg.add("A", key="a")
    bg.add("B", key="b")
    assert bg.disabled is True
    assert _member_states(bg) == ["disabled", "disabled"]


def test_disabled_property_toggles_all_members(app):
    bg = bs.ButtonGroup()
    bg.add("A", key="a")
    bg.add("B", key="b")
    assert _member_states(bg) == ["normal", "normal"]

    bg.disabled = True
    assert _member_states(bg) == ["disabled", "disabled"]

    bg.disabled = False
    assert _member_states(bg) == ["normal", "normal"]


def test_button_added_while_disabled_inherits_state(app):
    bg = bs.ButtonGroup()
    bg.add("A", key="a")
    bg.disabled = True
    bg.add("B", key="b")  # added after the group was disabled
    assert _member_states(bg) == ["disabled", "disabled"]


# ----- on_click -----

def test_on_click_reports_clicked_button(app):
    bg = bs.ButtonGroup()
    bg.add("Save", icon="save", key="save")
    bg.add("Delete", key="del")
    seen = []
    bg.on_click(lambda e: seen.append((e.key, e.text, e.icon)))

    bg.item("save").invoke()
    assert seen == [("save", "Save", "save")]


def test_disabled_member_does_not_fire(app):
    bg = bs.ButtonGroup()
    bg.add("Save", key="save")
    seen = []
    bg.on_click(lambda e: seen.append(e.key))

    bg.disabled = True
    bg.item("save").invoke()
    assert seen == []


def test_on_click_stream_form(app):
    bg = bs.ButtonGroup()
    bg.add("A", key="a")
    bg.add("B", key="b")
    keys = []
    bg.on_click().map(lambda e: e.key).listen(keys.append)

    bg.item("a").invoke()
    bg.item("b").invoke()
    assert keys == ["a", "b"]


# ----- item management -----

def test_keys_len_contains(app):
    bg = bs.ButtonGroup()
    bg.add("A", key="a")
    bg.add_all([dict(label="B", key="b"), "C"])  # "C" gets an auto key
    assert bg.keys[:2] == ("a", "b")
    assert len(bg) == 3
    assert "a" in bg
    assert "missing" not in bg


def test_remove_and_query(app):
    bg = bs.ButtonGroup()
    bg.add("Save", key="save")
    bg.add("Cancel", key="cancel")
    assert bg.query_item("save", "text") == "Save"

    bg.update_item("save", text="Saving…")
    assert bg.query_item("save", "text") == "Saving…"

    bg.remove("cancel")
    assert "cancel" not in bg
    assert len(bg) == 1
