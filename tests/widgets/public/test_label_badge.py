"""Tests for public Label and Badge widgets."""
from __future__ import annotations

import pytest


@pytest.fixture
def app_ctx(app):
    """A content Column under the shared session App.

    Yields a `Column` (the active container) so the tests' widgets parent into
    it; the shared `app` fixture scene-resets afterward.
    """
    from bootstack.widgets import Column
    with Column() as stack:
        yield stack


@pytest.mark.gui
def test_label_text_positional(app_ctx):
    from bootstack.widgets import Label
    lbl = Label("Hello")
    assert lbl.text == "Hello"


@pytest.mark.gui
def test_label_text_property_rw(app_ctx):
    from bootstack.widgets import Label
    lbl = Label("initial")
    lbl.text = "updated"
    assert lbl.text == "updated"




@pytest.mark.gui
def test_label_wrap_width_maps_to_wraplength(app_ctx):
    from bootstack.widgets import Label
    lbl = Label("Long text", wrap_width=200)
    assert int(lbl.tk.cget("wraplength")) == 200


@pytest.mark.gui
def test_label_tk_is_internal_label(app_ctx):
    from bootstack.widgets import Label
    from bootstack.widgets._impl.primitives.label import Label as _InternalLabel
    lbl = Label("Hi")
    assert isinstance(lbl.tk, _InternalLabel)


@pytest.mark.gui
def test_badge_defaults(app_ctx):
    from bootstack.widgets import Badge
    b = Badge("99+")
    assert b.text == "99+"


@pytest.mark.gui
def test_badge_is_label_subclass():
    from bootstack.widgets import Badge, Label
    assert issubclass(Badge, Label)


@pytest.mark.gui
def test_badge_tk_is_internal_badge(app_ctx):
    from bootstack.widgets import Badge
    from bootstack.widgets._impl.primitives.badge import Badge as _InternalBadge
    b = Badge("new")
    assert isinstance(b.tk, _InternalBadge)


@pytest.mark.gui
def test_label_text_signal(app_ctx):
    from bootstack.widgets import Label
    from bootstack.signals import Signal
    sig = Signal("initial")
    lbl = Label(textsignal=sig)
    assert lbl.text == "initial"
    sig.set("updated")
    assert lbl.text == "updated"

    # Setting .text writes through the bound variable and keeps the signal in
    # sync (#242 — the setter no-op'd while a textsignal owned the text).
    lbl.text = "Changed"
    assert lbl.text == "Changed"
    assert sig() == "Changed"
