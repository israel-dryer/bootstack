"""Theme.from_existing — derive a theme from a base, overriding only some tokens."""
from __future__ import annotations

import pytest

from bootstack.errors import ThemeError
from bootstack.style import Theme
from bootstack.style.themes import BOOTSTRAP


def test_derive_from_builtin_name_inherits_and_overrides():
    t = Theme.from_existing("bootstrap", name="acme", primary="#ff5722")
    assert isinstance(t, Theme)
    assert t.name == "acme"
    assert t.primary == "#ff5722"          # overridden
    assert t.success == BOOTSTRAP.success  # inherited
    assert t.danger == BOOTSTRAP.danger
    assert BOOTSTRAP.primary != "#ff5722"  # base untouched


def test_derive_from_theme_instance():
    t = Theme.from_existing(
        BOOTSTRAP, name="acme2", dark=dict(background="#101010", foreground="#eeeeee")
    )
    assert t.dark["background"] == "#101010"
    assert t.primary == BOOTSTRAP.primary


def test_variant_suffix_base_resolves_to_family():
    t = Theme.from_existing("bootstrap-dark", name="acme3", info="#00bcd4")
    assert t.info == "#00bcd4"
    assert t.success == BOOTSTRAP.success


def test_fork_family_with_own_canvas():
    t = Theme.from_existing(
        "bootstrap", name="midnight",
        light=dict(background="#fafafa", foreground="#1a1a1a"),
        dark=dict(background="#0a0a0a", foreground="#e0e0e0"),
        surfaces={"dark": {"chrome": "#000000"}},
    )
    assert t.primary == BOOTSTRAP.primary          # accent ramps inherited
    assert t.dark["background"] == "#0a0a0a"        # own canvas
    assert {v["name"] for v in t.variants()} == {"midnight-light", "midnight-dark"}


def test_single_mode_derivative():
    t = Theme.from_existing("bootstrap", name="dayonly", dark=None)
    assert [v["name"] for v in t.variants()] == ["dayonly-light"]


def test_unknown_base_raises_themeerror():
    with pytest.raises(ThemeError):
        Theme.from_existing("not-a-theme", name="x")


def test_unknown_override_token_raises_themeerror():
    with pytest.raises(ThemeError):
        Theme.from_existing("bootstrap", name="x", primarry="#000000")


def test_name_is_required():
    with pytest.raises(TypeError):
        Theme.from_existing("bootstrap")  # type: ignore[call-arg]