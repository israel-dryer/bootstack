"""Screenshot scenes for the Picture widget.

The demo images are generated once at import so no external assets are needed.
"""

import os
import tempfile

from PIL import Image as PILImage, ImageDraw
from PIL.Image import Resampling

import bootstack as bs
from bootstack.images import Image

_DIR = tempfile.gettempdir()


def _photo(name: str, w: int, h: int) -> str:
    """A simple gradient 'photo' with a light subject, written to a temp PNG."""
    path = os.path.join(_DIR, f"bs_pic_{name}.png")
    img = PILImage.new("RGB", (w, h))
    px = img.load()
    for y in range(h):
        for x in range(w):
            px[x, y] = (int(40 + 200 * x / w), int(60 + 150 * y / h), 170)
    # Draw the subject supersampled and downscale so its edge is antialiased
    # (ImageDraw.ellipse is jagged at 1x).
    ss = 4
    layer = PILImage.new("RGBA", (w * ss, h * ss), (0, 0, 0, 0))
    r = (min(w, h) // 4) * ss
    cx, cy = w * ss // 2, h * ss // 2
    ImageDraw.Draw(layer).ellipse([cx - r, cy - r, cx + r, cy + r], fill=(248, 248, 250, 255))
    layer = layer.resize((w, h), Resampling.LANCZOS)
    img = img.convert("RGBA")
    img.alpha_composite(layer)
    img.convert("RGB").save(path)
    return path


_LANDSCAPE = _photo("landscape", 320, 200)


def hero():
    with bs.App(title="Picture", padding=20) as app:
        bs.Picture(_LANDSCAPE, fit="cover", width=380, height=240, corner_radius=16)
    app.run()


def fit():
    with bs.App(title="Picture — Fit modes", padding=20, gap=8) as app:
        with bs.HStack(gap=16, fill="x"):
            for mode in ("contain", "cover", "fill"):
                with bs.VStack(gap=4):
                    bs.Picture(_LANDSCAPE, fit=mode, width=150, height=150, surface="card")
                    bs.Label(mode, font="caption", anchor="center")
    app.run()


def corners():
    with bs.App(title="Picture — Rounded corners", padding=20, gap=8) as app:
        with bs.HStack(gap=16, fill="x"):
            for radius in (0, 16, 36):
                with bs.VStack(gap=4):
                    bs.Picture(_LANDSCAPE, fit="cover", width=150, height=150,
                               corner_radius=radius)
                    bs.Label(f"radius={radius}", font="caption", anchor="center")
    app.run()


SCENES = {
    "hero": hero,
    "fit": fit,
    "corners": corners,
}
