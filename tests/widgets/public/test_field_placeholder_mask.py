"""Guards for what a visible placeholder is — and is not.

A placeholder is a readable hint, never user input. Two consequences are pinned
here: it renders unmasked under an input mask (#195 — a password bullet must not
turn the hint into dots), and it reads as EMPTY everywhere a field reports its
contents, so `required` does not pass on an untouched field and `text` agrees
with `value`.
"""
import pytest

import bootstack as bs


def test_password_placeholder_renders_unmasked(app):
    pf = bs.PasswordField(placeholder="Enter password")
    app._tk_root.update_idletasks()
    entry = pf._internal._entry

    # Empty + unfocused: placeholder shows in plain text, mask is suppressed.
    assert entry._showing_placeholder is True
    assert entry.cget("show") == ""
    assert entry.get() == "Enter password"


def test_password_mask_restored_for_real_input(app):
    pf = bs.PasswordField(placeholder="Enter password")
    app._tk_root.update_idletasks()
    entry = pf._internal._entry

    # Focus + type: placeholder is gone and the mask is back.
    entry.event_generate("<FocusIn>")
    entry.insert(0, "hunter2")
    app._tk_root.update_idletasks()
    assert entry._showing_placeholder is False
    assert entry.cget("show") == "•"  # the bullet mask
    assert entry.get() == "hunter2"


def test_password_placeholder_returns_unmasked_after_clearing(app):
    pf = bs.PasswordField(placeholder="Enter password")
    app._tk_root.update_idletasks()
    entry = pf._internal._entry

    entry.event_generate("<FocusIn>")
    entry.insert(0, "abc")
    app._tk_root.update_idletasks()
    entry.delete(0, "end")
    entry.event_generate("<FocusOut>")
    app._tk_root.update_idletasks()

    # Empty again: placeholder is back and unmasked.
    assert entry._showing_placeholder is True
    assert entry.cget("show") == ""
    assert entry.get() == "Enter password"


def test_visibility_toggle_does_not_mask_placeholder(app):
    # Pressing the eye toggle while the placeholder is showing must not re-mask it.
    pf = bs.PasswordField(placeholder="Enter password")
    app._tk_root.update_idletasks()
    entry = pf._internal._entry

    pf._internal._show_password(None)
    pf._internal._hide_password(None)
    app._tk_root.update_idletasks()

    assert entry._showing_placeholder is True
    assert entry.cget("show") == ""
    assert entry.get() == "Enter password"


def test_textfield_placeholder_unaffected_without_mask(app):
    # A plain field has no mask; placeholder still shows and clears normally.
    tf = bs.TextField(placeholder="Search...")
    app._tk_root.update_idletasks()
    entry = tf._internal._entry

    assert entry._showing_placeholder is True
    assert entry.cget("show") == ""
    assert entry.get() == "Search..."

    entry.event_generate("<FocusIn>")
    entry.insert(0, "query")
    app._tk_root.update_idletasks()
    assert entry._showing_placeholder is False
    assert entry.cget("show") == ""
    assert entry.get() == "query"


# --- A visible placeholder is not input, for validation either --------------

def test_required_field_with_placeholder_is_invalid_while_empty(app):
    # The placeholder is inserted into the entry to render it, and validation
    # read that raw text — so `required` saw the hint, passed, and an untouched
    # field submitted empty. `required=` + `placeholder=` is a common pairing,
    # so this silently defeated required across forms.
    field = bs.TextField(placeholder="Enter a name", required=True)
    app._tk_root.update_idletasks()
    assert field.validate() is False


def test_form_blocks_submit_on_empty_required_field_with_placeholder(app):
    form = bs.Form(items=[bs.FieldItem(key="name", label="Name", required=True,
                                       editor_options={"placeholder": "Enter a name"})])
    app._tk_root.update_idletasks()
    assert form.validate() is False
    assert "name" in form.errors


@pytest.mark.parametrize("rule, kwargs", [
    # Each rule REJECTS the placeholder text but ACCEPTS an empty field, so a
    # leaked hint flips the result. (`Hint` is 4 characters and not a number;
    # an empty field skips a format rule entirely — see `required` for
    # presence.) A rule the hint would satisfy, such as `min=3`, could not tell
    # the two apart and would prove nothing.
    ("stringLength", {"max": 2}),
    ("pattern", {"pattern": r"^\d+$"}),
])
def test_placeholder_field_validates_like_an_empty_one(app, rule, kwargs):
    # The invariant: a field showing its placeholder behaves exactly as a
    # genuinely empty one — for every rule, not just `required`. Assert the
    # concrete outcome, not just that the two agree: comparing two fields that
    # are both invalid for unrelated reasons proves nothing.
    plain, holder = bs.TextField(), bs.TextField(placeholder="Hint")
    plain.add_validation_rule(rule, **kwargs)
    holder.add_validation_rule(rule, **kwargs)
    app._tk_root.update_idletasks()
    plain_result, holder_result = plain.validate(), holder.validate()
    assert holder_result is True, f"{rule} saw the placeholder as input"
    assert plain_result is holder_result, f"{rule} differs with a placeholder"


def test_text_reports_empty_while_the_placeholder_shows(app):
    # `text` and `value` are a contract pair. `text` read the widget's raw
    # contents, which is where the hint physically lives, so it reported the
    # hint as though the user had typed it while `value` said empty.
    field = bs.TextField(placeholder="Enter a name")
    app._tk_root.update_idletasks()
    assert field.text == ""
    assert field.value == ""
    field.value = "Ada"
    app._tk_root.update_idletasks()
    assert field.text == "Ada"


def test_real_input_still_validates_through_a_placeholder_field(app):
    field = bs.TextField(placeholder="Hint", required=True)
    app._tk_root.update_idletasks()
    field.value = "Ada"
    app._tk_root.update_idletasks()
    assert field.validate() is True
    assert field.value == "Ada"


def test_masked_field_with_placeholder_validates_when_filled(app):
    pf = bs.PasswordField(placeholder="Password", required=True)
    app._tk_root.update_idletasks()
    assert pf.validate() is False
    pf.value = "hunter2"
    app._tk_root.update_idletasks()
    assert pf.validate() is True
