"""Regression tests for Form `editor_options` using public widget kwargs (#353).

A ``FieldItem``'s ``editor_options`` are the public editor widget's keyword
arguments — e.g. ``NumberField(step=)``, ``TextArea(show_border=)``,
``TextField(mask=)`` — not the internal Tk option names. Before the fix, the
Form built the internal impl widgets directly, so public names such as ``step``
raised ``TclError: unknown option "-step"`` and ``textarea`` (a raw ``tk.Text``)
could not accept ``show_border`` at all.
"""
from __future__ import annotations

import pytest

import bootstack as bs
from bootstack.errors import BootstackError


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


# --- add_validation_rule on the returned editor (#356) -------------------
#
# `field()` returns the public wrapper. That wrapper must still expose
# `add_validation_rule`, or the documented pattern
# `form.field(key).add_validation_rule("required", ...)` breaks. It regressed
# for `select` in 0.1.3: the wrapper swap dropped the method the internal
# SelectBox composite had inherited (the *Field wrappers keep it via the field
# mixin, so only the select editor lost it).

def test_select_field_exposes_add_validation_rule(app):
    form = bs.Form(items=[bs.FieldItem(key="state", label="State", editor="select",
                                       editor_options={"values": ["AL", "AK", "AZ"]})])
    app._tk_root.update_idletasks()
    assert hasattr(form.field("state"), "add_validation_rule")


def test_select_field_validation_rule_is_enforced(app):
    # The rule added on the returned Select must actually drive form.validate()
    # and surface its custom message — not just avoid the AttributeError.
    form = bs.Form(items=[bs.FieldItem(key="state", label="State", editor="select",
                                       editor_options={"values": ["AL", "AK", "AZ"]})])
    app._tk_root.update_idletasks()
    form.field("state").add_validation_rule(
        "required", message="State is required", trigger="blur")

    # Empty -> invalid, with the custom message.
    assert form.validate() is False
    assert form.errors.get("state") == "State is required"

    # Filled -> valid, error cleared.
    form.set_field_value("state", "AK")
    app._tk_root.update_idletasks()
    assert form.validate() is True
    assert "state" not in form.errors


def test_select_rule_uses_live_default_trigger(app):
    # A rule added without an explicit trigger must adopt the rule type's
    # sensible live default (required -> "always"), matching the field family.
    # Regression guard: a hardcoded "change" default (not a real trigger) made
    # live blur/key validation a silent no-op on Select while every other field
    # validated live.
    form = bs.Form(items=[bs.FieldItem(key="state", label="State", editor="select",
                                       editor_options={"values": ["AL", "AK", "AZ"]})])
    app._tk_root.update_idletasks()
    form.field("state").add_validation_rule("required", message="Required")

    entry = form.field("state")._internal._entry
    # Stored trigger is a real live trigger, not the bogus "change".
    assert entry._rules[-1].trigger in ("always", "blur", "key")
    # A blur-scoped run actually evaluates the rule (a no-op under "change").
    assert entry.validate(entry._get_validation_value(), trigger="blur") is False

# --- `tristate` and a `value` seed in editor_options (#358 follow-up) -----

def test_checkbox_tristate_starts_indeterminate(app):
    # Reported repro: a tristate checkbox editor rendered (and read) as
    # unchecked because the Form coerced the absent form value to False,
    # which the widget treats as an explicit "off" seed.
    form = bs.Form(items=[bs.FieldItem(key="contact", editor="checkbox",
                                       editor_options={"tristate": True})])
    app._tk_root.update_idletasks()
    field = form.field("contact")
    assert field.value is None
    assert field.checked is False


def test_checkbox_without_tristate_starts_unchecked(app):
    form = bs.Form(items=[bs.FieldItem(key="contact", editor="checkbox")])
    app._tk_root.update_idletasks()
    assert form.field("contact").value is False


def test_editor_options_value_seeds_the_editor(app):
    # Reported repro: any editor_options={'value': ...} raised
    # "got multiple values for keyword argument 'value'".
    form = bs.Form(items=[
        bs.FieldItem(key="name", editor="textfield", editor_options={"value": "Ada"}),
        bs.FieldItem(key="on", editor="checkbox", editor_options={"value": True}),
    ])
    app._tk_root.update_idletasks()
    assert form.field("name").value == "Ada"
    assert form.field("on").value is True


def test_form_data_wins_over_editor_options_value(app):
    form = bs.Form(data={"n": 41},
                   items=[bs.FieldItem(key="n", editor="numberfield",
                                       editor_options={"value": 7})])
    app._tk_root.update_idletasks()
    assert form.field("n").value == 41


def test_falsy_data_value_is_not_blanked(app):
    # A falsy-but-real datum is a value, not an absent one. Testing it for
    # truthiness blanked it in the editor and then synced the blank back into
    # the form data, silently destroying the record value.
    form = bs.Form(data={"code": 0},
                   items=[bs.FieldItem(key="code", editor="textfield")])
    app._tk_root.update_idletasks()
    assert form.field("code").value == "0"
    assert form.data["code"] == "0"


def test_falsy_value_survives_on_the_widget_itself(app):
    # The blanking lived in the field wrapper, one layer below the form.
    assert bs.TextField(value=0).value == "0"
    assert bs.PasswordField(value=0).value == "0"


def test_non_string_data_keeps_its_type(app):
    # `data` is the caller's record. Stringifying it to dodge the falsy bug
    # flipped a Decimal or a date to `str` in `form.data` at construction,
    # before the user had edited anything — and DataTable's edit dialog is a
    # Form, so a submit wrote the stringified value back to the source.
    from datetime import date
    from decimal import Decimal

    form = bs.Form(data={"amount": Decimal("3.50"), "when": date(2020, 1, 2)},
                   items=[bs.FieldItem(key="amount", editor="textfield"),
                          bs.FieldItem(key="when", editor="textfield")])
    app._tk_root.update_idletasks()
    assert form.data["amount"] == Decimal("3.50")
    assert form.data["when"] == date(2020, 1, 2)


def test_switch_editor_defaults_to_off(app):
    # The tristate fix seeds checkbox AND switch with `value=None`; Switch has
    # no tristate, so it must fall through to its unchecked value.
    form = bs.Form(items=[bs.FieldItem(key="s", editor="switch")])
    app._tk_root.update_idletasks()
    assert form.field("s").value is False
    assert form.data["s"] is False


def test_checkbox_editor_options_can_override_the_caption(app):
    # The boolean controls call their caption `label`; passing it positionally
    # made a `label` option collide instead of override.
    form = bs.Form(items=[bs.FieldItem(key="c", label="Ignored", editor="checkbox",
                                       editor_options={"label": "Contact me"})])
    app._tk_root.update_idletasks()
    assert form.field("c")._internal.cget("text") == "Contact me"


def test_spinnerfield_items_alias_reaches_the_widget(app):
    form = bs.Form(items=[bs.FieldItem(key="s", editor="spinnerfield",
                                       editor_options={"items": [1, 2, 3]})])
    app._tk_root.update_idletasks()
    assert list(form.field("s")._internal.cget("values")) == ["1", "2", "3"]


def test_select_items_alias_wins_over_values(app):
    # Both aliases name the same list; `items` is documented first, so it wins
    # and the redundant `values` must not leak into the editor's constructor.
    form = bs.Form(items=[bs.FieldItem(key="s", editor="select",
                                       editor_options={"items": ["a"], "values": ["b"]})])
    app._tk_root.update_idletasks()
    assert [o["value"] for o in form.field("s").options] == ["a"]


def test_editor_options_override_form_defaults(app):
    # editor_options are the editor's public kwargs, so an option naming a
    # parameter the Form also fills must OVERRIDE it, not raise
    # "got multiple values for keyword argument".
    form = bs.Form(items=[
        bs.FieldItem(key="n", label="Name", editor="textfield",
                     editor_options={"label": "Full name"}),
        bs.FieldItem(key="s", editor="select",
                     editor_options={"options": ["a", "b"]}),
    ])
    app._tk_root.update_idletasks()
    assert form.field("n")._internal.label_widget.cget("text") == "Full name"
    assert [o["value"] for o in form.field("s").options] == ["a", "b"]


def test_editor_options_cannot_reparent_the_field(app):
    # `parent` is structural: the field container owns placement. Setting it
    # raises a clear error naming the option, not a TypeError from an internal
    # class the caller never wrote.
    stray = bs.Column()
    with pytest.raises(BootstackError, match="editor_options"):
        bs.Form(items=[bs.FieldItem(key="n", editor="textfield",
                                    editor_options={"parent": stray})])
