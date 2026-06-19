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


def test_numberfield_string_rule_does_not_crash(app):
    # Was a hard TypeError: len() on a float / re.match on a float.
    nf = bs.NumberField(value=1234.5, value_format="#,##0.00")
    nf.add_validation_rule("stringLength", min=3, max=20, trigger="manual")
    app._tk_root.update_idletasks()
    assert nf.validate() is True  # no exception


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
