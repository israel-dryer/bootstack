"""Tests for public Label and Badge widgets."""
from __future__ import annotations

import pytest


@pytest.fixture
def app_ctx():
    from bootstack.widgets import App, Column
    with App() as app:
        with Column() as stack:
            yield stack
    app._tk_root.destroy()


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
def test_label_color_kwarg(app_ctx):
    from bootstack.widgets import Label
    lbl = Label("Hi", color="#ff0000")
    assert lbl.color == "#ff0000"


@pytest.mark.gui
def test_label_color_property_rw(app_ctx):
    from bootstack.widgets import Label
    lbl = Label("Hi")
    lbl.color = "#00ff00"
    assert lbl.color == "#00ff00"


@pytest.mark.gui
def test_label_disabled_kwarg(app_ctx):
    from bootstack.widgets import Label
    lbl = Label("Hi", disabled=True)
    assert lbl.disabled is True


@pytest.mark.gui
def test_label_disabled_property_rw(app_ctx):
    from bootstack.widgets import Label
    lbl = Label("Hi")
    assert lbl.disabled is False
    lbl.disabled = True
    assert lbl.disabled is True
    lbl.disabled = False
    assert lbl.disabled is False


@pytest.mark.gui
def test_label_wrap_width_maps_to_wraplength(app_ctx):
    from bootstack.widgets import Label
    lbl = Label("Long text", wrap_width=200)
    assert int(lbl.tk.cget("wraplength")) == 200


@pytest.mark.gui
def test_label_tk_is_internal_label(app_ctx):
    from bootstack.widgets import Label
    from bootstack.widgets.primitives.label import Label as _InternalLabel
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
    from bootstack.widgets.primitives.badge import Badge as _InternalBadge
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
