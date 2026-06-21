"""SpinnerField increment()/decrement() parity with NumberField (#234).

SpinnerField gains the programmatic stepping methods NumberField already
exposes. They are a thin abstraction over the native spinbox's own stepping
(its `<<Increment>>` / `<<Decrement>>` virtual events), so bounds, wrapping,
and the text-vs-numeric mode are all handled natively. A step commits the
value and fires `<<Change>>`, and is a no-op when disabled or read-only.
"""
import pytest

import bootstack as bs


def test_increment_decrement_numeric(app):
    sf = bs.SpinnerField(value=5, min_value=0, max_value=10, step=2)
    app._tk_root.update_idletasks()

    sf.increment()
    assert sf.value == "7"
    sf.increment(2)  # 7 -> 9 -> 10 (clamped)
    assert sf.value == "10"
    sf.decrement()
    assert sf.value == "8"


def test_numeric_clamps_at_bounds(app):
    sf = bs.SpinnerField(value=8, min_value=0, max_value=10, step=5)
    app._tk_root.update_idletasks()

    sf.increment()  # 13 -> clamped to 10
    assert sf.value == "10"
    sf.increment()  # stays at the max
    assert sf.value == "10"


def test_numeric_wraps_when_enabled(app):
    sf = bs.SpinnerField(value=9, min_value=0, max_value=10, step=2, wrap=True)
    app._tk_root.update_idletasks()

    sf.increment()  # 11 -> wraps
    assert sf.value == "0"
    sf.decrement()  # wraps back to the top
    assert sf.value == "10"


def test_increment_decrement_text_mode(app):
    sf = bs.SpinnerField(value="Low", options=["Low", "Medium", "High"], wrap=True)
    app._tk_root.update_idletasks()

    sf.increment()
    assert sf.value == "Medium"
    sf.increment()
    assert sf.value == "High"
    sf.decrement(2)
    assert sf.value == "Low"


def test_step_fires_change_event(app):
    sf = bs.SpinnerField(value=5, min_value=0, max_value=10, step=1)
    app._tk_root.update_idletasks()

    seen = []
    sf.on_change(lambda e: seen.append((e.prev_value, e.value)))

    sf.increment()
    sf.decrement()
    app._tk_root.update_idletasks()

    assert seen == [("5", "6"), ("6", "5")]


def test_step_noop_when_disabled(app):
    sf = bs.SpinnerField(value=5, min_value=0, max_value=10, step=1, disabled=True)
    app._tk_root.update_idletasks()

    sf.increment()
    assert sf.value == "5"


def test_step_noop_when_read_only(app):
    sf = bs.SpinnerField(value=5, min_value=0, max_value=10, step=1, read_only=True)
    app._tk_root.update_idletasks()

    sf.increment()
    assert sf.value == "5"
