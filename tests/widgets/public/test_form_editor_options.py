"""Regression tests for Form `editor_options` using public widget kwargs (#353).

A ``FieldItem``'s ``editor_options`` are the public editor widget's keyword
arguments — e.g. ``NumberField(step=)``, ``TextArea(show_border=)``,
``TextField(mask=)`` — not the internal Tk option names. Before the fix, the
Form built the internal impl widgets directly, so public names such as ``step``
raised ``TclError: unknown option "-step"`` and ``textarea`` (a raw ``tk.Text``)
could not accept ``show_border`` at all.
"""
from __future__ import annotations

import bootstack as bs


# --- The two scenarios reported in discussion #353 -----------------------

def test_numberfield_step_option_accepted(app):
    # Reported repro: editor_options={'step': 10} raised TclError before the fix.
    form = bs.Form(items=[bs.FieldItem(key="n", label="N", editor="numberfield",
                                       editor_options={"step": 10})])
    app._tk_root.update_idletasks()
    assert type(form.field("n")).__name__ == "NumberField"


def test_numberfield_step_takes_effect(app):
    # The public option is not just accepted — it drives the stepper.
    form = bs.Form(data={"n": 5},
                   items=[bs.FieldItem(key="n", editor="numberfield",
                                       editor_options={"step": 10})])
    app._tk_root.update_idletasks()
    field = form.field("n")
    field.increment()
    assert field.value == 15


def test_textarea_show_border_option_accepted(app):
    # Reported repro: editor_options={'show_border': True} raised TclError before
    # the fix because the textarea editor was a raw tk.Text.
    form = bs.Form(items=[bs.FieldItem(key="c", label="Comments", editor="textarea",
                                       editor_options={"height": 5, "show_border": True})])
    app._tk_root.update_idletasks()
    assert type(form.field("c")).__name__ == "TextArea"


# --- Other public option names that leaked internal names before ---------

def test_numberfield_bounds_and_steppers(app):
    form = bs.Form(items=[bs.FieldItem(key="n", editor="numberfield",
                                       editor_options={"min_value": 0, "max_value": 100,
                                                       "show_steppers": False})])
    app._tk_root.update_idletasks()
    assert type(form.field("n")).__name__ == "NumberField"


def test_textfield_mask_option(app):
    form = bs.Form(items=[bs.FieldItem(key="pin", editor="textfield",
                                       editor_options={"mask": "*"})])
    app._tk_root.update_idletasks()
    assert type(form.field("pin")).__name__ == "TextField"


def test_slider_bounds_options(app):
    form = bs.Form(items=[bs.FieldItem(key="s", editor="slider",
                                       editor_options={"min_value": 0, "max_value": 10})])
    app._tk_root.update_idletasks()
    assert type(form.field("s")).__name__ == "Slider"


def test_select_values_alias_round_trips(app):
    # The documented `values`/`items` alias maps to Select(options=...).
    form = bs.Form(data={"role": "B"},
                   items=[bs.FieldItem(key="role", editor="select",
                                       editor_options={"values": ["A", "B", "C"],
                                                       "allow_custom_values": True})])
    app._tk_root.update_idletasks()
    assert type(form.field("role")).__name__ == "Select"
    assert form.get()["role"] == "B"


# --- The dict-item shape that DataTable feeds through Form ----------------

def test_public_option_names_via_dict_items(app):
    # DataTable's add/edit dialog builds Form items as dicts; the same public
    # `editor_options` must work through that shape.
    form = bs.Form(items=[
        {"key": "n", "editor": "numberfield", "editor_options": {"step": 5}},
        {"key": "c", "editor": "textarea", "editor_options": {"show_border": True}},
    ])
    app._tk_root.update_idletasks()
    assert type(form.field("n")).__name__ == "NumberField"
    assert type(form.field("c")).__name__ == "TextArea"


def test_datatable_column_editor_options_build_form(app):
    # A DataTable column's editor_options (public names) must produce a buildable
    # add/edit Form — the same code path, exercised end to end.
    dt = bs.DataTable(
        rows=[{"n": 1}],
        columns=[{"key": "n", "editor": "numberfield", "editor_options": {"step": 10}}],
    )
    app._tk_root.update_idletasks()
    items = dt._internal._build_form_items()
    form = bs.Form(items=items)  # would raise TclError on the old internal path
    app._tk_root.update_idletasks()
    assert type(form.field("n")).__name__ == "NumberField"


# --- Value round-trip parity ---------------------------------------------

def test_datatable_bool_column_builds_edit_form(app):
    # A DataTable bool column becomes a checkbox editor; the table injects
    # `show_message` into every column's editor_options. That internal-only
    # option must be stripped so the strict Checkbox wrapper doesn't raise.
    dt = bs.DataTable(parent=app, rows=[{"ok": True}], columns=[{"key": "ok", "dtype": "bool"}])
    app._tk_root.update_idletasks()
    items = dt._internal._build_form_items()
    assert items[0]["editor_options"].get("show_message") is True  # table injects it
    form = bs.Form(items=items)  # used to raise TypeError on Checkbox(show_message=)
    app._tk_root.update_idletasks()
    assert type(form.field("ok")).__name__ == "Checkbox"


def test_slider_editor_renders_a_label(app):
    # Slider has no `label` parameter, so the Form renders a stacked caption.
    form = bs.Form(items=[bs.FieldItem(key="vol", label="Volume", editor="slider")])
    app._tk_root.update_idletasks()
    found = []

    def _walk(w):
        for c in w.winfo_children():
            try:
                if "label" in c.winfo_class().lower() and c.cget("text") == "Volume":
                    found.append(True)
            except Exception:
                pass
            _walk(c)

    _walk(form._internal if hasattr(form, "_internal") else form)
    assert found, "slider field label 'Volume' was not rendered"


def test_programmatic_set_does_not_notify(app):
    # A programmatic write must not report as a user edit — including for
    # `select`, whose change event is delivered asynchronously (when="tail").
    calls = []
    form = bs.Form(
        data={"c": "US"},
        items=[bs.FieldItem(key="c", editor="select",
                            editor_options={"values": ["US", "CA"]})],
        on_data_change=lambda d: calls.append(dict(d)),
    )
    app._tk_root.update_idletasks()
    calls.clear()
    form.set_field_value("c", "CA")
    for _ in range(3):
        app._tk_root.update()  # flush any deferred change events
    assert calls == []
    assert form.get()["c"] == "CA"


def test_value_roundtrip_across_editors(app):
    form = bs.Form(
        data={"name": "Ada", "age": 30, "active": True},
        items=[
            bs.FieldItem(key="name", editor="textfield"),
            bs.FieldItem(key="age", editor="numberfield", dtype="int"),
            bs.FieldItem(key="active", editor="checkbox", dtype="bool"),
        ],
    )
    app._tk_root.update_idletasks()
    assert form.get() == {"name": "Ada", "age": 30, "active": True}
    form.set({"name": "Grace", "age": 45, "active": False})
    app._tk_root.update_idletasks()
    assert form.get() == {"name": "Grace", "age": 45, "active": False}