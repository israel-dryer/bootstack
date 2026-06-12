"""Live `icon` / `image` properties and the icon-spec form (one App/process)."""

from __future__ import annotations

import pytest

import bootstack as bs
from bootstack.images import get_icon


@pytest.fixture(scope="module")
def app():
    a = bs.App()
    a._tk_root.withdraw()
    try:
        yield a
    finally:
        try:
            a._tk_root.destroy()
        except Exception:
            pass


def test_label_icon_and_image_settable(app):
    lbl = bs.Label("Hi", icon="house")
    lbl.icon = "gear"
    assert lbl.icon == "gear"
    lbl.image = get_icon("star", size=20)
    assert lbl.image is not None


def test_button_icon_and_image_settable(app):
    btn = bs.Button("Go", icon="house")
    btn.icon = "gear"
    assert btn.icon == "gear"
    btn.image = get_icon("star", size=20)
    assert btn.image is not None


def test_menubutton_and_selectbutton_icon_settable(app):
    mb = bs.MenuButton("M", icon="house")
    mb.icon = "gear"
    assert mb.icon == "gear"
    sb = bs.SelectButton(options=["a", "b"], icon="house")
    sb.icon = "gear"
    assert sb.icon == "gear"


def test_clearing_image_releases_theme_binding(app):
    lbl = bs.Label("Hi")
    # A token-colored icon follows the theme, installing a <<BsThemeChanged>>
    # binding that re-renders it on theme change.
    lbl.image = get_icon("star", size=20, color="primary")
    app._tk_root.update_idletasks()
    assert getattr(lbl, "_image_theme_binding", None) is not None

    # Clearing the image must release that binding — otherwise it keeps pinning
    # the old handle and re-applying a removed image on theme changes.
    lbl.image = None
    assert getattr(lbl, "_image_theme_binding", None) is None
    assert lbl.image is None


def test_icon_spec_with_size_and_token_color(app):
    spec = {"name": "bell-fill", "size": 24, "color": "primary"}
    btn = bs.Button("Go", icon=spec)
    app._tk_root.update_idletasks()
    assert btn.icon == spec  # accepted and round-trips
    # and assignable as a spec
    btn.icon = {"name": "gear", "size": 18, "color": "#ff8800"}
    assert btn.icon["name"] == "gear"
