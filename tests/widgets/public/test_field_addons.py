"""Public field addon API: insert_addon / update_addon / remove_addon / addons.

Covers auto-naming, the three addon types, validation guards, the reactive
toggle pattern, and in-place update / removal.
"""
import pytest

import bootstack as bs


pytestmark = pytest.mark.gui


def test_insert_auto_names_addons(app):
    f = bs.TextField()
    f.insert_addon("label", "before", icon="search")
    f.insert_addon("button", "after", icon="x-lg", on_click=lambda: None)
    app._tk_root.update()
    assert sorted(f.addons.keys()) == ["addon_0", "addon_1"]


def test_insert_named_addon_round_trips(app):
    amt = bs.NumberField(value=1)
    amt.insert_addon("label", "after", name="unit", text="px")
    app._tk_root.update()
    assert amt.addons["unit"].cget("text") == "px"


def test_label_rejects_on_click(app):
    f = bs.TextField()
    with pytest.raises(ValueError):
        f.insert_addon("label", "before", icon="x", on_click=lambda: None)


def test_signal_only_for_toggle(app):
    f = bs.TextField()
    with pytest.raises(ValueError):
        f.insert_addon("button", "after", signal=bs.Signal(False))


def test_bad_widget_type(app):
    f = bs.TextField()
    with pytest.raises(ValueError):
        f.insert_addon("slider", "after")


def test_update_addon(app):
    amt = bs.NumberField(value=1)
    amt.insert_addon("label", "after", name="unit", text="px")
    app._tk_root.update()
    amt.update_addon("unit", text="%", accent="secondary")
    app._tk_root.update()
    assert amt.addons["unit"].cget("text") == "%"


def test_update_missing_addon_raises(app):
    f = bs.TextField()
    with pytest.raises(KeyError):
        f.update_addon("nope", text="x")


def test_toggle_addon_drives_signal_and_updates(app):
    unit = bs.Signal(False)
    nf = bs.NumberField(value=0)
    nf.insert_addon("toggle", "after", name="u", text="px", signal=unit)
    unit.subscribe(lambda on: nf.update_addon("u", text="%" if on else "px"))
    app._tk_root.update()
    nf.addons["u"].invoke()
    app._tk_root.update()
    assert unit() is True
    assert nf.addons["u"].cget("text") == "%"


def test_remove_addon(app):
    f = bs.TextField()
    f.insert_addon("button", "after", name="clear", icon="x-lg", on_click=lambda: None)
    app._tk_root.update()
    f.remove_addon("clear")
    app._tk_root.update()
    assert "clear" not in f.addons


def test_remove_missing_addon_raises(app):
    f = bs.TextField()
    with pytest.raises(KeyError):
        f.remove_addon("nope")


# ----- read-only / disabled state ----------------------------------------

def test_addon_dims_on_readonly_by_default(app):
    f = bs.TextField(value="x", read_only=True)
    b = f.insert_addon("button", "after", name="clear", icon="x-lg", on_click=lambda: None)
    app._tk_root.update()
    assert b.instate(["disabled"])


def test_active_when_readonly_stays_live(app):
    f = bs.TextField(value="x", read_only=True)
    b = f.insert_addon("button", "after", name="copy", icon="clipboard",
                       on_click=lambda: None, active_when_readonly=True)
    app._tk_root.update()
    assert not b.instate(["disabled"])


def test_disabled_overrides_active_when_readonly(app):
    f = bs.TextField(value="x", disabled=True)
    b = f.insert_addon("button", "after", name="copy", icon="clipboard",
                       on_click=lambda: None, active_when_readonly=True)
    app._tk_root.update()
    assert b.instate(["disabled"])


def test_number_steppers_dim_on_readonly(app):
    n = bs.NumberField(value=5, read_only=True)
    app._tk_root.update()
    assert n.addons["increment"].instate(["disabled"])
    assert n.addons["decrement"].instate(["disabled"])


def test_readonly_toggle_at_runtime(app):
    f = bs.TextField(value="z")
    plain = f.insert_addon("button", "after", name="clear", icon="x-lg", on_click=lambda: None)
    safe = f.insert_addon("button", "after", name="copy", icon="clipboard",
                          on_click=lambda: None, active_when_readonly=True)
    app._tk_root.update()
    f.read_only = True
    app._tk_root.update()
    assert plain.instate(["disabled"])
    assert not safe.instate(["disabled"])
    f.read_only = False
    app._tk_root.update()
    assert not plain.instate(["disabled"])
