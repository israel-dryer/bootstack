# Initiative — Public API typing review (the typing sweep)

**Status:** ✅ COMPLETE on `feat/api-reference-widgets` — all widget batches swept
(Application → Overlays/Forms/Dialogs), each committed and maintainer-reviewed.
Execution was **path A** (incremental, by-widget). **DECISION (2026-06-09): the
standalone sweep is finished; remaining/future typing now folds into the Stage-4
API-Reference homing — a module gets typed when it is homed, not in a separate pass.**
The per-batch log + conventions below stay as the reference for that homing work.

Surfaced while the maintainer reviewed the Stage 4 API-reference pages: public
wrappers pervasively under-type params (`Any`, bare `str`), re-enumerate values in
docstrings that the type already encodes, and use a universal `AccentToken`/
`VariantToken` that is inaccurate per widget. This sweep fixes the public wrapper
signatures + docstrings so the **type is the single source of truth** for a param's
allowed values. Tracking memories: `project_enum_option_typing`,
`project_variant_type_revisit`, `project_docstring_backticks`.

---

## Guiding principle

**A `Literal` is self-documenting — let the type carry the values, and don't
re-enumerate them in the docstring.** The rendered API reference shows the literal
inline (we deliberately set NO `autodoc_type_aliases`, so aliases expand to their
underlying `Literal[...]`/union; `always_use_bars_union = True` renders `A | B`). The
docstring describes *meaning* + the *default*, not the value list.

Corollary: a type may only show values that are actually valid for that param — an
inaccurate superset is worse than `str`. Hence the accent/variant rules below.

---

## Per-param rules

For every public wrapper, audit each constructor/method param (and returns):

1. **Under-typed → promote.** `Any` or bare `str` that has a known closed shape:
   - Use an existing alias: `Anchor`, `Orient`, `Justify`, `Relief`, `CompoundMode`,
     `Fill`, `Sticky`, `Side`, `Direction`, `BorderMode`, `WidgetDensity`,
     `SurfaceToken`, `Padding`, `RuleType` (all in `bootstack.widgets.types`, except
     `RuleType` in `bootstack.validation`).
   - Or an inline `Literal[...]` for a one-off closed set.
   - **Leave `str`** for genuinely open sets: theme names, locale codes, icon names,
     font tokens, free text, record keys/field names, format strings.
   - **Open-set params that have an authority should LINK to it** (curated examples +
     `str` + a link), not a `Literal`: `language`/`theme` (CodeEditor) → Pygments
     (`https://pygments.org/languages/`, `/styles/`); `window_style` → pywinstyles;
     `value_format` (Label/DateField/Gauge/NumberField/Spinbox/TextField/TimeField) →
     stays `str` (named preset OR custom pattern OR dict — can't be a Literal). Docstring
     pattern: one named-preset example + one custom-pattern example + link to
     :doc:`/reference/localization`. The named presets are `NumberPreset` (10) /
     `DatePreset` (18) in `i18n/intl_format.py` (`'decimal'`,`'currency'`,`'percent'`,
     `'fixedPoint'`,`'thousands'`,… / `'shortDate'`,`'longDate'`,`'shortTime'`,…); custom
     patterns like `'#,##0'`, `'dd.MM.yy'` are also accepted. PREREQUISITE: enrich
     `reference/localization.rst` to list the full preset sets + custom-pattern syntax
     (today it only shows decimal/currency/percent) so the link target is complete.
   - `font` (Label/Button/Toolbar/CodeEditor/many) → stays `str` (open token set:
     `'body'`, `'heading-lg'`, `'heading-md'`, `'caption'`, `'code'`, `'body+2[italic]'`,
     …). Docstring: curated examples + cross-link to the font-token reference
     :doc:`/reference/typography`. (Verify that page lists the tokens + the
     `[size][modifier]` syntax; enrich if thin, like the localization formats section.)
2. **`accent` → `AccentToken | str | None`.** `AccentToken` is the 6 universal
   semantic accents (`'primary'`,`'secondary'`,`'info'`,`'success'`,`'warning'`,
   `'danger'`). The `| str` keeps `'default'`, `'muted'`, and modifiers
   (`'primary[+1]'`, `'primary[500]'`, `'primary[subtle]'`) valid. TEXT widgets where
   muted text is meaningful (Label, …) surface it: `AccentToken | Literal['muted'] |
   str | None`. (Keep the param's existing default, e.g. `= None` or `= "primary"`.)
3. **`surface` → `SurfaceToken | str | None`.** Same intent-token + `str` catch-all
   as accent: `SurfaceToken` is the advertised set (`'content'`,`'card'`,
   `'card_raised'`,`'chrome'`,`'overlay'`), and `| str` keeps unadvertised
   accent-derived/modified surfaces valid (`'primary[subtle]'`, `'card[+1]'`, …).
   Ensure every `surface` param has the `| str` (some are typed `SurfaceToken | None`).
4. **`variant` → per-widget `Literal[...]`.** NOT the universal `VariantToken`
   (Gauge `'full'`/`'semi'`, Badge `'pill'`/`'square'`, ProgressBar `'thin'`, …).
   If a widget has no real variants, drop the param or type its real set. (variant is
   a fixed set — no `| str` modifier syntax, unlike accent/surface.)
5. **`padding` → `Padding | None`** (`Padding = int | tuple[int,int] |
   tuple[int,int,int,int]`). The docstring keeps the *semantic* note (what the tuple
   positions mean) — that's not a value enumeration.
6. **`icon_position` governs `image` too.** It abstracts the ttk `compound`, which
   positions whatever image element is shown — an `icon=` OR an `image=` — relative to
   the text. So on any widget that has both an `image` param and `icon_position`, the
   docstring must say "icon or image" (not just "icon"), e.g. "Position of the icon or
   image relative to the text." Keep the inline `Literal['left','right','top','bottom']`.
7. **Docstrings:**
   - **Every public param needs an `Args:` entry.** Under
     `autodoc_typehints_description_target = "documented"`, a param NOT in `Args:`
     renders NO Parameters row at all (silently missing — confusing). Audit each
     widget for constructor params absent from `Args:` and add them (App was missing
     `padding`/`gap`/`fill_items`/`expand_items`/`anchor_items`/`surface`).
   - Drop value enumerations the type now shows ("One of `'a'`, `'b'`, …" → describe
     meaning only). KEEP the default (`Default \`'x'\`.` / `Defaults to ...`).
   - Convert RST double-backticks ` ``x`` ` → single `` `x` `` (default_role=code).
     (Advances `project_docstring_backticks`.)
   - No colon on the first line of an attribute docstring (napoleon `:type:` mangle).
6. **`on_*` event shorthands:** keep the `@overload`s (type-checkers), and in the
   impl docstring DOCUMENT the `handler` param with a `:class:`-linked payload + a
   `:class:`-linked `Stream`/`Subscription` return. The injected "Overloads:" block is
   stripped in `conf.py` (it renders unlinked). Native events use
   `:class:\`~bootstack.events.Event\``; data events use their specific payload.
7. **Catch-all** is `**kwargs` (never `**extra_kw`). Self-placement params
   (`fill`/`expand`/`anchor`/`row`/…) route through `_split_layout_kwargs`, not
   explicit params. **DOCUMENT `**kwargs`** with a concise `Args:` entry that NAMES
   the available layout options + links to the Layout guide (makes the opaque bag
   discoverable — shows *what's* available, not the routing mechanics):

       **kwargs: Layout placement options applied by the parent container —
           `fill`, `expand`, `anchor`, `margin`, `row`, `column`, `sticky`.
           See :doc:`/tasks/layout`.

   Canonical option table lives in `tasks/layout.rst` (real page; includes
   `shared/widget-sizing.rst`). If a widget's `**kwargs` also forwards non-layout
   options, note those too.

## New public types this sweep introduces / promotes

- `Padding` (added to `widgets/types.py`, re-exported from `bootstack.types`). DONE.
- `RuleType` (made public from `bootstack.validation`). DONE.
- `AccentToken` redefined to the 6 accents. DONE.
- Add any new alias to `bootstack.types`/subsystem `__all__`, to
  `tests/test_public_surface.py`, and (when its reference page exists) the API ref.

## Rendering config (already set in `docs/conf.py` — do not revert)

- NO `autodoc_type_aliases` (literals expand inline, on purpose).
- `always_use_bars_union = True` (`A | B`, not `Union[A, B]`).
- `_drop_overloads_field` hook strips the unlinked "Overloads:" block.

## Per-widget checklist (path A — one batch per group, maintainer reviews)

Work in the Stage 4 batch order; tick as completed:

- [x] Application: App, AppShell, Window — DONE.
- [x] Actions: Button, ButtonGroup — DONE.
- [x] Menus & Toolbars: Toolbar, MenuButton, MenuBar, ContextMenu — DONE
      (MenuButton/Toolbar variant→Literal incl 'default'; MenuBar add_button/add_menu
      accent:str→AccentToken; ContextMenu trigger→Literal, density→WidgetDensity).
- [x] Inputs: TextField, PasswordField, NumberField, SpinnerField, PathField,
      Slider, RangeSlider, TextArea, CodeEditor, DateField, TimeField — DONE.
      Across all 11: dropped accent/density/justify/orient value enumerations
      (type self-documents); `font` → `:doc:/reference/typography`; `value_format`
      (TextField/NumberField/DateField/TimeField) → named-preset + custom-pattern +
      `:ref:value-formats`; documented `**kwargs` layout cross-link; double→single
      backticks (textfield/numberfield/slider/passwordfield were still double).
      Literals promoted: `PathField.mode`, `TextArea.scrollbars`,
      `DateField.selection_mode`, `CodeEditor.scrollbars`; `PathField.file_filters`
      → `list[tuple[str,str]]`. Removed the uncurated `internal_kwargs.update(kwargs)`
      passthrough leak from Spinner/Path/TextArea/Date/Time (addons go through
      `insert_addon`, not ctor kwargs) so `**kwargs` is layout-only like TextField.
      `on_*` handler docs: every `on_*` impl now documents `handler` with a
      `:class:`-linked payload + typed `Subscription`/`Stream` Returns (the type was
      otherwise invisible — autodoc strips the Overloads block). Verified the payload
      renders as a cross-ref in the built stubs (NumberField shows 8 distinct links).
      `FieldAddonMixin.insert_addon` CURATED (per maintainer, during review): dropped
      the raw `**kwargs`→internal-primitive passthrough (leaked Tk options `command`/
      `textvariable`/`state`/…) for typed kw-only params — `text`/`icon`/`accent`/
      `on_click`(→`command`)/`signal`(toggle); validates param↔type applicability.
      Advances `project_enum_option_typing`'s "insert_addon `**kwargs` redesign".
- [x] Selection: Checkbox, Switch, ToggleButton, ToggleGroup, Radio,
      RadioToggleButton, RadioGroup, Select, SelectButton, Calendar — DONE.
      Typing/docs: dropped accent/density/orient/icon_position enumerations;
      under-typed `accent: str`→`AccentToken|str`, `density: str`→`WidgetDensity`,
      `signal: Any`→`Signal` (radio*/groups); `on_*` handler docs across all
      (ChangeEvent / Event / DateSelectEvent); documented `**kwargs` layout
      cross-link + removed the `internal_kwargs.update(kwargs)` passthrough leaks;
      fixed Calendar's `:class:datetime.date` RST leak.
      variant → concrete per-widget Literal sourced from `style/builders/`:
      ToggleButton `['solid','outline','ghost']` (toolbutton.py); ToggleGroup +
      SelectButton `['solid','outline','ghost','default']` (togglegroup/button.py —
      docstrings under-reported, omitted `'default'`).
      STRUCTURAL cleanup (maintainer-approved, mirrors the boolean restructure):
      `variant` is DEAD on Switch (hardwired `'switch'`) and Checkbox (only a
      `'default'` builder) → REMOVED; `density` is unsupported on Checkbox/Switch/
      Radio (RadioButton/CheckButton don't capture it) → REMOVED. Mechanism:
      `_BooleanControlBase`/`_RadioBase` became engines taking styling via an
      `_internal_options` dict + a private `_tristate`; each public subclass has its
      OWN `__init__` exposing only supported params, and the base now RAISES
      TypeError on unknown kwargs (so removed params are rejected at runtime, not
      silently forwarded via `**kwargs`). ToggleButton/RadioToggleButton keep
      variant/density. See memory `project_variant_type_revisit`.
- [x] Data Display: Label, Badge, ProgressBar, Gauge, ListView, DataTable, Tree —
      DONE (NOT committed — awaiting review). Across all: `accent: AccentToken|None`
      → `AccentToken|str|None` (keeps `'default'`/modifiers); removed the
      `internal_kwargs.update(kwargs)` passthrough leak so `**kwargs` is layout-only;
      documented `**kwargs` with the `:doc:/tasks/layout` cross-link; dropped value
      enumerations the type now shows (selection_mode/sorting_mode/paging_mode/mode/
      orient — kept the default + meaning); double→single backticks (Tree, Gauge,
      ProgressBar, Badge, + Label's leftover intro/icon lines). Under-typed promotions:
      ProgressBar `signal: Any`→`Signal`; ListView `items: list`→`list[dict]`,
      `data_source: Any`→`DataSourceProtocol`; Tree `data_source: Any`→
      `DataSourceProtocol`, `nodes: list`→`list[str|dict]`, `order: Any`→
      `str|Column|SortKey|Sequence[...]|None`; DataTable `export_formats: list[str]`→
      `list[Literal[csv|tsv|xlsx|json|jsonl|xml|parquet|feather|hdf5]]`. `on_*` handler
      docs completed everywhere (`:class:`-linked payload + typed Subscription/Stream
      Returns): ListView item events stay a plain record `dict` (the documented
      exception) + `selection_changed`→`Event`; DataTable Row/Rows/Selection/Export
      events; Gauge `SliderEvent`; Tree `on_selection_changed`→`TreeSelectionEvent`
      (was `Callable[[Any]]`), activate/expand/collapse→`TreeNode`, right_click→`dict`.
      Badge/Gauge/ProgressBar variant already concrete per-widget Literals (no change).
      Verified: `test_public_surface.py` green (127), clean `-W` build warning-free,
      payload cross-refs resolve to stubs in the built HTML.
      **Review fixes (maintainer, 2026-06-09):**
      - `on_*` IMPL signatures must be TYPED, not just the `@overload`s. Because
        `autodoc_typehints="description"`, the param type renders from the IMPL
        annotation (the signature itself stays bare by design) — a bare
        `def on_x(self, handler=None):` shows NO payload type at all. Typed every
        ListView (7) / DataTable (9) / Tree (5) impl as
        `handler: Callable[[Payload], Any] | None = None) -> Stream | Subscription`.
        (Inputs/Selection impls were already typed — gap was Data-Display-only;
        grep `def on_\w+\(self, handler=None\):` now returns nothing.)
      - PROPERTIES need docstrings too (autodoc renders them): added to ProgressBar
        (`value`/`max_value`) and Gauge (`value`/`subtitle`). Also swept already-reviewed
        widgets via an AST scan: DateField/TimeField `disabled`/`read_only`, Radio
        `disabled`, and the generic `.on()` impl on 10 input/select widgets (all were
        undocumented). Internal-only `Spinbox`/`Expander` props left as-is. FLAGGED (not
        an `on_*`, deferred): `guide_layout` on the page-frame handles (AccordionSection/
        StackPage/SplitPane/TabPage) is undocumented — likely DEMOTE to `_guide_layout`
        (internal layout-protocol hook) rather than document; decide during Layout/Nav.
      - Memory `feedback_autodoc_impl_typing` captures this convention + the AST scan.
      - `TreeNode` (public via `bootstack.widgets.tree`) had 9 undocumented `__slots__`
        data attributes — added class-level typed annotations + attribute docstrings
        (`label`/`icon`/`open_icon`/`closed_icon`/`expanded`/`children`/`parent`/`data`/
        `loader`); annotation-only + `__slots__` is safe (no class-var conflict).
      **Feature added (Tree, maintainer-requested):** `Tree.find(matcher)` +
      `find_all(matcher)` — predicate OR `col(...)` condition; condition pushes down
      on a data-source tree and loads (non-destructively) the path to each hit. Tests
      in `test_tree.py`. `filter()`/`search()` view-pruning DEFERRED. Memory
      `project_tree_find_filter`.
- [x] Layout: Separator, Card, GroupBox, VStack, HStack, Grid, ScrollView,
      Accordion, SplitView — DONE (NOT committed — awaiting review). Across all:
      `padding: Any`→`Padding|None`; `columns`/`rows: int|list`→`int|list[int|str]`;
      `fill_items`/`anchor_items`/`sticky_items` bare `str`→`Fill`/`Anchor`/`Sticky`
      (Card/GroupBox were untyped); double→single backticks; dropped value
      enumerations the type now shows (accent/orient/layout/auto_flow); documented
      `**kwargs` with the `:doc:/tasks/layout` cross-link; removed the
      `internal_kwargs.update(kwargs)` passthrough leak (Separator/ScrollView/
      Expander/Accordion) so `**kwargs` is layout-only.
      **New aliases (this batch):** `LayoutKind` (`'vstack'|'hstack'|'grid'`) +
      `AutoFlow` (`'row'|'column'|'row-dense'|'column-dense'|'none'`) added to
      `widgets/types.py`, re-exported from `bootstack.types`, added to
      `test_public_surface.py`. Used everywhere `layout=`/`auto_flow=` recur (6 sites
      each) — directly advances `project_enum_option_typing`. Expander/Accordion/
      SplitPane `auto_flow` widened 2→5 values (GridFrame supports all 5).
      **ScrollView:** `show_border`/`padding`/`height`/`width` were documented but
      only worked via the kwargs leak — PROMOTED to real typed params.
      **Accordion variant:** `VariantToken|None`→`AccordionVariant` (`Literal['solid',
      'default']`) — the `Expander.TFrame` builder only registers those two (the
      default reads as ghost); the old `'outline'`/`'ghost'` were never registered.
      **Maintainer review (interactive, 2026-06-09):**
      - Grid-columns pixel form (`'120px'`) added to the `e.g.` for every
        configurable-layout widget (Card/GroupBox/SplitView.add/Accordion.add).
      - GroupBox border default is NOT `'stroke'` — the `TLabelframe` builder derives
        it via `b.border(surface)` (blend toward on-color); `'stroke'` is the default
        only for plain `Frame` borders. Left accent as `AccentToken|str|None`.
      - **STRUCTURAL — SplitView pane management** (maintainer-approved): `min_size=`
        DROPPED (it forwarded `minsize` to `ttk.Panedwindow.add`, which has no such
        option — a guaranteed `TclError` at runtime; ttk panes only support `-weight`,
        confirmed via the man page + probing — requested per-pane width/height is NOT
        honored for sash placement, only `sashpos()` is). `SplitPane` enriched into a
        live handle: `key` + `weight` (read/write property via `pane(frame, weight=)`)
        + `remove()`. `SplitView` gained `add(key=)`, `insert(index, ...)`,
        `move(key, index)` (both via ttk `insert`, which also reorders an existing
        pane), `item(key)`, `panes`, `keys()`, `__len__`, `remove(key)`. `_panes`
        registry kept in live order via `_resync_order()` (rebuilt from
        `_internal.panes()`). Removal uses a direct `tk.call(w, 'forget', frame)` —
        `WidgetCapabilitiesMixin.forget()` shadows `ttk.Panedwindow.forget(pane)` with
        a zero-arg override. Guide page `min_size` section → "Managing panes".
      - **STRUCTURAL — `AccordionSection` enriched** (maintainer-approved): now the
        single public section handle (both a `with`-block context AND a live
        controller). Added `key`/`title`(get+set)/`expanded` props + `expand()`/
        `collapse()`/`toggle()`. `add()` retains one instance per section in
        `Accordion._sections`; `item(key)`→`AccordionSection` and `items(expanded=)`→
        `tuple[AccordionSection, ...]` now return handles instead of leaking the
        internal `_InternalExpander` (was typed `Any`/`tuple`). `remove()` drops it.
      - **STRUCTURAL — HStack/VStack render fix** (maintainer-approved): params lived
        in `_StackBase.__init__`, invisible under `autoclass_content="class"`. Gave
        each its OWN `__init__` (full typed signature) + a class-docstring `Args:`
        block (boolean-controls precedent). Verified params now render in built HTML.
        (Global `autoclass_content="both"` rejected — 5 classes carry Args in BOTH
        class + `__init__` docstrings and would double-render.)
      - FLAGGED (deferred, NOT done): (a) `guide_layout` on the handle classes
        (AccordionSection/SplitPane + StackPage/TabPage) stays public+undocumented —
        full demotion to `_guide_layout` is a protocol-wide rename (called by string
        in `base.py::_attach_to_parent`); do it holistically across all four handles
        in a dedicated pass, not piecemeal. (c) **Public `on_destroy` lifecycle hook** — not
        exposed on any widget today (`<Destroy>` bound internally for cleanup only);
        a uniform public lifecycle event is its own initiative.
      Verify: `test_public_surface.py` green (131); clean `-W` build warning-free;
      `LayoutKind`/`AutoFlow` expand inline in built HTML; HStack params render.
- [x] Navigation: PageStack, Tabs, SideNav — DONE (NOT committed — awaiting review).
      Core typing: `StackPage`/`TabPage` handles + `PageStack`/`Tabs.add()` got the
      Layout-batch promotions (`layout`→`LayoutKind`, `padding`→`Padding`,
      `fill_items`/`anchor_items`/`sticky_items`→`Fill`/`Anchor`/`Sticky`,
      `columns`/`rows`→`int|list[int|str]`, `auto_flow`→`AutoFlow`); single backticks;
      `**kwargs`→`:doc:/tasks/layout`; dropped value enumerations the type shows
      (DisplayMode/layout/auto_flow). `Tabs` `accent: AccentToken|None`→`AccentToken|
      str|None` + removed its `internal_kwargs.update(kwargs)` leak; `close_command:
      Callable`→`Callable[[],Any]`; columns px example added. `SideNav` `accent:
      AccentToken`→`AccentToken|str` (kept `'primary'` default); already returns public
      `SideNavItem`/`SideNavGroup` handles (no leak) — typing/docstring only.
      **STRUCTURAL — handle enrichment (mirrors approved Accordion/SplitView):**
      `StackPage` gained `key` + `navigate()`; `TabPage` gained `key` + `label`
      (get/set via `configure_tab`) + `select()`/`hide()`/`show()`/`remove()`.
      `PageStack`/`Tabs` retain handles in `_pages`; `item(key)`→handle and `items()`→
      `tuple[handle,...]` now return the page handle instead of leaking the internal
      page widget / tab header (both were typed `Any`). `remove`/`forget_tab` drop from
      the registry. No internal callers depended on the old leaked returns (verified).
      Verify: `test_public_surface.py` green (131); clean `-W` build; all new handle
      members render in built HTML. `guide_layout` flag now covers all four handles.
- [x] Overlays/Forms/Dialogs — DONE (NOT committed — awaiting review).
      **Tooltip/Toast** (overlays, leaf widgets — no `**kwargs` layout): `accent`→
      `AccentToken|str|None`; single backticks; dropped accent/justify enumerations;
      `Toast.on_dismiss`/`toast()`→`Callable[[dict|None],Any]`.
      **Form**: `accent: str`→`AccentToken|str|None` (the `project_enum_option_typing`
      first-fix); `buttons: Sequence`→`Sequence[str|DialogButton|dict[str,Any]]`
      (TYPE_CHECKING import to dodge the dialogs↔widgets cycle); removed the
      `kw.update(kwargs)` leak + documented `**kwargs`→`/tasks/layout`; single
      backticks. (Form's `field()`/`fields()`/`field_variable()` stay `Any`/`tuple` —
      Tk-coupled, `project_public_intent_backlog`. Form has no explicit `surface`/
      `padding` params now the leak is gone — possible follow-up like Card/GroupBox.)
      **Dialogs** (`dialogs/__init__.py` verbs + `FormDialog`/`ColorChooserDialog`/
      `FontDialog`/`FilterDialog` wrappers): global double→single backticks (76 lines);
      `confirm_role: str`→`ButtonRole`; `value_format`→`:ref:value-formats` link on
      ask_string/integer/float; `default_font`→`:doc:/reference/typography` on
      FontDialog/ask_font; dropped `severity` value enumerations (`SeverityToken` shows
      them). **Dialog/DialogButton** (`_impl/dialog.py`, public re-exports): global
      backticks; `window_style: str`→`WindowStyle|str|None`; `surface: str`→
      `SurfaceToken|str|None`. `DialogButton` dataclass already clean (attribute
      docstrings). `ColorChoice`/`FontChoice` are bare namedtuples (no class docstring;
      documented via the wrappers' `result` props). NOTE: `bootstack.dialogs` still
      lacks an `__all__` — that's Stage-4 homing Batch 6, not the typing sweep.
      Verify: `test_public_surface.py` green (131); clean `-W` build; dialog classes
      construct.

**TYPING SWEEP COMPLETE** — all widget batches done. Remaining cross-cutting follow-ups
(separate initiatives, NOT this sweep): the holistic `guide_layout`→`_guide_layout`
demotion on the 4 handle classes; a public `on_destroy` lifecycle hook; retiring the
now-unused `VariantToken`.

## Verify (each batch)

- Clean build (NOT incremental — masks warnings): build to a fresh output dir if
  `docs/_build` is locked by an open browser. `sphinx-build -b html docs <out> -W
  --keep-going` → warning-free.
- `python -m pytest tests/test_public_surface.py -q` → green.
- Run any touched widget's `docs/examples/<widget>.py` if behavior could change
  (these are type/docstring-only, so usually N/A — but accent `| str` removals etc.
  warrant a smoke check).

## CodeEditor follow-ups (when Inputs batch reaches it)

- `on_change`/`on_input` payloads FIXED (2026-06-09): public wrapper re-emits the
  core's raw `<<Change>>` as typed `<<BsChange>>`(ChangeEvent)/`<<BsInput>>`(InputEvent)
  on `self._internal`, like TextArea. `on_modified` already correct (TextModifiedEvent).
- `on_undo`/`on_redo` VERIFIED correct: `undo.py` emits `<<TextUndo>>`/`<<TextRedo>>`
  with `data=InputEvent(text=value)` (the content after the undo/redo). Annotations
  accurate, no fix needed.
- Remaining CodeEditor typing: `scrollbars: str` → `Literal['both','auto','vertical',
  'none']`; `accent` ok; add the `**kwargs` layout cross-link; `language`/`theme`
  docstrings DONE (Pygments links).

## Out of scope (separate flagged items)

- `show_indicator` REMOVAL (behavior + style builders + screenshots) —
  `project_show_indicator_removal`.
- `insert_addon` `**kwargs` discoverability redesign (explicit typed params) —
  `project_enum_option_typing`. DONE during the Inputs batch (see the Inputs checklist
  entry): now typed kw-only params, no Tk passthrough.
- Retiring the now-unused `VariantToken` (after per-widget variants land).
