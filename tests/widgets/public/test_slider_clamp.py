"""Value-clamping tests for Slider / RangeSlider.

Covers the contract that a slider's value never escapes its declared
``[min, max]`` range — whether set directly, or after the range is tightened
around an existing value. These are pure value reads (Tk traces fire
synchronously on ``set``), so no event-loop pumping is needed.
"""
from __future__ import annotations

import pytest

import bootstack as bs


# --- Slider --------------------------------------------------------------

def test_slider_value_setter_clamps_high(app):
    s = bs.Slider(value=0, min_value=0, max_value=100)
    s.value = 250
    assert s.value == 100.0


def test_slider_value_setter_clamps_low(app):
    s = bs.Slider(value=50, min_value=0, max_value=100)
    s.value = -30
    assert s.value == 0.0


def test_slider_tightening_max_reclamps_value(app):
    s = bs.Slider(value=80, min_value=0, max_value=100)
    s.max_value = 50
    assert s.value == 50.0


def test_slider_raising_min_reclamps_value(app):
    s = bs.Slider(value=10, min_value=0, max_value=100)
    s.min_value = 40
    assert s.value == 40.0


def test_slider_in_range_value_survives_range_change(app):
    s = bs.Slider(value=30, min_value=0, max_value=100)
    s.max_value = 80
    assert s.value == 30.0


# --- RangeSlider ---------------------------------------------------------

def test_rangeslider_setters_clamp(app):
    rs = bs.RangeSlider(low_value=10, high_value=90, min_value=0, max_value=100)
    rs.low_value = -5
    rs.high_value = 250
    assert rs.low_value == 0.0
    assert rs.high_value == 100.0


def test_rangeslider_tightening_max_reclamps_high(app):
    rs = bs.RangeSlider(low_value=10, high_value=90, min_value=0, max_value=100)
    rs.max_value = 50
    assert rs.high_value == 50.0
    assert rs.low_value == 10.0


def test_rangeslider_raising_min_reclamps_low(app):
    rs = bs.RangeSlider(low_value=10, high_value=90, min_value=0, max_value=100)
    rs.min_value = 30
    assert rs.low_value == 30.0
    assert rs.high_value == 90.0


def test_rangeslider_collapsing_range_keeps_lo_le_hi(app):
    rs = bs.RangeSlider(low_value=20, high_value=80, min_value=0, max_value=100)
    rs.max_value = 10
    assert rs.low_value <= rs.high_value
    assert rs.high_value == 10.0
    assert rs.low_value == 10.0