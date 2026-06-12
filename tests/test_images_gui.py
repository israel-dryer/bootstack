"""GUI tests for image binding, theme-following, and window icons.

One `App` per process: these all run under a single module-scoped application
(creating a second `App` in the same process crashes Tk on Windows).
"""

from __future__ import annotations

import pytest
from PIL import Image as PILImage

import bootstack as bs
from bootstack.images import AppIcon, Image, get_icon


@pytest.fixture(scope="module")
def app():
    with bs.App(theme="bootstrap-light") as a:
        yield a


@pytest.fixture(scope="module")
def png(tmp_path_factory):
    p = tmp_path_factory.mktemp("img") / "a.png"
    PILImage.new("RGBA", (24, 24), (200, 50, 50, 255)).save(p)
    return str(p)


def test_label_renders_image_handle(app, png):
    lbl = bs.Label("Hi", image=Image.open(png))
    app.tk.update()
    assert lbl._internal.cget("image")  # a real image is set
    assert lbl._image_photo is not None


def test_button_renders_icon_handle(app):
    btn = bs.Button("Save", image=get_icon("save", color="foreground"))
    app.tk.update()
    assert btn._internal.cget("image")


def test_token_icon_rerenders_on_theme_change(app):
    lbl = bs.Label("X", image=get_icon("house", color="foreground"))
    app.tk.update()
    before = lbl._image_photo
    app.theme = "bootstrap-dark"
    app.tk.update()
    assert lbl._image_photo is not before  # re-rendered for the new theme
    app.theme = "bootstrap-light"
    app.tk.update()


def test_hex_icon_does_not_rerender_on_theme_change(app):
    lbl = bs.Label("X", image=get_icon("gear", color="#ff8800"))
    app.tk.update()
    before = lbl._image_photo
    app.theme = "bootstrap-dark"
    app.tk.update()
    assert lbl._image_photo is before
    app.theme = "bootstrap-light"
    app.tk.update()


def test_window_accepts_each_icon_type(app, png):
    w_path = bs.Window(title="p", icon=png)
    w_image = bs.Window(title="i", icon=Image.open(png))
    w_appicon = bs.Window(title="a", icon=AppIcon("gear", background="#333333"))
    app.tk.update()
    assert w_image._window_icon_photo is not None
    # path / AppIcon routes go through the file path, not a retained photo
    assert w_path._window_icon_photo is None
    assert w_appicon._window_icon_photo is None
