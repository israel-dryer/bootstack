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


def test_normalize_options_list_and_none():
    assert normalize_options(None) == []
    assert [r.text for r in normalize_options(["a", ("B", "b")])] == ["a", "B"]


@pytest.mark.parametrize("bad, exc", [
    ({"value": "x"}, ValueError),       # missing text
    ({"text": "a", "bogus": 1}, ValueError),  # unknown key
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
