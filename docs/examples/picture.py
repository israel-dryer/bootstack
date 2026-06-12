"""Picture — image display with fit modes, rounded corners, and animation.

Run this directly to see the widget. The demo images are generated at startup,
so no external assets are needed.
"""

import os
import tempfile

from PIL import Image as PILImage, ImageDraw
from PIL.Image import Resampling

import bootstack as bs
from bootstack.images import Image


def _make_photo() -> str:
    """A simple gradient 'photo' (wide aspect) written to a temp PNG."""
    w, h = 320, 200
    img = PILImage.new("RGB", (w, h))
    px = img.load()
    for y in range(h):
        for x in range(w):
            px[x, y] = (int(255 * x / w), int(160 * y / h), 140)
    # Supersample the subject so its edge is antialiased (ellipse is jagged at 1x).
    ss = 4
    layer = PILImage.new("RGBA", (w * ss, h * ss), (0, 0, 0, 0))
    ImageDraw.Draw(layer).ellipse(
        [120 * ss, 60 * ss, 200 * ss, 140 * ss], fill=(250, 250, 250, 255)
    )
    layer = layer.resize((w, h), Resampling.LANCZOS)
    img = img.convert("RGBA")
    img.alpha_composite(layer)
    img = img.convert("RGB")
    path = os.path.join(tempfile.gettempdir(), "bs_picture_photo.png")
    img.save(path)
    return path


def _make_gif() -> str:
    """A 4-frame animated GIF (a sweeping wedge) written to a temp file."""
    frames = []
    for i in range(8):
        f = PILImage.new("RGB", (120, 120), (20, 24, 40))
        d = ImageDraw.Draw(f)
        start = i * 45
        d.pieslice([10, 10, 110, 110], start, start + 90, fill=(90, 200, 250))
        frames.append(f)
    path = os.path.join(tempfile.gettempdir(), "bs_picture_anim.gif")
    frames[0].save(path, save_all=True, append_images=frames[1:], duration=90, loop=0)
    return path


photo = _make_photo()
anim = _make_gif()

with bs.App(title="Picture", size=(560, 520), padding=16, gap=12) as app:
    bs.Label("Fit modes (same wide photo in a fixed square box)", font="heading-md")
    with bs.HStack(gap=12):
        for mode in ("contain", "cover", "fill"):
            with bs.VStack(gap=4):
                bs.Picture(photo, fit=mode, width=150, height=150, surface="card")
                bs.Label(mode, font="caption", anchor="center")

    bs.Separator()

    with bs.HStack(gap=16):
        with bs.VStack(gap=4):
            bs.Label("Rounded corners", font="heading-md")
            bs.Picture(photo, fit="cover", width=150, height=150, corner_radius=20)
        with bs.VStack(gap=4):
            bs.Label("Animated GIF (autoplay)", font="heading-md")
            bs.Picture(Image.open(anim), width=140, height=140, surface="card")

    bs.Separator()

    bs.Label("Responsive — resize the window", font="heading-md")
    bs.Picture(photo, fit="contain", surface="card", fill="both", expand=True)

app.run()
