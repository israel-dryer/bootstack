"""Regression for #375: Tk 9 moved Aqua's nominal resolution from 72 to 96 DPI.

bootstack keyed its scaling baseline off the *platform* alone, so on macOS + Tk 9
`get_ui_scale()` reported ~1.333 instead of 1.0 and every DPI-derived measurement
inflated by a third (icons re-rasterized 16px -> 22px, field height 42px -> 57px).
Separately, the macOS `+2` font bump — written to compensate for the 72 DPI point
unit — double-counted once Tk 9 converted points at 96 DPI, rendering `body` text
at 20px linespace instead of 16px.

The existing scaling tests could not catch either: they all *inject* a scale factor
(`set_scale_factor` / monkeypatched `get_ui_scale`) and assert that consumers respond
correctly. Nothing exercised the producer. These tests cover the producer, and they
run identically on Tk 8.6 and Tk 9 — no version skips, which would report green while
testing nothing (the trap the #373 touchpad tests fell into).
"""
from __future__ import annotations

import tkinter

import pytest

from bootstack._runtime.utility import _ScalingState, _platform_baseline
from bootstack.style.typography import build_desktop_tokens

WIN_LINUX_BASELINE = 1.33398982438864281  # 96 DPI / 72


@pytest.mark.parametrize("tk_version", [8.6, 9.0])
def test_aqua_baseline_tracks_tk_version(monkeypatch, tk_version):
    # Both branches are exercised on whichever Tk is installed, so this cannot
    # silently skip. Tk 8.6 Aqua is 72 DPI; Tk 9 aligned it with Win/Linux at 96.
    monkeypatch.setattr(tkinter, "TkVersion", tk_version)
    monkeypatch.setattr("platform.system", lambda: "Darwin")

    expected = 1.0 if tk_version < 9.0 else WIN_LINUX_BASELINE
    assert _platform_baseline() == pytest.approx(expected)


@pytest.mark.parametrize("tk_version", [8.6, 9.0])
@pytest.mark.parametrize("system", ["Windows", "Linux"])
def test_non_aqua_baseline_is_tk_version_independent(monkeypatch, tk_version, system):
    # Win/X11 were already 96 DPI under both versions — the fix must not move them.
    monkeypatch.setattr(tkinter, "TkVersion", tk_version)
    monkeypatch.setattr("platform.system", lambda: system)

    assert _platform_baseline() == pytest.approx(WIN_LINUX_BASELINE)


@pytest.mark.parametrize(
    "baseline, expected_pt",
    [(1.0, 13), (WIN_LINUX_BASELINE, 10)],
    ids=["tk8.6-aqua-72dpi", "tk9-aqua-96dpi"],
)
def test_macos_font_base_expressed_in_active_point_unit(monkeypatch, baseline, expected_pt):
    """The macOS size bump targets a physical size, so it must track the point unit.

    Tk 9 redefined what an Aqua "point" is worth in pixels, so the flat `+2` bump
    double-counted and rendered `body` at 20px linespace instead of 16px. Dividing
    by the baseline keeps the *rendered* size fixed: 13pt on Tk 8.6, 10pt on Tk 9 —
    the same point size Tk 9 itself picks for `TkDefaultFont`.

    Asserting on the token rather than a live font is deliberate: bootstack
    reconfigures `TkDefaultFont`, so comparing a rendered label against it moves
    both sides together and can never fail.
    """
    monkeypatch.setattr("platform.system", lambda: "Darwin")
    monkeypatch.setattr(_ScalingState, "_baseline", baseline)

    tokens = build_desktop_tokens(base_size=11)

    assert tokens.body.size == expected_pt
    # The invariant behind both numbers: rendered size is baseline-independent.
    assert tokens.body.size * baseline == pytest.approx(13.0, abs=0.5)