"""Carousel — one image slide at a time, with prev/next navigation.

Run this directly to see the widget. The demo images are generated at startup,
so no external assets are needed. Use the chevrons, the arrow keys, or the dots
to navigate; double-click is not needed — a single click on the slide prints it.
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
    path = os.path.join(_DIR, f"bs_carousel_{i}.png")
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


items = [{"id": i, "image": _slide(i), "name": f"Slide {i + 1}"} for i in range(5)]

with bs.App(title="Carousel", size=(620, 460), padding=16, gap=8) as app:
    bs.Label("Image carousel — chevrons, arrow keys, or dots", font="heading-md")
    carousel = bs.Carousel(
        items=items,
        image_field="image",
        caption_field="name",
        fit="cover",
        transition="slide",
        indicator="dots",
        corner_radius=14,
        grow=True,
        horizontal="stretch",
    )
    carousel.on_change(lambda r: print("slide:", r["name"]))
    carousel.on_item_click(lambda r: print("clicked:", r["name"]))

app.run()
