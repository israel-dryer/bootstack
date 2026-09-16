"""A relabelled tab tracks its own content width (issue #521).

The minimum-width pass freezes the tab frame with propagation off, so without a
re-measure a later, longer label is clipped -- and a tab that never reached the
minimum shrinks straight past it. Width is read as `winfo_reqwidth()`, which
reports the frozen width while propagation is off and the content width once it
is on, so neither assertion depends on how much room the strip happens to have.
"""
from __future__ import annotations

import pytest

import bootstack as bs

pytestmark = pytest.mark.gui

LONG = "A much longer label than before"


def _pump(app):
    app._tk_root.update_idletasks()
    app._tk_root.update()


def _build(app, label):
    tabs = bs.Tabs(grow=True)
    with tabs.add("a", label=label):
        bs.Label("body")
    _pump(app)
    return tabs, tabs._internal.tab("a")


def _min_width(tabs):
    return tabs._internal.tabs_widget._tab_min_width


def test_relabelling_a_short_tab_widens_it_to_fit(app):
    tabs, tab = _build(app, "A")
    minimum = _min_width(tabs)
    # The short label pinned the tab at the minimum -- the frozen state the
    # clipping came from.
    assert tab.winfo_reqwidth() == minimum

    tabs.item("a").label = LONG
    _pump(app)

    needed = tab._label.winfo_reqwidth()
    assert needed > minimum  # the new label genuinely wants more room
    assert tab.winfo_reqwidth() >= needed


def test_relabelling_a_wide_tab_stops_at_the_minimum(app):
    tabs, tab = _build(app, LONG)
    minimum = _min_width(tabs)
    # The long label kept the tab above the minimum, so the minimum was never
    # applied at construction.
    assert tab.winfo_reqwidth() > minimum

    tabs.item("a").label = "A"
    _pump(app)

    assert tab._label.winfo_reqwidth() < minimum  # the label alone is narrower
    assert tab.winfo_reqwidth() == minimum
