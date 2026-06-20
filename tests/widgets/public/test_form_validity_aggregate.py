"""Reactive form-level validity aggregate (#217, phase 3b of the validation
redesign). `Form.valid` is a `Signal[bool]` AND-ed over the member fields'
`valid` signals; `Form.errors` is a live dict of key -> message. Both build on
the field-level reactive signals shipped in phase 3 (PR #218).
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


def test_form_valid_aggregates_field_validity(app):
    form = bs.Form(items=[
        {"key": "name", "required": True},
        {"key": "email", "required": True},
    ])
    app._tk_root.update_idletasks()

    # A field is valid until proven otherwise, so the form reads valid up front.
    assert form.valid() is True
    assert form.errors == {}

    # A full pass with both fields empty fails; both keys carry a message.
    assert form.validate() is False
    assert form.valid() is False
    assert set(form.errors) == {"name", "email"}
    assert form.errors["name"]  # non-empty message

    # Fill both, re-validate -> valid, no errors.
    form.set_field_value("name", "Ada")
    form.set_field_value("email", "ada@example.com")
    assert form.validate() is True
    assert form.valid() is True
    assert form.errors == {}


def test_form_valid_is_reactive_to_a_single_field(app):
    # The aggregate updates from one field's validation path, without a
    # form-wide validate() call — proving the signal subscription, not a poll.
    form = bs.Form(items=[{"key": "name", "required": True}])
    app._tk_root.update_idletasks()

    seen = []
    form.valid.subscribe(seen.append)

    entry = form.field("name")._entry
    entry.validate("", trigger="manual")  # empty fails 'required'
    app._tk_root.update_idletasks()
    assert form.valid() is False
    assert seen and seen[-1] is False

    entry.validate("Ada", trigger="manual")
    app._tk_root.update_idletasks()
    assert form.valid() is True
    assert seen[-1] is True


def test_form_with_no_validation_is_always_valid(app):
    form = bs.Form(items=[{"key": "name"}, {"key": "active", "dtype": "bool"}])
    app._tk_root.update_idletasks()
    assert form.valid() is True
    assert form.errors == {}
    # validate() with no rules passes and leaves the aggregate valid.
    assert form.validate() is True
    assert form.valid() is True


def test_form_errors_track_partial_validity(app):
    form = bs.Form(items=[
        {"key": "name", "required": True},
        {"key": "city", "required": True},
    ])
    app._tk_root.update_idletasks()

    form.set_field_value("name", "Ada")  # city left empty
    assert form.validate() is False
    assert form.valid() is False
    assert set(form.errors) == {"city"}  # only the empty field reports
