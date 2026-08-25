"""Smoke tests for the public API base layer."""
from __future__ import annotations

import threading
import pytest

from bootstack.widgets._core.base import PublicWidgetBase
from bootstack.widgets._core.context import push_container, pop_container, current_container, _stack
from bootstack.widgets._core.events import resolve_event, register_widget_events, GLOBAL_EVENT_MAP
from bootstack.errors import UnknownEventError
from bootstack.events import Subscription


# ---------------------------------------------------------------------------
# G1: Context stack
# ---------------------------------------------------------------------------

class _FakeContainer:
    pass


def test_context_stack_push_pop():
    c = _FakeContainer()
    assert current_container() is None
    push_container(c)
    assert current_container() is c
    pop_container(c)
    assert current_container() is None


def test_context_stack_isolated_per_thread():
    c = _FakeContainer()
    push_container(c)

    seen = []

    def thread_fn():
        seen.append(current_container())

    t = threading.Thread(target=thread_fn)
    t.start()
    t.join()

    pop_container(c)
    assert seen == [None], "Thread should see an empty stack"


def test_context_stack_pop_out_of_order_is_safe():
    a, b = _FakeContainer(), _FakeContainer()
    push_container(a)
    push_container(b)
    # Pop a (not the top) — should not corrupt the stack.
    pop_container(a)
    # b is still on the stack since it's not `a`
    assert b in _stack()
    pop_container(b)


# ---------------------------------------------------------------------------
# G2: Layout kwarg split
# ---------------------------------------------------------------------------

# The seam is an INSTANCE method as of #383, so the error can name the widget.
# These build a bare instance rather than a real widget: the seam reads only
# `type(self).__name__` and the `_forwards_kwargs` class flag, so `__init__`
# would contribute nothing but a Tk dependency.
def _seam(name="Widget", forwards=False):
    cls = type(name, (PublicWidgetBase,), {"_forwards_kwargs": forwards})
    return object.__new__(cls)


def test_split_layout_kwargs_pack():
    # Only layout keys here: in a real wrapper a widget option like `padding`
    # is a NAMED parameter and never reaches the catch-all, so anything the
    # split does not claim is a typo (#383).
    kw = {"fill": "x", "expand": True}
    layout = _seam()._split_layout_kwargs(kw)
    assert layout == {"fill": "x", "expand": True}
    assert kw == {}


def test_split_layout_kwargs_grid():
    kw = {"row": 1, "column": 2, "sticky": "ew"}
    layout = _seam()._split_layout_kwargs(kw)
    assert layout == {"row": 1, "column": 2, "sticky": "ew"}
    assert kw == {}


def test_split_layout_kwargs_place_mode():
    # A forwarder, so the surviving `width` is legal and the test can still
    # assert the collision rule. On a strict widget `width` would be a named
    # parameter and never arrive here at all.
    kw = {"x": 10, "y": 20, "width": 100}
    layout = _seam("Picture", forwards=True)._split_layout_kwargs(kw)
    # x and y are trigger keys → place mode; width stays as widget option
    assert "x" in layout
    assert "y" in layout
    assert "width" not in layout   # collision — treated as widget option
    assert kw == {"width": 100}


# --- #383: whatever survives the split is a typo, not something to discard ---

def test_split_rejects_a_leftover_and_names_it():
    """The defect #383 gap 3 names: the public layer was LESS strict than the
    internal it wraps. `bs.TextField(bogus=1)` constructed while the internal
    `TextEntry(bogus=1)` raised.
    """
    with pytest.raises(TypeError) as exc:
        _seam("Gauge")._split_layout_kwargs({"fill": "x", "densty": "compact"})
    # the widget and the offending key both have to be in the message, or it
    # is no more useful than the silent drop it replaces
    assert "Gauge" in str(exc.value)
    assert "densty" in str(exc.value)
    assert "fill" not in str(exc.value)      # a real layout key is not a typo


def test_split_reports_every_leftover_not_just_the_first():
    with pytest.raises(TypeError) as exc:
        _seam()._split_layout_kwargs({"aaa": 1, "zzz": 2})
    assert "aaa" in str(exc.value) and "zzz" in str(exc.value)


def test_split_leaves_leftovers_alone_for_a_declared_forwarder():
    """The five deliberate forwarders (Chart, MenuButton, Picture, StatusBar,
    Toolbar) read what survives the split. The opt-out is a CLASS FLAG so a
    guard test can enumerate the exemptions; a per-call keyword could not.
    """
    kw = {"fill": "x", "cmap": "viridis"}
    layout = _seam("Chart", forwards=True)._split_layout_kwargs(kw)
    assert layout == {"fill": "x"}
    assert kw == {"cmap": "viridis"}          # still there for the internal


# ---------------------------------------------------------------------------
# G3: Subscription
# ---------------------------------------------------------------------------

@pytest.mark.gui
def test_subscription_cancel(tmp_tk_root):
    fired = []
    bind_id = tmp_tk_root.bind("<Button-1>", lambda e: fired.append(1), add="+")
    sub = Subscription(tmp_tk_root, "<Button-1>", bind_id)

    tmp_tk_root.event_generate("<Button-1>")
    assert fired == [1]

    sub.cancel()
    tmp_tk_root.event_generate("<Button-1>")
    assert fired == [1], "Handler should not fire after cancel"

    sub.cancel()  # idempotent
    assert sub.cancelled


@pytest.mark.gui
def test_subscription_context_manager(tmp_tk_root):
    fired = []
    bind_id = tmp_tk_root.bind("<Button-1>", lambda e: fired.append(1), add="+")
    sub = Subscription(tmp_tk_root, "<Button-1>", bind_id)

    with sub:
        tmp_tk_root.event_generate("<Button-1>")

    assert fired == [1]
    tmp_tk_root.event_generate("<Button-1>")
    assert fired == [1], "Handler should be cancelled after context exit"


# ---------------------------------------------------------------------------
# G4: Event resolution
# ---------------------------------------------------------------------------

class _FakeWidget:
    pass


def test_resolve_event_global():
    w = _FakeWidget()
    assert resolve_event(w, "click") == "<Button-1>"
    assert resolve_event(w, "hover") == "<Enter>"
    assert resolve_event(w, "focus") == "<FocusIn>"


def test_resolve_event_passthrough():
    w = _FakeWidget()
    assert resolve_event(w, "<Configure>") == "<Configure>"
    assert resolve_event(w, "<<ThemeChanged>>") == "<<ThemeChanged>>"


def test_resolve_event_unknown_raises():
    w = _FakeWidget()
    with pytest.raises(UnknownEventError):
        resolve_event(w, "nonsense_event_that_does_not_exist")


def test_resolve_event_class_map_takes_precedence():
    class _MyWidget:
        pass

    register_widget_events(_MyWidget, {"select": "<<MySelect>>"})
    w = _MyWidget()
    assert resolve_event(w, "select") == "<<MySelect>>"


def test_event_enum_values_are_strings():
    from bootstack.widgets._core.events import EventName
    assert EventName.Widget.CLICK == "click"
    assert EventName.Input.CHANGE == "change"
    assert EventName.App.THEME_CHANGE == "theme_change"


# ---------------------------------------------------------------------------
# G5 / G6: Integration (require a Tk display — gated with @pytest.mark.gui)
# ---------------------------------------------------------------------------

@pytest.mark.gui
def test_button_inside_row_placement(app):
    from bootstack.widgets import Row, Button

    with Row(gap=8) as row:
        b1 = Button("A")
        b2 = Button("B")

    assert b1._internal.master is row._internal
    assert b2._internal.master is row._internal
    assert row._internal.master is app._content_frame


@pytest.mark.gui
def test_explicit_parent_overrides_context_stack(app):
    from bootstack.widgets import Row, Column, Button

    with Column() as outer:
        with Row():
            btn = Button("hi", parent=outer)

    assert btn._internal.master is outer._internal


@pytest.mark.gui
def test_button_tk_property_returns_internal(app):
    from bootstack.widgets import Column, Button
    import tkinter.ttk as ttk

    with Column():
        btn = Button("X")

    assert isinstance(btn.tk, ttk.Button)


@pytest.mark.gui
def test_button_on_unknown_event_raises(app):
    from bootstack.widgets import Column, Button

    with Column():
        btn = Button("X")

    with pytest.raises(UnknownEventError):
        btn.on("nonsense", lambda e: None)
