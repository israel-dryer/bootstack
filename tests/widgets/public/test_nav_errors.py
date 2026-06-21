"""Missing-key behavior for the navigation containers — uniform NavigationError.

Tabs and PageStack raise NavigationError on any key operation that names a key
which does not exist (select, item, show/hide, navigate, remove/forget) and on a
duplicate add. NavModel has its own non-GUI coverage in tests/test_navmodel.py.
"""
from __future__ import annotations

import pytest

import bootstack as bs
from bootstack.errors import NavigationError


def test_tabs_missing_key_raises(app):
    t = bs.Tabs()
    t.add("a", label="A")
    for fn in (
        lambda: t.select("nope"),
        lambda: t.item("nope"),
        lambda: t.show_tab("nope"),
        lambda: t.hide_tab("nope"),
        lambda: t.forget_tab("nope"),
    ):
        with pytest.raises(NavigationError):
            fn()


def test_tabs_duplicate_key_raises(app):
    t = bs.Tabs()
    t.add("a", label="A")
    with pytest.raises(NavigationError):
        t.add("a")


def test_pagestack_missing_key_raises(app):
    ps = bs.PageStack()
    with ps.add("p"):
        bs.Label("P")
    for fn in (
        lambda: ps.navigate("nope"),
        lambda: ps.item("nope"),
        lambda: ps.remove("nope"),
    ):
        with pytest.raises(NavigationError):
            fn()


def test_pagestack_duplicate_key_raises(app):
    ps = bs.PageStack()
    with ps.add("p"):
        bs.Label("P")
    with pytest.raises(NavigationError):
        ps.add("p")