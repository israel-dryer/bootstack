"""Tests for the public Signal API.

Covers reading via call syntax, writing with `set()` (including int->float
widening), `subscribe(immediate=)` error propagation, and the duck-typed
`is_signal` detection that widget binding relies on. A signal is backed by the
App's variable system, so these need a running App; the module shares one
(creating multiple Apps in one process crashes the Tk runtime).
"""
from __future__ import annotations

import pytest

import bootstack as bs
from bootstack.signals.signal import Signal
from bootstack._core.capabilities.signals import is_signal


@pytest.fixture(scope="module")
def app():
    a = bs.App()
    a.__enter__()
    root = a._tk_root
    root.withdraw()
    try:
        yield a
    finally:
        try:
            a.__exit__(None, None, None)
        except Exception:
            pass
        try:
            root.destroy()
        except Exception:
            pass


@pytest.mark.gui
def test_call_reads_and_set_writes(app):
    s = bs.Signal("hello")
    assert s() == "hello"
    s.set("world")
    assert s() == "world"


@pytest.mark.gui
def test_get_method_is_removed(app):
    # `.get()` was removed; call syntax is the single getter.
    assert not hasattr(bs.Signal(0), "get")


@pytest.mark.gui
def test_tk_variable_methods_no_longer_leak(app):
    # The __getattr__ proxy onto the tk.Variable is gone.
    s = bs.Signal("x")
    assert not hasattr(s, "trace_add")
    assert not hasattr(s, "trace_remove")
    # The explicit escape hatches still exist.
    assert s.var is not None
    assert s.tk is s.var


@pytest.mark.gui
def test_set_rejects_wrong_type(app):
    s = bs.Signal(0)
    with pytest.raises(TypeError):
        s.set("nope")
    with pytest.raises(TypeError):
        s.set(1.5)          # float into an int signal: narrowing, rejected
    with pytest.raises(TypeError):
        s.set(True)         # bool is not an int here


@pytest.mark.gui
def test_set_widens_int_to_float(app):
    s = bs.Signal(0.0)
    s.set(5)
    assert s() == 5.0
    assert isinstance(s(), float)


@pytest.mark.gui
def test_subscribe_immediate_fires_with_current_value(app):
    s = bs.Signal(1)
    seen = []
    s.subscribe(seen.append, immediate=True)
    assert seen == [1]
    s.set(2)
    assert seen == [1, 2]


@pytest.mark.gui
def test_subscribe_returns_cancellable_handle(app):
    from bootstack.streams import Handle

    s = bs.Signal(0)
    seen = []
    sub = s.subscribe(seen.append)
    assert isinstance(sub, Handle)

    s.set(1)
    sub.cancel()
    s.set(2)            # no longer listening
    assert seen == [1]

    # idempotent
    sub.cancel()


@pytest.mark.gui
def test_subscribe_handle_as_context_manager(app):
    s = bs.Signal(0)
    seen = []
    with s.subscribe(seen.append):
        s.set(1)
    s.set(2)            # cancelled on exit
    assert seen == [1]


@pytest.mark.gui
def test_subscribe_immediate_propagates_callback_error(app):
    # A failing immediate callback must surface, not be swallowed.
    s = bs.Signal(0)

    def boom(_value):
        raise ValueError("boom")

    with pytest.raises(ValueError):
        s.subscribe(boom, immediate=True)


@pytest.mark.gui
def test_map_tracks_source(app):
    name = bs.Signal("world")
    shout = name.map(str.upper)
    assert shout() == "WORLD"
    name.set("hello")
    assert shout() == "HELLO"


@pytest.mark.gui
def test_is_signal_recognizes_signal_without_get(app):
    # Regression guard: is_signal must not depend on a `.get` method.
    assert is_signal(bs.Signal(0)) is True
    assert is_signal("not a signal") is False
    import tkinter as tk
    assert is_signal(tk.StringVar(value="x")) is False


@pytest.mark.gui
def test_widget_binding_recognizes_signal(app):
    # Integration guard: a Signal passed to a widget must be adopted, not
    # replaced by a fresh empty one (broke when is_signal checked for `.get`).
    # If the signal were not recognized, the field would create a fresh empty
    # signal and seed itself with "" instead of the signal's value.
    s = bs.Signal("seed")
    field = bs.TextField(textsignal=s)
    app._tk_root.update_idletasks()
    assert field.value == "seed"
