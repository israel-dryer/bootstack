"""A caller's option dict meeting the framework's own keyword arguments.

Several widgets accept a bag of options aimed at a widget they build for you —
`MenuButton`'s `menu_options`, the keyword passthrough on `ButtonGroup.add` /
`RadioGroup.add` / `ToggleGroup.add`, and `Toolbar` / `StatusBar`
`add_widget()`. Each used to splat that bag alongside its own explicit keyword
arguments, so naming a parameter the framework also filled raised
`TypeError: got multiple values for keyword argument` from an internal class
the caller never wrote.

The rule is now uniform: the caller's options win, except for structural keys
that raise `BootstackError` naming the API called and what to use instead.
"""
from __future__ import annotations

import pytest

import bootstack as bs
from bootstack.errors import BootstackError


# --- The caller's options win over the framework's defaults --------------

def test_menu_options_reach_the_menu(app):
    # Asserting construction alone would pass even if the options were dropped
    # on the floor, so read the value back off the menu it was aimed at.
    mb = bs.MenuButton("Actions", items=[{"type": "command", "text": "X"}],
                       menu_options={"anchor": "se"})
    assert mb._internal.context_menu._anchor == "se"


def test_button_group_add_all_accepts_text(app):
    # add_all() documents its dicts as "keyword arguments accepted by add()",
    # and `text` is what the rendered button calls its caption.
    group = bs.ButtonGroup()
    group.add_all([{"text": "Save"}, {"text": "Cancel"}])
    assert group.query_item(group.keys[0], "text") == "Save"


def test_button_group_caption_via_text_is_not_icon_only(app):
    # `icon_only` is derived from the caption. Deriving it from the `label`
    # argument instead of the merged text made a text+icon button icon-only,
    # which renders with zero padding — a crammed, clipped button.
    group = bs.ButtonGroup()
    group.add_all([{"text": "Save", "icon": "star"}])
    group.add("Save", icon="star")
    by_label, by_text = group.keys[1], group.keys[0]
    assert group.query_item(by_text, "icon_only") == group.query_item(by_label, "icon_only")


def test_button_group_icon_without_caption_is_icon_only(app):
    # The control for the test above: a genuine icon-only button still infers.
    group = bs.ButtonGroup()
    group.add("", icon="star")
    assert group.query_item(group.keys[0], "icon_only") is True


@pytest.mark.parametrize("factory", [bs.RadioGroup, bs.ToggleGroup])
def test_option_group_accepts_derived_render_kwargs(app, factory):
    # `icon_only` and `state` are derived from `icon`/`disabled`; passing them
    # explicitly must override, not collide — and must actually take effect.
    group = factory()
    group.add("", value="a", icon="house", icon_only=True)
    group.add("B", value="b", state="disabled")
    assert group._internal.item("b").instate(("disabled",)) is True


def test_toolbar_add_button_kwargs_win(app):
    bar = bs.Toolbar()
    button = bar.add_button("Go", text="Override")
    assert button.text == "Override"


# --- Structural keys raise a clear error, not a raw TypeError ------------

def test_button_group_command_is_reserved(app):
    group = bs.ButtonGroup()
    with pytest.raises(BootstackError, match=r"ButtonGroup\.add\(\) does not accept command="):
        group.add("Save", command=lambda: None)


@pytest.mark.parametrize("factory", [bs.RadioGroup, bs.ToggleGroup])
@pytest.mark.parametrize("key", ["text", "variable"])
def test_option_group_structural_keys_are_reserved(app, factory, key):
    # NB `value` is a named parameter of add(), so it can never arrive via
    # **kwargs and needs no guard.
    group = factory()
    with pytest.raises(BootstackError, match=rf"\.add\(\) does not accept {key}="):
        group.add("A", value="a", **{key: "x"})


@pytest.mark.parametrize("key", ["items", "command", "target", "trigger"])
def test_menu_options_structural_keys_are_reserved(app, key):
    # `trigger` is reserved because the button already opens its own menu on
    # click: a second trigger binds a rival handler that opens the menu at the
    # pointer, so the two fire on one click.
    with pytest.raises(BootstackError, match=rf"menu_options does not accept {key}="):
        bs.MenuButton("Actions", items=[{"type": "command", "text": "X"}],
                      menu_options={key: "click"})


def test_toolbar_add_widget_parent_is_reserved(app):
    bar = bs.Toolbar()
    with pytest.raises(BootstackError, match=r"Toolbar\.add_widget\(\) does not accept parent="):
        bar.add_widget(bs.Label, parent=bar)


def test_toolbar_add_button_parent_is_reserved(app):
    bar = bs.Toolbar()
    with pytest.raises(BootstackError, match=r"Toolbar\.add_button\(\) does not accept parent="):
        bar.add_button("Go", parent=bar)


def test_toolbar_add_label_parent_is_reserved(app):
    bar = bs.Toolbar()
    with pytest.raises(BootstackError, match=r"Toolbar\.add_label\(\) does not accept parent="):
        bar.add_label("Hi", parent=bar)


def test_statusbar_add_widget_parent_is_reserved(app):
    bar = bs.StatusBar()
    with pytest.raises(BootstackError, match=r"StatusBar\.add_widget\(\) does not accept parent="):
        bar.add_widget(bs.Label, parent=bar)
