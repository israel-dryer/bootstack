"""Value / checked / tristate coverage for the boolean controls.

`Checkbox`, `Switch`, and `ToggleButton` share `_BooleanControlBase`. These tests
lock down the public read API (`.value` / `.checked`), which previously had no
coverage — letting several state-reporting bugs ship:

- `ToggleButton(value=True).checked` returned `False` (#359): the base compared
  the backing var's *coerced* value against the Python `checked_value`, which
  only lined up for one var type.
- `Checkbox(tristate=True)` never produced an indeterminate state (#358).
- Non-bool `checked_value` (strings, ints) was silently lost on `Checkbox` /
  `Switch`, whose backing var coerced everything to `True` / `False`.

The base now reads the ttk `selected` / `alternate` state (type-agnostic) and
backs the control with a `StringVar` so on/off values round-trip verbatim.
"""
from __future__ import annotations

import pytest

import bootstack as bs


# --- Default boolean round-trip across all three controls (#359) ----------

@pytest.mark.parametrize("factory", [bs.Checkbox, bs.Switch, bs.ToggleButton])
def test_bool_value_and_checked_round_trip(app, factory):
    on = factory("w", value=True)
    off = factory("w", value=False)
    app._tk_root.update_idletasks()
    assert (on.value, on.checked) == (True, True)
    assert (off.value, off.checked) == (False, False)


@pytest.mark.parametrize("factory", [bs.Checkbox, bs.Switch, bs.ToggleButton])
def test_value_setter_updates_checked(app, factory):
    w = factory("w", value=False)
    app._tk_root.update_idletasks()
    w.value = True
    app._tk_root.update_idletasks()
    assert w.checked is True and w.value is True
    w.checked = False
    app._tk_root.update_idletasks()
    assert w.checked is False and w.value is False


# --- Non-bool checked_value / unchecked_value round-trip -------------------

@pytest.mark.parametrize("factory", [bs.Checkbox, bs.Switch, bs.ToggleButton])
def test_string_values_round_trip(app, factory):
    w = factory("w", checked_value="yes", unchecked_value="no", value="yes")
    app._tk_root.update_idletasks()
    assert w.value == "yes" and w.checked is True
    w.value = "no"
    app._tk_root.update_idletasks()
    assert w.value == "no" and w.checked is False


def test_arbitrary_string_values(app):
    # Values that are not Tcl booleans crashed the old BooleanVar backing.
    w = bs.Checkbox("w", checked_value="A", unchecked_value="B", value="A")
    app._tk_root.update_idletasks()
    assert w.value == "A" and w.checked is True


def test_int_values(app):
    w = bs.Checkbox("w", checked_value=1, unchecked_value=0, value=1)
    app._tk_root.update_idletasks()
    assert w.value == 1 and w.checked is True


# --- Checkbox tristate (#358) ---------------------------------------------

def test_tristate_starts_indeterminate(app):
    w = bs.Checkbox("w", tristate=True)
    app._tk_root.update_idletasks()
    assert w.value is None
    assert w.checked is False


def test_tristate_transitions(app):
    w = bs.Checkbox("w", tristate=True)
    app._tk_root.update_idletasks()
    for target in (True, None, False, None, True):
        w.value = target
        app._tk_root.update_idletasks()
        assert w.value is target


def test_tristate_explicit_initial_value(app):
    # tristate + an explicit value starts at that value, not indeterminate.
    w = bs.Checkbox("w", tristate=True, value=True)
    app._tk_root.update_idletasks()
    assert w.value is True


def test_click_from_indeterminate_leaves_indeterminate(app):
    w = bs.Checkbox("w", tristate=True)
    app._tk_root.update_idletasks()
    w.toggle()
    app._tk_root.update_idletasks()
    assert w.value is not None  # a user gesture resolves the indeterminate state


def test_non_tristate_never_indeterminate(app):
    # A plain checkbox with no value starts unchecked, never None.
    w = bs.Checkbox("w")
    app._tk_root.update_idletasks()
    assert w.value is False


# --- Signal binding still round-trips -------------------------------------

def test_signal_bound_value(app):
    sig = bs.Signal(True)
    w = bs.Checkbox("w", signal=sig)
    app._tk_root.update_idletasks()
    assert w.checked is True


@pytest.mark.parametrize("factory", [bs.Checkbox, bs.Switch])
def test_default_control_signal_is_boolean(app, factory):
    # A default bool control's auto-created signal carries real booleans, not
    # the Tcl "1"/"0" strings of the value-preserving StringVar backing (which
    # is only used when non-bool checked_value/unchecked_value are given).
    w = factory("w", value=True)
    app._tk_root.update_idletasks()
    assert w.signal() is True
    w.value = False
    app._tk_root.update_idletasks()
    assert w.signal() is False


def test_custom_value_signal_carries_the_value(app):
    # With custom values the signal round-trips them (matching .value), rather
    # than collapsing to a bool.
    w = bs.Checkbox("w", checked_value="yes", unchecked_value="no", value="yes")
    app._tk_root.update_idletasks()
    assert w.signal() == "yes"


# --- on_change reports the mapped (public) value ---------------------------

def test_on_change_reports_public_value(app):
    seen = []
    w = bs.Checkbox("w", checked_value="yes", unchecked_value="no")
    w.on_change(lambda e: seen.append((e.value, e.prev_value)))
    app._tk_root.update_idletasks()
    w.toggle()
    app._tk_root.update_idletasks()
    assert seen and seen[-1][0] == "yes"
