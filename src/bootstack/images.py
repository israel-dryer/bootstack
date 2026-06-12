"""Toolkit-free image handles and the icon factory.

This module is the public, framework-native way to work with images and icons:

- `Image` — a lightweight handle that holds image data (or a deferred icon spec)
  and is only rendered for display when you hand it to a widget. You can build one
  before an application exists; nothing about the underlying toolkit is exposed.
- `get_icon` — create a theme-aware `Image` from a Bootstrap Icons name. When the
  color is given as a theme token, the icon re-renders automatically as the theme
  changes.
- `AppIcon` — generate a platform application icon (a glyph on a filled,
  rounded background) for an `App` or `Window`.

Examples:
    ```python
    import bootstack as bs
    from bootstack.images import Image, get_icon

    with bs.App() as app:
        bs.Label(image=Image.open("logo.png"))
        bs.Button("Save", image=get_icon("save", color="primary"))
    app.run()
    ```
"""

from __future__ import annotations

import atexit
import io
import math
import os
import re
import sys
import tempfile
from dataclasses import dataclass
from pathlib import Path
from typing import TYPE_CHECKING

from bootstack._core.images import _ImageService

if TYPE_CHECKING:
    from PIL.Image import Image as _PILImage
    from PIL.ImageTk import PhotoImage as _Photo

__all__ = ["Image", "get_icon", "AppIcon", "list_icons"]

# A color is treated as a literal hex value only when it starts with '#';
# every other string is a theme color token resolved against the active theme.
_HEX_RE = re.compile(r"^#[0-9a-fA-F]{3,8}$")

_DEFAULT_ICON_SIZE = 20
_DEFAULT_ICON_COLOR = "foreground"

# Sizes baked into a Windows multi-resolution `.ico`. Includes the DPI-scaled
# title-bar/taskbar sizes (20, 40, ...) so Windows finds an exact match at
# 125%/150%/200% scaling instead of upscaling the nearest one (which blurs).
_APP_ICON_SIZES = [16, 20, 24, 32, 40, 48, 64, 96, 128, 256]

# With shape='auto' on Windows/Linux, frames below this size are drawn glyph-only
# (a bare mark reads cleaner than a cramped tile in a tiny title bar) and frames
# at or above it get the rounded tile (a branded icon for the taskbar, the task
# switcher, and launchers).
_AUTO_TILE_MIN_SIZE = 24
# The rounded tile is supersampled to at least this canvas size before being
# downscaled, so its curved corners get antialiased (PIL draws them aliased at
# 1x). The glyph is NOT supersampled with it — it is rendered at its final size.
_MIN_TILE_CANVAS = 128

# Fraction of the icon edge the glyph box occupies, interpolated by size. Small
# icons use less padding (a bigger glyph) so the mark stays legible when there are
# few pixels; large icons get app-icon-style margins. (The glyph renderer adds a
# little inset of its own, so the visible mark is somewhat smaller than this.)
# Endpoints are reached at <= 16 px and >= 96 px; sizes between interpolate.
_GLYPH_FRAC_SMALL_SIZE = 16
_GLYPH_FRAC_LARGE_SIZE = 96
# On a tile the glyph sits inside the rounded background; glyph-only icons (no
# tile) let the mark nearly fill the frame.
_TILE_GLYPH_FRAC = (0.80, 0.64)        # (small, large)
_GLYPH_ONLY_FRAC = (0.98, 0.90)


def _glyph_frac(size: int, *, tiled: bool) -> float:
    """Glyph box fraction for `size`, smaller icons getting less padding."""
    small, large = _TILE_GLYPH_FRAC if tiled else _GLYPH_ONLY_FRAC
    lo, hi = _GLYPH_FRAC_SMALL_SIZE, _GLYPH_FRAC_LARGE_SIZE
    if size <= lo:
        return small
    if size >= hi:
        return large
    t = (size - lo) / (hi - lo)
    return small + t * (large - small)


def _unlink_at_exit(path: str) -> None:
    """Best-effort removal of a generated runtime icon tempfile at interpreter exit."""

    def _remove() -> None:
        try:
            os.unlink(path)
        except OSError:
            pass

    atexit.register(_remove)


def _resolve_color(color: str) -> str:
    """Resolve a color string to a literal value.

    A `#hex` value is returned unchanged; any other string is treated as a theme
    color token and resolved against the active theme, falling back to the
    literal string when there is no theme or the token is unknown.
    """
    if _HEX_RE.match(color):
        return color
    from bootstack.style import get_theme_color

    try:
        return get_theme_color(color)
    except Exception:
        return color


@dataclass(frozen=True)
class _IconSpec:
    """A deferred icon: the parameters to render a glyph on demand."""

    name: str
    size: int
    color: str
    is_token: bool


class Image:
    """A toolkit-free image handle, rendered for display only when used.

    An `Image` carries a source — a file, raw bytes, an in-memory picture, or a
    deferred icon — without creating any display resource up front. The picture
    is rendered the moment it is handed to a widget (via `image=`), so a handle
    can be built before an application is running and shared across widgets.

    Build one with `Image.open`, `Image.from_bytes`, or `Image.from_pil`, or use
    `get_icon` for a Bootstrap icon. Read `width` and `height` at any time.

    File and byte sources accept the common raster image formats — PNG, JPEG,
    GIF, BMP, TIFF, WebP, and ICO. (Animated formats load their first frame.)
    """

    __slots__ = ("_pil", "_path", "_data", "_icon", "_photo", "_size")

    def __init__(
        self,
        *,
        pil: "_PILImage | None" = None,
        path: Path | None = None,
        data: bytes | None = None,
        icon: _IconSpec | None = None,
    ) -> None:
        self._pil = pil
        self._path = path
        self._data = data
        self._icon = icon
        self._photo: "_Photo | None" = None
        self._size: tuple[int, int] | None = None

    # =========================================================================
    # Constructors
    # =========================================================================

    @classmethod
    def open(cls, path: str | Path) -> "Image":
        """Create an image handle from a file on disk.

        The file is decoded lazily, so the path is not read until the image is
        displayed or its size is queried.

        Args:
            path: Path to the image file. Supports `~` expansion. Accepts the
                common raster formats — PNG, JPEG, GIF, BMP, TIFF, WebP, and ICO.

        Returns:
            A new image handle.
        """
        return cls(path=Path(path).expanduser())

    @classmethod
    def from_bytes(cls, data: bytes) -> "Image":
        """Create an image handle from raw, encoded image bytes.

        Args:
            data: Encoded image bytes in a common raster format — PNG, JPEG,
                GIF, BMP, TIFF, WebP, or ICO — for example, an embedded resource
                or a downloaded file.

        Returns:
            A new image handle.
        """
        return cls(data=bytes(data))

    @classmethod
    def from_pil(cls, image: "_PILImage") -> "Image":
        """Create an image handle from an in-memory Pillow image.

        Useful when you have already loaded or manipulated a picture with Pillow
        (resizing, filtering, compositing) and want to display the result.

        Args:
            image: A Pillow image object to wrap.

        Returns:
            A new image handle.
        """
        return cls(pil=image)

    # =========================================================================
    # Size
    # =========================================================================

    @property
    def width(self) -> int:
        """The width of the image in pixels."""
        return self._dimensions()[0]

    @property
    def height(self) -> int:
        """The height of the image in pixels."""
        return self._dimensions()[1]

    def _dimensions(self) -> tuple[int, int]:
        if self._size is None:
            if self._icon is not None:
                self._size = (self._icon.size, self._icon.size)
            else:
                pil = self._load_pil()
                self._size = (pil.width, pil.height)
        return self._size

    def _load_pil(self) -> "_PILImage":
        from PIL import Image as PILImage

        if self._pil is not None:
            return self._pil
        if self._path is not None:
            return PILImage.open(self._path)
        if self._data is not None:
            return PILImage.open(io.BytesIO(self._data))
        raise ValueError("image handle has no source")

    # =========================================================================
    # Internal rendering (called at the widget-binding boundary)
    # =========================================================================

    @property
    def _is_theme_following(self) -> bool:
        """Whether this image must re-render when the theme changes."""
        return self._icon is not None and self._icon.is_token

    def _invalidate(self) -> None:
        """Drop the rendered image so the next bind re-renders it."""
        self._photo = None

    def _materialize(self, master=None) -> "_Photo":
        """Render the source to a cached display image and return it.

        The ``master`` is accepted for interface symmetry; the backing service
        renders against the default application root, which exists by the time a
        handle is bound to a widget.
        """
        if self._photo is not None:
            return self._photo
        if self._icon is not None:
            color = self._resolve_icon_color()
            photo = _ImageService.get_icon(self._icon.name, self._icon.size, color)
        elif self._path is not None:
            photo = _ImageService.open(self._path)
        elif self._data is not None:
            photo = _ImageService.from_bytes(self._data)
        elif self._pil is not None:
            photo = _ImageService.from_pil(self._pil)
        else:
            raise ValueError("image handle has no source")
        self._photo = photo
        return photo

    def _resolve_icon_color(self) -> str:
        spec = self._icon
        assert spec is not None
        if not spec.is_token:
            return spec.color
        return _resolve_color(spec.color)


def get_icon(
    name: str,
    *,
    size: int = _DEFAULT_ICON_SIZE,
    color: str = _DEFAULT_ICON_COLOR,
) -> Image:
    """Create a theme-aware icon image from a Bootstrap Icons name.

    The returned handle can be passed to any widget that accepts `image=`. When
    `color` is a theme color token (the default), the icon re-renders to match
    whenever the theme changes; a literal hex color stays fixed.

    Args:
        name: Bootstrap Icons name, for example `'house'` or `'arrow-right'`.
            Browse the catalog at https://icons.getbootstrap.com.
        size: Icon size in pixels. Defaults to `20`.
        color: A theme color token (such as `'foreground'`, `'primary'`, or
            `'danger'`) or a literal hex string like `'#ff8800'`. Token colors
            follow the active theme; hex colors are fixed. Defaults to
            `'foreground'`.

    Returns:
        A new image handle that renders the icon on demand.
    """
    is_hex = bool(_HEX_RE.match(color))
    spec = _IconSpec(name=name, size=int(size), color=color, is_token=not is_hex)
    return Image(icon=spec)


def list_icons(contains: str | None = None) -> list[str]:
    """List the available Bootstrap Icons names, sorted.

    Each name can be used as a widget's `icon=` or passed to `get_icon`.

    Args:
        contains: If given, only names containing this text (case-insensitive)
            are returned. Defaults to `None` (all names).

    Returns:
        A sorted list of icon names.
    """
    _, glyphmap = _ImageService._load_icon_assets()
    names = sorted(glyphmap)
    if contains:
        needle = contains.lower()
        names = [n for n in names if needle in n]
    return names


class AppIcon:
    """A generated application icon.

    Renders a Bootstrap glyph in one of two shapes:

    - a **tile** — the glyph in `foreground` on a filled, rounded `background`
      (the macOS look); or
    - **glyph-only** — the glyph alone in the `background` (brand) color on a
      transparent field (the typical Windows and Linux look).

    By default (`shape='auto'`) the shape follows the platform and the size: a
    tile for macOS targets (`.icns`, or running on macOS); on Windows and Linux,
    glyph-only at small sizes (a clean mark in a tiny title bar) and a tile at
    larger sizes (a branded icon in the taskbar and launchers). A multi-size
    `.ico` therefore carries both. Set `shape` to `'tile'` or `'glyph'` to force
    one shape at every size.

    Pass an `AppIcon` as the `icon=` of an `App` or `Window` to set its taskbar
    and title-bar icon without supplying an icon file, or call `save` to export a
    packaging asset (for example, an icon for a PyInstaller build).

    Colors may be theme color tokens (such as `'primary'`) or literal hex
    strings. Tokens are resolved once, when the icon is generated, so the icon
    does not change as the theme changes; supply a token while an application is
    active, or use hex values. Generating an icon outside a running application —
    such as during a build — must use hex values, since no theme is available to
    resolve a token against.
    """

    def __init__(
        self,
        icon: str,
        *,
        background: str = "primary",
        foreground: str = "white",
        radius: float = 0.22,
        shape: str = "auto",
    ) -> None:
        """Describe an application icon.

        Args:
            icon: Bootstrap Icons name to draw, for example `'rocket'`.
            background: Brand color — fills the rounded background of a tile, or
                colors the glyph itself when glyph-only. A theme color token or a
                hex string. Defaults to `'primary'`.
            foreground: Color of the glyph on a tile (ignored when glyph-only).
                A theme color token or a hex string. Defaults to `'white'`.
            radius: Corner radius of the tile background as a fraction of the
                icon size, from `0.0` (square) to `0.5` (circle). Ignored when
                glyph-only. Defaults to `0.22`.
            shape: `'auto'` (default) follows the platform and size — a tile for
                macOS targets, and on Windows/Linux glyph-only at small sizes with
                a tile at larger sizes. `'tile'` or `'glyph'` force one shape at
                every size.
        """
        self._icon = icon
        self._background = background
        self._foreground = foreground
        self._radius = max(0.0, min(0.5, float(radius)))
        self._shape = shape
        self._cached_path: str | None = None

    def _tiled_for_size(self, size: int, *, suffix: str | None = None) -> bool:
        """Decide whether to draw a tile for a given target size.

        `shape='tile'`/`'glyph'` force the shape. With `shape='auto'`: macOS
        targets (an `.icns` file, or — when no suffix is given — running on
        macOS) are always a tile; Windows and Linux targets are glyph-only below
        `_AUTO_TILE_MIN_SIZE` and a tile at or above it, so a multi-size `.ico`
        carries bare marks for the title bar and tiles for the taskbar.
        """
        if self._shape == "tile":
            return True
        if self._shape == "glyph":
            return False
        if suffix == ".icns" or (suffix is None and sys.platform == "darwin"):
            return True
        return size >= _AUTO_TILE_MIN_SIZE

    def _render(self, size: int, *, tiled: bool) -> "_PILImage":
        from PIL import Image as PILImage, ImageDraw

        bg = _resolve_color(self._background)
        fg = _resolve_color(self._foreground)

        glyph_frac = _glyph_frac(size, tiled=tiled)
        glyph_color = fg if tiled else bg

        # Render the glyph at its FINAL on-screen size. A font glyph is crispest at
        # its display size — the glyph renderer grid-fits it there and sharpens
        # small sizes. If the glyph were supersampled with the tile and the whole
        # composite downscaled, it would lose that and go soft at 16/24 px.
        glyph_box = max(1, int(size * glyph_frac))
        glyph = _ImageService._render_icon(self._icon, glyph_box, glyph_color, align=True)

        def _center(base: "_PILImage") -> "_PILImage":
            base.alpha_composite(
                glyph, ((size - glyph.width) // 2, (size - glyph.height) // 2)
            )
            return base

        if not tiled:
            # Glyph-only: the brand-colored mark on a transparent field.
            return _center(PILImage.new("RGBA", (size, size), (0, 0, 0, 0)))

        # Tile: supersample ONLY the rounded background — its curved corners need
        # antialiasing PIL won't apply at 1x — then downscale at an integer ratio
        # for clean edges, and drop the native-size glyph on top.
        scale = max(2, math.ceil(_MIN_TILE_CANVAS / size))
        canvas = size * scale
        tile = PILImage.new("RGBA", (canvas, canvas), (0, 0, 0, 0))
        ImageDraw.Draw(tile).rounded_rectangle(
            [0, 0, canvas - 1, canvas - 1],
            radius=int(canvas * self._radius),
            fill=bg,
        )
        tile = tile.resize((size, size), PILImage.Resampling.LANCZOS)
        return _center(tile)

    def to_image(self, size: int = 256, *, tiled: bool | None = None) -> "Image":
        """Render the icon to an `Image` handle for on-screen display.

        Use this to show the application icon inside the app itself — for example
        on an about screen or a splash panel.

        Args:
            size: Rendered size in pixels. Defaults to `256`.
            tiled: Force the tile shape (`True`) or glyph-only (`False`). By
                default, follows the icon's `shape`.

        Returns:
            An image handle wrapping the rendered icon.
        """
        size = int(size)
        if tiled is None:
            tiled = self._tiled_for_size(size)
        return Image.from_pil(self._render(size, tiled=tiled))

    def save(self, path: str | Path) -> str:
        """Write the icon to a file, choosing the format by file extension.

        Use this to produce a packaging asset — for example, an icon to point a
        PyInstaller build at. The format follows the path suffix:

        - `.ico` — a multi-resolution Windows icon.
        - `.icns` — a macOS icon.
        - `.png` — a single 256-pixel image.

        Args:
            path: Destination file path ending in `.ico`, `.icns`, or `.png`.

        Returns:
            The path that was written, as a string.

        Raises:
            ValueError: If the file extension is not one of the supported types.
        """
        return self._write(Path(path))

    def _write(self, p: Path) -> str:
        suffix = p.suffix.lower()
        if suffix == ".ico":
            # Each frame chooses its own shape: under `auto`, small frames are
            # glyph-only and larger frames are tiled (see `_tiled_for_size`).
            imgs = [
                self._render(s, tiled=self._tiled_for_size(s, suffix=suffix))
                for s in _APP_ICON_SIZES
            ]
            # Largest first — Pillow skips sizes larger than the base image.
            imgs[-1].save(
                p,
                format="ICO",
                bitmap_format="bmp",
                sizes=[(s, s) for s in _APP_ICON_SIZES],
                append_images=imgs[:-1],
            )
        elif suffix == ".icns":
            self._render(1024, tiled=self._tiled_for_size(1024, suffix=suffix)).save(
                p, format="ICNS"
            )
        elif suffix == ".png":
            self._render(256, tiled=self._tiled_for_size(256, suffix=suffix)).save(
                p, format="PNG"
            )
        else:
            raise ValueError(
                f"unsupported app icon format {suffix!r}; use .ico, .icns, or .png"
            )
        return str(p)

    def _icon_path(self) -> str:
        """Generate a runtime icon asset and return its file path.

        On Windows a multi-resolution `.ico` is produced; elsewhere a `.png`.
        The shape follows the icon's `shape` — under `auto`, a tile on macOS and,
        on Windows/Linux, glyph-only for the small `.ico` frames and a tile for
        the larger ones. Generated once per `AppIcon` and cached for reuse.
        """
        if self._cached_path is not None:
            return self._cached_path
        suffix = ".ico" if sys.platform == "win32" else ".png"
        fd, tmp = tempfile.mkstemp(suffix=suffix, prefix="bs-appicon-")
        os.close(fd)
        self._cached_path = self._write(Path(tmp))
        _unlink_at_exit(self._cached_path)
        return self._cached_path
