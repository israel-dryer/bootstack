"""Field validation runs against the field's typed value.

Phase 1 of the validation-system redesign (docs/_dev/field-validation-system.md):
validation resolves the current input to its typed value — a number for a
numeric field, a date for a date field, the string itself for a text field —
and all seven field wrappers route their `validate()` through the same resolver.

Regression guard for the bug surfaced by the TextField review: a string rule on
a NumberField used to crash (`validate()` passed the raw `float` into `len()`),
and `custom` rules received the display text instead of the typed value.
"""
import datetime

import pytest

import bootstack as bs
from bootstack.validation import ValidationRule


def test_string_rule_is_crash_safe_on_typed_value():
    # Fields reject text rules on typed values at attach time (see the
    # rejection test below), but the rule itself must still never crash if
    # handed a non-string — the original bug was len()/re.match on a float.
    assert ValidationRule("stringLength", min=3).validate(1234.5).is_valid in (True, False)
    assert ValidationRule("pattern", pattern=r"\d+").validate(1234).is_valid in (True, False)
    assert ValidationRule("email").validate(None).is_valid in (True, False)


def test_numberfield_custom_rule_receives_number(app):
    seen = {}
    nf = bs.NumberField(value=1500, value_format="#,##0.00")
    nf.add_validation_rule(
        "custom",
        func=lambda v: seen.update(type=type(v).__name__, value=v) or v >= 1000,
    )
    app._tk_root.update_idletasks()
    assert nf.validate() is True
    assert seen["type"] in ("int", "float")
    assert seen["value"] == 1500


def test_plain_numberfield_custom_gets_numeric_not_string(app):
    # No value_format: the internal parse yields a string; the resolver must
    # still coerce it to a number for the rule.
    got = {}
    nf = bs.NumberField(value=42)
    nf.add_validation_rule(
        "custom",
        func=lambda v: got.update(type=type(v).__name__, value=v) or v >= 100,
    )
    app._tk_root.update_idletasks()
    assert nf.validate() is False
    assert got["type"] in ("int", "float")
    assert got["value"] == 42


def test_datefield_custom_rule_receives_date(app):
    seen = {}
    df = bs.DateField(value="2024-06-01")
    df.add_validation_rule("custom", func=lambda v: seen.update(t=type(v).__name__) or True)
    app._tk_root.update_idletasks()
    df.validate()
    assert seen["t"] in ("date", "datetime")


def test_textfield_string_length_still_works(app):
    tf = bs.TextField(value="ab")
    tf.add_validation_rule("stringLength", min=3, message="need 3")
    app._tk_root.update_idletasks()
    assert tf.validate() is False
    tf.value = "abcd"
    app._tk_root.update_idletasks()
    assert tf.validate() is True


def test_textfield_validates_live_input_not_committed(app):
    # Manual validate() must see what is currently typed, not the last commit.
    tf = bs.TextField(value="ab")
    tf.add_validation_rule("stringLength", min=3, trigger="manual")
    app._tk_root.update_idletasks()
    assert tf.validate() is False
    # Change the displayed text without committing (no blur / Enter).
    tf._internal._entry.text("abcd")
    app._tk_root.update_idletasks()
    assert tf.validate() is True


def test_required_rule_is_type_agnostic(app):
    # `required` runs against the typed value (the number 5), no string ops.
    nf = bs.NumberField(value=5)
    nf.add_validation_rule("required")
    app._tk_root.update_idletasks()
    assert nf.validate() is True
    nf.clear()  # value becomes None (an empty field)
    app._tk_root.update_idletasks()
    assert nf.validate() is False


def test_add_validation_rule_rejects_rule_object(app):
    # The silent double-wrap (ValidationRule inside ValidationRule -> never
    # validates) now raises a clear TypeError instead.
    tf = bs.TextField()
    with pytest.raises(TypeError):
        tf.add_validation_rule(ValidationRule("stringLength", min=3))


# --- Phase 2: range rule + attach-time dtype rejection ---


def test_range_rule_on_numberfield(app):
    nf = bs.NumberField(value=25)
    nf.add_validation_rule("range", min=18, message="must be 18+")
    app._tk_root.update_idletasks()
    assert nf.validate() is True
    nf.value = 10
    app._tk_root.update_idletasks()
    assert nf.validate() is False


def test_range_rule_on_datefield_with_date_bounds(app):
    df = bs.DateField(value="2024-06-01")
    df.add_validation_rule(
        "range", min=datetime.date(2024, 1, 1), max=datetime.date(2024, 12, 31)
    )
    app._tk_root.update_idletasks()
    assert df.validate() is True


def test_range_rule_empty_field_is_not_out_of_range(app):
    # An empty field passes range; use 'required' to demand presence.
    nf = bs.NumberField(value=5)
    nf.add_validation_rule("range", min=1)
    nf.clear()
    app._tk_root.update_idletasks()
    assert nf.validate() is True


@pytest.mark.parametrize(
    "factory, rule",
    [
        (lambda: bs.NumberField(value=1), "stringLength"),
        (lambda: bs.NumberField(value=1), "email"),
        (lambda: bs.NumberField(value=1), "pattern"),
        (lambda: bs.DateField(value="2024-01-01"), "email"),
        (lambda: bs.TextField(), "range"),
    ],
)
def test_inapplicable_rule_rejected_at_attach(app, factory, rule):
    from bootstack.errors import BootstackError

    field = factory()
    app._tk_root.update_idletasks()
    with pytest.raises(BootstackError):
        field.add_validation_rule(rule)


@pytest.mark.parametrize(
    "factory, rule, kwargs",
    [
        (lambda: bs.TextField(), "stringLength", {"min": 3}),
        (lambda: bs.TextField(), "email", {}),
        (lambda: bs.NumberField(value=1), "range", {"min": 0}),
        (lambda: bs.NumberField(value=1), "custom", {"func": lambda v: v > 0}),
        (lambda: bs.DateField(value="2024-01-01"), "required", {}),
        (lambda: bs.TimeField(value="08:30"), "required", {}),
    ],
)
def test_applicable_rule_attaches_cleanly(app, factory, rule, kwargs):
    field = factory()
    app._tk_root.update_idletasks()
    field.add_validation_rule(rule, **kwargs)  # no exception


# --- Phase 3: reactive validity surface ---


def test_valid_and_error_signals_track_validation(app):
    tf = bs.TextField(value="ab", message="helper")
    tf.add_validation_rule("stringLength", min=3, message="need 3+")
    app._tk_root.update_idletasks()

    assert tf.valid() is True  # nothing run yet
    assert tf.error() == ""

    assert tf.validate() is False
    app._tk_root.update_idletasks()
    assert tf.valid() is False
    assert tf.error() == "need 3+"

    tf.value = "abcd"
    app._tk_root.update_idletasks()
    assert tf.validate() is True
    app._tk_root.update_idletasks()
    assert tf.valid() is True
    assert tf.error() == ""


def test_error_signal_is_subscribable(app):
    tf = bs.TextField(value="x")
    tf.add_validation_rule("stringLength", min=3, message="too short")
    app._tk_root.update_idletasks()
    seen = []
    tf.error.subscribe(seen.append)
    tf.validate()
    app._tk_root.update_idletasks()
    assert seen == ["too short"]


def test_error_signal_binds_to_a_label(app):
    tf = bs.TextField(value="x")
    tf.add_validation_rule("stringLength", min=3, message="too short")
    app._tk_root.update_idletasks()
    lbl = bs.Label(textsignal=tf.error)
    tf.validate()
    app._tk_root.update_idletasks()
    assert lbl.text == "too short"


def test_on_invalid_event_still_fires(app):
    # The event API stays alongside the signals.
    tf = bs.TextField(value="x")
    tf.add_validation_rule("stringLength", min=3, message="too short")
    app._tk_root.update_idletasks()
    fired = []
    tf.on_invalid(lambda e: fired.append(e.message))
    tf.validate()
    app._tk_root.update_idletasks()
    assert fired == ["too short"]


def test_form_validate_updates_field_validity_signal(app):
    # Regression: the message label follows the error signal, so a form-level
    # validate must update it (not just emit events).
    form = bs.Form(items=[bs.FieldItem(key="name", label="Name", required=True)])
    app._tk_root.update_idletasks()
    entry = form.field("name")._entry

    assert form.validate() is False
    app._tk_root.update_idletasks()
    assert entry._error_signal() == "This field is required."
    assert entry._valid_signal() is False

    form.field("name").value = "Alice"
    app._tk_root.update_idletasks()
    assert form.validate() is True
    app._tk_root.update_idletasks()
    assert entry._error_signal() == ""
