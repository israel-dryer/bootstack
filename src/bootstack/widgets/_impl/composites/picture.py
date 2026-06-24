"""Internal Picture composite — a canvas-backed image display.

Renders a single image (or an animated sequence) into a themed canvas, fitting
it to the canvas's allocated size with a CSS `object-fit`-style policy. The
public `bootstack.Picture` wrapper drives this; nothing here is public.

The canvas (not a Label) is the backing widget on purpose: it does not
shrink-wrap to the image, it reports its allocated pixel size through
`<Configure>`, and it letterboxes cleanly behind a fitted image.
"""

from __future__ import annotations

from tkinter import Canvas, TclError
from typing import Any

from PIL import Image as PILImage, ImageSequence
from PIL.ImageTk import PhotoImage

from bootstack.events import ImageErrorEvent, ImageLoadEvent
from bootstack.style.style import get_style
from bootstack.widgets._impl.composites._image_fit import (
    FitMode, fit_image, round_corners, rounded_mask,
)
from bootstack.widgets._impl.primitives.frame import Frame
from bootstack.widgets.types import Master

# Map an anchor token to a (relative-x, relative-y) position in the box and the
# matching Tk canvas image anchor. Used to place an image that does not fill the
# box (contain / scale-down / none).
_ANCHOR_POS: dict[str, tuple[float, float]] = {
    "center": (0.5, 0.5),
    "n": (0.5, 0.0), "s": (0.5, 1.0), "e": (1.0, 0.5), "w": (0.0, 0.5),
    "nw": (0.0, 0.0), "ne": (1.0, 0.0), "sw": (0.0, 1.0), "se": (1.0, 1.0),
}


class Picture(Frame):
    """Canvas-backed image display with fit modes, resize, and GIF playback."""

    def __init__(
        self,
        master: Master = None,
        *,
        source: Any = None,
        fit: FitMode = "contain",
        anchor: str = "center",
        corner_radius: int = 0,
        autoplay: bool = True,
        loop: bool = True,
        img_width: int | None = None,
        img_height: int | None = None,
        **kwargs: Any,
    ) -> None:
        super().__init__(master, **kwargs)

        self._fit: FitMode = fit
        self._anchor = anchor if anchor in _ANCHOR_POS else "center"
        self._corner_radius = max(0, int(corner_radius))
        self._autoplay = autoplay
        self._loop = loop
        self._fixed_w = img_width
        self._fixed_h = img_height

        from bootstack.scheduling import Schedule

        self._source: Any = None              # public Image handle, or None
        self._frames: list[tuple[PILImage.Image, int]] = []  # (RGBA frame, ms)
        self._frame_index = 0
        self._schedule = Schedule(self)        # cancels itself on destroy
        self._anim_job = None
        self._photo: PhotoImage | None = None  # strong ref — Tk GC guard
        self._img_id: int | None = None
        self._box: tuple[int, int] = (0, 0)
        self._mask_key: tuple[int, int, int] | None = None  # single-entry cache
        self._mask: PILImage.Image | None = None

        self._surface_color = self._resolve_surface()
        self._canvas = Canvas(
            self,
            highlightthickness=0,
            bd=0,
            background=self._surface_color,
            width=self._fixed_w or 1,
            height=self._fixed_h or 1,
        )
        self._canvas.pack(fill="both", expand=True)
        self._canvas.bind("<Configure>", self._on_configure)
        self._canvas.bind("<Button-1>", self._forward_click)

        # Defer the initial load to idle so the constructor returns first: the
        # caller can bind on_load/on_error before the <<PictureLoad>> fires.
        if source is not None:
            self._schedule.idle(lambda: self.set_source(source))

    # ----- theme / surface ---------------------------------------------------

    def _resolve_surface(self) -> str:
        """Resolve the canvas letterbox color from the frame's surface token."""
        token = getattr(self, "_surface", None) or "background"
        builder = get_style().style_builder
        try:
            return builder.color(token)
        except Exception:
            return builder.color("background")

    def _bs_apply_theme(self, _event=None) -> None:
        self._surface_color = self._resolve_surface()
        try:
            self._canvas.configure(background=self._surface_color)
        except TclError:
            return
        # A theme-following icon source must re-render in the new theme color.
        src = self._source
        if src is not None and getattr(src, "_is_theme_following", False):
            self.set_source(src)

    # ----- source ------------------------------------------------------------

    def set_source(self, source: Any) -> None:
        """Replace the displayed image and (re)start playback if animated.

        Args:
            source: A public `bootstack.images.Image` handle, or None to clear.
        """
        self._stop_animation()
        self._source = source
        if source is None:
            self._frames = []
            self._clear_canvas()
            return
        try:
            self._frames = self._load_frames(source)
        except Exception as exc:  # decode/seek/format failures
            self._frames = []
            self._clear_canvas()
            self.event_generate(
                "<<PictureError>>", data=ImageErrorEvent(message=str(exc))
            )
            return

        self._frame_index = 0
        self._render_current()

        first = self._frames[0][0]
        self.event_generate(
            "<<PictureLoad>>",
            data=ImageLoadEvent(
                width=first.width, height=first.height, frames=len(self._frames)
            ),
        )
        if self._autoplay and len(self._frames) > 1:
            self.play()

    def _load_frames(self, image: Any) -> list[tuple[PILImage.Image, int]]:
        """Decode `image` into a list of (RGBA frame, duration-ms) tuples."""
        # A deferred icon handle has no raster source to open; render its glyph.
        icon = getattr(image, "_icon", None)
        if icon is not None:
            from bootstack._core.images import _ImageService

            color = image._resolve_icon_color()
            rgba = _ImageService._render_icon(icon.name, icon.size, color)
            return [(rgba.convert("RGBA"), 0)]

        pil = image._load_pil()
        frames: list[tuple[PILImage.Image, int]] = []
        for frame in ImageSequence.Iterator(pil):
            rgba = frame.convert("RGBA").copy()
            duration = int(frame.info.get("duration", 0) or 0)
            frames.append((rgba, duration))
        if not frames:
            raise ValueError("image has no frames")
        return frames

    # ----- fit / render ------------------------------------------------------

    def set_fit(self, fit: FitMode) -> None:
        """Change the fit policy and re-render."""
        self._fit = fit
        self._render_current()

    def _on_configure(self, event) -> None:
        box = (int(event.width), int(event.height))
        if box == self._box:
            return
        self._box = box
        self._render_current()

    def _render_current(self) -> None:
        """Compose the current frame to the live box and draw it."""
        if not self._frames:
            return
        bw, bh = self._box
        if self._fixed_w:
            bw = self._fixed_w
        if self._fixed_h:
            bh = self._fixed_h
        if bw <= 1 or bh <= 1:
            return  # not laid out yet; the <Configure> pass will render

        frame = self._frames[self._frame_index][0]
        composed = self._compose(frame, bw, bh)
        self._photo = PhotoImage(image=composed)

        rx, ry = _ANCHOR_POS[self._anchor]
        x = int(bw * rx)
        y = int(bh * ry)
        if self._img_id is None:
            self._img_id = self._canvas.create_image(
                x, y, image=self._photo, anchor=self._anchor
            )
        else:
            self._canvas.coords(self._img_id, x, y)
            self._canvas.itemconfigure(self._img_id, image=self._photo, anchor=self._anchor)

    def _compose(self, frame: PILImage.Image, bw: int, bh: int) -> PILImage.Image:
        """Scale/crop `frame` to the box per the fit policy; round the corners."""
        result = fit_image(frame, bw, bh, self._fit)
        if self._corner_radius > 0:
            result = round_corners(result, self._corner_radius, self._corner_mask(*result.size))
        return result

    def _corner_mask(self, w: int, h: int) -> PILImage.Image:
        """A cached rounded-rect mask for a `w`x`h` result (reused across frames)."""
        key = (w, h, self._corner_radius)
        if self._mask_key != key or self._mask is None:
            self._mask = rounded_mask(w, h, self._corner_radius)
            self._mask_key = key
        return self._mask

    def _clear_canvas(self) -> None:
        if self._img_id is not None:
            try:
                self._canvas.delete(self._img_id)
            except TclError:
                pass
            self._img_id = None
        self._photo = None

    # ----- animation ---------------------------------------------------------

    @property
    def is_playing(self) -> bool:
        return self._anim_job is not None

    def play(self) -> None:
        """Start (or resume) playback of an animated source."""
        if len(self._frames) <= 1 or self._anim_job is not None:
            return
        self._schedule_next()

    def pause(self) -> None:
        """Pause playback on the current frame."""
        self._stop_animation()

    def stop(self) -> None:
        """Stop playback and reset to the first frame."""
        self._stop_animation()
        if self._frames:
            self._frame_index = 0
            self._render_current()

    def _schedule_next(self) -> None:
        duration = self._frames[self._frame_index][1] or 100
        self._anim_job = self._schedule.delay(duration, self._advance_frame)

    def _advance_frame(self) -> None:
        self._anim_job = None
        nxt = self._frame_index + 1
        if nxt >= len(self._frames):
            if not self._loop:
                return
            nxt = 0
        self._frame_index = nxt
        self._render_current()
        self._schedule_next()

    def _stop_animation(self) -> None:
        if self._anim_job is not None:
            self._anim_job.cancel()
            self._anim_job = None

    # ----- events ------------------------------------------------------------

    def _forward_click(self, event) -> None:
        # The canvas covers the frame, so clicks land on it, not the frame the
        # public wrapper binds. Re-emit on the frame so on_click works.
        self.event_generate("<<PictureClick>>", x=event.x, y=event.y)
