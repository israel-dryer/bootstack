"""Regression for #90: the gap between a field's nine-patch border (whose slice
scales with DPI) and the entry inside must scale with it, or at high DPI the entry
overpaints the border slice and the resting border disappears.

The fix is `scale_padding_floor`: round (not truncate) the DPI-scaled padding so
intermediate scales like 1.5x don't lose a pixel and clip the rounded corners, and
floor at the baseline so low DPI keeps its tuned spacing. A field's `TField` frame
padding (and TextArea's) is computed from it at construction time.
"""
from __future__ import annotations

import pytest

import bootstack as bs
from bootstack._runtime.utility import _ScalingState, scale_padding_floor


def test_scale_padding_floor_never_below_base():
    # Below the baseline (low DPI) it must hold the tuned base, not shrink — a
    # smaller gap clips the rounded corners.
    _ScalingState.set_scale_factor(0.5)
    assert scale_padding_floor(5) == 5


def test_scale_padding_floor_rounds_not_truncates():
    # ui_scale 1.125 -> 5 * 1.125 = 5.625; truncation gave 5 (clipped at 1.5x DPI),
    # rounding gives 6.
    _ScalingState.set_scale_factor(1.5)          # ui_scale ~1.125 on a 1.333 baseline
    ui = _ScalingState.get_ui_scale()
    assert scale_padding_floor(5) == max(5, round(5 * ui))
    assert scale_padding_floor(5) >= 6


def test_scale_padding_floor_scales_up_for_hidpi():
    _ScalingState.set_scale_factor(2.667)        # ~200%
    assert scale_padding_floor(5) > 5            # grows with the border slice


@pytest.mark.gui
def test_field_padding_tracks_dpi(app):
    # The TextField's TField frame padding is built from scale_padding_floor.
    _ScalingState.set_scale_factor(1.0)
    low = bs.TextField(label="a")
    low_pad = low._internal._field.cget("padding")[0]

    _ScalingState.set_scale_factor(2.667)
    high = bs.TextField(label="b")
    high_pad = high._internal._field.cget("padding")[0]

    assert int(high_pad) > int(low_pad)
    assert int(low_pad) >= 5


@pytest.mark.gui
def test_textarea_padding_tracks_dpi(app):
    # TextArea/CodeEditor share the same TField border pattern and fix.
    _ScalingState.set_scale_factor(2.667)
    ta = bs.TextArea(label="notes")
    assert ta._internal._field_frame is not None
    assert int(ta._internal._field_frame.cget("padding")[0]) > 5
