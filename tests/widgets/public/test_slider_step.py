"""Snapping tests for the Slider / RangeSlider ``step`` parameter.

``step`` snaps values to multiples of the increment (measured from ``min_value``)
and clamps to the range; the exact maximum stays reachable when the range is not
an even multiple of ``step``. These are pure value reads (Tk traces fire on
``set``), so no event-loop pumping is needed.
"""
from __future__ import annotations

import pytest

import bootstack as bs


# --- Slider --------------------------------------------------------------

def test_slider_initial_value_snaps(app):
    s = bs.Slider(33, min_value=0, max_value=100, step=5)
    assert s.value == 35.0


def test_slider_set_snaps_to_nearest(app):
    s = bs.Slider(0, min_value=0, max_value=100, step=5)
    s.value = 37          # → 35
    assert s.value == 35.0
    s.value = 38          # → 40
    assert s.value == 40.0


def test_slider_step_none_is_continuous(app):
    s = bs.Slider(0, min_value=0, max_value=100)
    s.value = 33.3
    assert s.value == pytest.approx(33.3)


def test_slider_offgrid_max_is_reachable(app):
    s = bs.Slider(0, min_value=0, max_value=100, step=3)
    s.value = 100         # exact max wins even though 100 is off-grid
    assert s.value == 100.0
    s.value = 98          # closer to the 99 grid point
    assert s.value == 99.0


def test_slider_step_property_resnaps(app):
    s = bs.Slider(0, min_value=0, max_value=100)
    s.value = 37
    assert s.value == 37.0
    s.step = 10           # applying a grid re-snaps the current value
    assert s.value == 40.0
    assert s.step == 10.0


def test_slider_range_change_resnaps_onto_grid(app):
    s = bs.Slider(40, min_value=0, max_value=100, step=10)
    s.min_value = 5       # grid now 5, 15, 25, … ; 40 → 45
    assert s.value == 45.0


# --- RangeSlider ---------------------------------------------------------

def test_rangeslider_initial_values_snap(app):
    rs = bs.RangeSlider(22, 78, min_value=0, max_value=100, step=5)
    assert rs.low_value == 20.0
    assert rs.high_value == 80.0


def test_rangeslider_setters_snap(app):
    rs = bs.RangeSlider(20, 80, min_value=0, max_value=100, step=5)
    rs.low_value = 23     # → 25
    rs.high_value = 67    # → 65
    assert rs.low_value == 25.0
    assert rs.high_value == 65.0


def test_rangeslider_step_property_resnaps(app):
    rs = bs.RangeSlider(0, 100, min_value=0, max_value=100)
    rs.low_value = 12
    rs.high_value = 87
    rs.step = 25          # grid 0,25,50,75,100
    assert rs.low_value == 0.0     # 12 → 0
    assert rs.high_value == 75.0   # 87 → 75