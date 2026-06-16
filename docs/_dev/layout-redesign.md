# Layout redesign — flexbox/CSS-grid vocabulary on a grid engine

Branch: `feat/grid-layout-engine`. Started 2026-06-16.

Replace the stack layout API (`anchor_items` / `fill_items` / `expand_items`, and
Grid's `sticky_items`) with a flexbox/CSS-grid vocabulary — `justify` / `align` /
`grow` plus a `Spacer()` element — and reimplement stacks on the Tk **grid**
geometry manager instead of pack. Prototype validated in
`development/flexlayout_proto.py` (untracked scratch; run scenes with
`py -3.12 development/flexlayout_proto.py <scene>`).

This is a **breaking, core-engine** change. Do it before the 0.1.0 API freeze.

---

## Why

Two problems, one root cause.

1. **The trigger bug.** `HStack(fill="x", anchor_items="e")` does **not** right-align
   a button row. `anchor_items` maps to pack's `anchor`, which only positions a child
   *within its own cell on the cross axis*. For an `HStack` the cross axis is
   *vertical*, so `"e"` is a no-op horizontally. There is **no public way to
   right-align a group along an HStack's main axis** today — internally the dialog
   button bar does `btn.pack(side="right")`, and only `Toolbar`/`StatusBar` have a
   private `add_spacer()`.

2. **Tk-isms leak.** `anchor` (compass `n/s/e/w`), `fill` (`x/y/both`), and `sticky`
   (`nsew`) are raw Tkinter vocabulary in a framework whose whole premise is that you
   never see Tkinter. They also conflate concerns: a single compass `anchor` value
   means different things on H vs V stacks.

The fix is axis-relative, CSS-derived names that separate main-axis from cross-axis,
and an engine (grid) that can actually express main-axis group distribution.

---

## The model (validated)

| Tool | Job | Scope | Values |
|---|---|---|---|
| **`justify`** | whole-group **main-axis** distribution | container | `start` · `center` · `end` · `space-between` · `space-around` · `space-evenly` |
| **`align`** / `align_self` | **cross-axis** alignment | container default + per-child | `start` · `center` · `end` · `stretch` |
| **`grow`** / `grow_items` | **main-axis** item growth (flex-grow) | per-child / container | `int` weight |
| **`weights=`** | explicit per-track weight list (the `Grid(columns=)` form) | container | `list[int]` |
| **`Spacer()`** / `Spacer(size=)` / `Spacer(weight=)` | composable break / push — clusters, fixed gap, weighted slack | inline element | — |

2-D **`Grid`** uses the grid box-alignment names: **`justify_items`** /
**`align_items`** (in-cell alignment) + weighted **`columns=`** / **`rows=`** (track
sizing) + per-child **`justify_self`** / **`align_self`**.

### Mapping from the old pack knobs

Pack gives each child a *parcel* (a slice of the cavity). `fill` stretches the child
in its parcel, `expand` grows the parcel, `anchor` positions the child in the parcel.
Sorted by axis:

| Old (pack) | Axis | New |
|---|---|---|
| `anchor_items` n/s (H) · w/e (V) | cross | `align="start"\|"end"\|"center"` |
| `fill_items` cross part (`y` for H, `x` for V) | cross | `align="stretch"` |
| `expand_items` (distribute the group) | main | `justify` |
| `fill_items` main part **+** `expand_items` (items share space) | main | `grow` / `weights=` |
| `Grid` `sticky_items` (`nsew`) | both | `justify_items` + `align_items` |

`fill="both"` becomes `align="stretch", grow=True`.

### `justify` vs `Spacer` — complementary, not redundant

This was the central design debate. They have **different jobs**:

- **`justify`** is a *whole-group, container-level policy* — one value that
  moves/distributes **all** direct children as a single group.
- **`Spacer()`** is a *local, composable element* — a break at **one specific point**
  that pushes its neighbors apart.

`justify` alone **cannot** make clusters (`[New][Open]·····[Settings][Profile]` from a
flat list): `space-between` spreads *every* child evenly, and there's no `justify`
value for "split here." The flat alternative without `Spacer` is **nesting** each
cluster in a sub-stack + `justify="space-between"` — much more verbose. `Spacer` does
it inline with zero per-item kwargs and no nesting.

The only overlap is the trivial `justify="end"` ≈ a single leading `Spacer()`. The
teaching line is therefore crisp (no duplication tax):

> Use **`justify`** to position/distribute the **whole group**; drop a **`Spacer()`**
> where you want a **break** (clusters, or push part of a row aside).

`Spacer()` also **unifies the existing `Toolbar`/`StatusBar` `add_spacer()`** into one
element usable in any `Row`/`Col` (today those composites have a bespoke spacer that a
hand-built row can't use). `add_spacer()` should become "add a `Spacer()`."

### Rejected: `push=`

`push=True` (an implicit per-child spacer-before) was prototyped and **dropped**. It
was a third way to do something `Spacer` (inline break), `margin_x` (fixed gap), and
nesting (clusters) already cover — with a non-CSS name and no directional control. The
fixed-gap and cluster needs are served by `margin_x=` and nesting/`Spacer`.

---

## Why the grid engine

The thing that made `justify` ugly on pack was needing fake spacer *widgets* (which
pollute the child list and break `detach`/`attach` indexing). **Grid needs none of
that — an empty track with `weight` claims space without a widget in it.**

| Intent | Grid mechanism (HStack = 1 row, N columns) |
|---|---|
| `justify="end"` | leading empty column, `weight=1` |
| `justify="center"` | leading + trailing empty columns, `weight=1` |
| `justify="space-between"` | empty `weight=1` columns *between* content cells |
| `justify="space-evenly"` | empty `weight=1` columns everywhere |
| `justify="space-around"` | integer weights `1 : 2 : … : 2 : 1` (grid does this; pack couldn't) |
| `grow` (incl. **weighted** ratios) | weight on the **content** columns |
| `align` (cross) | per-cell `sticky` — `"ew"`=stretch, `"w"`=start, `"e"`=end, `""`=center |
| equal columns | `columnconfigure(uniform=…)` for *true* equal sizing |

Bonus wins: **true weighted grow** (2:1 panes/segments — pack fundamentally can't),
correct `space-around`, and it **collapses three geometry managers into one**:
`HStack` = grid 1 row / auto columns, `VStack` = grid 1 col / auto rows, `Grid` = 2-D.
That unifies `detach`/`attach` (which today carries pack-specific ordering logic *and*
a grid-specific gotcha) onto a single path.

`Spacer()` on this engine = a content-less cell whose track carries `weight=1`
(flexible) or a fixed `minsize` (`Spacer(size=)`). The *distinction* from `justify`'s
phantom tracks: a `Spacer` is an **explicit** child (legitimate tree member, known
index) — fine for `detach`/`attach`; `justify`'s injected tracks stay **phantom** (no
widget) and must never enter the child list.

---

## Naming audit (clash check before finalizing)

The mechanism that makes this matter: a per-child layout key works by being in
`PACK_KEYS`/`GRID_KEYS` (`widgets/_core/container.py`), and `_split_layout_kwargs`
strips those off **every** widget's `**kwargs`. **The moment a name enters that set it
shadows that kwarg on every widget.** So container-level params only collide within
the layout container classes; per-child params collide with *anything*.

| Proposed | Scope | Existing use | Verdict |
|---|---|---|---|
| `justify` | container | `Justify` text-align on Label / TextField / NumberField / SpinnerField / Tooltip | **No clash** — fields aren't containers, and `justify` is never a per-child key. **No `justify_text` rename needed.** |
| `align` | container | `align` on Snackbar/snackbar (bottom-edge placement) | No clash *as a container param*; **hard clash if used as a per-child key**. |
| `wrap` (future flex-wrap) | container | `wrap` on TextArea/CodeEditor (line-wrap) and NumberField/SpinnerField/Spinbox (value-wrap) | No clash today (no container has `wrap`); decide the flex-wrap name when building it. |
| `grow`, `grow_items`, `*_items`, `*_self`, `*_content` | — | none | Safe. |
| `columns` / `rows` | container | Grid/Card/etc. (ours); DataTable/Gallery (different classes) | No new clash; weight-list consistent with existing `Grid(columns=)`. |

**Resolution:** the **collision-free per-child key set is `grow`, `align_self`,
`justify_self`** — never bare `align`/`justify` as placement keys. Bare `align`/`justify`
stay container-only (this is also the CSS-correct `align-items` vs `align-self` split).

---

## Migration risks & things to watch out for

**Blast radius is the whole framework** — every one of ~60 widgets lives inside a
stack, so any sizing-default shift ripples through every example and screenshot. Treat
defaults as load-bearing decisions, not conveniences.

1. **★ Legacy `fill`/`expand` child kwargs are silently ignored by the grid engine.**
   In the prototype a `ListView(fill="both", expand=True)` collapsed (the recycling
   canvas needs a defined size). Migration is **not just renaming container props** —
   *every child* that relied on `fill="both"/expand=True` must move to `grow`/`align`,
   **data/canvas widgets especially** (ListView, DataTable, Tree, Gallery, Carousel,
   ScrollView contents). Grep for `fill=`/`expand=` across `docs/` and `src/` and
   convert. Consider a deprecation shim that maps `fill`/`expand` → `align`/`grow` for
   one release to avoid silent collapse, or at minimum a runtime warning.

2. **Cross track must always carry weight.** Cross-axis `align` (start/center/end) has
   no room to position a child unless the single cross track fills the container. The
   engine must `rowconfigure(0, weight=1)` (HStack) / `columnconfigure(0, weight=1)`
   (VStack) **unconditionally**, not only for `align="stretch"`. (Prototype does this.)

3. **Nested containers need explicit `align="stretch"`** to fill the cross axis;
   default `start` leaves them at natural size. **Decide whether `stretch` should be
   the default** for nested layout containers (CSS `align-items` defaults to stretch).

4. **`Spacer` children are real tree members** — fine for `detach`/`attach` since
   they're explicit and have a known index. But auto-flow + mid-insert (`index=` /
   `before=` / `after=`, the PR #123 placement work) must account for them, and the
   distinction from phantom `justify` tracks must hold (phantom = no widget, never in
   the child list).

5. **Gap synthesis.** Tk grid has **no native gap** — synthesize with edge-aware
   `padx`/`pady` per cell (what `PackFrame._compute_gap` does today), and **skip the
   empty spacer/justify tracks** so gap doesn't double up around them.

6. **Auto-flow + `_regrid_all`.** Stacks append without explicit `row`/`column`, so a
   grid-backed stack needs an auto-cursor and a re-grid pass on mid-insert (pack had
   `_repack_all`). `space-between` etc. recompute their phantom track count when a
   child is added/removed — more stateful than pack's static anchor.

7. **Grid sizing semantics differ from pack.** Grid `weight` distributes only space
   **above each track's minsize**, and equal-looking columns need `uniform=` or wide
   content makes them unequal. Effects only read with adequate slack. The `align`/
   `grow` defaults must be chosen against this, not pack's model.

8. **`detach`/`attach` (`container.py` `Placement`)** is pack-shaped today (pack
   ordering logic + a grid `grid_forget`+reconstruct gotcha). Unify it on grid — this
   should *simplify* it, but it's load-bearing and tested (`test_attach_detach.py`,
   one module-scoped App). Re-validate.

9. **`Toolbar`/`StatusBar` `add_spacer()`** should be re-pointed at the public
   `Spacer()` so there's one spacer concept. (Note: it's `Toolbar`, not `CommandBar` —
   the rename in the stale CLAUDE.md note was reverted.)

10. **ScrollView caps vertical fill** — a `grow` child inside a ScrollView gets natural
    height, not viewport-filling (the ScrollView sizes content and scrolls). Real
    behavior, not just a harness artifact; document it.

11. **`flex-wrap` is a future capability** the grid engine enables (HStack spilling to
    `rows=2,3,…`). Out of v1 scope; grid doesn't auto-wrap (you compute wrap points).

12. **Capture/harness note:** windows wider than the screen grab black in the
    prototype's screenshot helper — keep prototype scene windows ≤ ~820px wide.

---

## Defaults to decide (open)

- **`align` default** — pack defaults `anchor` to *center*; CSS `align-items` defaults
  to *stretch*. Prototype used `start`. Pick deliberately (changing it shifts every
  layout).
- **`grow` granularity** — keep both a container `grow_items` default *and* per-child
  `grow`, or per-child only?
- **Keep `justify`'s `space-*` modes now that `Spacer` exists?** They overlap on N=2
  but `justify` is far more concise for uniform distribution of many items. Lean: keep.
- **Hard break vs deprecation shim** for `anchor_items`/`fill_items`/`expand_items`/
  `sticky_items` and child `fill`/`expand`. Pre-release favors a hard break, but risk
  #1 (silent collapse) argues for at least a one-release warning shim.
- **Grid box-alignment scope** — ship `justify_items`/`align_items` (replacing
  `sticky_items`); defer `justify_content`/`align_content` (whole-grid track
  distribution) unless needed.

---

## Prototype reference

`development/flexlayout_proto.py` — grid-backed `Row`/`Col`/`Grid2D`/`Spacer` with the
final vocabulary. Scenes (all validated green): `justify`, `grow`, `align`, `col`,
`weights`, `toolbars`, `spacer`, `overflow`, `grid`, `nesting`. It monkeypatches the
per-child key set and defers layout to `__exit__` (needs the full child count to plan
phantom tracks) — both are prototype shortcuts the real implementation won't need.

What it proved: justify distribution via phantom tracks (no spacer widgets), weighted
& uniform grow, cross `align` + `align_self`, `Spacer` clusters/fixed/weighted, 2-D
`justify_items`/`align_items` + weighted tracks, fixed gaps via `margin_x`, nesting,
overflow. What it surfaced: migration risks #1–#3 above.

---

## Verification (every step)

- Clean Sphinx build warning-free (`sphinx-build -W --keep-going`).
- Run the prototype scenes; capture at ≤820px window width.
- `tests/test_attach_detach.py` and the layout tests must pass after the engine swap.
- Re-generate the doc screenshots affected by layout changes (the docs
  code-blocks were aligned to scenes in PR #164 and will move again here).

## Sequencing

1. Lock the public vocabulary (this brief) — engine-agnostic, so it can be frozen
   independent of the pack→grid swap.
2. Build the grid engine behind `Row`/`Col`/`Grid` + `Spacer`.
3. De-risk first: gap synthesis, auto-flow mid-insert, `detach`/`attach` on grid.
4. Migrate children off `fill`/`expand` (risk #1) — framework + docs + examples.
5. Re-point `Toolbar`/`StatusBar` `add_spacer()` at `Spacer()`.
