"""Regression guard for #216 — an empty NumberField is representable at
construction. `NumberField(value=None)` (and `value=""`) used to raise
`ValueError: could not convert string to float: ''` while applying bounds to the
initial value: `None`/`""` flowed through to an empty string, then `float("")`
blew up. An empty numeric field must construct cleanly (it already did
post-construction — `clear()` sets `value` to `None`).
"""
import pytest

import bootstack as bs


@pytest.mark.parametrize("empty", [None, ""])
def test_numberfield_empty_constructs(app, empty):
    """Constructing an empty field does not raise; value reads back as None."""
    nf = bs.NumberField(value=empty)
    app._tk_root.update_idletasks()
    assert nf.value is None
    assert nf.text == ""


def test_numberfield_empty_with_bounds_constructs(app):
    """Bounds must not be applied to an empty value (the crash site)."""
    nf = bs.NumberField(value=None, min_value=1, max_value=10)
    app._tk_root.update_idletasks()
    assert nf.value is None


def test_numberfield_empty_then_step_uses_min(app):
    """An empty field still steps off its min/zero base — value is usable after."""
    nf = bs.NumberField(value=None, min_value=5, max_value=10)
    app._tk_root.update_idletasks()
    nf.increment()
    app._tk_root.update_idletasks()
    assert nf.value == 6  # base min (5) + one step


def test_numberfield_value_still_constructs(app):
    """A real initial value is unaffected by the empty-value guard."""
    nf = bs.NumberField(value=42, min_value=0, max_value=100)
    app._tk_root.update_idletasks()
    assert nf.value == 42
