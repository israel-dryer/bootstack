# bootstack — docs and widget authoring patterns

Split out of `CLAUDE.md` on 2026-08-20 (it had reached ~60,000 tokens). This is
**reference consulted when you do docs or widget-page work**, not standing
handoff state — every rule below was live and unchanged at the split.

**Read this before** homing a widget into the API Reference, writing or editing a
widget page, taking screenshots, or touching the docs IA. The companion checklist
is `docs/_dev/widget-review-and-docs-standards.md`; the API Reference re-cut brief
is `docs/_dev/api-reference-restructure.md`.

---

## Prior initiative — Sphinx docs + public API audit (MERGED)

Branch `feat/docs-api-improvements`, merged to `main`. Shipped: the docs structure,
the public Table (`DataTable`), the typed-event redesign, the theming + font public
APIs, the DataSource verb rename + filtering DSL, and the observable-query layer.
Full detail lives in git history and memories; only the still-live conventions and
the open backlog are kept here.

### Still-live conventions

- **Docs structure** — top-level navbar is **3 pillars** (numpy-style):
  **User Guide · Widgets · API Reference** (`docs/index.rst`). (The old **Production**
  pillar was folded into the User Guide as the **Developer tools** caption — PR after
  #330, 2026-06-24; navbar overflow stays low.)
  - **User Guide** (`docs/user-guide/index.rst`) folds Getting Started + Tasks +
    Reference + the former Production pages into ONE pillar with four `:caption:`
    toctree groups — **Getting started** (`/getting-started/*`), **How-to guides**
    (`/tasks/*`, goal-indexed recipes), **Feature guides** (`/reference/*` +
    `/production/app-settings`, subsystem-indexed usage guides — renamed from
    **Topics** 2026-06-24; both how-to and feature guides are example-rich — the split
    is goal-vs-subsystem, NOT recipe-vs-theory, so do NOT call them
    "Concepts"/"Explanation"), and **Developer tools** (`/production/cli` ·
    `hot-reload` · `debugging` · `distribution`). The leaf pages STAY in their
    `getting-started/`/`tasks/`/`reference/`/`production/` dirs (no URL churn — the
    `production/` dir name is now just an internal artifact); only the landing + top
    toctree changed. The section `index.rst` landings (incl. `production/index.rst`)
    are DELETED. **`composing-fields` → `customizing-fields`** (#323, the one accepted
    URL churn — the title clashed with "Composing with Builders"; no redirect, per the
    no-shims stance).
  - **Widgets** (`docs/widgets/index.rst`) = flat leaf pages grouped by
    `.. toctree:: :caption:` blocks (curated common-first order, NOT alphabetical);
    kept as its own pillar (large *visual* catalog). The 10 old category landing pages
    are RETIRED. `docs/api/` + `docs/deeper/` are GONE.
  - **API Reference** (`docs/api-reference/index.rst`) = the by-concept lookup layer
    (semantic groups, full-path stub titles, pandas-style card landing — see the IA
    re-cut in `docs/_dev/api-reference-restructure.md`).
  - `show_nav_level: 1` (collapsed by default). Do NOT promote sub-groups to top-level
    (pydata navbar overflows ~6+). The old "Reference page pattern" is SUPERSEDED by the
    API Reference & Guide pattern below.
- **Title casing + how-to naming** (2026-06-15) — TWO-TIER casing, applied
  consistently: **page titles (H1) and card/sidenav titles are Title Case**
  (`Building Forms`, `Images and Icons` — conjunctions like `and` stay lowercase);
  **in-page section headers are sentence case** (`Backing a widget with a data
  source`). **How-to (`/tasks/*`) titles are action-driven gerunds** —
  `‹Gerund› ‹object›` (`Displaying Data`, `Using the Clipboard`, `Showing Dialogs`),
  NOT topical nouns. **Feature guides (`/reference/*`) keep noun/subsystem titles**
  (`Events`, `Data Sources`) — that's correct, not a violation. Keep titles short enough to not
  wrap in the sidenav (~≤20 chars; drop articles: `Setting App Icons`, not `Setting an
  Application Icon`). **A page's H1, its User-Guide card title, and its sidenav entry
  must all match** (the sidenav shows the H1, so a card/H1 mismatch shows as drift).
  How-to card grid + the hidden toctree are ordered by **learning progression** (build
  a screen → compose → app structure → ship), and both must stay in the SAME order.
- **No Tkinter in docs or docstrings** — no `tk.*` types/terms unless strictly
  necessary; don't feature the escape hatch. Full `src/` docstring scrub still
  pending. LEFT BY DESIGN: `.tk`/`.var` escape-hatch property docstrings,
  `signals/integration.py` (the Tk bridge).
- **Event / theming / DataSource APIs are DONE** — reflected in the Architecture +
  Gotchas sections below and in memories `project_typed_events`,
  `project_theming_public_api`, `project_datasource_api_naming`,
  `project_datasource_change_events`. Deferred-only: the visual theme builder
  (Phase 5, near-ship — emits `bs.Theme(...)` code; do NOT build yet).

### API/cleanup backlog (deferred, memory-tracked)

- `project_capabilities_relevance` — `_core/capabilities` may be redundant now the
  public layer abstracts Tk; still imported by data/i18n/mixins.
- `project_docstring_backticks` — **DONE (PR #182):** swept to single backticks
  (`default_role="code"` makes them render as inline code). Convention is Google +
  SINGLE backticks; RST cross-ref roles (`:class:`/`:doc:`/`:ref:`) are kept (deliberate).
- `project_event_naming_revisit` — past-tense event names pending rename:
  `SideNav.on_pane_toggled`/`on_display_mode_changed`, `ListView.on_selection_changed`,
  `Calendar.on_date_selected`.
- ~~`project_signal_subscribe_subscription`~~ — **DONE (#157)**: `Signal.subscribe()`
  now returns a cancelable `streams.Handle` (was a `str` token), unifying with
  events/streams.
- `project_editfilter_public_api` — `EditFilter` DEMOTED (Tk-coupled raw text
  indices/tags); investigate a de-Tkinter-ed CodeEditor extension API before any
  re-promotion. `NOTE(editfilter-public-api)` in
  `widgets/_impl/composites/textarea/filter.py`.
- `project_window_api_hardening` — `bs.Window` leaks uncurated `**kwargs` to the
  internal Toplevel (raw Tk options in; useful `icon`/`alpha`/`toolwindow`/
  `window_style` only via the escape hatch), has no live properties
  (`title`/`size`/`topmost` are construction-only), and never releases the modal
  grab. Curate to typed params + add a live `title` + release on close. Own branch.
- `project_show_indicator_removal` — **KEEP (reversed 2026-06-15).** `show_indicator=`
  was briefly flagged for removal but is being kept: the `show_indicator=False` +
  `on_icon`/`off_icon` combo is exactly what makes an icon-driven custom checkbox, and
  removing it would orphan that. GitHub #144 closed won't-do. Do NOT re-propose removal.
- `project_enum_option_typing` — promote recurring enumerated `str` kwargs to NAMED
  `Literal` aliases in `widgets/types.py` (re-exported from `bootstack.types`); the
  ALIAS docstring carries the value list once, widget docstrings describe meaning only
  (no value enumeration — REVERSES the Code-standards "valid values per kwarg" rule for
  aliased types; keep the default). First fixes: `accent: str`→`AccentToken` in
  `form.py`/`menubar.py`. New aliases: `SelectionMode`/`IconPosition`/`LayoutKind`/
  `AutoFlow`/`ExportScope`; reuse existing `Orient`/`Fill`/`Anchor`/`Sticky`. Own branch.
- Lower-priority: bare index/landing pages (root, `widgets/`, `reference/`);
  localization/windowing `tasks/` how-tos; screenshots pending (Tooltip/Toast, 7
  Dialog pages); AppShell deferred improvements (`nav_pane_width=` not wired to
  `SideNav(pane_width=)`, hardcoded nav density/font, group active-child highlight +
  indentation, footer non-page widgets).

---

## API Reference & Guide page pattern (established — follow exactly)

The docs are a **Diátaxis-style split** (PR #107): a narrative layer (**Widgets** +
**Guides**) plus a **unified, complete API Reference** that mirrors each submodule's
`__all__`. **Load-bearing rule: every object has exactly ONE autodoc home, and it
lives in the API Reference.** Narrative pages cross-link in (`:class:` / `:func:` /
`:meth:`) and may carry a *table-only* `autosummary` summary; they never re-document.
A second autodoc home reintroduces the "duplicate object description" warnings PR #106
removed. Full brief + all staged-sweep decisions: `docs/_dev/api-reference-restructure.md`.
Memory `project_api_reference_restructure`.

### The autosummary templates (locked, PR #107 + Stage 2)

THREE custom templates under `docs/_templates/autosummary/`, one per documenter
kind autosummary uses for the data surface — `class.rst`, `function.rst`,
`data.rst`. **All THREE must title the stub page with the bare `{{ objname }}`**
(not `{{ fullname }}`). This is load-bearing: autosummary picks the template by
object kind, and the **stub's title is what the sidebar shows**. The built-in
fallback templates title with the full dotted path (`bootstack.data.col`), so
relying on the fallback for functions/data produces a sidebar where classes read
bare (`MemoryDataSource`) but functions/aliases read fully-qualified
(`bootstack.data.col`) — the exact inconsistency Stage 2 fixed. Keep the bare-title
line identical across all three.

`class.rst` (also serves dataclasses + Protocols):

```rst
{{ objname | escape | underline }}

.. currentmodule:: {{ module }}

.. autoclass:: {{ objname }}
   :members:
   :inherited-members:
   :show-inheritance:
```

`function.rst` → `.. autofunction:: {{ objname }}`; `data.rst` →
`.. autodata:: {{ objname }}` — each with the same bare-title + `currentmodule`
header.

- `:inherited-members:` (class template) is what makes a concrete-source stub
  **complete** (e.g. `SqliteDataSource` shows inherited
  `save`/`on_change`/`observe`/`export_csv`).
- The Protocol page stays noise-free because `undoc-members` is off and there is no
  `:special-members:` — `_private`/dunder/Generic members are filtered out.
- Some type aliases classify as class-like and pick up `class.rst` (e.g.
  `Primitive`), others as data and pick up `data.rst` (e.g. `Record`) — both now
  title bare, so it no longer matters which. A new documenter kind a future module
  needs (e.g. `exception.rst`) must get the SAME bare-title treatment.
- **Per-class curation** (a class needing different members than the global
  `class.rst`): add a per-class template file `_templates/autosummary/<name>.rst`
  and point that class's `autosummary` entry at it with `:template: <name>` —
  **WITHOUT the `.rst` extension**. Sphinx's autosummary resolves `:template: X`
  as `autosummary/X.rst`; passing `signal.rst` builds `autosummary/signal.rst.rst`,
  silently misses, and falls back to the built-in `base.rst` (full title, no
  members) — NOT even `class.rst`. `:template:` applies to every name in that
  directive block, so put the curated class in its own one-name block. Exemplar:
  `signal.rst` (Signal needs `__call__` shown + `tk`/`var`/`name`/`from_variable`
  excluded); wired in `api-reference/signals.rst` as `:template: signal`.

### API Reference page recipe (the autodoc home — one per submodule)

A page like `docs/api-reference/data.rst`. Text-only, **NO screenshots, NO hero**.

1. Title = the dotted module path (`bootstack.data`), then `.. currentmodule::` it.
2. One prose paragraph orienting the module + a `:doc:` link to its Guide.
3. **Group the surface into labeled sections** (`---` headings), each: a one-sentence
   prose lead-in, then an `.. autosummary::` table with `:toctree: generated` and
   `:nosignatures:`. The table renders as a two-column **name | first-line-summary**
   table (pandas/SciPy style) and toctrees each name into an auto-generated per-object
   stub under `docs/api-reference/generated/` (gitignored — regenerates at build).
   **Grouping conventions** (from the batch-1 review, applied across all pages):
   (a) **Don't mix kinds in one list** — separate the things you *call*
   (functions/constructors) from the *supporting types* they produce/consume, from
   *enumerations/aliases*. E.g. `events` = payload sections + "Supporting types"
   (`TabRef`, a value carried *inside* a payload) + "Enumerations" (`ChangeReason`…);
   `data` = "Query language" (`col`/`any_of`/`all_of`) vs "Query expression types"
   (`Column`/`Condition`/`SortKey`) vs "Type aliases" (`Record`/`Primitive`). A type
   that only appears *inside* another object (not handed to the user directly) is a
   supporting type, not a primary entry. (b) **Order sections most-reached-for first,
   lowest-level lookups last** — primary objects → common callables → their supporting
   types → feature areas → bare type aliases at the bottom (`data` order: Data sources
   → Query language → Query expression types → Readers and writers → Type aliases).
   (c) **Don't sub-section a small/uniform module** — follow the
   `bootstack.streams` model (intro prose + ONE `autosummary` table, no `---`
   sub-headings) whenever a module is just a few names of the same kind. Sub-section
   only when the surface is large OR genuinely mixes kinds (a). `streams`
   (`Stream`/`Handle`), `validation` (`ValidationRule`/`ValidationResult`),
   `scheduling` (`Schedule`/`Job`), `shortcuts` (3), and `errors` (5 exceptions) are
   all single-table; `data`/`events`/`style` earn their groups. The intro carries
   any rule-vs-result / base-vs-specific nuance — don't spend a heading on it.
   (d) **Order ENTRIES within a group ALPHABETICALLY** — the API Reference is the
   lookup layer, so within-group order should be predictable for scanning (the
   pandas/NumPy convention), NOT curated/common-first. Curated common-first order
   is the GUIDES' job (the `widgets/index.rst` caption toctrees keep it). The
   category grouping + a one-line lead-in already carry the semantics; clusters
   mostly stay adjacent alphabetically anyway (`Radio`/`RadioGroup`/`RadioToggleButton`,
   `Select`/`SelectButton`, `ToggleButton`/`ToggleGroup`). (e) The audit also
   surfaces half-public names to demote — e.g. `TraceOperation` (internal trace
   tag, no public signature exposes it) was dropped from `bootstack.signals.__all__`
   during this sweep.
4. List **exactly** the module's `__all__` across the grouped tables (the reference
   IS `__all__`). Good first-line docstrings matter — that line is the summary cell.
5. Wire the page into `docs/api-reference/index.rst`'s toctree.

Re-exported names (shallowest path wins): a name exported at two public paths gets
ONE stub, on the **shallowest** page (`Signal` → top-level `bootstack` page). Deeper
module pages list it in a **table-only** summary (no `:toctree:`, links up to the
stub) and own only their module-local names.

### Guide page recipe (the former `reference/*` prose pages)

A page like `docs/reference/data-sources.rst`. This is the teaching layer.
**Guiding principle: the API Reference is a LAST RESORT — the Guide carries the
practical teaching load** (generous worked examples, common compositions, recipes,
do/don't). A user should build real things from the Guide alone.

1. Prose intro → task-ordered usage sections (code blocks) → See also.
2. **No bottom `autoclass`** — instead end with an **"API reference"** section: a
   one-line pointer (`:doc:` link to the API Reference page) + an at-a-glance
   `.. autosummary::` table **WITHOUT `:toctree:`** (a table is NOT an object
   description, so it's not a second autodoc home; its links resolve to the stubs).
3. Cross-link types inline with roles (`:class:` / `:func:` / `:meth:` / `:data:`)
   at the **public home path** (`bootstack.data.SqliteDataSource`, not the impl path).
4. Inline usage only — NO separate Full Example file. Non-visual: NO screenshots.

### Verify (every stage)

Clean-build, always — incremental builds MASK warnings:
`rm -rf docs/_build && sphinx-build -b html docs docs/_build/html -W --keep-going`.
Build is warning-free; keep it there. Attribute-docstring rules (PR #106) still
apply (no `Attributes:`/`Args:` for dataclass fields; no colon on the first line of
an attribute docstring). A `-n` nitpicky build surfaces dangling cross-refs once a
home moves — fix the link or add a `nitpick_ignore_regex`.

---

## Reviewing a widget + docs standards (read first)

**Before any widget review or widget-docs work, read
`docs/_dev/widget-review-and-docs-standards.md`** — the consolidated checklist.
It is the single source of truth for both halves; the highlights:

- **A review is audit → fix → test → document → file follow-ups**, not a
  read-through. Audit the public wrapper vs `_impl` for correctness bugs AND
  unexposed capability. Recurring bug classes: value clamping (setters + re-clamp
  on range change), disabled state honored on *every* input path (incl. Home/End),
  event consistency (keyboard jumps commit like a drag-release), no Tab focus-trap.
  Then API hygiene (typed params, `on_*` payload audit, drop dead kwargs,
  live-vs-construction props). **File additive features / out-of-scope bugs as
  tracked issues — don't scope-creep the review branch.**
- **Docs: the Guide teaches; the API Reference is a last resort.** **Lead with the
  mental model** (foundational concept up front, not buried later). **No
  kitchen-sink — one idea per paragraph, scannable**, teach the decisions not every
  kwarg. Examples are **tight, API-verified, with the relevant import on first
  use** (and they must run). Use a `.. note::` for an **adjacent-but-distinct topic**
  (placed by the relevant screenshot, linking the other section) rather than inline
  prose — keep each topic its own section/TOC entry. Document the **Events** (change
  vs commit — public, not an impl detail) and **Keyboard** behavior of interactive
  widgets. **One screenshot per visually-distinct usage section**, not just the hero;
  a behavioral-only feature (e.g. step snapping) gets prose, no screenshot.
  Sentence-case section headers; Title Case page title.
- Verify: GUI test files run **one per process** (#150); `tests/test_public_surface.py`
  green; examples run; clean `-W` docs build; held for user test + per-commit approval.

## Widget documentation pattern (established — follow exactly)

> ⚠ **Migrating a widget = also clean up its public API** (the maintainer's
> standing pattern, memory `feedback_cleanup_api_while_documenting`). When you home
> a widget into the API Reference, audit it the way `App`/`AppShell`/`Window` were:
> drop dead/redundant kwargs, demote set-once config from runtime properties to
> construction-only (a property is "live" only if changing it has a complete effect
> a user would bind to a control), de-Tkinter leaks, fix docstring nits.
> **In particular, complete the typed-payload `on_*` audit for that widget** (memory
> `project_typed_event_payloads`, INCOMPLETE): a DATA event gets its specific
> `bootstack.events` payload type in `@overload` + impl signature; a NATIVE event
> (`click`/`hover`/`focus`/`blur`/`resize`) keeps `Event`. Known offenders: the
> boolean/selection controls (`Checkbox` etc.) still type `on_change`/`on_check`/…
> as generic `Callable[[Event]]`. (Payloads render in the autodoc "Overloads:"
> block, so fixing the source is enough.)

1. **Audit** — Explore agent comparing public wrapper vs `_impl/` internals.
2. **Fix wrapper** — typed params (`AccentToken`, the widget's own per-widget
   `variant` Literal, `WidgetDensity`);
   `@overload` event shorthands; no low-level color kwargs; layout via `**kwargs`
   + `_split_layout_kwargs`; catch-all must be `**kwargs` not `**extra_kw`.
3. **`docs/widgets/<widget>.rst`** (NOTE: was `docs/api/` — moved 2026-06-04) —
   intro sentence → hero screenshot → Usage sections (code block then screenshot)
   → Widget sizing include → See also → table-only `autosummary` API section +
   cross-links (NO bottom `autoclass`, per the Guide-page recipe) → Full Example
   literalinclude. No intro code block above hero.
4. **`docs/examples/<widget>.py`** — runnable visual-states-only demo. No
   `app.tk.after()`, no screenshot scaffolding, no `fill="x"` in RST snippets.
5. **`docs/screenshots/<widget>.py`** — SCENES dict. Each scene: own `bs.App`,
   tight `size=(W,H)`, `HStack(fill="x")` for button rows to avoid centering
   offset, `app.run()`. Hero for button/action widgets: single representative
   state with menu/popdown open if applicable.
6. **Screenshots:** `py -3.12 docs/scripts/take_screenshots.py <widget> [--scene X] [--light]`
   Outputs: `docs/_static/examples/<widget>-<scene>-light/dark.png`
7. **Wire** into the matching `:caption:` toctree in `docs/widgets/index.rst`
   (category landing pages are retired — captions group the widgets now).
8. **Commit** on a dedicated `feat/*`/`docs/*` branch.

### Screenshot image pattern

```rst
.. image:: /_static/examples/<widget>-<scene>-light.png
   :class: bs-screenshot-light
   :alt: <Widget> <scene> — light theme

.. image:: /_static/examples/<widget>-<scene>-dark.png
   :class: bs-screenshot-dark
   :alt: <Widget> <scene> — dark theme
```

Hero uses `-hero-light/dark.png`. Dialogs add `bs-dialog-screenshot` to the class
(e.g. `:class: bs-screenshot-light bs-dialog-screenshot`).
Margin/radius owned by `docs/_static/custom.css` — no inline styles.

### Widget sizing section pattern

```rst
Widget sizing
~~~~~~~~~~~~~

.. include:: ../shared/widget-sizing.rst
```

Path is file-relative from `docs/api/`. Omit from dialog pages.

---

