"""Screenshot scenes for the Carousel widget.

Demo images are generated once at import, so no external assets are needed.
"""

import os
import tempfile

from PIL import Image as PILImage, ImageDraw
from PIL.Image import Resampling

import bootstack as bs

_DIR = tempfile.gettempdir()
_PALETTE = [
    (220, 90, 90), (90, 170, 110), (90, 130, 220), (210, 160, 70), (160, 110, 200),
]


def _slide(i: int) -> str:
    path = os.path.join(_DIR, f"bs_carshot_{i}.png")
    w, h = 480, 300
    base = _PALETTE[i % len(_PALETTE)]
    img = PILImage.new("RGB", (w, h))
    px = img.load()
    for y in range(h):
        for x in range(w):
            px[x, y] = (
                int(base[0] * (0.5 + 0.5 * x / w)),
                int(base[1] * (0.5 + 0.5 * y / h)),
                int(base[2] * (0.6 + 0.4 * y / h)),
            )
    ss = 4
    layer = PILImage.new("RGBA", (w * ss, h * ss), (0, 0, 0, 0))
    r = 70 * ss
    cx, cy = w * ss // 2, h * ss // 2
    ImageDraw.Draw(layer).ellipse([cx - r, cy - r, cx + r, cy + r], fill=(255, 255, 255, 225))
    layer = layer.resize((w, h), Resampling.LANCZOS)
    img = img.convert("RGBA")
    img.alpha_composite(layer)
    img.convert("RGB").save(path)
    return path


_MANY = [{"id": i, "image": _slide(i), "name": f"Photo {i + 1}"} for i in range(24)]


def many():
    # With more than 8 slides, indicator="dots" auto-switches to a count label.
    with bs.App(title="Carousel — many slides", size=(620, 440), padding=16) as app:
        bs.Carousel(items=_MANY, image_field="image", caption_field="name",
                    fit="cover", indicator="dots", corner_radius=14,
                    grow=True, horizontal="stretch")
    app.run()


SCENES = {
    "many": many,
}
