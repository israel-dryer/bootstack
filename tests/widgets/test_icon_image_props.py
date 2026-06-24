"""Live `icon` / `image` properties and the icon-spec form.

Uses the shared `app` fixture from tests/conftest.py, which pushes a container so
bare widgets created in a test have somewhere to mount. (A private module-scoped
fixture used to create a second Tk root and push no container, which raised under
the builder-pattern parent guard.)
"""

from __future__ import annotations

import bootstack as bs
from bootstack.images import get_icon


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
