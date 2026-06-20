"""A TimeField with no value starts empty, like the rest of the field family.

It used to default to the current time (`datetime.now().time()`), which made it
the only field that didn't start empty and silently defeated `required=True`
(the field was pre-filled, so validation passed with no user input). Pass an
explicit `value=` to seed a starting time.
"""
import datetime as dt

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


def test_timefield_starts_empty(app):
    tf = bs.TimeField()
    app._tk_root.update_idletasks()
    assert tf.value is None
    assert tf.text == ""


def test_required_empty_timefield_is_invalid(app):
    # required must actually demand input — it used to auto-pass when the field
    # silently pre-filled to the current time.
    tf = bs.TimeField(required=True)
    app._tk_root.update_idletasks()
    assert tf.validate() is False


@pytest.mark.parametrize("seed,expected", [
    ("14:30", dt.time(14, 30)),
    (dt.time(9, 0), dt.time(9, 0)),
])
def test_explicit_value_still_seeds(app, seed, expected):
    tf = bs.TimeField(value=seed)
    app._tk_root.update_idletasks()
    assert tf.value == expected
