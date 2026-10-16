"""A destroyed widget stops listening for locale changes (#538).

Each localizing widget bound its refresh handler on its toplevel with
`add="+"`, and nothing removed it when the widget was destroyed. The toplevel
kept every handler's binding line and Tcl command, the bound method kept the
destroyed widget alive, and a later locale change still called it.
"""
from __future__ import annotations

import gc
import weakref

import pytest

import bootstack as bs
from bootstack.i18n import add_translations

pytestmark = pytest.mark.gui

_KEY = "Locale refresh release"
_TRANSLATED = "Sprachwechsel freigeben"


def _tabs():
    tabs = bs.Tabs()
    tabs.add("a", label=_KEY)
    return tabs


# Every kind that registers its own refresh, with what it shows before and
# after the switch from en to de.
_KINDS = {
    "label": (lambda: bs.Label(_KEY), lambda w: w._internal.cget("text"), _KEY, _TRANSLATED),
    "textfield": (
        lambda: bs.TextField(value=1234.5, value_format="decimal"),
        lambda w: w.text, "1,234.5", "1.234,5",
    ),
    "spinnerfield": (
        lambda: bs.SpinnerField(value=1234.5, value_format="decimal"),
        lambda w: w.text, "1,234.5", "1.234,5",
    ),
    "select": (lambda: bs.Select([_KEY], value=_KEY), lambda w: w.text, _KEY, _TRANSLATED),
    "selectbutton": (lambda: bs.SelectButton([_KEY], value=_KEY), lambda w: w.text, _KEY, _TRANSLATED),
    "tabs": (_tabs, lambda w: w.item("a").label, _KEY, _TRANSLATED),
}


def _locale_bindings(app):
    root = app._tk_root
    return str(root.tk.call("bind", root._w, "<<LocaleChanged>>"))


@pytest.fixture
def en(app):
    add_translations("de", {_KEY: _TRANSLATED})
    app.locale = "en"
    bs.Label("warm-up")  # so the window's own listener exists before the baseline
    app._tk_root.update()
    return app


@pytest.mark.parametrize("kind", list(_KINDS))
def test_a_destroyed_widget_leaves_no_locale_handler_behind(en, kind):
    app = en
    build, shown, before, after = _KINDS[kind]
    bindings = _locale_bindings(app)

    host = bs.Column()
    with host:
        widget = build()
    app._tk_root.update()
    assert shown(widget) == before, "precondition failed - built in the wrong locale"

    # Still refreshes while it lives. Without this the assertion below passes
    # against a widget that never registered anything.
    app.locale = "de"
    app._tk_root.update()
    assert shown(widget) == after

    host.destroy()
    app._tk_root.update()
    assert _locale_bindings(app) == bindings


def test_a_destroyed_label_can_be_collected(en):
    app = en
    host = bs.Column()
    with host:
        ref = weakref.ref(bs.Label(_KEY)._internal)
    app._tk_root.update()
    # Detached first because a stack keeps a destroyed child in its layout
    # list until it next re-plans, which would hold the label regardless.
    host.detach()
    host.destroy()
    del host
    app._tk_root.update()
    gc.collect()
    assert ref() is None


def test_a_destroyed_field_does_not_write_its_value_into_a_shared_signal(en):
    app = en
    name = bs.Signal("")
    old = bs.Column()
    with old:
        bs.TextField(textsignal=name)
    app._tk_root.update()
    name.set("Alice")
    app._tk_root.update()
    old.destroy()
    app._tk_root.update()

    with bs.Column():
        bs.TextField(textsignal=name)
    app._tk_root.update()
    name.set("Bob")
    app._tk_root.update()

    app.locale = "de"
    app._tk_root.update()
    assert name() == "Bob"
