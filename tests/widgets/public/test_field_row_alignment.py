"""Adding a validation rule must not misalign a row of fields (#394).

A field reserves a message row the moment it carries a validation rule, making
it taller than a field without one. Reported as a single bug, it was two:

  (a) In a `Form`, every grid cell is already stretched to the tallest field in
      the row, and the entry row inside the field absorbed that slack and
      centered itself in it — so an unvalidated field's entry sat ~half a
      message row low.
  (b) In a hand-built `bs.Row`, the field frames keep their natural heights and
      the row's cross-axis default (`center`) dropped the shorter ones.

(b) is fixed by letting the field family contribute `vertical='top'` as a *soft*
default — one that an explicit `vertical_items` on the container or `vertical` on
the child still overrides. Those precedence tests are the important half of this
file: a widget's own default must never silently beat an argument the author
actually wrote.
"""
from __future__ import annotations

import bootstack as bs


def _sticky(widget) -> str:
    """The Tk sticky string the layout engine gave this child's cell."""
    return widget._internal.grid_info().get("sticky", "")


def _entry_top(field) -> int:
    """Screen y of the field's entry row — what misalignment is visible as."""
    return field._internal._field.winfo_rooty()


def _require(field, message: str = "required") -> None:
    field.add_validation_rule("required", message=message, trigger="blur")


# ----- (b) the hand-built Row --------------------------------------------------

def test_row_of_fields_stays_aligned_when_only_some_are_validated(app):
    row = bs.Row(parent=app, gap=4)
    first = bs.TextField(parent=row, label="First")
    middle = bs.TextField(parent=row, label="Middle")
    last = bs.TextField(parent=row, label="Last")
    app._tk_root.update_idletasks()

    _require(first, "First is required")
    _require(last, "Last is required")
    app._tk_root.update_idletasks()

    # Precondition: the rule really did make those two fields taller. Without
    # this the alignment assertion below could pass vacuously.
    assert first._internal.winfo_reqheight() > middle._internal.winfo_reqheight()

    tops = {_entry_top(f) for f in (first, middle, last)}
    assert len(tops) == 1, f"entries misaligned across the row: {tops}"


def test_field_in_a_row_declares_top_alignment(app):
    row = bs.Row(parent=app, gap=4)
    field = bs.TextField(parent=row, label="Name")
    label = bs.Label("Plain", parent=row)
    app._tk_root.update_idletasks()

    assert _sticky(field) == "n"
    # The soft default belongs to the field family only — everything else keeps
    # the framework-wide centered cross axis.
    assert _sticky(label) == ""


def test_explicit_vertical_items_overrides_the_field_default(app):
    # THE TRAP this fix had to avoid: a widget's own default must not win over
    # an alignment the author wrote out.
    row = bs.Row(parent=app, gap=4, vertical_items="center")
    first = bs.TextField(parent=row, label="First")
    second = bs.TextField(parent=row, label="Second")
    app._tk_root.update_idletasks()

    assert _sticky(first) == ""
    assert _sticky(second) == ""


def test_explicit_vertical_items_stretch_still_reaches_fields(app):
    row = bs.Row(parent=app, gap=4, vertical_items="stretch")
    field = bs.TextField(parent=row, label="Name")
    app._tk_root.update_idletasks()

    assert _sticky(field) == "ns"


def test_per_child_vertical_overrides_the_field_default(app):
    row = bs.Row(parent=app, gap=4)
    bottom = bs.TextField(parent=row, label="Bottom", vertical="bottom")
    plain = bs.TextField(parent=row, label="Plain")
    app._tk_root.update_idletasks()

    assert _sticky(bottom) == "s"
    assert _sticky(plain) == "n"


def test_field_default_applies_on_the_append_fast_path_and_on_relayout(app):
    # `_grid_appended_plain` (O(1) append) and `_relayout` resolve the cross
    # axis at two separate call sites; a `grow` child forces the second one.
    # Missing either would make alignment depend on whether a relayout ran.
    fast = bs.Row(parent=app, gap=4)
    fast_field = bs.TextField(parent=fast, label="Fast")
    app._tk_root.update_idletasks()
    assert fast._internal._can_append_in_place()
    assert _sticky(fast_field) == "n"

    slow = bs.Row(parent=app, gap=4)
    slow_field = bs.TextField(parent=slow, label="Slow")
    bs.TextField(parent=slow, label="Grower", grow=1)
    app._tk_root.update_idletasks()
    assert not slow._internal._can_append_in_place()
    assert _sticky(slow_field) == "n"


def test_column_of_fields_is_unaffected(app):
    # In a Column the cross axis is horizontal, so the field's vertical default
    # must not leak into it — a Column still stretches/centers as documented.
    column = bs.Column(parent=app, gap=4)
    field = bs.TextField(parent=column, label="Name")
    app._tk_root.update_idletasks()

    assert _sticky(field) == ""


def test_unset_items_read_back_as_the_effective_alignment(app):
    # The axes now store None internally when unset, so the configure delegate
    # (the only read path for them) must report the effective alignment rather
    # than leaking the None. These four values are the documented defaults.
    row = bs.Row(parent=app)
    column = bs.Column(parent=app)
    app._tk_root.update_idletasks()

    assert row._internal.cget("vertical_items") == "center"
    assert row._internal.cget("horizontal_items") == "left"
    assert column._internal.cget("horizontal_items") == "center"
    assert column._internal.cget("vertical_items") == "top"


def test_select_aligns_with_the_field_family(app):
    # Select is the one Field-backed widget outside `FieldAddonMixin`, so it was
    # left behind by the first pass and sat low beside real fields.
    row = bs.Row(parent=app, gap=4)
    text = bs.TextField(parent=row, label="Text")
    select = bs.Select(parent=row, label="Select", options=["x", "y"])
    number = bs.NumberField(parent=row, label="Num")
    app._tk_root.update_idletasks()

    _require(text)
    app._tk_root.update_idletasks()

    tops = {_entry_top(w) for w in (text, select, number)}
    assert len(tops) == 1, f"Select misaligned against the field family: {tops}"


# ----- row-mode containers other than Row --------------------------------------

def test_row_mode_containers_align_their_fields(app):
    # Card/GroupBox/Expander/Tabs/PageStack/SplitView/the AppShell page all used
    # to resolve an unset cross axis to 'center' themselves, which suppressed the
    # field default and left the same 9px offset inside them.
    for factory in (
        lambda: bs.Card(parent=app, layout="row", gap=4),
        lambda: bs.GroupBox(parent=app, layout="row", gap=4),
    ):
        container = factory()
        first = bs.TextField(parent=container, label="First")
        middle = bs.TextField(parent=container, label="Middle")
        app._tk_root.update_idletasks()

        _require(first)
        app._tk_root.update_idletasks()

        tops = {_entry_top(f) for f in (first, middle)}
        assert len(tops) == 1, (
            f"{type(container).__name__}(layout='row') misaligned fields: {tops}"
        )


def test_row_mode_container_still_honors_an_explicit_alignment(app):
    card = bs.Card(parent=app, layout="row", gap=4, vertical_items="center")
    first = bs.TextField(parent=card, label="First")
    app._tk_root.update_idletasks()

    assert _sticky(first) == ""


def test_column_mode_container_keeps_its_documented_cross_default(app):
    # Passing None through must not change what a column does: these containers
    # center their children horizontally, and the AppShell page stretches them.
    card = bs.Card(parent=app, layout="column", gap=4)
    label = bs.Label("x", parent=card)
    app._tk_root.update_idletasks()

    assert _sticky(label) == ""


def test_grid_mode_container_still_stretches_cells(app):
    # Grid mode has no notion of unset, so it must keep receiving real values.
    card = bs.Card(parent=app, layout="grid", columns=2, gap=4)
    label = bs.Label("x", parent=card)
    app._tk_root.update_idletasks()

    assert set(_sticky(label)) == set("nesw")  # Tk normalizes the char order


# ----- (a) the Form / grid half ------------------------------------------------

def test_form_row_stays_aligned_when_only_some_fields_are_validated(app):
    form = bs.Form(parent=app, col_count=4, items=[
        bs.FieldItem(key="first", label="First"),
        bs.FieldItem(key="middle", label="Middle"),
        bs.FieldItem(key="last", label="Last"),
        bs.FieldItem(key="suffix", label="Suffix"),
    ])
    app._tk_root.update_idletasks()

    _require(form.field("first"), "First is required")
    _require(form.field("last"), "Last is required")
    app._tk_root.update_idletasks()

    tops = {_entry_top(form.field(k)) for k in ("first", "middle", "last", "suffix")}
    assert len(tops) == 1, f"form entries misaligned: {tops}"
