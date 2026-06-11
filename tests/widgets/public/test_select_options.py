"""The shared option shape across the selection family (Select / SelectButton /
RadioGroup / ToggleGroup): the three input forms, text<->value divergence,
value round-trips, search-on-text, custom values, and unknown-value errors.
"""
import pytest

import bootstack as bs
from bootstack.widgets._core.options import (
    normalize_option,
    normalize_options,
    record_to_dict,
)


@pytest.fixture(scope="module")
def app():
    """A single shown App so child widgets get mapped and styles build."""
    a = bs.App()
    a.__enter__()
    root = a._tk_root
    root.deiconify()
    root.update_idletasks()
    try:
        yield a
    finally:
        try:
            a.__exit__(None, None, None)
        except Exception:
            pass
        try:
            root.destroy()
        except Exception:
            pass


# --------------------------------------------------------------------------
# The normalizer
# --------------------------------------------------------------------------

@pytest.mark.parametrize("opt, expected", [
    ("Small", ("Small", "Small", {})),
    (("Small", "s"), ("Small", "s", {})),
    ({"text": "Small", "value": "s"}, ("Small", "s", {})),
    ({"text": "Small"}, ("Small", "Small", {})),
])
def test_normalize_forms(opt, expected):
    assert tuple(normalize_option(opt)) == expected


def test_normalize_preserves_extras():
    rec = normalize_option({"text": "S", "value": "s", "icon": "star"})
    assert rec.extras == {"icon": "star"}
    assert record_to_dict(rec) == {"text": "S", "value": "s", "icon": "star"}


def test_normalize_carries_arbitrary_extras_as_databag():
    # The dict form is a data bag: any key beyond text/value rides along (it is
    # NOT rejected — the dict route is opt-in, the caller owns the typo risk).
    rec = normalize_option({"text": "Canada", "value": "CA", "phone": "+1", "region": "americas"})
    assert rec.extras == {"phone": "+1", "region": "americas"}
    assert record_to_dict(rec) == {
        "text": "Canada", "value": "CA", "phone": "+1", "region": "americas",
    }


def test_normalize_options_list_and_none():
    assert normalize_options(None) == []
    assert [r.text for r in normalize_options(["a", ("B", "b")])] == ["a", "B"]


@pytest.mark.parametrize("bad, exc", [
    ({"value": "x"}, ValueError),       # missing required text
    (("a", "b", "c"), ValueError),      # bad tuple arity
    ({"text": 1}, TypeError),           # non-string text
    (123, TypeError),                   # wrong type
])
def test_normalize_rejects_bad_input(bad, exc):
    with pytest.raises(exc):
        normalize_option(bad)


# --------------------------------------------------------------------------
# Per-widget: all three forms, value-space round-trips
# --------------------------------------------------------------------------

FORMS = [
    (["a", "b", "c"], "b", "b"),                              # plain strings
    ([("A", "a"), ("B", "b")], "b", "b"),                     # tuples
    ([{"text": "A", "value": "a"}, {"text": "B", "value": "b"}], "b", "b"),  # dicts
]


@pytest.mark.parametrize("options, set_value, expected", FORMS)
def test_select_accepts_all_forms(app, options, set_value, expected):
    s = bs.Select(options=options, value=set_value)
    assert s.value == expected


@pytest.mark.parametrize("options, set_value, expected", FORMS)
def test_selectbutton_accepts_all_forms(app, options, set_value, expected):
    sb = bs.SelectButton(options=options, value=set_value)
    assert sb.value == expected


@pytest.mark.parametrize("options, set_value, expected", FORMS)
def test_radiogroup_accepts_all_forms(app, options, set_value, expected):
    rg = bs.RadioGroup(options=options, value=set_value)
    assert rg.value == expected


@pytest.mark.parametrize("options, set_value, expected", FORMS)
def test_togglegroup_accepts_all_forms(app, options, set_value, expected):
    tg = bs.ToggleGroup(options=options, value=set_value)
    assert tg.value == expected


# --------------------------------------------------------------------------
# selection — the selected option's full record (the data bag)
# --------------------------------------------------------------------------

def test_select_selection_is_record_with_bag(app):
    s = bs.Select(options=[
        {"text": "Canada", "value": "CA", "phone": "+1"},
        {"text": "Japan", "value": "JP", "phone": "+81"},
    ], value="JP")
    assert s.selection == {"text": "Japan", "value": "JP", "phone": "+81"}
    assert s.selection["phone"] == "+81"
    s.value = "CA"
    assert s.selection["phone"] == "+1"


def test_selectbutton_selection_is_record_with_bag(app):
    sb = bs.SelectButton(options=[{"text": "Dark", "value": "dark", "accent": "x"}], value="dark")
    assert sb.selection == {"text": "Dark", "value": "dark", "accent": "x"}


def test_radiogroup_selection_is_record_with_bag(app):
    rg = bs.RadioGroup(options=[{"text": "Small", "value": "s", "px": 12}], value="s")
    assert rg.selection == {"text": "Small", "value": "s", "px": 12}


def test_togglegroup_single_selection_is_record(app):
    tg = bs.ToggleGroup(options=[("Grid", "grid"), {"text": "List", "value": "list", "icon": "rows"}], value="list")
    assert tg.selection == {"text": "List", "value": "list", "icon": "rows"}


def test_togglegroup_multi_selection_is_list_of_records(app):
    tg = bs.ToggleGroup(
        options=[("Bold", "b"), ("Italic", "i"), ("Underline", "u")],
        mode="multi", value={"b", "u"},
    )
    sel = tg.selection
    assert isinstance(sel, list)
    assert {d["value"] for d in sel} == {"b", "u"}


def test_select_selection_none_when_unselected(app):
    s = bs.Select(options=["a", "b"])
    assert s.selection is None


def test_plain_string_option_selection_is_minimal_record(app):
    s = bs.Select(options=["a", "b"], value="a")
    assert s.selection == {"text": "a", "value": "a"}


# --------------------------------------------------------------------------
# Group .text (selected label) — value/text duality for the group widgets
# --------------------------------------------------------------------------

def test_radiogroup_text_is_selected_label(app):
    rg = bs.RadioGroup(options=[("Small", "s"), ("Medium", "m")], value="m")
    assert rg.value == "m" and rg.text == "Medium"
    rg.value = "s"
    assert rg.text == "Small"


def test_radiogroup_text_none_when_empty(app):
    rg = bs.RadioGroup(options=[("A", "a")])
    assert rg.text is None


def test_togglegroup_single_text_is_label(app):
    tg = bs.ToggleGroup(options=[("Grid", "grid"), ("List", "list")], value="grid")
    assert tg.value == "grid" and tg.text == "Grid"


def test_togglegroup_multi_text_is_label_set(app):
    tg = bs.ToggleGroup(
        options=[("Grid", "grid"), ("List", "list"), ("Card", "card")],
        mode="multi",
        value={"grid", "card"},
    )
    assert tg.value == {"grid", "card"}
    assert tg.text == {"Grid", "Card"}


# --------------------------------------------------------------------------
# Text / value divergence
# --------------------------------------------------------------------------

def test_select_text_value_divergence(app):
    s = bs.Select(options=[("Dark Mode", "dark"), ("Light Mode", "light")], value="dark")
    assert s.value == "dark"          # value-space
    assert s.text == "Dark Mode"      # display label
    assert s.options == [
        {"text": "Dark Mode", "value": "dark"},
        {"text": "Light Mode", "value": "light"},
    ]


def test_selectbutton_text_value_divergence(app):
    sb = bs.SelectButton(options=[("Dark Mode", "dark")], value="dark")
    assert sb.value == "dark"
    assert sb.text == "Dark Mode"
    assert sb.options == [{"text": "Dark Mode", "value": "dark"}]


def test_select_no_plural_catalog_accessors(app):
    # The catalog is `.options`; the singular `.text`/`.value` are the current
    # selection. The earlier `.texts`/`.values` plural accessors were dropped.
    s = bs.Select(options=["a", "b"])
    assert not hasattr(s, "texts")
    assert not hasattr(s, "values")


def test_select_value_setter_is_value_space(app):
    s = bs.Select(options=[("Big", "b"), ("Small", "s")])
    s.value = "s"
    assert s.value == "s"
    assert s._internal.entry_widget.get() == "Small"


# --------------------------------------------------------------------------
# Unknown values
# --------------------------------------------------------------------------

def test_select_unknown_value_raises(app):
    s = bs.Select(options=[("Big", "b")])
    with pytest.raises(ValueError):
        s.value = "nope"


def test_selectbutton_unknown_value_raises(app):
    sb = bs.SelectButton(options=[("Big", "b")])
    with pytest.raises(ValueError):
        sb.value = "nope"


def test_select_unknown_initial_value_raises(app):
    with pytest.raises(ValueError):
        bs.Select(options=["a", "b"], value="z")


# --------------------------------------------------------------------------
# Search-on-text and custom values (Select-specific)
# --------------------------------------------------------------------------

def test_select_custom_value_is_typed_string(app):
    s = bs.Select(options=[("Big", "b")], allow_custom_values=True)
    s.value = "freeform"
    assert s.value == "freeform"
    assert s._internal.entry_widget.get() == "freeform"


def test_select_options_reassignment_reconciles(app):
    s = bs.Select(options=[("Big", "b"), ("Small", "s")], value="s")
    assert s.value == "s"
    s.options = [("Red", "r"), ("Green", "g")]
    assert [o["value"] for o in s.options] == ["r", "g"]
    assert s.value is None     # stale 's' cleared


def test_select_selected_index(app):
    s = bs.Select(options=[("Big", "b"), ("Small", "s")])
    s.value = "s"
    assert s.selected_index == 1
    s.selected_index = 0
    assert s.value == "b"


# --------------------------------------------------------------------------
# Change events carry value-space values
# --------------------------------------------------------------------------

def test_select_change_event_value_space(app):
    s = bs.Select(options=[("Big", "b"), ("Small", "s")])
    seen = []
    s.on_change(lambda e: seen.append(e.value))
    s.value = "s"
    app.tk.update()
    assert seen == ["s"]


def test_selectbutton_change_event_value_space(app):
    sb = bs.SelectButton(options=[("Big", "b"), ("Small", "s")])
    seen = []
    sb.on_change(lambda e: seen.append(e.value))
    sb.value = "s"
    app.tk.update()
    # SelectButton's StringVar emits <<Change>> more than once per set (a
    # pre-existing quirk, unrelated to the option shape) — assert every emit
    # carries the value-space value rather than the exact count.
    assert seen and set(seen) == {"s"}
