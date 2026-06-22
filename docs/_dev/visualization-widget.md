# Visualization widget (`bs.Chart`) — design brief

Status: **Phase 1 shipped** (PR #279, `feat/chart-widget`). **Phase 2 +
animation** built on `feat/chart-reactive` (combined PR). Optional dependency —
core installs never import matplotlib. Supersedes the placeholder note in memory
`project_seaborn_viz_plugin`. Tracked: GitHub #277.

Decisions locked with the maintainer (2026-06-21): widget name is **`Chart`**;
seaborn is an additive extra, not a separate integration.

**Phase 2 — shipped (reactive + animation).** Two update paths landed on top of
the figure host:

- **Managed render** (`render=` + `signal=`) — the chart owns the figure and
  redraw loop, applying the theme as rcParams (incl. a semantic accent
  `prop_cycle`) before each `render(ax, data)`. Re-renders on theme change and
  on signal change; rapid changes **coalesce to one render per idle frame** so a
  fast source can't starve the loop.
- **Blitting animation** (`chart.animate(setup, update, interval=)`) — the fast
  path for continuous animation. A full `clear()`+rebuild is ~31 ms/frame
  (~32 fps ceiling); blitting (update artists in place + redraw only them over a
  cached background) is ~0.2 ms/frame. Decisions made during build:
  - **Time-based motion** — the callback receives elapsed *seconds* (not a frame
    index) for the default continuous animation, so apparent velocity stays
    constant under Tk timer jitter. Explicit `frames=` still steps fixed data.
  - **Visibility gating** — runs only when *actually visible*: paused on
    `<Map>`/`<Unmap>` (tabs/pages/minimize — reliable cross-platform) and on
    `<Visibility>` full-cover (best-effort, mainly X11). Off-screen charts on a
    dashboard cost nothing. A theme change that arrives while hidden is applied
    on the next `<Map>` (deferred via the `Frame` theme-repaint hook).
  - **Theme on blit** — clearing FuncAnimation's `_blit_cache` on theme change
    forces a background re-grab (the cache otherwise only refreshes on a view
    change). Animated *series* keep their `setup` colors; chart *chrome* tracks
    the theme.
  - Returns a `ChartAnimation` handle (`stop`/`start`/`running`); auto-stops on
    destroy. What you draw with stays pure matplotlib.

Remaining: **Phase 3** (`data_source=` ingestion) and **Phase 4** (seaborn extra
+ themed nav toolbar + docs page).

## Goal

Empower data visualization inside bootstack without making it a charting library.
A user composes a chart the same way they compose any other widget, it matches the
active theme (light/dark) automatically, and it can live-update from a `Signal` or
a `DataSource`. matplotlib is the engine; seaborn rides on top of it for free.

**Non-goal:** a bespoke plotting API. We do not wrap matplotlib's plotting calls.
The user draws with matplotlib/seaborn; we own embedding, theming, and the redraw
loop.

## Why this shape

Everything needed already exists in the framework — no core changes:

- **Widget pattern** — `PublicWidgetBase` wrapper + internal `Frame` composite
  hosting a canvas. Model file-for-file on `Picture` / `Avatar`
  (`widgets/picture.py` + `widgets/_impl/composites/picture.py`). matplotlib's
  `FigureCanvasTkAgg(fig, master=self).get_tk_widget().pack(fill="both",
  expand=True)` drops straight into the internal `Frame`.
- **Theme bridge** — `get_theme_color(token)`, `get_theme_provider().mode` /
  `.typography`, and the canvas theme-repaint hook
  (`Frame._enable_theme_repaint(self._redraw)`, fires on Publisher `Channel.STD`
  after a rebuild, gated on `winfo_viewable()`).
- **Reactivity** — `Signal.subscribe(cb) -> Handle` (cancel on `<Destroy>`),
  `.map()` for derived; `DataSource.observe(cond, *order) -> Stream[list[Record]]`
  and `.on_change()`, exactly as `ListView` / `DataTable` consume them today.
- **Optional deps** — the `excel` / `parquet` / `hdf5` extras already establish the
  pattern.

## Dependency strategy

```toml
[project.optional-dependencies]
viz = ["matplotlib>=3.8"]
viz-seaborn = ["matplotlib>=3.8", "seaborn>=0.13"]
```

`chart.py` imports matplotlib **lazily inside `__init__`** and raises a friendly
`BootstackError` ("install with `pip install bootstack[viz]`") if missing. Pillow
(already core) covers any raster needs; no new core deps.

Two embedding correctness rules:

- **Use `matplotlib.figure.Figure` directly — never `pyplot`.** pyplot keeps
  global figure-manager state and pops separate OS windows. Embedded figures must
  be standalone `Figure()` objects.
- **Set the figure DPI from the Tk scaling factor** (`ui_scale`) so charts stay
  crisp on high-DPI — same family as issue #267.

## Public API — two layers

### Layer 0 — figure host (escape hatch, full control) — PHASE 1

```python
from matplotlib.figure import Figure
fig = Figure()
fig.add_subplot().plot([1, 2, 3])
bs.Chart(fig)          # embeds it, applies best-effort theme recolor, redraws on theme change
```

### Layer 1 — managed render callback (reactive, recommended) — PHASE 2+

```python
def render(ax, data):
    ax.plot(data["x"], data["y"])

bs.Chart(render=render, signal=my_signal)     # re-renders when the signal changes
bs.Chart(render=render, data_source=ds)       # re-renders when the source mutates
```

In the managed path the widget owns the whole lifecycle: clear axes → apply theme
styling → call `render(ax, data)` → `canvas.draw()`.

Conveniences: `chart.figure` / `chart.ax` accessors, `chart.draw()`, `debounce=`
(ms) for high-frequency sources, and `toolbar=True` (see below).

## Theme bridge (the differentiator)

An internal helper translates the active theme into a matplotlib rcParams dict
(figure/axes facecolors, text/tick/spine colors, grid, an accent `prop_cycle`, and
fonts from `get_theme_provider().typography`). The managed render runs inside
`with matplotlib.rc_context(rc):` so plotting calls inherit themed defaults *and* a
semantic color cycle. On `<<BsThemeChanged>>` / Publisher `Channel.STD`, the widget
re-renders under the new rc and redraws.

**Honest tradeoff:** rc_context only governs the managed (`render=`) path. For the
Layer-0 `figure=` escape hatch the figure is already built, so the widget can only
do best-effort recolor of existing artists (facecolors, tick/spine/text). A fully
bespoke figure owns its own styling — documented as such.

## Navigation toolbar — replace the raw-Tk one (Phase 4)

> ⚠ matplotlib's built-in `NavigationToolbar2Tk` (pan / zoom / home / back /
> forward / save) is a raw `tk.Frame` of unstyled tk buttons. It clashes with the
> themed app and violates the no-raw-Tk principle (memory
> `feedback_no_raw_tk_use_framework_idioms`). **We must not pack it.**

matplotlib separates navigation *logic* (`matplotlib.backend_bases.NavigationToolbar2`
— history, pan, zoom-rectangle, mouse handlers) from the *Tk rendering*. Recommended
(`toolbar=True`): instantiate `NavigationToolbar2Tk(canvas, master,
pack_toolbar=False)` so its tk frame is created but **never mapped**, then build a
bootstack `Toolbar` of themed icon buttons wired to `nav.home`/`back`/`forward`/
`pan`/`zoom`/`save_figure`. This reuses matplotlib's pan/zoom math and the
canvas-drawn rubber-band (painted on the canvas, not the toolbar frame) — zero
reimplementation. Follow-ups: route `save_figure` through bootstack's file-dialog
verb; feed `set_message` to a Label/StatusBar; reflect pan/zoom toggle state via
button styling.

## Signals — live update (Phase 2)

`signal=` accepts one signal or a list, each `subscribe`d to `self._redraw` (cancel
on `<Destroy>`). matplotlib `draw()` is not cheap → expose `debounce=<ms>` (route
through `Stream.debounce`) and gate redraws on `winfo_viewable()`. `.map()`-derived
signals work unchanged (keep a reference — weakref-held).

## Data source — ingestion (Phase 3)

`data_source=` accepts any `DataSourceProtocol`. Static: `ds.page_slice(0, big_n)`.
Live: `ds.observe(condition, *order).listen(self._on_rows)` (re-emits the full
matching set; initial emit immediate). For very large sources prefer `ds.on_change()`
+ a windowed read, as `ListView` / `DataTable` do. A chart and a `DataTable` on the
**same source** stay in lockstep — the headline demo.

## Seaborn (Phase 4)

No separate integration. seaborn draws onto a matplotlib `Axes`, so
`render(ax, data)` takes `sns.barplot(..., ax=ax)` directly. Seed seaborn's palette
from accent colors inside the rc_context. Keep seaborn in `viz-seaborn`, out of the
import path.

## File layout

| Purpose | Path |
|---|---|
| Public wrapper | `src/bootstack/widgets/chart.py` |
| Internal composite | `src/bootstack/widgets/_impl/composites/chart.py` |
| Register (lazy) | `widgets/__init__.py` → `_EXPORTS["Chart"] = "chart"` |
| Register (top-level) | `bootstack/__init__.py` import + `__all__` |

## Phasing

1. **Phase 1 (MVP, this branch):** `bs.Chart(figure=...)` + theme bridge +
   theme-change redraw + `viz` extra. Proves embedding + theming end-to-end.
2. **Phase 2:** managed `render=` + `signal=` live updates + `debounce=`.
3. **Phase 3:** `data_source=` ingestion (static + `observe`); Chart+DataTable demo.
4. **Phase 4:** `viz-seaborn` extra + palette seeding; themed nav toolbar; docs page.

## Risks / gotchas

- **pyplot vs Figure** — the single biggest embedding bug if missed.
- **Raw-Tk nav toolbar** — never pack `NavigationToolbar2Tk`; drive its methods
  from a themed bootstack `Toolbar`.
- **Redraw cost** — debounce reactive sources; gate on visibility.
- **DPI** — set figure DPI from `ui_scale`.
- **Don't advertise before it ships** — no docs/demo/promo mention of charts until
  the widget is real (per `project_seaborn_viz_plugin`).