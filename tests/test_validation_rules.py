"""Tests for the standalone ValidationRule engine and its widget/form wiring.

The rule-engine tests run headless. The App-backed tests (Signal-based compare,
field/form integration) share one module-scoped App and are marked ``gui``.
"""
from __future__ import annotations

import pytest

import bootstack as bs
from bootstack.validation import ValidationRule


@pytest.fixture(scope="module")
def shown_app():
    """A single App shared by the App-backed tests, torn down at the end."""
    app = bs.App()
    app.__enter__()
    root = app._tk_root
    root.withdraw()
    root.update_idletasks()
    try:
        yield app
    finally:
        try:
            app.__exit__(None, None, None)
        except Exception:
            pass
        try:
            root.destroy()
        except Exception:
            pass


def test_required_rejects_empty_and_whitespace():
    rule = ValidationRule("required")
    assert rule.validate("ok").is_valid
    assert not rule.validate("").is_valid
    assert not rule.validate("   ").is_valid
    assert rule.validate("").message == "This field is required."


def test_email_shape():
    rule = ValidationRule("email")
    assert rule.validate("a@b.co").is_valid
    assert not rule.validate("not-an-email").is_valid


def test_string_length_bounds():
    rule = ValidationRule("stringLength", min=3, max=5)
    assert rule.validate("abcd").is_valid
    assert not rule.validate("ab").is_valid
    assert not rule.validate("abcdef").is_valid


def test_pattern_match():
    rule = ValidationRule("pattern", pattern=r"\d{4}")
    assert rule.validate("2026").is_valid
    assert not rule.validate("26").is_valid


def test_custom_func():
    rule = ValidationRule("custom", func=lambda v: v.isdigit())
    assert rule.validate("123").is_valid
    assert not rule.validate("12a").is_valid


def test_compare_against_literal():
    rule = ValidationRule("compare", other_field="secret")
    assert rule.validate("secret").is_valid
    assert not rule.validate("nope").is_valid
    assert rule.validate("nope").message == "Values do not match."


def test_compare_against_callable():
    """A Signal — or any zero-arg callable — is read at validation time."""
    box = {"v": "abc"}
    rule = ValidationRule("compare", other_field=lambda: box["v"])
    assert rule.validate("abc").is_valid
    box["v"] = "xyz"
    assert not rule.validate("abc").is_valid     # other field changed
    assert rule.validate("xyz").is_valid


def test_compare_against_value_object():
    """An object exposing a `value` property (a field wrapper) is supported."""
    class Field:
        value = "hunter2"

    rule = ValidationRule("compare", other_field=Field())
    assert rule.validate("hunter2").is_valid
    assert not rule.validate("hunter1").is_valid


def test_compare_custom_message():
    rule = ValidationRule("compare", other_field="a", message="Passwords must match.")
    assert rule.validate("b").message == "Passwords must match."


def test_compare_default_trigger_is_blur():
    assert ValidationRule("compare", other_field="x").trigger == "blur"


@pytest.mark.gui
def test_compare_against_signal(shown_app):
    """End-to-end with a real bs.Signal as the other field."""
    other = bs.Signal("topsecret")
    rule = ValidationRule("compare", other_field=other)
    assert rule.validate("topsecret").is_valid
    other.set("changed")
    assert not rule.validate("topsecret").is_valid


# ---------- widget/form integration ----------

@pytest.mark.gui
def test_field_with_no_rules_validates_true(shown_app):
    """A field with no rules passes vacuously (regression: returned False)."""
    assert bs.TextField().validate() is True


@pytest.mark.gui
def test_form_enforces_compare_on_submit(shown_app):
    """Form.validate() must run blur-trigger rules like compare on submit."""
    form = bs.Form(data={"pw": "secret", "confirm": ""})
    form.field("confirm").add_validation_rule("compare", other_field=form.field("pw"))

    form.field("confirm").value = "WRONG"
    assert form.validate() is False
    form.field("confirm").value = "secret"
    assert form.validate() is True


@pytest.mark.gui
def test_form_enforces_string_length_on_submit(shown_app):
    """stringLength (blur trigger) is also enforced on an explicit form submit."""
    form = bs.Form(data={"name": ""})
    form.field("name").add_validation_rule("stringLength", min=3)

    form.field("name").value = "ab"
    assert form.validate() is False
    form.field("name").value = "abcd"
    assert form.validate() is True


@pytest.mark.gui
def test_form_with_unruled_fields_still_validates(shown_app):
    """Fields without rules don't block a form submit (regression for #4)."""
    form = bs.Form(data={"name": "", "note": ""})
    form.field("name").add_validation_rule("required")
    form.field("name").value = "Ada"        # note has no rules
    assert form.validate() is True
