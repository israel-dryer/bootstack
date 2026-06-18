"""Internal Carousel composite — a one-at-a-time image stepper.

A canvas-backed stage that shows a single slide from an ordered collection, with
overlaid navigation chevrons, a slide indicator, an optional caption, autoplay,
and slide/fade transitions. The public `bootstack.Carousel` wrapper drives this.

The stage is its OWN canvas (built like Picture's internal, on the shared
`_image_fit` helpers) rather than an embedded Picture widget — that is what makes
the transitions possible: a slide animates two image items via `canvas.move`, and
a fade blends two composed images frame by frame. Chevrons and dots are drawn from
the Bootstrap icon font through the icon renderer.
"""

from __future__ import annotations

from tkinter import Canvas, TclError
from typing import Any, Literal

from PIL import Image as PILImage, ImageOps
from PIL.ImageTk import PhotoImage

from bootstack._core.images import _ImageService
from bootstack.data import MemoryDataSource, DataSourceProtocol
from bootstack.scheduling import Schedule
from bootstack.style.style import get_style
from bootstack.widgets._impl.composites._image_fit import (
    FitMode, fit_image, resolve_pil, rounded_mask,
)
from bootstack.widgets._impl.primitives.frame import Frame
from bootstack.widgets.types import Master

Transition = Literal["slide", "fade", "none"]
Indicator = Literal["dots", "count", "none"]

_NAV_SIZE = 34            # chevron glyph size
_NAV_MARGIN = 14         # inset of a chevron from the stage edge
_DOT_SIZE = 13
_DOT_GAP = 6
_DOTS_MAX = 8            # above this, 'dots' auto-switches to a 'count' label
_CAPTION_INSET = 14      # caption baseline inset from the bottom
_FRAME_MS = 16


def _hex_rgb(color: str) -> tuple[int, int, int]:
    """Parse a `#rgb`/`#rrggbb` color to an (r, g, b) tuple."""
    c = color.lstrip("#")
    if len(c) == 3:
        c = "".join(ch * 2 for ch in c)
    try:
        return int(c[0:2], 16), int(c[2:4], 16), int(c[4:6], 16)
    except (ValueError, IndexError):
        return (255, 255, 255)


class Carousel(Frame):
    """Canvas-backed single-slide stepper with transitions and nav chrome."""

    def __init__(
        self,
        master: Master = None,
        *,
        items: list | None = None,
        datasource: DataSourceProtocol | None = None,
        image_field: str = "image",
        caption_field: str | None = None,
        index: int = 0,
        fit: FitMode = "contain",
        transition: Transition = "slide",
        show_arrows: bool = True,
        indicator: Indicator = "dots",
        autoplay: bool = False,
        interval: int = 4000,
        loop: bool = True,
        corner_radius: int = 0,
        aspect_ratio: float = 1.5,
        height: int | None = None,
        accent: str | None = None,
        **kwargs: Any,
    ) -> None:
        super().__init__(master, **kwargs)

        self._image_field = image_field
        self._caption_field = caption_field
        self._fit: FitMode = fit
        self._transition: Transition = transition
        self._show_arrows = show_arrows
        self._indicator: Indicator = indicator
        self._loop = loop
        self._radius = corner_radius
        # None -> neutral white dots (the carousel default); a token brands the
        # active dot with that accent color.
        self._accent = accent
        self._interval = max(250, int(interval))

        if datasource is not None:
            self._datasource = datasource
        elif items:
            self._datasource = MemoryDataSource(page_size=10_000).load(items)
        else:
            self._datasource = MemoryDataSource(page_size=10_000).load([])

        n = self._count()
        self._index = max(0, min(index, n - 1)) if n else 0
        self._box = (0, 0)
        self._cur_pil: PILImage.Image | None = None
        self._photo: PhotoImage | None = None
        self._img_id: int | None = None
        self._frame_id: int | None = None        # rounded corner-mask overlay
        self._frame_photo: PhotoImage | None = None
        self._frame_key: tuple | None = None
        self._transitioning = False
        self._schedule = Schedule(self)

        self._autoplay = bool(autoplay)
        self._autoplay_job = None
        self._first_render = True

        # Strong refs to overlay PhotoImages (Tk GC) — keyed so they survive redraws.
        self._nav_photos: dict[str, PhotoImage] = {}
        self._dot_photos: dict[str, PhotoImage] = {}
        self._fade_photo: PhotoImage | None = None
        self._next_photo: PhotoImage | None = None

        surface = self._surface_color()
        # Requested-height FLOOR so the carousel never collapses in a container
        # that doesn't impose a height (a scroll view, an auto-fit window). The
        # public wrapper freezes this frame with `pack_propagate(False)`, so its
        # own configured `height` is its requested height; `fill`/`expand` still
        # grow it past this floor when the parent has room.
        floor_h = height if height else round(400 / max(0.1, aspect_ratio))
        self.configure(height=floor_h)
        self._stage = Canvas(self, highlightthickness=0, bd=0, background=surface)
        self._stage.pack(fill="both", expand=True)
        self._stage.bind("<Configure>", self._on_configure, add="+")
        self._stage.bind("<Button-1>", self._on_stage_click, add="+")
        self._stage.bind("<Left>", lambda e: self.previous())
        self._stage.bind("<Right>", lambda e: self.next())
        self._enable_theme_repaint(self._on_theme)

        # Auto-refresh when the data source changes externally (parity with the
        # other record-native widgets); the subscription is released on destroy.
        self._change_sub = None
        on_change = getattr(self._datasource, "on_change", None)
        if callable(on_change):
            try:
                self._change_sub = on_change(self._on_source_change)
            except Exception:
                self._change_sub = None
        self.bind("<Destroy>", self._on_destroy, add="+")

    # ----- theme / data ------------------------------------------------------

    def _on_source_change(self, _event: Any = None) -> None:
        try:
            self.reload()
        except Exception:
            pass

    def _on_destroy(self, event: Any = None) -> None:
        if event is not None and getattr(event, "widget", None) is not self:
            return
        sub, self._change_sub = self._change_sub, None
        if sub is not None:
            try:
                sub.cancel()
            except Exception:
                pass

    def reload(self) -> None:
        """Reload from the data source and refresh the current slide."""
        n = self._count()
        self._index = max(0, min(self._index, n - 1)) if n else 0
        if self._box[0] > 1 and self._box[1] > 1:
            self._set_current(self._compose(self._pil_at(self._index), *self._box))
            self._ensure_frame(*self._box)
            self._draw_overlays(*self._box)

    def _surface_color(self) -> str:
        token = getattr(self, "_surface", None) or "background"
        b = get_style().style_builder
        try:
            return b.color(token)
        except Exception:
            return b.color("background")

    def _on_theme(self, _event=None) -> None:
        try:
            self._stage.configure(background=self._surface_color())
        except TclError:
            return
        self._nav_photos.clear()
        self._dot_photos.clear()
        self._frame_key = None   # surface color changed — rebuild the corner mask
        if self._box[0] > 1:
            self._ensure_frame(*self._box)
            self._draw_overlays(*self._box)

    def _count(self) -> int:
        try:
            return int(self._datasource.count)
        except Exception:
            return 0

    def _raw_at(self, i: int) -> dict | None:
        try:
            rows = self._datasource.page_slice(i, 1)
        except Exception:
            return None
        return rows[0] if rows else None

    def _public_at(self, i: int) -> dict | None:
        raw = self._raw_at(i)
        if raw is None:
            return None
        pub = getattr(self._datasource, "_public_record", None)
        return pub(raw) if callable(pub) else dict(raw)

    def _pil_at(self, i: int) -> "PILImage.Image | None":
        raw = self._raw_at(i)
        return resolve_pil(raw.get(self._image_field)) if raw else None

    def _caption_at(self, i: int) -> str:
        raw = self._raw_at(i)
        if raw is None or not self._caption_field:
            return ""
        return str(raw.get(self._caption_field, ""))

    # ----- compositing -------------------------------------------------------

    def _compose(self, pil: "PILImage.Image | None", w: int, h: int) -> PILImage.Image:
        """Fit `pil` into a full `w`x`h` RGBA frame (centered; transparent margin).

        Corners are NOT rounded here — `corner_radius` rounds the whole stage via
        a fixed corner-mask overlay, so transitions slide under a steady frame.
        """
        base = PILImage.new("RGBA", (w, h), (0, 0, 0, 0))
        if pil is None:
            return base
        fitted = fit_image(pil.convert("RGBA"), w, h, self._fit)
        base.alpha_composite(fitted, ((w - fitted.width) // 2, (h - fitted.height) // 2))
        return base

    def _set_current(self, pil_box: PILImage.Image) -> None:
        self._cur_pil = pil_box
        self._photo = PhotoImage(pil_box)
        if self._img_id is None:
            self._img_id = self._stage.create_image(0, 0, anchor="nw", image=self._photo)
        else:
            self._stage.itemconfigure(self._img_id, image=self._photo)
            self._stage.coords(self._img_id, 0, 0)
        self._stage.tag_lower(self._img_id)

    def _ensure_frame(self, w: int, h: int) -> None:
        """Create/update the rounded corner-mask that rounds the whole stage.

        The mask paints the four corner nooks in the surface color (antialiased),
        so the viewport reads as a rounded card while slides move underneath it.
        """
        if self._radius <= 0:
            if self._frame_id is not None:
                self._stage.delete(self._frame_id)
                self._frame_id = None
            return
        key = (w, h, self._radius, self._surface_color())
        if self._frame_key != key or self._frame_photo is None:
            rgb = _hex_rgb(self._surface_color())
            cover = PILImage.new("RGBA", (w, h), rgb + (255,))
            inside = rounded_mask(w, h, self._radius)      # 255 inside (AA edge)
            cover.putalpha(ImageOps.invert(inside))        # opaque only in the corners
            self._frame_photo = PhotoImage(cover)
            self._frame_key = key
        if self._frame_id is None:
            self._frame_id = self._stage.create_image(
                0, 0, anchor="nw", image=self._frame_photo, tags="frame"
            )
        else:
            self._stage.itemconfigure(self._frame_id, image=self._frame_photo)
            self._stage.coords(self._frame_id, 0, 0)
        self._stage.tag_raise(self._frame_id)

    # ----- layout / render ---------------------------------------------------

    def _on_configure(self, event) -> None:
        box = (int(event.width), int(event.height))
        if box == self._box:
            return
        self._box = box
        if box[0] <= 1 or box[1] <= 1:
            return
        # Don't fight an in-flight transition; it recomposes at the settled box.
        if self._transitioning:
            return
        self._set_current(self._compose(self._pil_at(self._index), *box))
        self._ensure_frame(*box)
        self._draw_overlays(*box)
        if self._first_render:
            self._first_render = False
            if self._autoplay:
                self._arm_autoplay()

    # ----- navigation --------------------------------------------------------

    def show(self, index: int, *, direction: int = 0) -> None:
        n = self._count()
        if n == 0 or self._transitioning:
            return
        index = index % n if self._loop else max(0, min(index, n - 1))
        if index == self._index and self._img_id is not None:
            return
        w, h = self._box
        if w <= 1 or h <= 1:
            # Not laid out yet — record the index and announce the change; the
            # first <Configure> will render it.
            self._index = index
            record = self._public_at(index)
            if record is not None:
                self.event_generate("<<Change>>", data=record)
            return
        next_pil = self._compose(self._pil_at(index), w, h)
        self._index = index

        if self._transition == "none" or self._img_id is None or direction == 0:
            self._set_current(next_pil)
            self._after_change()
        elif self._transition == "fade":
            self._fade_to(next_pil)
        else:
            self._slide_to(next_pil, direction)

    def next(self) -> None:
        self.show(self._index + 1, direction=1)

    def previous(self) -> None:
        self.show(self._index - 1, direction=-1)

    def go_to(self, index: int) -> None:
        direction = (index > self._index) - (index < self._index)
        self.show(index, direction=direction)

    def _slide_to(self, next_pil: PILImage.Image, d: int) -> None:
        w, h = self._box
        self._transitioning = True
        self._next_photo = PhotoImage(next_pil)
        next_id = self._stage.create_image(d * w, 0, anchor="nw", image=self._next_photo)
        cur_id = self._img_id
        self._stage.tag_lower(next_id)
        if cur_id is not None:
            self._stage.tag_lower(cur_id)
        steps = 12
        dx = -d * w / steps

        def step(i: int) -> None:
            if i >= steps:
                if cur_id is not None:
                    self._stage.delete(cur_id)
                self._stage.coords(next_id, 0, 0)
                self._img_id = next_id
                self._photo = self._next_photo
                self._cur_pil = next_pil
                self._stage.tag_lower(self._img_id)
                self._transitioning = False
                self._after_change()
                return
            self._stage.move(next_id, dx, 0)
            if cur_id is not None:
                self._stage.move(cur_id, dx, 0)
            self._schedule.delay(_FRAME_MS, lambda: step(i + 1))

        step(1)

    def _fade_to(self, next_pil: PILImage.Image) -> None:
        cur = self._cur_pil
        if cur is None:
            self._set_current(next_pil)
            self._after_change()
            return
        self._transitioning = True
        steps = 10

        def step(i: int) -> None:
            if i > steps:
                self._set_current(next_pil)
                self._transitioning = False
                self._after_change()
                return
            blended = PILImage.blend(cur, next_pil, i / steps)
            self._fade_photo = PhotoImage(blended)
            self._stage.itemconfigure(self._img_id, image=self._fade_photo)
            self._schedule.delay(_FRAME_MS + 6, lambda: step(i + 1))

        step(1)

    def _after_change(self) -> None:
        bw, bh = self._box
        if bw > 1 and bh > 1:
            # A resize deferred during the transition leaves the settled image at
            # the old size — recompose if it no longer matches the live box.
            if self._cur_pil is None or self._cur_pil.size != (bw, bh):
                self._set_current(self._compose(self._pil_at(self._index), bw, bh))
            self._ensure_frame(bw, bh)
            self._draw_overlays(bw, bh)
        record = self._public_at(self._index)
        if record is not None:
            self.event_generate("<<Change>>", data=record)
        if self._autoplay:
            self._arm_autoplay()

    # ----- overlays (chevrons, indicator, caption) ---------------------------

    def _draw_overlays(self, w: int, h: int) -> None:
        self._stage.delete("ov")
        n = self._count()
        self._draw_caption(w, h)
        self._draw_indicator(w, h, n)
        if self._show_arrows and n > 1:
            self._draw_chevrons(w, h)

    def _nav_photo(self, glyph: str) -> PhotoImage:
        if glyph not in self._nav_photos:
            pad = 3
            canvas = _NAV_SIZE + pad * 2
            base = PILImage.new("RGBA", (canvas, canvas), (0, 0, 0, 0))
            shadow = _ImageService._render_icon(glyph, _NAV_SIZE, "#000000")
            white = _ImageService._render_icon(glyph, _NAV_SIZE, "#ffffff")
            base.alpha_composite(shadow, (pad, pad + 1))   # soft 1px drop shadow
            base.alpha_composite(white, (pad, pad))
            self._nav_photos[glyph] = PhotoImage(base)
        return self._nav_photos[glyph]

    def _draw_chevrons(self, w: int, h: int) -> None:
        left = self._nav_photo("chevron-left")
        right = self._nav_photo("chevron-right")
        cy = h // 2
        # Tag the chevrons "nav" so the stage's Button-1 handler knows the click
        # was navigation and skips emitting ItemClick (a "break" from an item-tag
        # binding does NOT stop the canvas-wide binding — separate mechanisms).
        lid = self._stage.create_image(_NAV_MARGIN, cy, anchor="w", image=left, tags=("ov", "nav"))
        rid = self._stage.create_image(w - _NAV_MARGIN, cy, anchor="e", image=right, tags=("ov", "nav"))
        self._stage.tag_bind(lid, "<Button-1>", lambda e: self.previous())
        self._stage.tag_bind(rid, "<Button-1>", lambda e: self.next())

    def _dot_photo(self, key: str, color: str, glyph: str) -> PhotoImage:
        if key not in self._dot_photos:
            self._dot_photos[key] = _ImageService.get_icon(glyph, _DOT_SIZE, color)
        return self._dot_photos[key]

    def _effective_indicator(self, n: int) -> Indicator:
        if self._indicator == "dots" and n > _DOTS_MAX:
            return "count"
        return self._indicator

    def _draw_indicator(self, w: int, h: int, n: int) -> None:
        mode = self._effective_indicator(n)
        if mode == "none" or n <= 1:
            return
        y = h - _CAPTION_INSET
        if mode == "count":
            label = f"{self._index + 1} / {n}"
            self._stage.create_text(w // 2 + 1, y + 1, text=label, anchor="s",
                                    fill="#000000", font=("", 10, "bold"), tags="ov")
            self._stage.create_text(w // 2, y, text=label, anchor="s",
                                    fill="#ffffff", font=("", 10, "bold"), tags="ov")
            return
        # Neutral by default — solid white active, translucent white inactive;
        # an explicit accent brands the active dot.
        active_color = get_style().style_builder.color(self._accent) if self._accent else "#ffffff"
        active = self._dot_photo(f"active:{active_color}", active_color, "circle-fill")
        inactive = self._dot_photo("inactive", "#ffffff66", "circle-fill")
        total = n * _DOT_SIZE + (n - 1) * _DOT_GAP
        x = w // 2 - total // 2 + _DOT_SIZE // 2
        for i in range(n):
            photo = active if i == self._index else inactive
            did = self._stage.create_image(x, y - _DOT_SIZE // 2, image=photo, tags=("ov", "nav"))
            self._stage.tag_bind(did, "<Button-1>", lambda e, idx=i: self.go_to(idx))
            x += _DOT_SIZE + _DOT_GAP

    def _draw_caption(self, w: int, h: int) -> None:
        text = self._caption_at(self._index)
        if not text:
            return
        n = self._count()
        bump = _DOT_SIZE + 8 if self._effective_indicator(n) != "none" and n > 1 else 0
        y = h - _CAPTION_INSET - bump
        self._stage.create_text(w // 2 + 1, y + 1, text=text, anchor="s",
                                fill="#000000", font=("", 11, "bold"), tags="ov")
        self._stage.create_text(w // 2, y, text=text, anchor="s",
                                fill="#ffffff", font=("", 11, "bold"), tags="ov")

    # ----- autoplay ----------------------------------------------------------

    @property
    def is_playing(self) -> bool:
        return self._autoplay

    def play(self) -> None:
        if self._count() <= 1:
            return
        self._autoplay = True
        self._arm_autoplay()

    def pause(self) -> None:
        self._autoplay = False
        self._cancel_autoplay()

    def stop(self) -> None:
        """Stop autoplay and return to the first slide."""
        self.pause()
        self.go_to(0)

    def _arm_autoplay(self) -> None:
        self._cancel_autoplay()
        if self._autoplay:
            self._autoplay_job = self._schedule.delay(self._interval, self._autoplay_tick)

    def _cancel_autoplay(self) -> None:
        if self._autoplay_job is not None:
            self._autoplay_job.cancel()
            self._autoplay_job = None

    def _autoplay_tick(self) -> None:
        self._autoplay_job = None
        if self._transitioning:
            # A tick landed mid-transition; next() would no-op and autoplay would
            # die (no _after_change to re-arm). Retry shortly instead.
            if self._autoplay:
                self._autoplay_job = self._schedule.delay(_FRAME_MS * 8, self._autoplay_tick)
            return
        self.next()   # _after_change re-arms

    # ----- events / accessors ------------------------------------------------

    def _on_stage_click(self, event) -> None:
        self._stage.focus_set()
        # Skip when the click landed on a chevron or dot — that was navigation,
        # not a click on the slide. The canvas-wide binding fires in addition to
        # the item bindings (a "break" from an item binding won't stop it), so
        # check the topmost item at the click point for the "nav" tag.
        hit = self._stage.find_overlapping(event.x, event.y, event.x, event.y)
        if hit and "nav" in self._stage.gettags(hit[-1]):
            return
        record = self._public_at(self._index)
        if record is not None:
            self.event_generate("<<ItemClick>>", data=record)

    @property
    def index(self) -> int:
        return self._index

    @property
    def current(self) -> dict | None:
        return self._public_at(self._index)

    @property
    def count(self) -> int:
        return self._count()

    def get_datasource(self) -> DataSourceProtocol:
        return self._datasource
