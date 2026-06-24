"""Internal Gallery composite — a recycling thumbnail grid.

A scrollable, selectable grid of image tiles. Record-native: it reads from a
`DataSourceProtocol` and reuses the selection model the list/table/tree widgets
share. The public `bootstack.Gallery` wrapper drives this.

Recycle model: a FIXED pool of tiles sits in stable grid slots; scrolling slides
the data window over the pool and each tile re-renders only when the record in
its slot actually changes. Modeled as a vertical scroll of rows, each row a strip
of `columns` tiles — the 1D list recycle generalized one axis, not a 2D recycler.
"""

from __future__ import annotations

import contextlib
from tkinter import Canvas, TclError
from typing import Any, Literal

from PIL import Image as PILImage, ImageDraw
from PIL.Image import Resampling
from PIL.ImageTk import PhotoImage

from bootstack.data import MemoryDataSource, DataSourceProtocol
from bootstack.style.style import get_style
from bootstack.widgets._impl.composites._image_fit import (
    FitMode, fit_image, resolve_pil, round_corners,
)
from bootstack.widgets._impl.primitives.frame import Frame
from bootstack.widgets._impl.primitives.label import Label
from bootstack.widgets._impl.primitives.scrollbar import Scrollbar
from bootstack.widgets.types import Master, ScrollbarVariant

OVERSCAN_ROWS = 1
_RING_THICKNESS = 3
_RING_GAP = 3                       # separation between the image and the ring
_RING_PAD = _RING_GAP + _RING_THICKNESS   # margin reserved around the image
_CAPTION_H = 24            # vertical space reserved per caption row in the height floor
EMPTY = {"__empty__": True, "id": "__empty__"}


class GalleryTile(Frame):
    """One thumbnail cell — a canvas (image + selection ring) and a caption."""

    def __init__(self, master, *, tile_w, tile_h, fit, corner_radius, caption,
                 on_click=None, on_activate=None, **kwargs):
        super().__init__(master, **kwargs)
        self._tw = tile_w
        self._th = tile_h
        self._fit: FitMode = fit
        self._radius = corner_radius
        self._has_caption = caption
        self._on_click_cb = on_click
        self._on_activate_cb = on_activate
        self._record: dict | None = None
        self._cur_src: Any = "\x00unset"   # sentinel distinct from None
        self._cur_id: Any = "\x00unset"
        self._photo: PhotoImage | None = None
        self._ring_photo: PhotoImage | None = None

        # The canvas is larger than the image by a margin on every side, so the
        # selection ring can sit OUTSIDE the image (with a gap) without changing
        # the layout when toggled. The image is centered; the margin blends into
        # the surface when unselected.
        cw, ch = tile_w + 2 * _RING_PAD, tile_h + 2 * _RING_PAD
        self._canvas = Canvas(self, width=cw, height=ch,
                              highlightthickness=0, bd=0,
                              background=self._surface_color())
        self._canvas.pack()
        self._img_id = self._canvas.create_image(cw // 2, ch // 2, anchor="center")
        self._ring_id = self._canvas.create_image(0, 0, anchor="nw", state="hidden")

        if caption:
            self._caption = Label(self, text="", anchor="center", font="caption")
            self._caption.pack(fill="x", pady=(4, 0))
        else:
            self._caption = None

        for seq in ("<Button-1>",):
            self._canvas.bind(seq, self._on_click)
        self._canvas.bind("<Double-Button-1>", self._on_double_click)

    def _surface_color(self) -> str:
        token = getattr(self, "_surface", None) or "background"
        b = get_style().style_builder
        try:
            return b.color(token)
        except Exception:
            return b.color("background")

    def set_ring(self, ring_photo: "PhotoImage | None") -> None:
        """Share the gallery's prebuilt selection-ring image with this tile."""
        self._ring_photo = ring_photo
        if ring_photo is not None:
            self._canvas.itemconfigure(self._ring_id, image=ring_photo)

    def update_data(self, record, image_source, caption_text, selected: bool) -> None:
        """Bind `record` to this tile, re-rendering the thumbnail only if changed."""
        empty = record is None or record.get("__empty__", False)
        self._record = None if empty else record
        rid = None if empty else record.get("id")
        if rid != self._cur_id:
            self._cur_id = rid
            if self._caption is not None:
                self._caption.configure(
                    text="" if empty else self._fit_caption(str(caption_text)))
        source = None if empty else image_source
        if source is not self._cur_src and source != self._cur_src:
            self._render_thumb(source)
            self._cur_src = source
        self._canvas.itemconfigure(
            self._ring_id, state="normal" if (selected and not empty) else "hidden"
        )

    def _fit_caption(self, text: str) -> str:
        """Ellipsize `text` to the tile width so a caption never widens its tile.

        Keeps every tile a uniform width — so grid columns stay put instead of
        shifting as longer/shorter captions scroll through them.
        """
        if not text:
            return text
        avail = self._tw + 2 * _RING_PAD - 6
        cap = self._caption
        try:
            font = cap.cget("font")
            measure = lambda s: int(cap.tk.call("font", "measure", font, s))
        except Exception:
            return text
        if measure(text) <= avail:
            return text
        ell = "…"
        lo, hi = 0, len(text)
        while lo < hi:
            mid = (lo + hi + 1) // 2
            if measure(text[:mid] + ell) <= avail:
                lo = mid
            else:
                hi = mid - 1
        return text[:lo] + ell if lo > 0 else ell

    def _render_thumb(self, source: Any) -> None:
        pil = resolve_pil(source)
        if pil is None:
            self._canvas.itemconfigure(self._img_id, image="")
            self._photo = None
            return
        composed = fit_image(pil.convert("RGBA"), self._tw, self._th, self._fit)
        if self._radius > 0:
            composed = round_corners(composed, self._radius)
        # A plain PhotoImage (kept alive by self._photo, GC'd when replaced) — do
        # NOT route through the global _ImageService cache, which never evicts and
        # would accumulate one entry per distinct thumbnail as the grid scrolls.
        self._photo = PhotoImage(composed)
        self._canvas.itemconfigure(self._img_id, image=self._photo)

    def refresh_surface(self) -> None:
        """Re-resolve the canvas background after a theme change."""
        try:
            self._canvas.configure(background=self._surface_color())
        except TclError:
            pass

    def _on_click(self, _event) -> None:
        # Call the gallery directly: virtual events do NOT bubble from a child
        # widget to an ancestor's bindings, so a container binding would never fire.
        if self._record is not None and self._on_click_cb is not None:
            self._on_click_cb(self._record)

    def _on_double_click(self, _event) -> None:
        if self._record is not None and self._on_activate_cb is not None:
            self._on_activate_cb(self._record)


class Gallery(Frame):
    """Recycling thumbnail grid bound to a data source."""

    def __init__(
        self,
        master: Master = None,
        *,
        items: list | None = None,
        datasource: DataSourceProtocol | None = None,
        image_field: str = "image",
        caption_field: str | None = None,
        columns: "int | Literal['auto']" = "auto",
        tile_size: tuple[int, int] = (160, 160),
        fit: FitMode = "cover",
        corner_radius: int = 0,
        gap: int = 8,
        selection_mode: Literal["none", "single", "multi"] = "none",
        accent: str | None = None,
        scrollbar_variant: ScrollbarVariant = "thin",
        rows: int = 2,
        **kwargs: Any,
    ) -> None:
        super().__init__(master, **kwargs)
        self._scrollbar_variant = scrollbar_variant
        self._min_rows = max(1, rows)

        self._image_field = image_field
        self._caption_field = caption_field
        self._columns_opt = columns
        self._tw, self._th = tile_size
        self._fit: FitMode = fit
        self._corner_radius = corner_radius
        self._gap = gap
        self._selection_mode = selection_mode
        self._accent = accent or "primary"

        page = 200
        if datasource is not None:
            self._datasource = datasource
        elif items:
            self._datasource = MemoryDataSource(page_size=page).load(items)
        else:
            self._datasource = MemoryDataSource(page_size=page).load([])

        self._tiles: list[GalleryTile] = []
        self._cols = 1
        self._cfg_cols = 0   # highest grid column given a weight, for resetting
        self._visible_rows = 1
        self._pool_rows = 1
        self._start_row = 0
        self._ring_photo: PhotoImage | None = None
        self._row_h = self._th + 2 * _RING_PAD + (_CAPTION_H if caption_field else 0) + gap

        sb_surface = getattr(self, '_surface', None)
        sb_kw = {'surface': sb_surface} if sb_surface else {}
        self._scrollbar = Scrollbar(
            self, orient="vertical", command=self._on_scroll,
            variant=self._scrollbar_variant, **sb_kw)
        self._scrollbar.pack(side="right", fill="y")
        self._container = Frame(self)
        self._container.pack(side="left", fill="both", expand=True)

        # Requested-height FLOOR so the grid never reports ~0 height in a
        # container that doesn't impose one (a scroll view, an auto-fit window).
        # The public wrapper freezes this frame with `pack_propagate(False)`, so
        # its own configured `height` is its requested height; `fill`/`expand`
        # still grow it past this floor when the parent has room.
        self.configure(height=self._min_rows * self._row_h)

        # Bind resize on the CONTAINER and use the event's width/height directly —
        # winfo_width() read during the parent's <Configure> lags a cycle behind
        # the new size, which would wedge the column count at its initial value.
        self._container.bind("<Configure>", self._on_resize, add="+")
        self._bind_scroll(self)
        self._bind_scroll(self._container)

        self._change_sub = None
        on_change = getattr(self._datasource, "on_change", None)
        if callable(on_change):
            try:
                self._change_sub = on_change(self._on_source_change)
            except Exception:
                self._change_sub = None
        self.bind("<Destroy>", self._on_destroy, add="+")
        # Tile surfaces + the accent ring are painted imperatively, so re-resolve
        # on a theme change — gated to on-screen by the Frame base hook (an
        # off-screen gallery defers its thumbnail-grid repaint to <Map>).
        # First render is driven by the container's <Configure> (bound above);
        # no init timer needed.

    # ----- theme / silence / source change ----------------------------------

    def _bs_apply_theme(self, _event=None) -> None:
        """Re-apply theme-dependent colors after a theme switch.

        The tile surface backgrounds and the accent selection ring are resolved
        from theme tokens; rebuild them so they track the new theme.
        """
        for tile in self._tiles:
            tile.refresh_surface()
        if self._tiles:
            self._build_ring()   # new accent color, re-shared to every tile

    def _silence_source(self):
        silence = getattr(self._datasource, "_silence", None)
        return silence() if callable(silence) else contextlib.nullcontext()

    def _on_source_change(self, _event: Any = None) -> None:
        try:
            self._relayout()
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

    # ----- layout / recycle --------------------------------------------------

    def _resolve_columns(self, width: int) -> int:
        if self._columns_opt != "auto":
            return max(1, int(self._columns_opt))
        cell = self._tw + 2 * _RING_PAD
        # Each tile occupies cell + gap of width — _regrid gives every tile a
        # symmetric padx of gap//2 on both sides. So the count is
        # width // (cell + gap); the "(n-1) gaps between items" form
        # ((width + gap) // (cell + gap)) permits one column too many and clips
        # the last column off the frame's right edge.
        return max(1, width // (cell + self._gap))

    def _on_resize(self, event) -> None:
        self._relayout(event.width, event.height)

    def _relayout(self, width: int | None = None, height: int | None = None) -> None:
        """Recompute the column count and tile pool, then refill.

        `width`/`height` come straight from a `<Configure>` event when available
        (authoritative); otherwise the container is measured (the initial tick).
        """
        if width is None or height is None:
            try:
                width = self._container.winfo_width()
                height = self._container.winfo_height()
            except TclError:
                return
        if width <= 1 or height <= 1:
            return

        cols = self._resolve_columns(width)
        visible_rows = max(1, height // self._row_h + 1)
        pool_rows = visible_rows + OVERSCAN_ROWS
        needed = cols * pool_rows

        rebuild_geometry = cols != self._cols
        self._cols = cols
        self._visible_rows = visible_rows
        self._pool_rows = pool_rows

        if self._ring_photo is None or rebuild_geometry:
            self._build_ring()

        self._ensure_pool(needed)
        self._regrid()
        self._update_tiles()

    def _build_ring(self) -> None:
        """Build the shared antialiased accent selection-ring overlay image.

        Sized to the full padded canvas; the ring stroke runs near the canvas
        edge so it sits a `_RING_GAP` outside the centered image, with corners
        concentric to the image's rounded corners.
        """
        w, h = self._tw + 2 * _RING_PAD, self._th + 2 * _RING_PAD
        color = get_style().style_builder.color(self._accent)
        ss = 4
        big = PILImage.new("RGBA", (w * ss, h * ss), (0, 0, 0, 0))
        t = _RING_THICKNESS * ss
        inset = t // 2
        radius = self._corner_radius + _RING_GAP + _RING_THICKNESS // 2
        ImageDraw.Draw(big).rounded_rectangle(
            [inset, inset, w * ss - 1 - inset, h * ss - 1 - inset],
            radius=max(0, radius) * ss, outline=color, width=t,
        )
        self._ring_photo = PhotoImage(image=big.resize((w, h), Resampling.LANCZOS))
        for tile in self._tiles:
            tile.set_ring(self._ring_photo)

    def _ensure_pool(self, needed: int) -> None:
        while len(self._tiles) < needed:
            tile = GalleryTile(
                self._container, tile_w=self._tw, tile_h=self._th, fit=self._fit,
                corner_radius=self._corner_radius, caption=bool(self._caption_field),
                on_click=self._handle_tile_click, on_activate=self._handle_tile_activate,
            )
            tile.set_ring(self._ring_photo)
            self._bind_scroll(tile)
            self._bind_scroll(tile._canvas)
            if tile._caption is not None:
                self._bind_scroll(tile._caption)
            self._tiles.append(tile)
        while len(self._tiles) > needed:
            tile = self._tiles.pop()
            try:
                tile.destroy()
            except TclError:
                pass

    def _regrid(self) -> None:
        pad = self._gap // 2
        # Weight the active columns equally so the fixed-width tiles spread to
        # fill the row instead of left-packing with a ragged right margin (which
        # reads as a wasted extra column). Tiles are gridded without sticky, so
        # each stays its cell width and centers in its column. Stale columns from
        # a wider previous layout are zeroed.
        for c in range(self._cfg_cols):
            self._container.grid_columnconfigure(c, weight=0, uniform="")
        for c in range(self._cols):
            self._container.grid_columnconfigure(c, weight=1, uniform="gallerycol")
        self._cfg_cols = self._cols
        for i, tile in enumerate(self._tiles):
            tile.grid(row=i // self._cols, column=i % self._cols, padx=pad, pady=pad)

    def _total_rows(self) -> int:
        count = self._datasource.count
        return (count + self._cols - 1) // self._cols if count else 0

    def _clamp(self) -> None:
        max_start = max(0, self._total_rows() - self._visible_rows)
        self._start_row = max(0, min(self._start_row, max_start))

    def _update_tiles(self) -> None:
        self._clamp()
        start_index = self._start_row * self._cols
        window = self._datasource.page_slice(start_index, len(self._tiles))
        for i, tile in enumerate(self._tiles):
            if i < len(window):
                raw = window[i]
                pub = self._public(raw)
                rid = pub.get("id")
                image = raw.get(self._image_field)
                caption = raw.get(self._caption_field, "") if self._caption_field else ""
                selected = False
                if rid is not None:
                    try:
                        selected = bool(self._datasource.is_selected(rid))
                    except Exception:
                        selected = False
                tile.update_data(pub, image, caption, selected)
            else:
                tile.update_data(None, None, "", False)
        self._update_scrollbar()

    def _update_scrollbar(self) -> None:
        total = max(1, self._total_rows())
        first = self._start_row / total
        last = min(1.0, (self._start_row + self._visible_rows) / total)
        self._scrollbar.set(first, last)

    # ----- scrolling ---------------------------------------------------------

    def _on_scroll(self, *args) -> None:
        if args[0] == "moveto":
            fraction = float(args[1])
            max_start = max(0, self._total_rows() - self._visible_rows)
            self._start_row = int(round(fraction * max_start))
        elif args[0] == "scroll":
            amount, unit = int(args[1]), args[2]
            step = max(1, self._visible_rows - 1) if unit == "pages" else 1
            self._start_row += amount * step
        self._clamp()
        self._update_tiles()

    def _bind_scroll(self, widget) -> None:
        widget.bind("<MouseWheel>", self._on_wheel, add="+")
        widget.bind("<Button-4>", self._on_wheel, add="+")
        widget.bind("<Button-5>", self._on_wheel, add="+")

    def _on_wheel(self, event) -> None:
        if getattr(event, "num", None) == 4:
            delta = 1
        elif getattr(event, "num", None) == 5:
            delta = -1
        else:
            delta = 1 if event.delta < 0 else -1
        self._start_row += delta
        self._clamp()
        self._update_tiles()
        return "break"

    def scroll_to_top(self) -> None:
        self._start_row = 0
        self._update_tiles()

    def scroll_to_bottom(self) -> None:
        self._start_row = self._total_rows()
        self._clamp()
        self._update_tiles()

    # ----- selection ---------------------------------------------------------

    def get_selected(self) -> list[dict]:
        try:
            rows = self._datasource.selected()
        except Exception:
            rows = []
        return [self._public(r) for r in rows]

    def _public(self, raw: dict) -> dict:
        pub = getattr(self._datasource, "_public_record", None)
        return pub(raw) if callable(pub) else dict(raw)

    def select_items(self, record_ids: list) -> None:
        with self._silence_source():
            if self._selection_mode == "single":
                self._datasource.deselect_all()
                if record_ids:
                    self._datasource.select(record_ids[-1])
            else:
                for rid in record_ids:
                    self._datasource.select(rid)
        self._after_selection_change()

    def deselect_items(self, record_ids: list) -> None:
        with self._silence_source():
            for rid in record_ids:
                self._datasource.deselect(rid)
        self._after_selection_change()

    def select_all(self) -> None:
        if self._selection_mode != "multi":
            return
        with self._silence_source():
            self._datasource.select_all()
        self._after_selection_change()

    def clear_selection(self) -> None:
        with self._silence_source():
            self._datasource.deselect_all()
        self._after_selection_change()

    def _after_selection_change(self) -> None:
        self._update_tiles()
        self.event_generate("<<SelectionChange>>")

    # ----- tile events -------------------------------------------------------

    def _handle_tile_click(self, record: dict) -> None:
        rid = record.get("id")
        if self._selection_mode != "none" and rid is not None:
            with self._silence_source():
                if self._selection_mode == "single":
                    self._datasource.deselect_all()
                    self._datasource.select(rid)
                else:
                    if self._datasource.is_selected(rid):
                        self._datasource.deselect(rid)
                    else:
                        self._datasource.select(rid)
            self._update_tiles()
            self.event_generate("<<SelectionChange>>")
        # record is already the public record (the tile holds the projected copy).
        self.event_generate("<<ItemClick>>", data=record)

    def _handle_tile_activate(self, record: dict) -> None:
        if record:
            self.event_generate("<<ItemActivate>>", data=record)

    def get_datasource(self) -> DataSourceProtocol:
        return self._datasource

    def reload(self) -> None:
        self._relayout()
