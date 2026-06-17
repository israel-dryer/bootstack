"""Gallery — a scrollable, selectable grid of image thumbnails.

Run this directly to see the widget. The demo images are generated at startup,
so no external assets are needed. Click a tile to select it; double-click to
"open" it (printed to the console).
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
    """A gradient thumbnail with an antialiased numbered disc."""
    path = os.path.join(_DIR, f"bs_gallery_{i}.png")
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
    d = ImageDraw.Draw(layer)
    r = 46 * ss
    cx, cy = w * ss // 2, h * ss // 2
    d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=(255, 255, 255, 230))
    layer = layer.resize((w, h), Resampling.LANCZOS)
    img = img.convert("RGBA")
    img.alpha_composite(layer)
    img.convert("RGB").save(path)
    return path


items = [
    {"id": i, "image": _thumb(i), "name": f"Photo {i + 1}"}
    for i in range(18)
]

with bs.App(title="Gallery", size=(620, 480), padding=16, gap=8) as app:
    bs.Label("Image gallery — click to select, double-click to open", font="heading-md")
    gallery = bs.Gallery(
        items=items,
        image_field="image",
        caption_field="name",
        columns="auto",
        tile_size=(140, 110),
        corner_radius=10,
        selection_mode="multi",
        grow=True,
        horizontal="stretch",
    )
    gallery.on_item_activate(lambda r: print("open:", r["name"]))

app.run()
