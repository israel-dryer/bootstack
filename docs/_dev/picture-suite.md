# Picture suite — design brief

Branch: `feat/picture-suite`. The PR #125 (Image/Icon API) follow-up: a media-display
widget suite built on the public `Image` handle (`bootstack.images`).

## Motivation

`Image` is a toolkit-free **source** handle (file/bytes/PIL/deferred-icon). It holds no
display resource until handed to a widget via `image=`, and it is **not a widget** — it
cannot be placed in a layout. Today the only host is `Label(image=...)`, a *text-first*
widget that renders a fixed-size bitmap via Tk `compound`. It has no media semantics: no
fit/scale, no responsive resize, no animation, no splash/placeholder states.

The suite adds real display widgets that **consume** an `Image`, the way `Button` consumes
a `command`.

## The three widgets

Distinguished by *cardinality of attention*:

| Widget      | Shows                  | Role                          | Analog                  |
|-------------|------------------------|-------------------------------|-------------------------|
| `Picture`   | one image              | the display **atom**          | (new)                   |
| `Gallery`   | many, all at once      | **browse** a collection       | `ListView` (recycled)   |
| `Carousel`  | one of many at a time  | **focus** on one, prev/next   | `PageStack`             |

### Locked decisions

- **Lightbox is a mode, not a 4th widget.** "Click a Gallery tile → fullscreen viewer with
  prev/next" = a Gallery opening a Carousel in an overlay. Design the seam; don't add a class.
- **Don't collapse Gallery + Carousel** into one `layout=` switch. Different nav models
  (scroll-and-select vs step-through), different selection semantics (Gallery = record-native
  multi-select; Carousel = single active index), different chrome (Carousel wants arrows /
  dots / autoplay). Keep them separate; share `Picture` + the recycle-view internals.
- **Gallery is record-native.** Reuse the existing record family rails — the data bag,
  universal `.selection`, `data_source=` backing, recycle-view — so it slots in as "the
  thumbnail-grid member" alongside ListView/DataTable/Tree. Recycling is mandatory: a
  5,000-photo gallery must never materialize 5,000 Tk photos.

### Sequencing

`Picture` → `Gallery` → `Carousel`. Picture is the prerequisite atom and must be solid
(fit, resize, animation) before the collection widgets are worth attempting — each of them
is N Pictures plus selection/stepping plus recycling.

---

## Picture API (PROPOSED — pending maintainer review)

A plain-Python wrapper over an internal widget (Label-backed is sufficient for v1).

### Constructor

```python
bs.Picture(
    image,                       # Image | str | Path | None  — str/Path auto-wraps Image.open
    *,
    fit="contain",               # 'contain'|'cover'|'fill'|'none'|'scale-down'  (object-fit vocab)
    width=None,                  # int | None — fixed display box width (px)
    height=None,                 # int | None — fixed display box height (px)
    anchor="center",             # placement of the image within the box when it doesn't fill it
    corner_radius=0,             # int | float — rounded corners (PIL-masked at render time)
    autoplay=True,               # animated sources (GIF/WebP): start playing on display
    loop=True,                   # animated sources: loop playback
    surface=None,                # letterbox/background surface token
    parent=None,
    **kwargs,                    # layout placement (fill/expand/anchor/row/column/...)
)
```

**Fit modes** (CSS `object-fit` vocabulary, the well-known mental model):
- `contain` — scale to fit inside the box, preserve aspect, letterbox the remainder (default).
- `cover` — scale to fill the box, preserve aspect, crop the overflow.
- `fill` — stretch to the box, ignore aspect ratio.
- `none` — native size, no scaling.
- `scale-down` — like `contain` but never enlarge past native size.

**Sizing:** with `width`/`height` given, that's the box. Without, the box is the container
allocation (when filled/expanded) or the image's native size (`none`). A coalesced
`<Configure>` re-render makes contain/cover/fill responsive to container resize.

### Live properties

- `image` (get/set) — swap the source; re-renders.
- `fit` (get/set).
- `is_playing` (read) — animation state.

### Methods (animated sources)

- `play()` / `pause()` / `stop()` — playback control. Driven by the framework scheduler
  (`bootstack.scheduling`), never `app.tk.after`.

### Events

- `on_load(handler)` — fired when the image is decoded and displayed (payload TBD).
- `on_error(handler)` — fired when decoding fails (payload TBD).
- `on_click(handler)` — curated `Event` (enables the Gallery-tile → lightbox seam).

### Decisions (LOCKED 2026-06-12)

- **Caption: OUT.** `Picture` is image-only; a caption is a `VStack(Picture, Label)` or a
  Gallery-tile concern.
- **`corner_radius`: IN** for v1 (PIL mask at render time, no Canvas needed).
- **`on_load`/`on_error` payloads: TYPED** `bootstack.events` dataclasses, per the
  typed-payload convention.
- **Internal backing: Label-backed for v1** (PIL re-render → PhotoImage → configure; corner
  radius via PIL mask; animation via scheduler frame swap). Canvas only if a later need
  (overlays) forces it.

## Docs category — "Media" (LOCKED)

The narrative widget catalog (`docs/widgets/index.rst`) gets a new **Media** caption
(placed right after *Data Display*), not under Data Display and not called "Images".
`picture` is its first entry; `gallery`/`carousel` follow. "Media" over "Images" is
deliberate: a silent-video source is a plausible later addition (see Phase 2), so
"Images" would force a category rename + URL/anchor churn down the road. "Media" is
forward-compatible at no cost (animated GIF/WebP are already motion). The API Reference is
unaffected (one alphabetical *Widgets* concept page). The `__all__` comment group in
`bootstack/__init__.py` is retagged `# Media` to match.

## Phase 2 (planned, much later) — silent video source via `bootstack[video]`

A muted, looping, short/low-res clip used like a GIF (sticker/splash/motion), NOT a full
media player. Tk has no video and no audio; Pillow can't decode video — so this needs an
ffmpeg-backed decoder (`imageio[ffmpeg]`/PyAV/OpenCV) behind an **optional extra**
(`bootstack[video]`), a background decode thread feeding a frame queue, and the UI thread
blitting at a capped fps (PhotoImage creation must stay on the UI thread). It rides the
SAME threaded-frame rails as Phase 1.5 async load — do it after that. EXPLICIT BOUNDARY:
no audio, no A/V sync, no scrub-bar — a true player (audio + sync + codec coverage) is out
of scope for the framework; point users at an embedded external player instead. This is
why the docs category is "Media", not "Images".

## Gallery (BUILT — branch feat/gallery)

A scrollable, selectable thumbnail grid. Record-native: reuses the ListView/DataTable/Tree
rails (data bag, universal `.selection`, `data_source=`, recycle-view).

**Recycle design (the key insight):** NOT a hard 2D recycler. Model the grid as a VERTICAL
scroll of rows where each row is a HORIZONTAL strip of N tiles — so it's ListView's proven
1D row-recycle, each "row" rendering `columns` records (a slice) instead of one. Pool =
`(visible_rows + overscan) × columns` tiles. Each tile embeds a `Picture` (cover-fit
thumbnail) + optional caption `Label`; recycle swaps each tile's `image`/caption from the
new record (Picture's live `image` setter makes this cheap). No existing 2D-grid recycle in
the codebase — ListView 1D is the only precedent; this reuses it.

**API:**
```python
bs.Gallery(items=None, data_source=None, *, image_field="image", caption_field=None,
           columns="auto", tile_size=(160,160), fit="cover", corner_radius=0, gap=8,
           selection_mode="none", surface=None, parent=None, **kwargs)
```
- `items=`/`data_source=` like ListView; universal `.selection` (single→dict|None,
  multi→list[dict]); `select_items`/`deselect_items`/`select_all`/`clear_selection`;
  auto-refresh on source change.
- `image_field`/`caption_field` NAME keys in the flat record (Tree(parent_field=)/
  Select(group_by=) idiom).
- Events: `on_select` (coarse change → read `.selection`, family convention), `on_item_click`
  (record dict), `on_item_activate` (double-click → record dict — the Carousel/lightbox seam).

**Decisions LOCKED (2026-06-12):**
- **Responsive columns** — `columns="auto"` default (reflow on `<Configure>` from container
  width / tile width), `int` override for a fixed grid.
- **Captions opt-in** — `caption_field=` off by default (galleries usually want them, unlike
  Picture which is caption-out).
- **Highlight-ring selection** — accent-colored ring/overlay on selected tiles (NOT a
  ListView-style checkbox control).

**Deferred v1:** drag-reorder, remove buttons, grouping/section headers, async thumbnail
decode (Phase 1.5), rich keyboard nav.

## Carousel (BUILT — branch feat/carousel)

One-at-a-time image stepper — the "focus on one" member (single active index, NOT
record-native multi-select). Plugs into the lightbox seam Gallery exposes via
`on_item_activate` (open a Carousel over the same `items` at the activated index).

**Canvas-based stage (the key implementation decision):** the stage is its OWN `tk.Canvas`
(built like Picture's internal / the Gallery tile — canvas + shared `_image_fit`/
`_ImageService` helpers), NOT the Picture widget embedded. This is what makes transitions
work: **slide** = two image items on the canvas animated via `coords()`/`move()` (genuinely
needs a canvas); **fade** = `PIL.Image.blend(A, B, t)` over frames → PhotoImage swaps. Both
driven by the `Schedule` service. Tradeoff: Picture's GIF animation loop is NOT reused, so
**animated-GIF slides are deferred** — v1 slides are static (first frame). Compose each slide
to a full-box RGBA (fitted image centered on transparent → canvas surface letterboxes) so
slide/fade operate on uniform `(w,h)` images.

**API:**
```python
bs.Carousel(items=None, data_source=None, *, image_field="image", caption_field=None,
            index=0, fit="contain", transition="slide", show_arrows=True,
            indicator="dots", autoplay=False, interval=4000, loop=True,
            corner_radius=0, accent=None, surface=None, parent=None, **kwargs)
```
- Properties: `index` (get/set), `current` (record dict), `count`, `is_playing`.
- Methods: `next()`, `previous()`, `go_to(index)`, `play()`, `pause()`.
- Events: `on_change` (active slide changed → current record dict), `on_item_click`
  (click the stage — close-lightbox / open-detail seam).
- Keyboard: ←/→ navigate.

**Decisions LOCKED (2026-06-12):**
- **`transition="slide"` default** (the carousel standard), `"fade"` and `"none"` options;
  both implemented v1.
- **Static slides** (animated-GIF-in-a-slide deferred).
- **`indicator="dots"`** default, auto-switch dots→`"count"` past ~8 slides; `"none"` option.
- **Chevrons overlaid** on the stage (left/right center). Caption + indicator overlaid
  bottom-center (canvas items; white text w/ dark shadow for readability — full gradient
  scrim is a later refinement).
- **`fit="contain"`** default (show the whole image, vs Gallery's `cover`).
- **`corner_radius` rounds the CONTAINER, not each image** (maintainer call) — a fixed
  rounded corner-mask overlay (4 corners painted the surface color, AA via `rounded_mask`)
  sits above the images and below the chrome, so slides move *under* a steady rounded frame.
  Rounding each image (Picture/Gallery behavior) would make rounded corners slide across.
  Note: with `contain` on a same-surface parent the rounded corners fall in the letterbox and
  blend away (correct) — the rounding reads against `cover` or a contrasting parent surface.

**Deferred v1:** animated-GIF slides, swipe/drag, thumbnail filmstrip, gradient caption scrim.

**Follow-up — demo video:** a short looping MP4 of the transitions belongs on the Carousel
guide (a still can't show motion). The first attempt had a screen-recorder pay watermark and
was pulled. When a clean capture is ready: drop it at `docs/_static/examples/carousel-active.mp4`,
re-add a `.bs-video` CSS rule (full-window capture → border+radius+shadow like
`bs-window-screenshot`) and a `.. raw:: html` `<video class="bs-video" autoplay loop muted
playsinline controls>` block after the hero in `docs/widgets/carousel.rst`.

## Phase 1.5 (planned, NOT this pass) — async load + web URLs

URLs are a *source* concern → `Image.from_url(url)` on the handle (not a `Picture` special
case), so every `image=` consumer gets it. But a network fetch on the UI thread (where
`_load_pil()` runs at bind time) would freeze the app — so URLs ARE the async-load
initiative: background fetch (stdlib `urllib`, no new dep for v1), `placeholder=` while
loading, `on_error` on failure, result marshaled back to the UI thread (reuse the
DataSource thread-marshaled coalescing, [[project_datasource_change_events]]), URL-keyed
mem+disk cache so resize/theme re-renders never refetch. Independent value: large *local*
files also want off-thread decode. The Picture API above doesn't change — `placeholder=`
slots in, the events already exist. Ship the local atom first; layer this on as its own
reviewable unit.

### Implementation notes

- Reuse `Image._load_pil()` for the source PIL, do the fit/crop/resize/mask in the Picture
  internal, feed the result through the content-keyed `_ImageService.from_pil` for caching.
- Animation: `PIL.ImageSequence` for frames; advance via a `Schedule`; respect each frame's
  duration; render each frame through the same fit pipeline.
- Keep a strong ref to the live PhotoImage on the wrapper (Tk GC), as `bind_image` does.
- Theme-following only matters for token-colored icons, not photos — photos don't re-render
  on `<<BsThemeChanged>>`. (A token-colored `get_icon` shown in a Picture is an edge case;
  decide whether Picture honors theme-following like `bind_image` does.)
