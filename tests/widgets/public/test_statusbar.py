"""Tests for the public StatusBar — class-only add_widget + bar defaults.

`add_widget()` is class-only (the band builds the widget, applying its own
density/surface). A self-built widget is added via `parent=statusbar`. One
module-scoped App (creating several Apps crashes Tk).
"""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.gui


@pytest.fixture(scope="module")
def app():
    import bootstack as bs

    app = bs.App()
    app._tk_root.withdraw()
    try:
        yield app
    finally:
        try:
            app._tk_root.destroy()
        except Exception:
            pass


def test_add_widget_builds_class_and_returns_instance(app):
    import bootstack as bs

    sb = bs.StatusBar(density="compact")
    pb = sb.add_widget(bs.ProgressBar, value=65)
    assert isinstance(pb, bs.ProgressBar)
    app._internal.update_idletasks()
    assert len(sb._internal.content.winfo_children()) == 1


def test_add_widget_class_inherits_band_density_skips_unsupported_surface(app):
    import bootstack as bs

    sb = bs.StatusBar(density="compact")
    kw: dict = {}
    sb._apply_bar_defaults(bs.TextField, kw)
    # density is injected (TextField accepts it); surface is skipped (it does not).
    assert kw == {"density": "compact"}


def test_add_widget_right_side_adds_spacer(app):
    import bootstack as bs

    sb = bs.StatusBar()
    sb.add_widget(bs.ProgressBar, value=10, side="right")
    assert sb._has_right_spacer is True
