"""Smoke tests for the v2 public API base layer."""
from __future__ import annotations

import threading
import pytest

from bootstack.widgets.public.base import PublicWidgetBase
from bootstack.widgets.public.context import push_container, pop_container, current_container, _stack
from bootstack.widgets.public.events import resolve_event, register_widget_events, GLOBAL_EVENT_MAP
from bootstack.widgets.public.exceptions import UnknownEventError
from bootstack.widgets.public.subscription import Subscription


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

def test_split_layout_kwargs_pack():
    kw = {"fill": "x", "expand": True, "padding": 4, "text": "hi"}
    layout = PublicWidgetBase._split_layout_kwargs(kw)
    assert layout == {"fill": "x", "expand": True}
    assert kw == {"padding": 4, "text": "hi"}


def test_split_layout_kwargs_grid():
    kw = {"row": 1, "column": 2, "sticky": "ew", "text": "hello"}
    layout = PublicWidgetBase._split_layout_kwargs(kw)
    assert layout == {"row": 1, "column": 2, "sticky": "ew"}
    assert kw == {"text": "hello"}


def test_split_layout_kwargs_place_mode():
    kw = {"x": 10, "y": 20, "width": 100, "text": "hi"}
    layout = PublicWidgetBase._split_layout_kwargs(kw)
    # x and y are trigger keys → place mode; width stays as widget option
    assert "x" in layout
    assert "y" in layout
    assert "width" not in layout   # collision — treated as widget option
    assert kw.get("text") == "hi"


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
    from bootstack.widgets.public.events import Event
    assert Event.Widget.CLICK == "click"
    assert Event.Input.CHANGE == "change"
    assert Event.App.THEME_CHANGE == "theme_change"


# ---------------------------------------------------------------------------
# G5 / G6: Integration (require a Tk display — gated with @pytest.mark.gui)
# ---------------------------------------------------------------------------

@pytest.mark.gui
def test_button_inside_hstack_placement():
    from bootstack.widgets.public import App, HStack, Button

    with App(title="Test") as app:
        with HStack(gap=8) as row:
            b1 = Button("A")
            b2 = Button("B")

    assert b1._internal.master is row._internal
    assert b2._internal.master is row._internal
    assert row._internal.master is app._content_frame
    app._tk_root.destroy()


@pytest.mark.gui
def test_explicit_parent_overrides_context_stack():
    from bootstack.widgets.public import App, HStack, VStack, Button

    with App() as app:
        with VStack() as outer:
            with HStack():
                btn = Button("hi", parent=outer)

    assert btn._internal.master is outer._internal
    app._tk_root.destroy()


@pytest.mark.gui
def test_button_tk_property_returns_internal():
    from bootstack.widgets.public import App, VStack, Button
    import tkinter.ttk as ttk

    with App() as app:
        with VStack():
            btn = Button("X")

    assert isinstance(btn.tk, ttk.Button)
    app._tk_root.destroy()


@pytest.mark.gui
def test_button_on_unknown_event_raises():
    from bootstack.widgets.public import App, VStack, Button

    with App() as app:
        with VStack():
            btn = Button("X")

    with pytest.raises(UnknownEventError):
        btn.on("nonsense", lambda e: None)
    app._tk_root.destroy()
