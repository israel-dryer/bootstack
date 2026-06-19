"""Regression guard for #191 — the color chooser carries a "Themed" tab of the
active theme's color bands alongside the spectrum picker.

Covers: both tabs exist; every swatch resolves to a real on-theme color;
clicking a swatch loads that exact color into the chooser; and the themed page
matches the spectrum page size exactly (so switching tabs doesn't shift layout).
"""
import pytest
from PIL import ImageColor

import bootstack as bs
from bootstack.style import get_theme_color
from bootstack.dialogs._impl.colorchooser import (
    ColorChooser,
    THEMED_FAMILIES,
    THEMED_SHADES,
)


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


@pytest.fixture
def chooser(app):
    cc = ColorChooser(None, "#0d6efd")
    cc.pack()
    cc.update_idletasks()
    return cc


def test_both_tabs_present(chooser):
    # Themed first, then the freeform Custom (spectrum) picker.
    assert list(chooser.notebook._tab_map.keys()) == ["themed", "custom"]


def test_themed_families_resolve_to_theme_colors(app):
    # Every family/shade shown is a real band stop the theme exposes.
    for family in THEMED_FAMILIES:
        for shade in THEMED_SHADES:
            color = get_theme_color(f"{family}[{shade}]")
            assert color.startswith("#") and len(color) == 7


def test_clicking_swatch_loads_exact_color(chooser):
    target = get_theme_color("danger[500]")
    chooser.on_press_swatch(target)
    assert chooser.hex.get().lower() == target.lower()
    r, g, b = chooser.red.get(), chooser.grn.get(), chooser.blu.get()
    assert (r, g, b) == ImageColor.getrgb(target)


def test_themed_page_matches_spectrum_size(chooser):
    spectrum = chooser.notebook["custom"]
    themed = chooser.notebook["themed"]
    assert themed.winfo_reqwidth() == spectrum.winfo_reqwidth()
    assert themed.winfo_reqheight() == spectrum.winfo_reqheight()
