"""#305 — a text+icon Button/MenuButton icon must DPI-scale once, not twice.

`icon_size()` (the text branch) sizes the icon to the font ascent, which is
already physical. The value is then handed to `normalize_icon_spec`, which
re-applies DPI scaling, so the icon must return a *logical* size or it ends up
~ui_scale x too large at high DPI.
"""
from tkinter import font

import pytest

from bootstack._runtime.utility import _ScalingState, scale_size
from bootstack.style.builders.utils import icon_size


def test_icon_only_size_is_logical_and_dpi_invariant(app, monkeypatch):
    # The icon-only branch returns a logical literal regardless of DPI;
    # normalize_icon_spec applies the single scale.
    monkeypatch.setattr(_ScalingState, "get_ui_scale", classmethod(lambda cls: 1.5))
    assert icon_size(True, "default") == 20
    assert icon_size(True, "compact") == 17


@pytest.mark.parametrize("density", ["default", "compact"])
def test_text_icon_scales_once_not_twice(app, monkeypatch, density):
    monkeypatch.setattr(_ScalingState, "get_ui_scale", classmethod(lambda cls: 1.5))
    font_name = "caption" if density == "compact" else "body"
    buffer = 4 if density == "compact" else 3
    ascent = font.nametofont(font_name).metrics()["ascent"] + buffer

    # Re-scaling the logical result (as normalize_icon_spec does) lands back at
    # ~the ascent — a single scale, not the ascent x ui_scale double-scale.
    physical = scale_size(icon_size(False, density))
    assert abs(physical - ascent) <= 1
    assert physical < round(ascent * 1.5) - 1  # would fail on the double-scale