"""Headless tests for the public image handles and icon factory.

These exercise `bootstack.images` without creating an application, proving that a
handle carries no toolkit resource until it is bound to a widget.
"""

from __future__ import annotations

import io

import pytest
from PIL import Image as PILImage

from bootstack.images import AppIcon, Image, get_icon


def _png_bytes(size=(7, 11), color=(10, 20, 30, 255)) -> bytes:
    buf = io.BytesIO()
    PILImage.new("RGBA", size, color).save(buf, "PNG")
    return buf.getvalue()


def test_open_reports_size_without_an_app(tmp_path):
    p = tmp_path / "a.png"
    p.write_bytes(_png_bytes((13, 17)))
    img = Image.open(p)
    assert (img.width, img.height) == (13, 17)
    assert img._photo is None  # nothing rendered yet


def test_from_bytes_reports_size():
    img = Image.from_bytes(_png_bytes((5, 9)))
    assert (img.width, img.height) == (5, 9)


def test_from_pil_reports_size():
    img = Image.from_pil(PILImage.new("RGB", (4, 6)))
    assert (img.width, img.height) == (4, 6)


def test_get_icon_builds_no_toolkit_object():
    icon = get_icon("house")
    assert (icon.width, icon.height) == (20, 20)
    assert icon._photo is None


def test_get_icon_size_override():
    assert get_icon("gear", size=32).width == 32


def test_token_color_is_theme_following():
    assert get_icon("house", color="primary")._is_theme_following is True


def test_hex_color_is_static():
    assert get_icon("house", color="#ff8800")._is_theme_following is False


@pytest.mark.parametrize("ext", [".ico", ".png", ".icns"])
def test_appicon_save_exports_each_format(tmp_path, ext):
    out = tmp_path / f"app{ext}"
    AppIcon("rocket", background="#0d6efd", foreground="#ffffff").save(out)
    assert out.exists() and out.stat().st_size > 0


def test_appicon_rejects_unknown_format(tmp_path):
    with pytest.raises(ValueError):
        AppIcon("rocket").save(tmp_path / "app.bmp")


def test_appicon_hex_render_needs_no_app(tmp_path):
    # Hex colors resolve without a running application (the build-time path).
    out = AppIcon("rocket", background="#222222", foreground="#ffffff").save(
        tmp_path / "build.ico"
    )
    assert PILImage.open(out).size == (256, 256)


def _edge_alpha(path) -> int:
    # Top-edge midpoint: opaque on a tile (filled background), transparent on a
    # glyph-only mark.
    im = PILImage.open(path).convert("RGBA")
    w, _ = im.size
    return im.getpixel((w // 2, 2))[3]


def _ico_edge_alpha(path, size: int) -> int:
    # Same probe, but for a specific frame inside a multi-size `.ico`.
    frame = PILImage.open(path).ico.getimage((size, size)).convert("RGBA")
    return frame.getpixel((size // 2, max(1, size // 16)))[3]


def test_auto_shape_is_mixed_for_ico(tmp_path):
    # auto on Windows/Linux: small frames glyph-only, large frames tiled.
    out = AppIcon("rocket", background="#0d6efd").save(tmp_path / "a.ico")
    assert _ico_edge_alpha(out, 16) == 0      # title-bar frame — bare mark
    assert _ico_edge_alpha(out, 256) == 255   # large frame — filled tile


def test_auto_shape_is_tiled_for_icns(tmp_path):
    out = AppIcon("rocket", background="#0d6efd").save(tmp_path / "a.icns")
    assert _edge_alpha(out) == 255  # filled tile


def test_forced_tile_on_ico(tmp_path):
    out = AppIcon("rocket", background="#0d6efd", shape="tile").save(tmp_path / "t.ico")
    assert _edge_alpha(out) == 255


def test_forced_glyph_on_icns(tmp_path):
    out = AppIcon("rocket", background="#0d6efd", shape="glyph").save(tmp_path / "g.icns")
    assert _edge_alpha(out) == 0
