"""Shared image fit/crop/round helpers for the media widgets.

Pure functions used by both `Picture` and the `Gallery` tile so the
object-fit scaling and antialiased rounded-corner masking live in one place.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any, Literal

from PIL import Image as PILImage, ImageChops, ImageDraw
from PIL.Image import Resampling

FitMode = Literal["contain", "cover", "fill", "none", "scale-down"]


def resolve_pil(source: Any) -> "PILImage.Image | None":
    """Resolve an image source (Image handle, path, or PIL image) to a PIL image.

    Returns the first frame for an animated source, or None when `source` is
    None or cannot be decoded.
    """
    if source is None:
        return None
    from bootstack.images import Image as _ImageHandle

    try:
        if isinstance(source, _ImageHandle):
            return source._load_pil()
        if isinstance(source, (str, Path)):
            return PILImage.open(Path(source).expanduser())
        if isinstance(source, PILImage.Image):
            return source
    except Exception:
        return None
    return None


def fit_image(frame: PILImage.Image, bw: int, bh: int, fit: FitMode) -> PILImage.Image:
    """Scale (and for `cover`, crop) `frame` to a `bw`x`bh` box per `fit`.

    For `contain`/`scale-down`/`none` the result may be smaller than the box —
    the caller positions it. For `cover`/`fill` the result is exactly the box.
    """
    iw, ih = frame.size
    if iw <= 0 or ih <= 0:
        return frame

    if fit == "fill":
        return frame.resize((bw, bh), Resampling.LANCZOS)

    if fit == "cover":
        scale = max(bw / iw, bh / ih)
        scaled = frame.resize(
            (max(1, round(iw * scale)), max(1, round(ih * scale))), Resampling.LANCZOS
        )
        left = (scaled.width - bw) // 2
        top = (scaled.height - bh) // 2
        return scaled.crop((left, top, left + bw, top + bh))

    # contain / scale-down / none — never crop.
    if fit == "none":
        scale = 1.0
    else:
        scale = min(bw / iw, bh / ih)
        if fit == "scale-down":
            scale = min(scale, 1.0)
    tw, th = max(1, round(iw * scale)), max(1, round(ih * scale))
    if (tw, th) == (iw, ih):
        return frame.copy()
    return frame.resize((tw, th), Resampling.LANCZOS)


def rounded_mask(w: int, h: int, radius: int) -> PILImage.Image:
    """An antialiased rounded-rectangle alpha mask for a `w`x`h` box.

    Drawn supersampled and downscaled with LANCZOS — `ImageDraw.rounded_rectangle`
    is aliased at 1x, so the curve would otherwise be jagged. Callers should cache
    the result; it depends only on `(w, h, radius)`.
    """
    radius = min(radius, w // 2, h // 2)
    ss = 4 if max(w, h) <= 600 else 2
    big = PILImage.new("L", (w * ss, h * ss), 0)
    ImageDraw.Draw(big).rounded_rectangle(
        [0, 0, w * ss - 1, h * ss - 1], radius=radius * ss, fill=255
    )
    return big.resize((w, h), Resampling.LANCZOS)


def round_corners(
    img: PILImage.Image, radius: int, mask: PILImage.Image | None = None
) -> PILImage.Image:
    """Apply a rounded-rectangle alpha mask to `img` (intersecting existing alpha).

    Pass a precomputed `mask` (from `rounded_mask`) to avoid rebuilding it.
    """
    w, h = img.size
    if radius <= 0:
        return img
    if mask is None:
        mask = rounded_mask(w, h, radius)
    out = img.convert("RGBA")
    out.putalpha(ImageChops.multiply(mask, out.getchannel("A")))
    return out
