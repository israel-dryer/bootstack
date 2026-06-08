# bootstack — Claude Handoff

## Project overview

bootstack is a batteries-included Python desktop UI framework. It is **not**
advertised as a Tkinter wrapper — the goal is to abstract Tkinter away entirely
so that Tkinter's warts, naming conventions, and legacy API are invisible to the
user. Widget names, arguments, methods, and events are designed for modern Python
and ease of use, not compatibility with the raw tk/ttk surface.

**Design philosophy:** Opinionated and configurable within a reasonable range.
Go from nothing to something fast. The user should never need to `import tkinter`.

**Working directory:** `D:\Development\bootstack`
**Branch strategy:** `feat/*` branches off `main`. PRs go `feat/*` → `main`.

---

## Recently completed (all merged to `main`)

Listed as pointers only — these shipped and live in code, docs, and the linked
memories (see them for rationale and gotchas).

- **Unified data bag** (PR #92) — undisplayed / non-scalar fields are carried
  across Tree, DataTable, ListView; SQLite stores non-scalars in a hidden
  `_bs_data` JSON column; `bs.SerializationError` for non-JSON values on
  persistent sources. Memory `project_data_bag`.
- **Large-file streaming** (PRs #93–#96) — streaming chunked `load()`; pluggable
  reader/writer registries (`data/readers.py`, `data/writers.py`:
  CSV/TSV/JSON/JSONL/XML built in; Parquet/Feather/HDF5 via `bootstack[parquet]` /
  `[hdf5]`); `FileDataSource` rebuilt to ingest a file into a SQLite working store
  (temp / `cache=` / `:memory:`; `close()` + context-manager + finalizer cleanup;
  mtime cache); source `save()` + DataTable `export_formats`. Memory
  `project_file_source_streaming`. **Deferred:** background/progressive ingest,
  keyset pagination, auto-index on sorted/filtered columns.
- **Tree public-API modernization** (PR #91) — recycle-view canvas Tree with
  `TreeNode` handles (icon + label rows). Memories `project_tree_row_model`,
  `reference_listrow_button_focus_stick`, `reference_treeview_perrow_indicator_state`.
- **Icon rendering + DataTable polish** — ink-metric icon renderer; `Table`→
  `DataTable` rename + DataSource decoupling. Memories `project_icon_rendering`,
  `project_table_datasource_coupling`.
- **Docs + public API audit, typed events, theming/font tracks, DataSource
  observable query + verb rename** — see "Prior initiative" below and the
  `project_*` memories.
- **Tree data-source backing** (branch `feat/tree-datasource`, awaiting merge) —
  `Tree(
  data_source=src, parent_field="parent_id", root_value=None, label_field=,
  icon_field=, node_builder=, order=)` projects a FLAT adjacency-list source as a
  lazy hierarchy: auto-generated per-node `loader`s issue
  `src._query(col(parent_field)==id, ...)` on expand (uses `_query`, not
  `where()`, so view state is undisturbed). Record→node = fields + optional
  `node_builder`; chevrons via a batched has-children `IN(...)` query per expand;
  `data_source` property + `refresh()`. Impl in
  `widgets/_impl/composites/tree/source_binding.py`. Mutually exclusive with
  `nodes=`. Memory `project_tree_datasource_backing`. **Deferred:** per-node child
  pagination, tree filtering, auto-refresh on `on_change`, native
  `TreeDataSourceProtocol`, Tree widget doc page. **Found (not fixed):** latent
  `SqliteDataSource` TEXT-affinity bug — a column whose FIRST row value is NULL
  gets TEXT affinity, so int values store as strings (worked around in the binding
  by string-normalizing the has-children key comparison).

## Next up — candidates (pick one)

- **SqliteDataSource schema inference** — fix the TEXT-affinity-from-leading-NULL
  bug surfaced by Tree backing (infer a column's type by scanning more than the
  first row, or accept explicit dtypes). General correctness win for the
  data-science/engineering audience; see `project_tree_datasource_backing`.
- **Persistent KV / prefs store** (`bs.Store`) — memory `project_persistent_kv_store`.
- **Deferred file-streaming items** — background/progressive ingest, keyset
  pagination, auto-index (memory `project_file_source_streaming`).
- **Signal runtime-cleanup pass** — memory `project_signal_api_audit_findings`.

---

## Prior initiative — Sphinx docs + public API audit (MERGED)

**Branch:** `feat/docs-api-improvements` (merged to `main`)

### Docs structure (RESOLVED 2026-06-04, committed b7625f36 + follow-ups)

Top-level sections (pydata horizontal navbar — keep this set SMALL, ~5):
**Getting Started · Tasks · Widgets · Reference · Production**.

- **`docs/widgets/`** — every widget as a flat leaf page. Grouping is done with
  **caption toctrees** in `widgets/index.rst` (one `.. toctree:: :caption: <Group>`
  per group, listing widget pages directly). The 10 old category landing pages
  (`actions.rst`, `inputs.rst`, …) were RETIRED — captions replace them. Curated
  (common-first) order within groups, NOT alphabetical.
- **`docs/reference/`** — framework primitives: theming, typography, signals,
  events, validation, data-sources, shortcuts, scheduling. Flat (no captions).
- **`docs/api/` and `docs/deeper/` are GONE.** typography moved into reference/.
- `show_nav_level: 2` (conf.py) renders the caption groups as sidebar headers.
- Sections are **flat by default**; add caption toctrees only when a section
  needs internal organization (e.g. if Common Tasks grows).
- Do NOT promote widget groups to top-level — ~14 navbar items overflow pydata.

**Reference page pattern** (distinct from widgets — non-visual, NO screenshots):
prose intro → task-ordered usage sections (code blocks) → See also → curated
`autoclass`. **Inline usage only — NO separate "Full Example" / `docs/examples/<topic>.py`
for reference pages** (decided 2026-06-05; widget pages DO keep their Full Example).
When dropping a Full Example, make sure the inline usage covers the same patterns
(memory `feedback_reference_page_examples`). The **API reference section is FLAT** —
no `~~~` sub-group headers (the sidebar is narrow); use a prose lead-in to group.
Autoclass at the **PUBLIC home path** (`bootstack.signals.Signal`, NOT
`signals.signal.Signal`); `:members:`, curating internal members with
`:exclude-members:` where needed. Single backticks, Google style.
**Exemplars: `docs/reference/signals.rst`, `docs/reference/events.rst`.**

DONE to this pattern (2026-06-05): signals, events, streams, scheduling,
shortcuts, validation, data-sources, **theming**; errors already fine. **PARKED:
typography** (blocked on the font track — see Track 2). Docs build is
warning-free (0).

**Theming public API — DONE (2026-06-05, this branch, Phases 1–4).** New public
`bs.Theme` (`style/theme.py`): keyword ctor, `base=` inheritance, `from_dict`/
`to_dict`, `install(activate=)`. All 14 built-ins converted JSON → Python
`Theme` instances in `style/themes/` (auto-installed; deleted `assets/themes/`
JSON + `importlib` loading = the PyInstaller fix). Removed `register_user_theme`
+ CLI `add theme` + the whole `list` command. Demoted `Style`/`Typography`/`Font`
from the public API (still importable from their modules). `theming.rst`
rewritten; `ask_font`→`tkinter.font.Font` leak flagged for the font track.
Deferred: font track (Phase 2-fonts) + `typography.rst`, and the visual theme
builder (near-ship). See memory `project_theming_public_api`.

**No Tkinter in docs or docstrings** — no `tk.*` types or Tkinter terms unless
strictly necessary; don't feature escape-hatch interop. A full docstring scrub of
`src/` is still pending. DONE so far: `signals/signal.py`, `streams/_stream.py`,
and the public widget wrappers swept this session (`GroupBox`/`Tree` ttk names,
`CodeEditor` now defaults `font='code'` not `'TkFixedFont'`). LEFT BY DESIGN:
`.tk`/`.var` escape-hatch property docstrings, `signals/integration.py` (the Tk
bridge). FONT-TRACK leaks still flagged: `ask_font`/`FontDialog` `default_font`
accepts Tk font names + `ask_font` returns `tkinter.font.Font` (NOTE(font-track)
in `widgets/dialogs.py`).

### Status

**Done** (wrapper ✓ · doc page ✓ · example ✓ · screenshots ✓):
- Actions: Button, ButtonGroup
- Inputs: TextField, PasswordField, NumberField, Slider, RangeSlider,
  PathField, SpinnerField, TextArea, CodeEditor, DateField, TimeField
- Selection: Checkbox, Select, Switch, ToggleButton, RadioGroup, ToggleGroup,
  SelectButton, Calendar
- Data Display: Label, Badge, ProgressBar, Gauge, ListView, **DataTable**
  (renamed from `Table`), **Tree** (rebuilt as a recycle-view; icon+label rows)
- Layout: Separator, Card, GroupBox, VStack, HStack, Grid, Accordion,
  ScrollView, SplitView
- Menus and Toolbars: Toolbar, MenuButton, ContextMenu
- Navigation: PageStack, Tabs, SideNav, AppShell
- Overlays: Tooltip, Toast
- Dialogs: 7 pages (message, input, color, font, filter, dialog, formdialog)
- Forms

**Pending:**
- (none) — Tree is DONE (see "Current initiative — Tree public-API
  modernization"); `git push` the branch.
- Actions: DropdownButton is internal (public face is MenuButton — no separate page needed)

### Table — DONE (branch `feat/public-table`, this initiative)

Full public Table: sorting, search, column filters, grouping, paging, inline
editing (form dialogs), two-tier export (materialized + streaming/async), live
data binding. Highlights from this branch:
- **Selection checkboxes** — `show_selection_controls=True` shows a per-row
  checkbox in `#0` (multi only); accent-filled checked / muted-outline unchecked
  (icons baked at `_MARKER_ICON_SIZE=20`, unscaled for crispness). Visible
  checkboxes flip selection to **click-to-toggle** (checklist UX, no Ctrl/Shift).
  Single-select shows no marker (the row wash suffices).
- **Grouping restructure** — the native tree indicator was **removed from the
  shared `{style}.Item` layout** (`style/builders/treeview.py`, now `[image,
  iconspacer, text]`); group expand/collapse uses a **custom chevron image** on
  group-header rows (swap on click + `<<TreeviewOpen/Close>>`; toggle target =
  any row with children). Grouped view promotes the **first non-group column into
  `#0`** so children nest under the header (leaf rows get a transparent
  placeholder to preserve the depth indent); the group-by column drops out of the
  value columns; `#0` has no heading. (NOTE: this regressed `bs.Tree`'s native
  indicator. Tree will NOT use a custom indicator-element — that state path is
  broken on Tk 8.6.15; it composites `[chevron][icon]` into the item image slot
  instead. See "Next initiative — Tree public-API modernization".)
- **Cell `format`** — `ColumnSpec` gains `format` (a format-spec string or a
  callable), display-only (sort/filter/edit/export use the raw value).
- **Stable row identity** — `id_field` (default `"id"`): a record's own `id`
  becomes the row identity (sources adopt it; `bs.DuplicateIdError` on dup /
  non-int auto-insert). Both Sqlite + Memory sources aligned.
- **Events** — batch CRUD/move events renamed **plural present tense**:
  `on_rows_insert`/`on_rows_update`/`on_rows_delete`/`on_rows_move` (carry a
  `RowsEvent`, fire **once per call** — `insert_rows(6000)` = 1 event).
  Single-row stays singular (`on_row_click`/`_double_click`/`_right_click`).
  Double-click a row opens the editor when `allow_edit`.
- **Docs** — comprehensive `widgets/table.rst` (full `ColumnSpec` reference,
  `format`, `id_field`, event cross-refs, all features); `ExportEvent` +
  `DuplicateIdError` added to the reference pages.
- **DataSource coupling — RESOLVED** (branch `feat/table-datasource-decouple`):
  the table no longer reads Sqlite-internal columns. Identity/selection route
  through protocol-level `_record_id`/`_public_record`/`_internal_fields`
  (defaults on `BaseDataSource`, overrides on `SqliteDataSource` +
  `MemoryDataSource`), so any `DataSourceProtocol` source works and `select_rows`
  round-trips. Same branch: `Table`→`DataTable` rename, `density=` exposed,
  built-in `show_border` removed (wrap in a `Card`/`Frame`), footer separator.

### Cross-cutting wrapper improvements (this + prior sessions)
- `commit()` and `set_cursor()` removed from all field widgets (TextField,
  PasswordField, NumberField, PathField, SpinnerField) — internal plumbing
- `placeholder` property removed from TextField, PasswordField, PathField —
  constructor-only concern
- `trigger=` param removed from `validate()` on all 8 field wrappers —
  internal routing concern, callers are always doing a manual check
- All field wrappers now have full event parity: 8 shorthands, typed tokens
- `TextArea.width=` added (was missing; internal hardcoded default)
- `CodeEditor.height=` added (was hardcoded to 20; now configurable)
- `LineNumbers` sidebar height bug fixed — no longer overrides `height=`
- `TextArea` critical bugs fixed: `<<Change>>` vs `<<Changed>>` event name,
  undefined `inner_sequences` in `on()` (crash), `text_signal` → `textsignal`
- `CodeEditor`: `text_signal` → `textsignal`, removed `disabled` alias,
  cleaned up inline imports, added `signal` property
- DateField calendar picker right-aligns to button side; `position_anchored`
  now uses actual rendered size (`winfo_width`) for widget anchors
- **SideNav compact mode**: selection indicator bar now matches fill color
  (invisible) instead of accent color. `SideNavItem.set_compact()` rebuilds
  the frame style via `configure_style_options(icon_only=) + rebuild_style()`.
- **`AppShell.on_page_change`** bug fixed: was binding `<<PageChanged>>`
  (never fired) — corrected to `<<PageChange>>`.
- **`Tabs.item()` / `items()`** bug fixed: were calling non-existent
  `TabView.item/items` — corrected to `tab()` / `tabs()`.
- **`TabView`** now forwards `<<TabAdd>>` and `<<TabClose>>` to itself so
  the public wrapper needs no private `_tabs` access for event routing.
- **`PublicWidgetBase.emit`** simplified: now wraps `event_generate(data=data)`
  directly — `_bs_emit_data` side-channel removed.
- **`ContextMenu`**: `ValueError` on unknown `trigger=`; `add_items()` type
  hint broadened to `list[ContextMenuItem | dict[str, Any]]`.
- **`AppShell.mainloop`** alias removed from public API.
- **`Tabs.items()` / `PageStack.items()`** return type fixed to `tuple[Any, ...]`.
- **`RangeSliderEvent` / `RangeSliderCommitEvent`** payload attrs renamed to
  snake_case: `lovalue`/`hivalue`/`prev_lovalue`/`prev_hivalue` →
  `low_value`/`high_value`/`prev_low_value`/`prev_high_value` (matches the
  wrapper's `low_value`/`high_value` props). Internal RangeSlider widget still
  uses `lovalue`/`hivalue` internally — separate cleanup.

### Event system redesign — DONE (2026-06-05, commits 40a4495d…56d09d59)

Unpacked typed payloads + curated `Event`; `bootstack.events` is the catalog
(memory `project_typed_events`). Data-carrying handlers get the payload dataclass
DIRECTLY (`on_change(lambda e: e.value)`); native handlers get a curated, Tk-free
`Event` (modifier bools `ctrl/shift/alt/meta`, clean `key/char`, no
state/serial/keysym_num). The transform lives in `adapt_handler()` at the public
`on()` boundary (`widgets/_core/base.py`) — `_runtime/events.py` was left
UNTOUCHED (confirmed). Payloads are namespaced in `bs.events` ONLY (not
top-level). ListView keeps dict record payloads (dynamic records). GUI tests:
`tests/widgets/public/test_slider_events.py`. (Note: slider virtual events only
deliver to a MAPPED widget — show the window in tests.)

### Next session — Track 2 + queued refactors (all memory-tracked)

**RECOMMENDED NEXT: pick from the queued refactors below — the DataSource
observable query (item 0) is now DONE.** Font track and the DataSource verb
rename + filtering DSL were already DONE.

0. **DataSource change broadcasting / observable query — DONE (this branch,
   memory `project_datasource_change_events`).** Both layers shipped: `_ChangeHub`
   (`data/_observable.py`) + `bs.events.DataChangeEvent`; `ds.on_change(handler=None)`
   → Subscription/`Stream`, `ds.observe(condition, *order)` → live result-set
   `Stream`; read-only `_query()` per source; thread-marshal (worker → main via
   `app.after`) + coalescing (`after_idle`, one flush/turn) + headless sync-degrade
   + re-entrancy guards. `silence()` is THREAD-LOCAL. Table/ListView auto-refresh
   (refetch visible window via `page`/`page_slice`, NOT observe) with ALL internal
   source mutations silenced (TableView silences where/order too — revised policy).
   ListView `_on_source_change` re-measures (resizes the virtual row pool +
   scrollbar). Tests `tests/data/test_observable.py`; docs `data-sources.rst`
   ("Observing changes"); example `docs/examples/observable_datasource.py`.
   DEFERRED perf opts (relevance-skip, content-hash signature, count cache,
   `observe_count`) noted in memory — gated by the observe-small/on_change-large
   routing contract (now documented + enforced by the widgets).

1. **Track 2 — theming public API + font track: DONE.** Theming Phases 1–4
   (memory `project_theming_public_api`) and the **font track** (Phase 2-fonts —
   `bs.set_font_family`/`update_font_token`/`get_font_families`, Tk-free
   `FontChoice`, fixed the `use_fonts(fallback=True)` bug, `typography.rst`
   written) both COMMITTED (font track commit `250b3d41`). REMAINS only the
   **visual theme builder (Phase 5)** — deferred until near-ship; emits
   `bs.Theme(...)` code (CodeEditor + file). Do NOT build yet.
2. **DataSource verb rename + filtering DSL: DONE** (UNCOMMITTED until this
   session's commit; memory `project_datasource_api_naming`). Verbs:
   `load`/`page`/`page_slice`/`insert`/`get`/`update`/`delete`/`move`/`select`/
   `deselect`/`selected`, `count`/`selected_count` (properties), `export_csv`.
   `set_filter`/`set_sort` → **`where(condition)`/`order(*keys)`** with a Tk/SQL-
   free `col` expression DSL (`data/query.py`: `col`, `is_in`, `contains`/etc.,
   `&`/`|`/`~`, `all_of`/`any_of`; parameterized SQL, injection-safe). Dropped the
   Table "SQL" search mode; fixed `FormDialog(master=)`→`parent=`. Also docs-config
   cleanup (removed `viewcode`, `html_show_sourcelink`/`copy_source` off,
   `_templates/sidebar-nav-bs.html` drops the "Section Navigation" header).
3. **Persistent KV / prefs store** (proposed, memory `project_persistent_kv_store`):
   no public persistent K-V exists (`MemoryDataSource`=RAM, `SqliteDataSource`=
   record-oriented, `AppSettings`=window-geometry-only despite its name). Propose
   `bs.Store` (dict-like, file-backed). Ties into theme persistence.

**Signal API — DECIDED (prior session):** `signal()` is the single getter,
`.set()` writes, `.get()` deprecated (doc-excluded). Do NOT adopt callable-setter
`signal(x)`.

**Carryover (lower priority):**
1. **Index/landing pages** — root `index.rst`, `widgets/index.rst`,
   `reference/index.rst`, section indexes are bare; add orientation/gallery.
2. **Signal runtime-cleanup pass** — memory `project_signal_api_audit_findings`
   (remove `.get()` + `__getattr__` proxy; `set()` numeric widening; silent
   swallow in `subscribe(immediate=)`).
3. **Tree/Table doc pages** (deferred — complex). DataSource rename should land first.
4. **localization / windowing** `tasks/` how-tos.
5. **Screenshots pending:** Tooltip/Toast, 7 Dialog pages.
6. **AppShell deferred improvements:** `nav_pane_width=` not wired to
   `SideNav(pane_width=)`; nav density/font hardcoded; `toolbar`/`nav` expose
   internals; group active-child highlight + indentation; footer non-page widgets.

### API/cleanup backlog from the 2026-06-05 audit (memory-tracked)
- `project_toplevel_api_surface` — audit `bs.*` vs namespaced (events: DONE,
  payloads live in `bs.events` only).
- `project_capabilities_relevance` — `_core/capabilities` may be redundant now
  the public layer abstracts Tk; still imported by data/i18n/mixins.
- `project_legacy_naming_cleanup` — `TTKBootstrapError` (`_core/exceptions`,
  overlaps `bootstack.errors`) + pervasive `bootstyle`/`Bootstyle` in `style/`.
- `project_docstring_backticks` — ~77 files use RST double-backticks; convention
  is Google + SINGLE backticks. (Markdown ```fences``` in docstrings render
  broken via autodoc — fixed in `data/` + `_runtime/shortcuts.py`; others remain.)
- Past-tense event names still pending rename: `SideNav.on_pane_toggled` /
  `on_display_mode_changed`, `ListView.on_selection_changed`,
  `Calendar.on_date_selected` (memory `project_event_naming_revisit`).

---

## Widget documentation pattern (established — follow exactly)

1. **Audit** — Explore agent comparing public wrapper vs `_impl/` internals.
2. **Fix wrapper** — typed params (`AccentToken`, `VariantToken`, `WidgetDensity`);
   `@overload` event shorthands; no low-level color kwargs; layout via `**kwargs`
   + `_split_layout_kwargs`; catch-all must be `**kwargs` not `**extra_kw`.
3. **`docs/widgets/<widget>.rst`** (NOTE: was `docs/api/` — moved 2026-06-04) —
   intro sentence → hero screenshot → Usage sections (code block then screenshot)
   → Widget sizing include → See also → API autoclass → Full Example
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
8. **Commit** on `feat/docs-api-improvements`.

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

## Gotchas

### Layout and wrappers
- **Self-placement via `**kwargs`** — `fill`, `expand`, `anchor`, `row`, `column` etc.
  are NOT explicit params. Route through `self._split_layout_kwargs(kwargs)`.
- **`**kwargs` not `**extra_kw`** — catch-all must be named `**kwargs` throughout.
- **`**kwargs` override protection** — when merging user kwargs into `internal_kwargs`,
  filter out reserved keys so explicit constructor params can't be silently overridden.
  Pattern: `_RESERVED_INTERNAL_KEYS = frozenset({...})` then skip collisions.
- **`margin_x=` / `margin_y=`** — axis-specific external spacing. Never `padx=`/`pady=`.
- **`.. include::` path is file-relative** — from `docs/api/`, use `../shared/widget-sizing.rst`.

### Screenshots
- **HStack centering** — App's VStack centers children. For button-row scenes, wrap in
  `HStack(fill="x")` so buttons are left-aligned, not centered with dead space on the left.
- **No `size=` by default** — omit `size=` from `bs.App` in screenshot scenes unless there
  is a specific reason (popdown/dropdown needs room to render inside the capture bbox). Let
  the window auto-fit its content. For input/field/slider rows use `minsize=(720, 1)` to
  enforce a minimum width without locking height. Never add `size=` just to "feel right".
- **Popdown menus in screenshots** — runner sets app `topmost=True` at t=800ms, grabs at
  t=950ms. Call `mb.show_menu()` at t=850ms (after topmost set, before grab). Size the
  app window tall enough to contain the menu within its capture bbox — the menu Toplevel
  is captured via `ImageGrab.grab(bbox=app_region)` which is a screen grab, not a window
  grab.
- **`_ToplevelContextMenu` topmost** — `show()` now sets `-topmost True` on the
  overrideredirect Toplevel so it appears above a parent with `-topmost True`.
- **SelectBox popup topmost** — `_create_popup_toplevel` sets `-topmost True` so the
  popup appears above the screenshot runner's topmost window.
- **Screenshot runner 2px inset** — crops 2px from each edge to remove Windows border artifact.
- **Dialog hero pattern** — open non-modally at t=200ms, lift dialog at t=850ms, screenshot
  at t=950ms. Use `app._capture_target = <toplevel>` to capture a dialog instead of the app.
- **Full-app widget sizing** — PageStack, SideNav, AppShell use `fill="both", expand=True`
  and need `size=(W, H)` (not `minsize=`) to give the canvas a defined size.
- **Navigation window padding** — use `padding=8` on the App for full-app nav scenes to
  give footer-pinned items breathing room at the bottom edge.
- **Tabs vertical scene** — use `padding=16` and `size=(W, H)` since `fill="both"` needs
  a canvas; `minsize=` is sufficient for horizontal tabs scenes.

### MenuButton specifics
- **`icon_only` inferred** — `DropdownButton.__init__` auto-sets `icon_only=True` in
  `style_options` when `icon` is in style_options and `text` is None/empty. The public
  wrapper doesn't need to infer it.
- **Menubutton layout centering** — `Menubutton.label` has `side="left"` in the ttk
  layout. When `icon_only=True` and no dropdown, drop `side="left"` so the label fills
  the full content area and `anchor="center"` can take effect.
- **Item type names** — public API uses `'command'`, `'check'`, `'radio'`, `'separator'`.
  Internal ContextMenu uses `'checkbutton'` / `'radiobutton'`. Translate at the wrapper
  boundary via `_ITEM_TYPE_MAP`. Legacy names accepted for backwards compat.
- **Radio group variable** — `add_radio_item()` auto-creates a shared `StringVar` on the
  internal widget. Values are stored as strings internally. Use `selected=True` to
  pre-select. Multiple `add_radio_item()` calls share one group variable per MenuButton.
- **`show_menu()` respects disabled state** — guard with
  `self._internal.instate(("!disabled", "!readonly"))` before delegating.
- **`disabled` property** — use `instate(("disabled",))`, not string comparison on `cget`.
- **`shortcut=` in `add_item()`** — display-only label. Passes through `format_shortcut()`
  which handles: registered key name → platform display, `"Mod+S"` pattern → `"Ctrl+S"` /
  `"⌘S"` (no registration required), literal string → pass-through.
- **MenuButton hero pattern** — show a standalone "Actions" button (Edit/Duplicate/Archive/
  Delete), NOT a File/Edit/View menubar pattern. Shortcuts section uses the File menu example.

### Style rebuild pattern
- **`configure_style_options` alone doesn't rebuild** — it only updates the stored
  `_style_options` dict. Call `rebuild_style()` immediately after to regenerate the TTK
  style with the new options and apply it to the widget.
- **`emit` wraps `event_generate`** — `PublicWidgetBase.emit(event, data=...)` calls
  `self._internal.event_generate(sequence, data=data)` directly. For internal widgets
  use `event_generate` with `data=` natively (the event system is patched to support it).

### Widgets and API
- **`disabled` on Label** — not appropriate. Label is display-only.
- **`color=` / `background_color=`** — removed. Use `accent=` / `surface=`.
- **`bs.App` accepts `theme=`** directly (overrides the `"theme"` key in
  `settings` if both given). `light_theme=`/`dark_theme=` are NOT direct params —
  set those via `settings={"light_theme": ..., "dark_theme": ...}`.
- **`bs.Signal()` crashes at module level** — must be inside `with bs.App():`.
- **`textsignal=`** — standard kwarg for text-bearing widgets. `signal=` for non-text
  (Slider, Checkbox, etc.). Never expose `textvariable=` / `variable=` publicly.
- **`TTKWrapperBase.__init__` overwrites `self._accent`** — store accent before `super().__init__()`,
  re-assign after.
- **`<<BsThemeChanged>>`** fires after full rebuild (use this). `<<ThemeChanged>>` fires before.
- **`bs.SelectButton`** — button-styled non-editable picker. Distinct from `bs.MenuButton`
  (action menu) and `bs.Select` (editable combobox).
- **`bs.DataTable`** (renamed from `bs.Table`) — works with any
  `DataSourceProtocol` source (decoupled from `SqliteDataSource`); identity reads
  route through `_record_id`/`_public_record`/`_internal_fields`. Defaults to an
  in-memory `SqliteDataSource` when given `rows=`. No built-in border (wrap in a
  `Card`/`Frame`); `density=` and a footer separator are supported.
- **`RadioGroup.set()` validates against keys**, not values.
- **`bs.Form` uses `col_count=`**, not `columns=`.
- **`ToggleGroup(padding=N)`** — bug fixed; safe to pass.
- **`value=` ignored when `signal=` also passed** on boolean widgets — seed the Signal directly.

### Boolean controls
- **Switch/ToggleButton unsupported features** — Switch: no `on_icon`/`off_icon`/`icon_only`/
  `show_indicator`/`tristate`/`density`. ToggleButton: no `tristate`/`show_indicator`.
  Checkbox: only widget supporting `tristate`.
- **Density** — Checkbox and Switch do NOT support `density=`. ToggleButton DOES.
- **Sphinx signatures** — give each subclass its own `__init__` to avoid inheriting
  unsupported params. Use `:inherited-members: PublicWidgetBase` in autoclass.

### Layout widgets
- **`height=`/`width=` on VStack/HStack** — setting one collapses the other axis.
  Add `fill=` + `expand=True` for the unconstrained axis.
- **`show_border=True` needs padding** — border is inside the frame edge.
- **`Grid columns=N` shorthand** — `columns=3` ≡ `[1,1,1]`. `0` == `'auto'`.
- **`**extra_kw` removed from layout wrappers** — `Card`, `GroupBox`, `VStack`,
  `HStack`, `Grid` only accept `**kwargs`.
- **`variant=` removed from VStack/HStack** — use `bs.Card` for card-variant layout.

### Dialogs
- **7 doc pages** — `dialogs.rst` is toctree-only. `ColorDropperDialog` is internal.
- **`content_builder`** receives an internal `_Frame` — use `_Label`/`_Frame` primitives.
- **`Frame.configure(surface=...)`** does NOT work at runtime — use `configure_style_options(surface=...)`.
- **`Dialog.__init__`** is fully keyword-only; `parent=` not `master=`; `min_size=`/`max_size=`.
- **`ButtonRole`** values: `"primary"`, `"secondary"`, `"danger"`, `"cancel"`.
- **`bs-dialog-screenshot` CSS class** — dialog screenshots only; adds border + drop shadow.

### Sliders / fields
- **Slider/RangeSlider spacing** — `VStack gap=` does not visually separate tracks.
  Use `margin_y=10` on each widget. Track heights: plain ≈ 24px, ticks ≈ 45px, badge+ticks ≈ 65px.
- **Screenshot widths** — use `minsize=(720, 1)` for all input/field/slider scenes.
- **`anchor_items="baseline"`** — invalid. Use `"s"`.
- **`select.py` / `calendar.py` shadow stdlib** — use `selectfield.py` and `calendarwidget.py`.

### Misc
- **American English** — all docstrings and user-facing text. Spelling scrub still pending.
- **`font="heading-md"`** not `"heading-md[bold]"` — headings already bold.
- **`&` in `bs.Label` text** — Tkinter strips `&`. Use `"and"`.
- **`Expander` is internal** — use `bs.Accordion`.
- **Run examples after editing** — always `python docs/examples/<widget>.py` before committing.
- **Dark mode Note admonition** — override in `custom.css` inside `html[data-theme="dark"]`:
  `--pst-color-info: #6ea8fe; --pst-color-info-bg: #0d306e`.
- **`Shortcuts` service** — `register(key, "Mod+S", fn)` + `bind_to(app)` wires the keyboard
  handler. `format_shortcut(spec)` resolves display text only (no binding side effect).

---

## Architecture (settled)

**Public API** is a composition layer over internal widgets. Public widgets are plain Python
objects (NOT `tk.Widget` subclasses) holding `self._internal`.

Constructor order: resolve parent → split layout kwargs → construct internal → attach to parent.
`_split_layout_kwargs` strips pack/grid/place keys before internal widget construction.

`.tk` property returns the underlying ttk widget — escape hatch, user's responsibility.

### Context-manager parenting

```python
with bs.App(title="Demo", padding=16, gap=8) as app:
    with bs.HStack(gap=4):
        bs.Label("Hello")
        bs.Button("OK", on_click=lambda: ...)
app.run()
```

`__enter__` pushes container, `__exit__` pops. App hides on enter, shows on exit.

### Events  (redesigned 2026-06-05 — see memory `project_typed_events`)

```python
sub = widget.on_change(handler)   # → Subscription (cancellable)
widget.on_change().debounce(300).listen(handler)  # → Stream (composable)
```

All `on_*()` shorthands use `@overload`: no-arg → `Stream`, with handler → `Subscription`.

**What the handler receives** (the redesign):
- **Data events** (`change`, `input`, `select`, validation, …) → the typed
  payload dataclass, **unpacked**: `on_change(lambda e: e.value)`. Payloads live
  in `bootstack.events` (the catalog) — `bs.events.ChangeEvent`, `SliderEvent`,
  etc. Namespaced there ONLY, not top-level. ListView item events are the
  exception: a plain record `dict` (`e["field"]`).
- **Native events** (`click`, `hover`, `focus`, `blur`, `resize`, key, scroll) →
  a curated, Tk-free `Event`: `widget`, `x/y/x_root/y_root`, `width/height`,
  `delta`, modifier bools `ctrl/shift/alt/meta`, clean `key/char`, `time`.
- `Button`/`Label` `on_click()` METHOD now passes the `Event` (the no-arg
  `on_click=` constructor command is unchanged).
- The generic `on(name, handler)` is typed `Callable[[Any], Any]` (string-keyed,
  can't infer the payload); the precise types are on the `on_<event>()` shorthands.
- Transform happens in `adapt_handler()` (`widgets/_core/base.py`); emit sites
  build the dataclass: `event_generate("<<Change>>", data=ChangeEvent(...))`.
  `_runtime/events.py` (the data-cache transport) is untouched.

### Signals

```python
sig = bs.Signal(value)
bs.TextField(textsignal=sig)   # two-way binding
sig.subscribe(lambda v: ...)
```

### Layout

```python
bs.VStack(padding=20, gap=12, fill="both", expand=True)
bs.HStack(gap=8, anchor_items="center", fill="x")
bs.Grid(columns=["auto", 1], gap=8, sticky_items="ew", fill="x")
```

`fill_items=`, `expand_items=`, `anchor_items=` — container defaults, per-child kwargs override.

---

## Source structure

```
src/bootstack/
├── _core/       infrastructure (capabilities, colorutils, mixins, publisher, images)
├── _runtime/    Tk patches (app, toplevel, menu, shortcuts, events)
├── assets/      locales, icons (themes are now Python, see style/themes/)
├── data/        DataSource (Base, Memory, Sqlite, File)
├── dialogs/     dialog implementations
├── signals/     Signal, TraceOperation
├── style/       Theme (public), themes/ (built-in Theme instances),
│                Style/Typography/Font (internal engine), builders
├── validation/  ValidationRule, ValidationResult
└── widgets/
    ├── _core/   public framework internals (base, container, context, events)
    ├── _impl/   internal implementation (primitives, composites, mixins)
    ├── app.py, button.py, ...  (~40 public wrapper files)
    └── types.py AccentToken, VariantToken, WidgetDensity, SurfaceToken, etc.
```

---

## Key API reference

```python
import bootstack as bs

with bs.App(title="My App", size=(800,600), padding=16, gap=8) as app:
    sig = bs.Signal("World")
    bs.Label("Hello!", font="heading-lg")
    bs.Button("OK", accent="primary", on_click=lambda: ...)
app.run()

# AppShell
with bs.AppShell(title="My App", settings={"theme": "bootstrap-light"}) as shell:
    shell.toolbar.add_button(icon="sun", command=bs.toggle_theme)
    with shell.add_page("home", text="Home", icon="house"):
        bs.Label("Welcome!")
    shell.navigate("home")
shell.run()

# Tokens
accent  = "primary|secondary|info|success|warning|danger|default"
variant = "solid|outline|ghost|toggle"
surface = "content|card|chrome|overlay"
font    = "body|heading-lg|heading-md|caption|code|body+2[italic]"

# Dialogs
bs.alert("Done.")
bs.confirm("Delete?")          # → bool
bs.ask_string("Name:")         # → str | None
bs.ask_integer("Age:", min_value=0)  # → int | None
bs.ask_date("Pick date:")      # → date | None
bs.ask_color()                 # → ColorChoice | None
bs.ask_font()                  # → Font | None
```

---

## Code standards

**Docstrings:** one-line summary + description + `Args:` (name: description, no types).
Single backtick `` `X` `` — never double. No RST roles. Valid values + defaults per kwarg.

**Dataclasses — document fields with ATTRIBUTE DOCSTRINGS, never `Args:`.** Put a
one-line class summary (+ optional prose), then a short docstring string literal
*directly under each field*. Do NOT also list the fields in an `Args:` block —
that renders them twice (a synthesized "Parameters" block + the attribute list).
autodoc `:members:` then renders each field once with its type + description.
(Functions/methods keep using `Args:`.) The conf setting
`autodoc_typehints_description_target = "documented"` suppresses the redundant
synthesized Parameters block for dataclasses. Exemplars: `bootstack.events`
payloads, `bootstack.style.theme.Theme`.

```python
@dataclass
class ChangeEvent:
    """Fires when a field's value is committed (on blur or Enter)."""

    value: Any = None
    """The committed, parsed value."""
    prev_value: Any = None
    """The value before this change."""
```

**`on_*()` shorthands:**
```python
@overload
def on_change(self) -> Stream: ...
@overload
def on_change(self, handler: Callable[[Event], Any]) -> Subscription: ...
def on_change(self, handler=None):
    return self.on("change", handler)
```

---

## Open bugs

- `value=` silently ignored when `signal=`/`variable=` also passed (all boolean widgets)
- `Style._tk_widgets` grows forever — partially resolved; pages are never destroyed

ButtonGroup/ToggleGroup now have **separate** style builders: `ButtonGroup`
(action widgets) uses `style/builders/buttongroup.py`; `ToggleGroup` (selection
widgets) uses `style/builders/togglegroup.py` (registered for the `ToggleGroup`
ttk class; composite sets `ttk_class='ToggleGroup'`). They share the baked
`button_group_*` nine-patch shapes but have independent colors/normal states. The
old ToggleGroup solid-variant contrast issue is fixed.
