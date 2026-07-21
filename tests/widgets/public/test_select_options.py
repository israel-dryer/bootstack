"""The shared option shape across the selection family (Select / SelectButton /
RadioGroup / ToggleGroup): the three input forms, text<->value divergence,
value round-trips, search-on-text, custom values, and unknown-value errors.
"""
import pytest

import bootstack as bs
from bootstack.widgets._core.options import (
    normalize_option,
    normalize_options,
    option_display,
    option_is_icon_only,
    record_to_dict,
)


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

def test_select_unknown_value_is_displayed_not_rejected(app):
    # Was: raised ValueError. A fixed list constrains what a user can pick, so
    # rejecting a value the PROGRAM supplies crashed editors opened on records
    # whose option had been retired (#355). SelectButton, which maps a value to
    # an option's label and has no text entry, still rejects.
    s = bs.Select(options=[("Big", "b")])
    s.value = "nope"
    assert s.value == "nope"


def test_selectbutton_unknown_value_raises(app):
    sb = bs.SelectButton(options=[("Big", "b")])
    with pytest.raises(ValueError):
        sb.value = "nope"


def test_select_unknown_initial_value_is_displayed(app):
    # Seeding and setting must agree; construction used to raise while a later
    # write was silently dropped.
    assert bs.Select(options=["a", "b"], value="z").value == "z"


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


# --------------------------------------------------------------------------
# Reserved option keys: icon (rendered beside the label) + disabled
# (dimmed, not user-selectable). Both ride in the data bag and are acted on.
# --------------------------------------------------------------------------

def test_option_display_extracts_icon_and_disabled():
    plain = normalize_option("a")
    assert option_display(plain) == (None, False)

    full = normalize_option({"text": "M", "value": "m", "icon": "star", "disabled": True})
    assert option_display(full) == ("star", True)

    # Falsy/absent disabled normalizes to a plain bool False.
    icon_only = normalize_option({"text": "M", "value": "m", "icon": "star"})
    assert option_display(icon_only) == ("star", False)


# These two reserved keys still ride in the bag like any extra (selection).
def test_disabled_and_icon_carried_on_selection(app):
    rg = bs.RadioGroup(
        options=[{"text": "Medium", "value": "m", "icon": "star", "disabled": True}],
        value="m",
    )
    assert rg.selection == {"text": "Medium", "value": "m", "icon": "star", "disabled": True}


DISABLED_OPTS = [
    ("Small", "s"),
    {"text": "Medium", "value": "m", "disabled": True, "icon": "star"},
    ("Large", "l"),
]


def test_radiogroup_disabled_option_button_is_disabled(app):
    rg = bs.RadioGroup(options=DISABLED_OPTS)
    assert "disabled" in rg._internal.item("m").state()
    assert "disabled" not in rg._internal.item("s").state()


def test_togglegroup_single_disabled_option_button_is_disabled(app):
    tg = bs.ToggleGroup(options=DISABLED_OPTS, mode="single")
    assert "disabled" in tg._internal.item("m").state()
    assert "disabled" not in tg._internal.item("l").state()


def test_togglegroup_multi_disabled_option_button_is_disabled(app):
    tg = bs.ToggleGroup(options=DISABLED_OPTS, mode="multi")
    assert "disabled" in tg._internal.item("m").state()


def test_disabled_option_still_settable_programmatically(app):
    # `disabled` blocks USER interaction only — a programmatic set still works.
    rg = bs.RadioGroup(options=DISABLED_OPTS, value="s")
    rg.value = "m"
    assert rg.value == "m"
    assert rg.selection["disabled"] is True


def test_group_runtime_add_disabled_and_icon(app):
    rg = bs.RadioGroup(options=[("Small", "s")])
    rg.add("Medium", "m", icon="star", disabled=True)
    assert "disabled" in rg._internal.item("m").state()
    rg.value = "m"
    assert rg.selection == {"text": "Medium", "value": "m", "icon": "star", "disabled": True}

    tg = bs.ToggleGroup(options=[("Grid", "grid")])
    tg.add("List", "list", disabled=True)
    assert "disabled" in tg._internal.item("list").state()


def test_select_first_enabled_index_skips_leading_disabled(app):
    s = bs.Select(options=[
        {"text": "X", "value": "x", "disabled": True},
        ("Y", "y"),
    ])
    assert s._internal._first_enabled_index() == 1


def test_selectbutton_disabled_menu_item(app):
    sb = bs.SelectButton(options=DISABLED_OPTS)
    backend = sb._internal._context_menu
    items = list(getattr(backend, "_items", {}).values())
    # item order matches option order: Small, Medium (disabled), Large
    assert "disabled" in items[1].state()
    assert "disabled" not in items[0].state()


# --------------------------------------------------------------------------
# Icon-only options — inferred from an icon + blank text (no icon_only flag)
# --------------------------------------------------------------------------

def test_normalize_allows_icon_only_dict_without_text():
    # `text` may be omitted when icon + value are present — text defaults to "".
    rec = normalize_option({"icon": "grid", "value": "grid"})
    assert tuple(rec) == ("", "grid", {"icon": "grid"})


# --------------------------------------------------------------------------
# Select grouping — group_by clusters popup rows under headers; the grouping
# field is read from the flat record, ordering is first-appearance, and the
# selection contract (value/text/selection/options) is unaffected.
# --------------------------------------------------------------------------

from bootstack.widgets._core.options import cluster_records, record_field


def test_record_field_spans_text_value_and_extras():
    rec = normalize_option({"text": "Apple", "value": "a", "category": "Fruit"})
    assert record_field(rec, "text") == "Apple"
    assert record_field(rec, "value") == "a"
    assert record_field(rec, "category") == "Fruit"
    assert record_field(rec, "missing") is None


def test_cluster_records_first_appearance_order_and_ungrouped_bucket():
    recs = normalize_options([
        {"text": "Apple", "value": "a", "cat": "Fruit"},
        {"text": "Banana", "value": "b", "cat": "Fruit"},
        {"text": "Carrot", "value": "c", "cat": "Veg"},
        "Other",                                            # no 'cat' -> ungrouped
        {"text": "Date", "value": "d", "cat": "Fruit"},     # non-contiguous Fruit
    ])
    clusters = cluster_records(recs, "cat")
    assert [label for label, _ in clusters] == ["Fruit", "Veg", None]
    assert [r.text for r in clusters[0][1]] == ["Apple", "Banana", "Date"]
    assert [r.text for r in clusters[2][1]] == ["Other"]


def test_cluster_records_none_group_by_is_single_bucket():
    recs = normalize_options(["a", "b"])
    clusters = cluster_records(recs, None)
    assert len(clusters) == 1 and clusters[0][0] is None
    assert [r.text for r in clusters[0][1]] == ["a", "b"]


def test_cluster_records_blank_field_is_ungrouped():
    recs = normalize_options([{"text": "X", "value": "x", "g": ""}])
    assert cluster_records(recs, "g") == [(None, recs)]


GROUP_OPTS = [
    {"text": "Apple", "value": "a", "category": "fruit"},
    {"text": "Banana", "value": "b", "category": "fruit"},
    {"text": "Carrot", "value": "c", "category": "produce"},
    {"text": "Other", "value": "x"},                         # ungrouped, headerless
]


def _open_popup(select, app):
    box = select._internal
    app.tk.update()  # lay the field out so the popup gets a real width
    box._show_selection_options()
    app.tk.update_idletasks()
    return box


def _dismiss(box):
    if box._popup_rows:
        box._popup_rows[0].winfo_toplevel().destroy()
    box._popup_open = False
    box._popup_frame = box._popup_inner = None
    box._item_labels = box._group_headers = box._popup_rows = []


def test_select_grouped_popup_render_order(app):
    s = bs.Select(options=GROUP_OPTS, group_by="category")
    box = _open_popup(s, app)
    try:
        # Option buttons sit in clustered render order; ungrouped trails.
        assert [b._item_value for b in box._item_labels] == ["a", "b", "c", "x"]
        # Two named groups; the header label (last widget in each group's
        # header_widgets) carries the verbatim, untransformed group value.
        labels = [hw[-1].cget("text") for hw, _ in box._group_headers]
        assert labels == ["fruit", "produce"]
        # Headers are not selectable rows.
        assert all(not hasattr(hw[-1], "_item_value") for hw, _ in box._group_headers)
    finally:
        _dismiss(box)


def test_select_first_group_has_no_leading_separator(app):
    s = bs.Select(options=GROUP_OPTS, group_by="category")
    box = _open_popup(s, app)
    try:
        first_widgets, _ = box._group_headers[0]
        second_widgets, _ = box._group_headers[1]
        assert len(first_widgets) == 1    # top group: header label only
        assert len(second_widgets) == 2   # later group: separator + header label
    finally:
        _dismiss(box)


def test_grouping_is_presentational_only(app):
    s = bs.Select(options=GROUP_OPTS, group_by="category", value="c")
    # The selection contract is untouched; the group field rides in the bag.
    assert s.value == "c"
    assert s.text == "Carrot"
    assert s.selection == {"text": "Carrot", "value": "c", "category": "produce"}
    assert [o.get("category") for o in s.options] == ["fruit", "fruit", "produce", None]


def test_grouped_initial_highlight_uses_render_index(app):
    # Non-contiguous groups make render order differ from source order: source
    # is [a(fruit), c(produce), b(fruit)] but render clusters to [a, b, c].
    opts = [
        {"text": "Apple", "value": "a", "category": "fruit"},
        {"text": "Carrot", "value": "c", "category": "produce"},
        {"text": "Banana", "value": "b", "category": "fruit"},
    ]
    s = bs.Select(options=opts, group_by="category", value="c")
    box = _open_popup(s, app)
    try:
        assert [b._item_value for b in box._item_labels] == ["a", "b", "c"]
        # 'c' is render index 2 (not its source index 1).
        assert box._initial_highlight_index() == 2
        assert box._item_labels[2]._item_value == "c"
    finally:
        _dismiss(box)


def test_grouped_search_hides_empty_group_header(app):
    s = bs.Select(options=GROUP_OPTS, group_by="category", searchable=True)
    box = _open_popup(s, app)
    try:
        box.entry_widget.delete(0, "end")
        box.entry_widget.insert(0, "carr")          # matches only produce/Carrot
        box._apply_search_filter(box._popup_state)  # drive the filter directly
        vis = lambda w: bool(w.winfo_manager())
        assert [b._item_text for b in box._item_labels if vis(b)] == ["Carrot"]
        fruit_label = box._group_headers[0][0][-1]
        produce_label = box._group_headers[1][0][-1]
        produce_sep = box._group_headers[1][0][0]
        assert vis(fruit_label) is False            # whole group filtered out
        assert vis(produce_label) is True
        # produce is now the top visible group, so its leading divider is dropped
        assert vis(produce_sep) is False
    finally:
        _dismiss(box)


def test_group_by_property_roundtrip(app):
    s = bs.Select(options=GROUP_OPTS)
    assert s.group_by is None
    s.group_by = "category"
    assert s.group_by == "category"
    s.group_by = None
    assert s.group_by is None


# --------------------------------------------------------------------------
# Select max_visible_items — caps the popup height before it scrolls.
# --------------------------------------------------------------------------

def test_max_visible_items_caps_popup_height(app):
    opts = [{"text": f"Item {i}", "value": i} for i in range(20)]
    s = bs.Select(options=opts, max_visible_items=5)
    box = _open_popup(s, app)
    try:
        item_h = box._item_labels[0].winfo_reqheight()
        top = box._popup_rows[0].winfo_toplevel()
        top.update_idletasks()
        # 20 items overflow the cap, so the popup is pinned at ~5 rows tall.
        assert top.winfo_height() <= 5 * item_h + 8 + 2
    finally:
        _dismiss(box)


def test_max_visible_items_property_roundtrip(app):
    s = bs.Select(options=["a", "b"])
    assert s.max_visible_items is None
    s.max_visible_items = 8
    assert s.max_visible_items == 8
    s.max_visible_items = None
    assert s.max_visible_items is None


def test_normalize_icon_without_value_still_requires_text():
    # An icon alone isn't enough to omit text — value is needed to identify it.
    with pytest.raises(ValueError):
        normalize_option({"icon": "grid"})


def test_option_is_icon_only_inference():
    assert option_is_icon_only(normalize_option({"icon": "grid", "value": "g"})) is True
    assert option_is_icon_only(normalize_option({"text": "G", "icon": "grid", "value": "g"})) is False
    assert option_is_icon_only(normalize_option(("Grid", "g"))) is False  # no icon
    assert option_is_icon_only(normalize_option("Grid")) is False


ICON_ONLY_OPTS = [
    {"icon": "list-ul", "value": "list"},
    {"icon": "grid", "value": "grid"},
    {"icon": "geo-alt", "value": "map", "disabled": True},
]


def test_togglegroup_infers_icon_only_buttons(app):
    tg = bs.ToggleGroup(options=ICON_ONLY_OPTS, value="grid")
    for key in ("list", "grid", "map"):
        btn = tg._internal.item(key)
        assert btn.cget("text") == ""
        assert btn.configure_style_options("icon_only") is True
    # disabled still applies alongside icon-only
    assert "disabled" in tg._internal.item("map").state()


def test_radiogroup_infers_icon_only_buttons(app):
    rg = bs.RadioGroup(options=ICON_ONLY_OPTS, value="list")
    assert rg._internal.item("list").configure_style_options("icon_only") is True


def test_icon_with_text_is_not_icon_only(app):
    tg = bs.ToggleGroup(options=[{"text": "List", "icon": "list-ul", "value": "list"}], value="list")
    assert tg._internal.item("list").configure_style_options("icon_only") in (None, False)


def test_group_runtime_add_blank_label_is_icon_only(app):
    rg = bs.RadioGroup()
    rg.add("", "grid", icon="grid")
    assert rg._internal.item("grid").configure_style_options("icon_only") is True


def test_icon_only_selection_carries_bag(app):
    tg = bs.ToggleGroup(options=ICON_ONLY_OPTS, value="grid")
    assert tg.selection == {"text": "", "value": "grid", "icon": "grid"}


# --- A value the list no longer offers (#355) ------------------------------

def test_off_list_value_displays_without_joining_the_list(app):
    # A fixed option list constrains what a USER can pick; it is not a schema
    # for the data the program supplies. A stored record whose option has since
    # been retired must still display — and must not become pickable again.
    select = bs.Select(options=["US", "CA"])
    app._tk_root.update_idletasks()
    select.value = "MX"
    app._tk_root.update_idletasks()
    assert select.value == "MX"
    assert [o["value"] for o in select.options] == ["US", "CA"]


def test_form_seeds_and_sets_an_off_list_value(app):
    # Construction used to raise and a later write was silently dropped, so the
    # same value produced two different wrong answers. Both now round-trip.
    form = bs.Form(data={"c": "MX"},
                   items=[bs.FieldItem(key="c", editor="select",
                                       editor_options={"values": ["US", "CA"]})])
    app._tk_root.update_idletasks()
    assert form.get()["c"] == "MX"          # seeded at construction

    form.set_field_value("c", "BR")
    app._tk_root.update_idletasks()
    assert form.get()["c"] == "BR"          # and set programmatically


def test_datatable_edit_form_opens_on_a_retired_option(app):
    # The real-world case: opening the add/edit dialog on a legacy record.
    table = bs.DataTable(rows=[{"country": "MX"}],
                         columns=[{"key": "country", "editor": "select",
                                   "editor_options": {"values": ["US", "CA"]}}])
    app._tk_root.update_idletasks()
    form = bs.Form(items=table._internal._build_form_items(), data={"country": "MX"})
    app._tk_root.update_idletasks()
    assert form.get()["country"] == "MX"


def test_in_list_selection_is_unaffected(app):
    select = bs.Select(options=["US", "CA"], value="US")
    app._tk_root.update_idletasks()
    select.value = "CA"
    app._tk_root.update_idletasks()
    assert select.value == "CA"


def test_validate_reports_an_off_list_value(app):
    # Reporting an out-of-list value is a validation rule's job — it reports
    # rather than crashing the editor that opened the record.
    allowed = {"US", "CA"}
    select = bs.Select(options=sorted(allowed))
    select.add_validation_rule("custom", func=lambda v: not v or v in allowed,
                               message="That option is no longer available.")
    app._tk_root.update_idletasks()
    select.value = "MX"
    app._tk_root.update_idletasks()
    assert select.validate() is False
    select.value = "US"
    app._tk_root.update_idletasks()
    assert select.validate() is True

def test_off_list_value_keeps_its_type(app):
    # The entry stores text, and the option list is what decodes it back to a
    # real value. A retired value has no option, so without registering it the
    # int 7 would come back as "7" — and Form.get() would hand a string to the
    # caller's persistence layer.
    select = bs.Select(options=[("One", 1), ("Two", 2)], value=1)
    app._tk_root.update_idletasks()
    select.value = 7
    app._tk_root.update_idletasks()
    assert select.value == 7 and isinstance(select.value, int)


def test_off_list_value_keeps_its_type_through_a_form(app):
    form = bs.Form(data={"s": 7},
                   items=[bs.FieldItem(key="s", editor="select",
                                       editor_options={"values": [("One", 1), ("Two", 2)]})])
    app._tk_root.update_idletasks()
    assert form.get()["s"] == 7


def test_picking_an_option_supersedes_a_retired_value(app):
    # The retired value is registered under its own display text. Selecting a
    # real option must drop that registration, or it would shadow the option
    # the next time the same text is shown.
    select = bs.Select(options=[("One", 1), ("Two", 2)])
    app._tk_root.update_idletasks()
    select.value = 7
    app._tk_root.update_idletasks()
    select.value = 2
    app._tk_root.update_idletasks()
    assert select.value == 2
    assert select._internal._retired_text is None


def test_replacing_the_options_drops_a_retired_value(app):
    select = bs.Select(options=["US", "CA"])
    app._tk_root.update_idletasks()
    select.value = "MX"
    app._tk_root.update_idletasks()
    select.options = ["GB", "FR"]
    app._tk_root.update_idletasks()
    assert select.value is None                      # the observable outcome
    assert select._internal._retired_text is None    # and no stale decoder key
    assert "MX" not in select._internal._value_by_text


def test_off_list_value_that_matches_an_option_label_resolves_to_that_option(app):
    # Two values rendering the same text are indistinguishable to the widget
    # AND to the user, so the real option wins rather than being shadowed.
    select = bs.Select(options=[{"text": "MX", "value": "mex"},
                                {"text": "US", "value": "usa"}])
    app._tk_root.update_idletasks()
    select.value = "MX"
    app._tk_root.update_idletasks()
    assert select.value == "mex"


def test_dismissing_a_search_popup_without_typing_keeps_the_value(app):
    # Opening the list to look at it, then dismissing, must not rewrite the
    # field — the user selected nothing and typed nothing.
    select = bs.Select(options=["US", "CA", "GB"], searchable=True)
    app._tk_root.update_idletasks()
    select.value = "MX"
    app._tk_root.update_idletasks()
    inner = select._internal
    inner._show_selection_options()
    app._tk_root.update_idletasks()
    inner._close_popup(inner._popup_frame.winfo_toplevel(), inner._popup_state)
    app._tk_root.update_idletasks()
    assert select.value == "MX"


def test_dismissing_a_search_popup_after_typing_still_commits_the_match(app):
    # The counterpart: type-to-filter then dismiss keeps committing the top
    # match, so the guard above did not disable the feature.
    select = bs.Select(options=["US", "CA", "GB"], searchable=True)
    app._tk_root.update_idletasks()
    inner = select._internal
    inner._show_selection_options()
    app._tk_root.update_idletasks()
    inner.entry_widget.delete(0, "end")
    inner.entry_widget.insert(0, "G")
    inner._apply_search_filter(inner._popup_state)
    app._tk_root.update_idletasks()
    inner._close_popup(inner._popup_frame.winfo_toplevel(), inner._popup_state)
    app._tk_root.update_idletasks()
    assert select.value == "GB"


def test_rules_run_against_the_value_not_the_label(app):
    # A decoupled option shows "United States" but means "US". Validating the
    # label would reject every valid selection.
    select = bs.Select(options=[{"text": "United States", "value": "US"},
                                {"text": "Canada", "value": "CA"}])
    select.add_validation_rule("custom", func=lambda v: not v or v in {"US", "CA"},
                               message="no longer available")
    app._tk_root.update_idletasks()
    select.value = "US"
    app._tk_root.update_idletasks()
    assert select.validate() is True
    select.value = "MX"
    app._tk_root.update_idletasks()
    assert select.validate() is False


def test_a_locale_change_keeps_a_retired_value(app):
    # Re-translating the options rebuilds the decode map. A translation change
    # does not retire a value the field is still holding, so its registration
    # has to survive — otherwise an int would come back as a string.
    select = bs.Select(options=[("One", 1), ("Two", 2)], value=1)
    app._tk_root.update_idletasks()
    select.value = 7
    app._tk_root.update_idletasks()
    select._internal.winfo_toplevel().event_generate("<<LocaleChanged>>")
    app._tk_root.update_idletasks()
    assert select.value == 7 and isinstance(select.value, int)


# --- Validation reads LIVE text, decoded (guards the automatic triggers) ----

def test_validation_sees_text_being_typed_not_the_committed_value(app):
    # Rules must judge what the user is typing, not the last committed value —
    # key/blur triggers fire mid-edit. TimeField shares this machinery (it is
    # built on the same composite), so getting this wrong let an out-of-range
    # time validate clean.
    from datetime import time

    field = bs.TimeField(value=time(9, 0))
    field.add_validation_rule("range", min=time(8, 0), max=time(10, 0))
    app._tk_root.update_idletasks()
    entry = field._internal._entry
    entry.delete(0, "end")
    entry.insert(0, "11:45 PM")
    app._tk_root.update_idletasks()
    assert field.validate() is False


def test_typing_into_a_custom_value_select_is_not_reported_as_empty(app):
    # `required` fires on every keystroke, so reading the last committed value
    # showed "required" while the user was part-way through typing.
    select = bs.Select(options=["alpha", "beta"], allow_custom_values=True,
                       required=True)
    app._tk_root.update_idletasks()
    entry = select._internal._entry
    entry.delete(0, "end")
    entry.insert(0, "gamma")
    app._tk_root.update_idletasks()
    assert entry._get_validation_value() == "gamma"
