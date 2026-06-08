# Initiative — API Reference restructure (docs)

**Status:** Stage 1 (the `bootstack.data` prototype slice) MERGED (PR #107).
Stage 2 (recipe-lock) done on `feat/api-reference-stage2` — the templates + the
API-Reference-page / Guide-page recipes are now locked into `CLAUDE.md` under
"## API Reference & Guide page pattern". Stages 3–5 not started. Decided 2026-06-08
with the maintainer.

> `docs/_dev/` is excluded from the Sphinx build (`conf.py` `exclude_patterns`).
> This is a dev note, not a published page.

---

## The problem

The docs currently mix two incompatible jobs on the same pages:

1. **Narrative** — widget pages (`docs/widgets/*`) and subsystem pages
   (`docs/reference/*`) are prose-first: intro, screenshots, task-ordered usage,
   examples.
2. **API reference** — each of those pages ends with a hand-**curated**
   `.. autoclass:: ... :members:` block.

Consequences:

- There is **no traditional, complete, by-module API tree** anywhere. The
  closest is `getting-started/api-overview.rst`, which is a *namespace map*
  (names only), not a browsable reference. A Python dev who wants "everything on
  `SqliteDataSource`" or "what's in `bootstack.data`?" has no canonical home.
- The bottom-of-page `autoclass` is **curated** (hand-picked members), so the
  page view and any tree view would diverge.
- The tension is worst for the **non-widget subsystems** (data, signals, events,
  query DSL, theming): they are more API-shaped and less visual than widgets, so
  prose carries less of the weight and the missing tree hurts more.

MUI ("Components" + "Components API") and Ant Design (all-on-one-page) are both
**component-only**, so neither maps cleanly to a desktop framework that also has
data sources, signals, theming, scheduling, etc.

## The decision

Adopt a **Diátaxis-style split**: one narrative layer + one **unified, complete
API-reference layer** that mirrors the import tree. The narrative **links into**
the reference rather than re-documenting it.

Precedent (the audience's expectation): pandas / NumPy / SciPy (User Guide +
exhaustive by-module API reference), Flask (User's Guide + API Reference),
Django (topic guides + how-tos + reference) — the big multi-concern Python
frameworks all keep the API reference as its own pillar.

## Target structure (keep navbar at 5)

| Section | Role | Source |
|---|---|---|
| **Getting Started** | onboarding | as-is |
| **Widgets** | visual catalog — usage, screenshots, examples | as-is, but **drop the bottom `autoclass`**; cross-link to API Reference |
| **Guides** | task + topic narrative for subsystems | merge today's `tasks/` + the **prose** from today's `reference/` (theming, data, signals, events, validation, i18n, scheduling, store, shortcuts) |
| **API Reference** | **complete, by-module tree** — the new pillar | autosummary-generated, mirrors each submodule's `__all__` |
| **Production** | packaging etc. | as-is |

The current `reference/` section **dissolves**: its prose → **Guides**; its API
role → **API Reference**. `api-overview.rst` becomes the **landing page of API
Reference** (the map), drilling into per-module pages:

```
API Reference
  bootstack                 # App/AppShell/Window, widgets, Signal, dialog verbs, set_theme/toggle_theme
  bootstack.data            # SqliteDataSource/Memory/File, col, any_of/all_of, readers/writers
  bootstack.style           # Theme, get_theme/get_themes/get_theme_color, font verbs
  bootstack.events
  bootstack.signals
  bootstack.streams
  bootstack.validation
  bootstack.i18n
  bootstack.scheduling
  bootstack.shortcuts
  bootstack.store
  bootstack.errors
  bootstack.types
  bootstack.dialogs
```

Because the reference mirrors `__all__` exactly, the public structure becomes
self-documenting and stays in lockstep with `tests/test_public_surface.py`.

## THE load-bearing rule: one autodoc *home*

Every object may be the autodoc home in **exactly one place**. Two `autoclass`
directives for the same object = the "duplicate object description" warnings that
PR #106 just eliminated. So:

- **Move the autodoc home INTO API Reference** (full `:members:`).
- Widgets/Guides **cross-link in** with roles —
  `` :class:`bootstack.data.SqliteDataSource` ``, `` :func:`bootstack.data.col` ``
  — instead of re-documenting. Narrative pages keep their prose/usage/examples.
- **Optional best-of-both** (Django/pandas do this): a small `.. autosummary::`
  *table* (names + one-line summaries, linking into the reference) at the top or
  bottom of a narrative page, for at-a-glance members without leaving. This
  closes the gap with Ant's inline feel WITHOUT creating a second autodoc home
  (autosummary tables are not object descriptions).

## Tooling

Use `sphinx.ext.autosummary` (already enabled; `autosummary_generate = True`)
with `:toctree:` + `:recursive:` and class/module templates so every
class/function gets its own auto-generated page, grouped by module. This is the
pandas/numpy approach and is **lower** maintenance than today's hand-curated
`autoclass` blocks — the tree regenerates from the code.

- Per-module landing pages (`bootstack.data`, etc.) with autosummary tables that
  toctree into per-object stub pages.
- The top-level `bootstack` page has 50+ widgets — use autosummary tables
  grouped by category (Layout / Actions / Inputs / …), each linking to per-class
  stubs, rather than one giant `automodule`.
- Custom templates likely needed under `docs/_templates/autosummary/`
  (`class.rst`, `module.rst`) to control member curation (e.g. exclude inherited
  Tk noise, keep Google-style sections).

## Staged plan (discrete PRs)

1. **Prototype slice (FIRST DELIVERABLE, for maintainer review):**
   `bootstack.data` only. Build the API-Reference page(s) for the data module
   (autosummary tree + per-object stubs), strip the `autoclass` from
   `reference/data-sources.rst` and re-point it as a Guide that **cross-links**
   into the new reference, add the optional summary table. Wire a minimal "API
   Reference" toctree. Build warning-free. **Stop and get reaction before
   sweeping.**
2. **Lock the pattern** — fold review feedback into the autosummary templates +
   the page recipe; document the new "API Reference page" and "Guide page"
   patterns (replacing the curated-autoclass recipe in `CLAUDE.md`).
3. **Sweep subsystems** — move every `reference/*` page's autodoc home into API
   Reference; convert the prose pages into Guides; dissolve the `reference/`
   section.
4. **Sweep widgets** — drop the bottom `autoclass` from ~40 widget pages; add
   per-widget API entries under `bootstack` in API Reference; add summary tables.
   **See "Stage 4 detail — the widget page shape" below** for the category
   grouping, the widget-cluster handling, and the `__all__`-hygiene audit this
   stage doubles as.
5. **Nav re-cut** — `tasks/` + subsystem prose → **Guides**; new **API
   Reference** section; `api-overview.rst` becomes its landing page. Update
   `docs/index.rst` toctree and `conf.py` `show_nav_level`/captions as needed.

Each stage ends with a clean-build verification (below) and is its own PR.

## Stage 1 prototype — outcome (2026-06-08)

Built on `feat/api-reference-data-prototype`, clean-build warning-free
(non-nitpicky `-W`). Shipped:

- `docs/api-reference/index.rst` (section landing) + `docs/api-reference/data.rst`
  (the `bootstack.data` module page: grouped autosummary tables → 22
  auto-generated per-object stubs under `docs/api-reference/generated/`).
- `docs/_templates/autosummary/class.rst` — one custom class template:
  `:members: :inherited-members: :show-inheritance:`. `:inherited-members:` is
  what makes concrete-source pages complete — `SqliteDataSource` shows inherited
  `save`/`on_change`/`observe`/`export_csv`/`reload` alongside its own methods,
  and (verified) the Protocol page stays clean (no `_private`/dunder/Generic
  leak) because `undoc-members: False` + no `:special-members:` filter it.
- `reference/data-sources.rst` re-pointed: curated `autoclass` block removed,
  replaced with a cross-link to `/api-reference/data` + an at-a-glance
  `autosummary` table WITHOUT `:toctree:` (a table only — NOT a second autodoc
  home; links resolve to the stubs).
- `docs/api-reference/generated/` gitignored (stubs regenerate at build time).
- Root toctree gained `api-reference/index` → navbar is temporarily **6** items;
  Stage 5 re-cut returns it to 5 by dissolving `reference/` into Guides + API
  Reference.

Templates/recipe LOCKED in Stage 2: the `class.rst` template above works unchanged
for plain classes, dataclasses (`FileSourceConfig`), and Protocols. **Stage 2 also
added `function.rst` + `data.rst`** — NOT for completeness (the built-in fallbacks
documented the objects fine) but to fix a **sidebar-title inconsistency**: the
sidebar shows each stub's page title, and the built-in `function.rst`/`base.rst`
fallbacks title with the full dotted path (`bootstack.data.col`) while our custom
`class.rst` titles bare (`MemoryDataSource`) — so functions/aliases rendered
fully-qualified next to bare classes. All three custom templates now title with the
bare `{{ objname }}`. Type aliases split across templates by how autosummary
classifies them (`Primitive` → class-like → `class.rst`; `Record` → data →
`data.rst`), so both must title bare. Any future documenter kind (`exception.rst`,
`method.rst`, …) needs the same bare-title treatment.

## Stage 4 detail — the widget page shape

The widget API reference is NOT ~40 separate module pages. It is the **single
top-level `bootstack` module page** (same role `data.rst` plays), but because
the top-level surface is large (85 names: 68 classes, 15 functions — see
`tests/test_public_surface.py`) it uses **autosummary tables grouped by
category**, each entry linking to a per-class stub. Categories mirror the
widget-guide caption groups:

Resolved category map (accounts for all 85 `__all__` names; companions shown
indented only to mark the cluster — they render as flat siblings). **`AppShell`
lives under Application, NOT Navigation** (it is a top-level app shell, not a nav
control — decided 2026-06-08; the Widgets caption toctree should move it too):

```
bootstack
├─ Application       App · AppShell · Window
├─ State             Signal
│
├─ Actions           Button · ButtonGroup
├─ Inputs            TextField · PasswordField · NumberField · SpinnerField ·
│                    PathField · Slider · RangeSlider · TextArea · CodeEditor ·
│                    DateField · TimeField
├─ Selection         Checkbox · Switch · ToggleButton · ToggleGroup ·
│                    RadioGroup [Radio · RadioToggleButton] · Select ·
│                    SelectButton · Calendar
├─ Data Display      Label · Badge · ProgressBar · Gauge · ListView ·
│                    DataTable [EditFilter? · EditorType?] · Tree [TreeNode]
├─ Layout            Separator · Card · GroupBox · VStack · HStack · Grid ·
│                    ScrollView · Accordion [AccordionSection] · SplitView [SplitPane]
├─ Menus & Toolbars  Toolbar · MenuButton · MenuBar · ContextMenu [ContextMenuItem]
├─ Navigation        PageStack [StackPage] · Tabs [TabPage] ·
│                    SideNav [SideNavGroup · SideNavHeader · SideNavItem · SideNavSeparator]
├─ Overlays          Tooltip · Toast
├─ Forms             Form [FormItem · FieldItem · GroupItem · TabsItem · TabItem]
│
├─ Dialogs  (verbs)  alert · confirm · toast · ask_string · ask_integer ·
│                    ask_float · ask_date · ask_date_range · ask_color ·
│                    ask_font · ask_item · ask_filter
└─ Theme    (verbs)  set_theme · toggle_theme
```

Most widgets are a single stub (one widget → one page). The exceptions are
**widget clusters** — a parent widget plus companion classes that are ALSO in
the top-level `__all__`. They render as **flat adjacent siblings within the same
category group** (no nesting); each gets its own stub. The legibility lever is
ordering + a one-line group lead-in (companions listed right after their parent).
Known clusters (from `__all__`, 2026-06-08):

| Widget | Companion classes (also top-level public) |
|---|---|
| `Tree` | `TreeNode` |
| `SideNav` | `SideNavGroup`, `SideNavHeader`, `SideNavItem`, `SideNavSeparator` |
| `Form` | `FormItem`, `FieldItem`, `GroupItem`, `TabsItem`, `TabItem` |
| `RadioGroup` | `Radio`, `RadioToggleButton` |
| `Accordion` | `AccordionSection` |
| `Tabs` | `TabPage` |
| `PageStack` | `StackPage` |
| `SplitView` | `SplitPane` |
| `ContextMenu` | `ContextMenuItem` |

Deliberately NOT on the widget page (cross-linked from their own module instead,
documented once):
- **Event payloads** (`ChangeEvent`, `SliderEvent`, `RowsEvent`, …) → live in
  the `bootstack.events` reference page; a widget guide's "what `on_change`
  hands you" is a `:class:` link into events.
- **Token/keyword types** (`AccentToken`, `WidgetDensity`, …) → `bootstack.types`.

The widget GUIDE (`widgets/<w>.rst`) keeps its screenshots/usage/examples, drops
its bottom `autoclass`, and its summary table lists the whole cluster (e.g.
`tree.rst` → `Tree` + `TreeNode`).

### Stage 4 doubles as an `__all__`-hygiene audit

Because the reference renders **exactly** `__all__`, the sweep surfaces every
half-public type. First case already found: **`ColumnSpec`** (`DataTable`'s
primary column-config object) is a `TypedDict` in `widgets/datatable.py` that is
in **no `__all__`** — not top-level, not `bootstack.types` — yet `datatable.rst`
documents it heavily. So it currently has **no reference home**. Per-case
decision the sweep must make:

- **Promote** to a public home (lean: `bootstack.types` for config TypedDicts, or
  expose as a `DataTable` companion in top-level `__all__`) — then it gets a stub
  and the guide can `:class:`-link it; **or**
- **Leave guide-only** — then the guide must NOT `:class:`-link it (a `-n`
  nitpicky build flags the dangling xref).

Recommendation: promote the compose-surface config types (`ColumnSpec` and any
siblings the audit turns up). Settle each case in Stage 4, not before. Keep
`tests/test_public_surface.py` in lockstep with whatever is promoted.

Also-flagged, same bucket: **`EditFilter`** and **`EditorType`** are both in the
top-level `__all__` but have no natural widget category (both are
DataTable/filter companions). The audit must decide whether they are genuine
compose-surface (place them, likely near DataTable) or should be demoted.

### Re-exports: shallowest path wins (the "one home" rule for duplicated names)

Several objects are exported at more than one public path — `Signal` is in BOTH
`bootstack.__all__` and `bootstack.signals.__all__`; likewise widgets re-exported
from `bootstack.widgets`. The single autodoc home is the **shallowest public
path**: `Signal`'s stub lives on the top-level `bootstack` page (State), and the
`bootstack.signals` page lists it in a **table-only** summary (no `:toctree:`,
links UP to the top-level stub — the same trick the data Guide uses) while owning
the signals-only names (`TraceOperation`, …). Apply this uniformly in the Stage 3
subsystem sweep so a re-exported name is never documented twice.

### Presentation — the grouped links must read as tables, not a wall of links

CONCERN raised 2026-06-08: a category with 11 entries must not render as an
unreadable block of hyperlinks. It does not — `.. autosummary::` renders a
**two-column table: linked name | first-line docstring summary**, exactly the
pandas/SciPy reference style. The Stage 1 prototype already proves this in-repo —
see the rendered `docs/_build/html/api-reference/data.html` (e.g.
`SqliteDataSource | SQLite-backed data manager with pagination, filtering, …`).

Precedent to mirror for the big `bootstack` page (one large namespace, many
objects, sectioned): **SciPy module pages** — `scipy.stats`, `scipy.signal` —
which chunk ~100 functions into labeled sections, each a prose lead-in + an
autosummary name/summary table. (pandas' per-object reference pages, e.g.
`DataFrame`, do the same with method groups.)

Readability levers, all already available:
- `:nosignatures:` on each `autosummary` → compact rows (name + summary only).
- A one-sentence prose lead-in before each category table (SciPy pattern; the
  prototype's "Query language"/"Readers and writers" lead-ins are the model).
- The category headers chunk the page and populate the right-sidebar page-TOC
  (`secondary_sidebar_items: ["page-toc"]`), so a reader jumps by category.
- DEPENDS ON good first-line docstrings: the summary column is the object's
  docstring first line. Widget classes all have one; the audit gap is type
  aliases (`Record`/`Primitive` render a blank summary cell). The sweep should
  ensure every newly-homed object has a one-line summary, or accept the blank.

### Follow-on (post-migration) — enrich the widget Guides

**Guiding principle: the API Reference is a last resort.** The Guides must carry
essentially all of the *practical* teaching load — a user should be able to build
real things from the Guides alone and only drop to the API Reference for an
exhaustive-lookup edge case (the one method the Guide didn't cover, an exact
signature, the full member list). The reference exists to *guarantee
completeness*, not to be the primary path. If a user routinely has to leave a
Guide for the reference to get something done, the Guide is underwritten.

This is the *payoff* of the split, and an explicit deliverable AFTER the
structural sweep (its own pass/PR, not blocking the migration). Once each widget
page is a pure Guide — the long API surface lifted out into the reference, no
bottom `autoclass` competing for the page — the Guide is free to be generous.
So the widget pages should be **fleshed out with far more examples and usage
patterns** than today: multiple worked snippets per feature, common compositions
("X inside a Form", "X bound to a Signal/DataSource"), recipes, and do/don't
guidance. Completeness is no longer the page's job (the reference guarantees it),
so the page can spend all its room on *teaching how to use the widget well* — to
the point that reaching for the reference is the exception.

Keep the established widget-page pattern (intro → hero → usage sections with
screenshots → Widget sizing → See also → cross-link/summary-table into the
reference), but treat the example density as a feature, not a budget. Applies
first to widget Guides; the subsystem Guides (former `reference/*` prose) benefit
the same way. Ties into the existing "Reference docs examples" carryover and the
`project_docs_initiative` memory.

## Gotchas / guardrails

- **Clean-build to verify, always.** Incremental Sphinx builds MASK warnings.
  `rm -rf docs/_build && sphinx-build -b html docs docs/_build/html -W
  --keep-going`. The build is currently warning-free (PR #106) — keep it there.
- **`__all__` IS the reference now.** Member hygiene and `__all__` accuracy
  directly determine reference quality. `tests/test_public_surface.py` already
  guards the surface; the reference should render the same shape.
- **No duplicate autodoc home** (see the load-bearing rule). This is the single
  easiest way to reintroduce the warnings we just removed.
- **Attribute-docstring rules still apply** (from PR #106): no `Attributes:`/
  `Args:` block for dataclass fields; **no colon on the first line** of an
  attribute docstring (napoleon mangles the rendered `:type:`).
- **Cross-ref hygiene** — `conf.py` already has `nitpick_ignore_regex` for
  stdlib/typing/Tk/private names; a `-n` nitpicky build will surface narrative
  pages whose cross-refs don't resolve once the home moves. Expect to add a few
  ignores or fix links.
- **No Tkinter leakage** — the reference will now expose *complete* public
  members; double-check nothing internal/Tk-typed sneaks into a public `__all__`
  (the style-accessor demotion in PR #106 was exactly this class of issue).
- **Screenshots stay on widget pages** — the API Reference is text-only
  (no hero images), like the current `reference/` page pattern.

## First task for the next session

Read this brief, then build **stage 1 (the `bootstack.data` prototype slice)**
and present it warning-free for maintainer review. Do NOT proceed to the full
sweep until the prototype is approved.
