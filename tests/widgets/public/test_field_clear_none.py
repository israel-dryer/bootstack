"""Regression tests for clearing a field with `None` (#387).

`TextEntryPart.value()` is a combined getter/setter that used `None` as its
"no argument passed" sentinel, so `entry.value(None)` returned the current
value instead of clearing. Every public path down to it inherited the no-op:
`DateField.value = None`, `DateField.clear()` (which passes `None`), and
`Form.set({key: None})`.

Passing `''` worked and was the accidental workaround — it reaches the same
set branch, which already mapped an empty string to a `None` value. The setter
was never broken; only the door was locked.

Filed from discussion #386.
"""
from __future__ import annotations

from datetime import date, time

import pytest

import bootstack as bs


# --- The reported bug: DateField cannot be cleared ----------------------

def test_datefield_value_none_clears(app):
    # Reported repro: `.value = None` left the previous date in place.
    field = bs.DateField(value=date(2024, 5, 5))
    app._tk_root.update_idletasks()

    field.value = None

    assert field.value is None


def test_datefield_clear_method_clears(app):
    # `clear()` is implemented as `self._internal.value = None`, so the public
    # method was a silent no-op too.
    field = bs.DateField(value=date(2024, 5, 5))
    app._tk_root.update_idletasks()

    field.clear()

    assert field.value is None


def test_datefield_clear_empties_the_display(app):
    # A cleared value with stale text on screen would not be a usable clear.
    field = bs.DateField(value=date(2024, 5, 5))
    app._tk_root.update_idletasks()

    field.clear()

    assert field.text == ""


# --- The whole family agrees on `None` ----------------------------------

@pytest.mark.parametrize("factory, seed", [
    (bs.DateField, date(2024, 5, 5)),
    (bs.TimeField, time(9, 30)),
    (bs.TextField, "hello"),
    (bs.NumberField, 42),
    (bs.PathField, "C:/tmp"),
    (bs.SpinnerField, 3),
])
def test_value_none_clears_every_field(app, factory, seed):
    field = factory(value=seed)
    app._tk_root.update_idletasks()
    assert field.value == seed or field.value is not None

    field.value = None

    assert field.value is None
    assert field.text == ""


@pytest.mark.parametrize("factory, seed", [
    (bs.DateField, date(2024, 5, 5)),
    (bs.TimeField, time(9, 30)),
    (bs.TextField, "hello"),
    (bs.NumberField, 42),
    (bs.PathField, "C:/tmp"),
    (bs.SpinnerField, 3),
])
def test_clear_method_empties_every_field(app, factory, seed):
    field = factory(value=seed)
    app._tk_root.update_idletasks()

    field.clear()

    assert field.value is None
    assert field.text == ""


# --- The `''` path must keep working ------------------------------------

def test_empty_string_still_clears(app):
    # The pre-fix workaround stays valid — `''` and `None` agree.
    field = bs.DateField(value=date(2024, 5, 5))
    app._tk_root.update_idletasks()

    field.value = ""

    assert field.value is None
    assert field.text == ""


# --- Reading still works with no argument -------------------------------

def test_no_argument_still_reads_the_value(app):
    # Deliberately exercises the internal accessor: the fix swapped its "no
    # argument passed" sentinel, so the getter half needs its own cover. The
    # public `.value` property below is the path users take.
    field = bs.TextField(value="hello")
    app._tk_root.update_idletasks()

    assert field._entry_widget().value() == "hello"
    assert field.value == "hello"


# --- Form-level clearing (the reporter's `clear_form` loop) --------------

def test_form_set_none_clears_a_date_field(app):
    form = bs.Form(items=[
        bs.FieldItem(key="d", label="D", editor="datefield",
                     editor_options={"value": date(2024, 5, 5)}),
    ])
    app._tk_root.update_idletasks()

    form.set({"d": None})

    assert form.get()["d"] is None


def test_form_clear_loop_empties_every_field(app):
    # The shape of the reporter's clear_form(): read the keys, write None back.
    form = bs.Form(items=[
        bs.FieldItem(key="name", label="Name"),
        bs.FieldItem(key="d", label="D", editor="datefield",
                     editor_options={"value": date(2024, 5, 5)}),
    ])
    app._tk_root.update_idletasks()
    form.set({"name": "Bob"})

    form.set({key: None for key in form.get()})

    assert form.get() == {"name": None, "d": None}
