"""Screenshot scenes for the Gallery widget.

Demo images are generated once at import, so no external assets are needed.
"""

import os
import tempfile

from PIL import Image as PILImage, ImageDraw
from PIL.Image import Resampling

import bootstack as bs

_DIR = tempfile.gettempdir()
_PALETTE = [
    (220, 90, 90), (90, 170, 110), (90, 130, 220), (210, 160, 70),
    (160, 110, 200), (80, 180, 200), (200, 110, 160), (120, 140, 90),
]


def _thumb(i: int) -> str:
    path = os.path.join(_DIR, f"bs_galshot_{i}.png")
    w, h = 240, 180
    base = _PALETTE[i % len(_PALETTE)]
    img = PILImage.new("RGB", (w, h))
    px = img.load()
    for y in range(h):
        for x in range(w):
            px[x, y] = (
                int(base[0] * (0.5 + 0.5 * x / w)),
                int(base[1] * (0.5 + 0.5 * y / h)),
                int(base[2] * (0.6 + 0.4 * x / w)),
            )
    ss = 4
    layer = PILImage.new("RGBA", (w * ss, h * ss), (0, 0, 0, 0))
    r = 46 * ss
    cx, cy = w * ss // 2, h * ss // 2
    ImageDraw.Draw(layer).ellipse([cx - r, cy - r, cx + r, cy + r], fill=(255, 255, 255, 230))
    layer = layer.resize((w, h), Resampling.LANCZOS)
    img = img.convert("RGBA")
    img.alpha_composite(layer)
    img.convert("RGB").save(path)
    return path


_ITEMS = [{"id": i, "image": _thumb(i), "name": f"Photo {i + 1}"} for i in range(15)]


def hero():
    with bs.App(title="Gallery", size=(620, 460), padding=16) as app:
        bs.Gallery(items=_ITEMS, image_field="image", caption_field="name",
                   tile_size=(140, 110), corner_radius=10, selection_mode="multi",
                   fill="both", expand=True)
    app.run()


def selection():
    with bs.App(title="Gallery — Selection", size=(620, 460), padding=16) as app:
        g = bs.Gallery(items=_ITEMS, image_field="image", caption_field="name",
                       tile_size=(140, 110), corner_radius=10, selection_mode="multi",
                       accent="primary", fill="both", expand=True)
        g.select_items([1, 4, 5])
    app.run()


SCENES = {
    "hero": hero,
    "selection": selection,
}
