"""A stretched image element paints from a pre-tiled copy of its image.

ttk draws a stretched image element by repeating the image's middle column
across the parcel, one draw per repeat. The field and button images are a few
dozen pixels wide, so a field stretched across a wide window painted dozens of
repeats per element and its paint time grew with its width. The builder now
registers a copy whose middle column is already repeated, which draws the same
pixels in a few repeats. None of it may be visible: not the pixels, not the
element's requested size, and not an element that does not stretch.
"""
from __future__ import annotations

import base64
import io
import itertools
import tkinter
from tkinter import ttk

import pytest
from PIL import Image as PILImage
from PIL import ImageTk

from bootstack.style.element import ElementImage
from bootstack.style.style import get_style
from bootstack.style.utility import recolor_element_image

pytestmark = pytest.mark.gui

_ids = itertools.count()


def _name():
    return f"PretileTest{next(_ids)}.border"


@pytest.fixture
def created(app, monkeypatch):
    """The style builder, and the images each element it creates is given."""
    style = get_style()
    real = style.element_create
    calls = []

    def spy(name, kind, *args, **kwargs):
        calls.append((args, kwargs))
        return real(name, kind, *args, **kwargs)

    monkeypatch.setattr(style, "element_create", spy)
    return style.style_builder, calls


def _striped(width=20, height=6):
    """A photo whose every pixel differs, some of them partly transparent."""
    img = PILImage.new("RGBA", (width, height))
    img.putdata([
        (x * 12, 255 - x * 12, y * 40, 128 if (x + y) % 3 == 0 else 255)
        for y in range(height) for x in range(width)
    ])
    return ImageTk.PhotoImage(img)


def _pixels(app, image):
    data = app.tk.call(image, "data", "-format", "png")
    if not isinstance(data, bytes):  # a Tk that returns PNG data base64-encoded
        data = base64.b64decode(data)
    return PILImage.open(io.BytesIO(data)).convert("RGBA")


def test_a_stretched_element_draws_the_same_pixels_in_fewer_repeats(app, created):
    builder, calls = created
    source = _striped()
    # Three values are left, top-and-bottom, right.
    left, right = 3, 5
    builder.create_style_element_image(
        ElementImage(_name(), source, border=(left, 1, right), sticky="ew"))
    (image, *_), _ = calls[-1]

    original = _pixels(app, str(source))
    tiled = _pixels(app, image)
    middle = original.width - left - right
    span = tiled.width - left - right
    # The copy repeats the middle in whole repeats, and few enough of them fill
    # a 1000-pixel parcel. The original's 12-pixel middle takes 84.
    assert span % middle == 0
    assert -(-1000 // span) <= 4

    # What ttk draws over the copy's width from the original: the left and right
    # columns as they are, the middle repeated from its left edge.
    expected = PILImage.new("RGBA", tiled.size)
    expected.paste(original.crop((0, 0, left, original.height)), (0, 0))
    for x in range(left, left + span, middle):
        expected.paste(original.crop((left, 0, left + middle, original.height)), (x, 0))
    expected.paste(original.crop((original.width - right, 0, original.width, original.height)), (left + span, 0))
    assert tiled.tobytes() == expected.tobytes()


def test_a_pretiled_element_keeps_the_size_its_image_asks_for(app, created):
    builder, calls = created
    result = recolor_element_image("input_default", "#ffffff", "#000000")
    sizes = []
    labels = []
    for stock in (True, False):
        name = _name()
        if stock:
            app.tk.call("ttk::style", "element", "create", name, "image", result.image,
                        "-border", result.meta.border, "-sticky", "nsew")
        else:
            builder.create_style_element_image(
                ElementImage(name, result.image, border=result.meta.border, sticky="nsew"))
            (image, *_), _ = calls[-1]
            assert image != str(result.image)  # precondition: given a copy
        style = name.replace(".border", ".TLabel")
        get_style().layout(style, [(name, {"sticky": "nsew", "children": [
            ("Label.label", {"sticky": "nsew"})]})])
        label = ttk.Label(app.tk, style=style)
        labels.append(label)
        sizes.append((label.winfo_reqwidth(), label.winfo_reqheight()))
    for label in labels:
        label.destroy()
    assert sizes[1] == sizes[0]


@pytest.mark.parametrize("sticky", ["", "ns"])
def test_an_element_that_does_not_stretch_keeps_its_image(app, created, sticky):
    builder, calls = created
    source = _striped()
    builder.create_style_element_image(ElementImage(_name(), source, border=4, sticky="ew"))
    (image, *_), _ = calls[-1]
    assert image != str(source)  # precondition: the same image stretched gets a copy

    builder.create_style_element_image(ElementImage(_name(), source, border=4, sticky=sticky))
    (image, *_), options = calls[-1]
    assert image == str(source)
    assert "width" not in options


def test_an_image_that_cannot_be_copied_is_registered_as_it_is(app, created):
    builder, calls = created
    # A bitmap image has a size but is not a photo, so it cannot be copied from.
    source = tkinter.BitmapImage(master=app.tk, data=(
        "#define b_width 8\n#define b_height 8\n"
        "static unsigned char b_bits[] = {\n"
        "   0xff, 0x81, 0x81, 0x81, 0x81, 0x81, 0x81, 0xff };\n"))
    name = _name()
    builder.create_style_element_image(ElementImage(name, source, border=2, sticky="ew"))
    (image, *_), options = calls[-1]
    assert image == str(source)
    assert "width" not in options
    assert name in get_style().element_names()


def test_elements_sharing_an_image_share_one_copy(app, created, monkeypatch):
    builder, calls = created
    source = _striped()
    before = set(map(str, app.tk.call("image", "names")))

    # No sticky draws stretched both ways, the same as `nsew`.
    name = _name()
    builder.create_style_element_image(ElementImage(name, source, border=2))
    builder.create_style_element_image(
        ElementImage(_name(), source, border=2, sticky="nsew").state_specs([("disabled", source)]))
    (first, *_), _ = calls[-2]
    (second, (_, state)), _ = calls[-1]
    assert first != str(source)  # precondition: given a copy
    assert first == second == state

    assert set(map(str, app.tk.call("image", "names"))) - before == {first}

    # A theme rebuild builds every style again; the element already exists, so
    # its images are not looked up at all.
    lookups = []
    monkeypatch.setattr(
        "bootstack.style.style_builder_ttk.pretile_element_image",
        lambda image, *args: lookups.append(image) or image)
    builder.create_style_element_image(ElementImage(_name(), source, border=2))
    assert lookups  # precondition: a new element does look its images up
    del lookups[:]
    builder.create_style_element_image(ElementImage(name, source, border=2))
    assert not lookups
