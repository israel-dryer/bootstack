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

Pointers only — these shipped; rationale, detail, and gotchas live in the linked
memories and git history.

- **Field-family widget reviews + validation follow-ons** (this session; all
  MERGED) — closed out the `TextField` review that spawned the validation rebuild,
  then reviewed the whole **field family** one PR each (audit→fix→test→docs→
  file-follow-ups). **Validation follow-ons first:** **#216** (PR **#219**) —
  `NumberField(value=None)`/`value=""` crashed at construction (`float('')`; an
  empty number field stores `''`, the guard only checked `is not None`) → normalize
  empty→`None`, skip bounds. **#217 part 1** (PR **#220**) — reactive **`Form.valid`**
  (`Signal[bool]` AND-ed over the member fields' `valid` signals via subscriptions)
  + **`Form.errors`** (live `dict[str,str]` from the fields' `error` signals), on
  internal+public `Form`; a submit button binds `form.valid`. **#217 part 2
  (stream-based triggers) DEFERRED** — re-evaluated as pure internal churn (current
  `_setup_validation_binds`/`after()` works, not Tk-coupled). **Docs cross-ref rule**
  (PR **#221**) — added to `docs/_dev/widget-review-and-docs-standards.md`: a widget
  section on a cross-cutting subject (validation/events/data/layout/…) must
  `:doc:`-link the matching how-to/topic guide (the field-items *Validation* gap was
  the trigger). **Then the 7 reviews:** TextField (#223), NumberField (#224),
  PasswordField (#225 docs + **#229** read-only-reveal fix), DateField (#228),
  TimeField (#230), PathField (#231), SpinnerField (#233). **Pattern:** NO wrapper
  had correctness bugs (every audit-agent "critical" claim died under adversarial
  verification — e.g. the "addon-state bypass" was false: `configure(state=)` routes
  through `Field._delegate_state` which syncs addons; "`.text` needs a setter"
  contradicts the locked read-only value/text contract). The yield was **docs** —
  every page lacked the `/reference/validation` cross-link, the reactive
  `field.valid`/`field.error` surface, and a fleshed See-also; each got a
  mental-model lead, Date/Time/Path gained full Validation sections. **Two real code
  changes (decided with maintainer):** PasswordField reveal toggle now `active_when_
  readonly=True` (#229 — the flag postdates the widget; revealing only flips the mask
  char, safe under read-only); **TimeField now starts EMPTY** (#230 — was
  `datetime.now().time()` in `timeentry.py`, the only field not starting empty, which
  silently **defeated `required=True`**; pre-release clean break). **Systemic bug
  fixed across the family:** validation screenshot scenes called `field.validate("blur")`
  but public `validate()` takes **no** arg (raised in the `after()` tick → error never
  rendered); fixed to `field.validate()` + regenerated. **Open follow-ups (additive,
  not bugs):** **#227** (`Signal` is StringVar-backed for objects → `Date/TimeField`
  `signal=` reads back a *string*, and field→signal doesn't fire on programmatic
  `.value=`; so Date/Time docs keep `textsignal=`; NumberField unaffected) · **#232**
  (PathField dialog-config options as live properties) · **#234** (SpinnerField↔
  NumberField parity: increment/decrement, live min/max/step). Memory
  `project_field_family_review`. **Process gotcha:** a fix pushed to a branch AFTER
  its PR merged is stranded — cherry-pick onto a fresh branch (bit us with #225→#229).
- **Field validation redesign** (PR **#218**, MERGED) — started as a `TextField`
  review (audit→fix→test→docs), surfaced that validation was **fundamentally
  broken for typed fields**, and turned into a 4-phase rebuild. **Phase 1:**
  validation now runs against the field's **typed value** via one resolver
  (`TextEntryPart._get_validation_value` = `_parse_or_none(get())`;
  `NumberEntryPart` override coerces to its numeric type) — all 7 field wrappers
  route through it (was 4 passing the raw datum → `TypeError`, 2 passing text);
  `add_validation_rule` guards the silent `ValidationRule`-object double-wrap with
  a `TypeError`. **Phase 2:** type-aware rule taxonomy — text-rules
  (`stringLength`/`pattern`/`email`) vs value-rules; new **`range`** rule
  (number/date/time bounds with a message, vs silent `min_value`/`max_value`
  clamping); an inapplicable rule is **rejected at attach time** with
  `BootstackError`, keyed off a per-wrapper `_VALIDATION_KIND` class attr
  (`number`/`date`/`time`; `text` default); redundant date/time
  `add_validation_rule` overrides removed (they bypassed the guard). **Phase 3:**
  reactive validity surface — the engine owns `_valid_signal`/`_error_signal`
  (source of truth, set via `_set_validity` on every run); public **`field.valid`**
  / **`field.error`** Signals (`bs.Label(textsignal=field.error)`); the Field
  message label is now bound to the error signal (imperative `_show_error`/
  `_clear_error` gone); `Form.validate()` routed through the entry's validator.
  **Phase 4:** `docs/reference/validation.rst` rewritten (typed-value model,
  `range`, type-aware behavior, reactive signals); api-ref `RuleType` += `range`.
  Brief `docs/_dev/field-validation-system.md`; memory
  `project_field_validation_redesign`. Tests `test_field_validation_typed.py`
  (27). **Follow-ups BOTH DONE this session** (see the field-family entry above):
  **#216** (PR #219) NumberField empty-construction crash · **#217 part 1** (PR #220)
  reactive `Form.valid`/`Form.errors` (part 2 stream-triggers deferred). NB the
  **string-only `add_validation_rule`** decision is locked (a `ValidationRule` object
  carries no info the string form lacks).
- **Slider/RangeSlider review** (PR **#212**, MERGED) — value clamps to range, disabled
  honored on every key (incl. Home/End), Home/End emit `<<Commit>>`, tightening the range
  re-clamps the value(s); widget pages gained Events + Keyboard sections + value/min-max
  screenshots. (The `fix/slider-review` branch is merged — stale.) `step=` follow-up
  (#213/#210) and the Tab focus-trap (#211) are under "Next up".
- **Shell chrome divider + context-menu / DataTable interaction fixes** (this
  session; PRs **#206** and **#209**, both MERGED to `main`) — two batches from
  dogfooding the AppShell + DataTable demos:
  - **#206 — persistent chrome→content border + softer inter-toolbar divider**
    (`fix/shell-content-border`). The chrome→workspace boundary is now owned by
    **`ShellLayout`** (a content-surfaced `_body_sep` at the soft
    `DIVIDER_BORDER_STRENGTH=0.90`, always packed between the chrome stack and the
    body, mirroring the bottom `_status_sep`) — authors no longer rely on
    `add_toolbar(divider=True)` for it, and the stroke matches the rail/sidebar/
    status dividers instead of reading heavy (the original complaint). The
    per-toolbar `add_toolbar(divider=True)` hairline was **softened to 0.90 + kept
    chrome-surfaced** (was the default heavy blend) so an inter-bar divider matches;
    it's now reserved for separating stacked bars. `appshell.rst` notes the
    auto-boundary. Plain `App`/`Window` keep `divider=` as their chrome separator
    (no shell layout, no auto border).
  - **#209 — context-menu dismissal + DataTable right-click/selection + FormDialog
    action result** (`fix/contextmenu-outside-dismiss`). (a) **ContextMenu**: the
    overrideredirect popup's outside-dismiss now watches **all mouse buttons**
    (was `<Button-1>` only — a right-click to open another menu slipped past it);
    a one-shot **`_suppress_next_outside`** guard set in `show()` kills the
    reopen-race that widening introduced (right-click another row reopens, doesn't
    self-dismiss); and **`hide()` now runs BEFORE an item's handler** (a modal
    handler was blocking with the menu still visible). (b) **DataTable**:
    right-click **no longer changes the selection** (it set `_context_iid`; the
    row-menu commands target it via new **`_context_iids()`** = clicked row, or the
    whole selection when the click is inside a multi-selection); a left-click on a
    checkbox/group table now **dismisses an open menu through the `'break'`** path
    (`_dismiss_context_menus()` at the top of `_on_header_click`, since the tree's
    `'break'` stopped the toplevel outside handler); and **selection survives a
    `_refresh_tree` rebuild** for still-visible rows (sort keeps all, search narrows
    — was a full clear on every search/sort/page). (c) **FormDialog**: `show()` was
    overwriting `result` with form data for any non-cancel close, discarding a
    custom button's `result` — so the edit dialog's **Delete** (`{"result":
    "delete"}`) returned data instead of `"delete"` and the row was updated, never
    deleted; new **`_resolve_result()`** maps submit buttons→form data, action
    buttons→their result, cancel→None. (d) **Docs**: fixed stale `event["text"]`
    dict-subscript in ContextMenu/MenuButton examples+guides (`on_select` gets a
    `MenuSelectEvent` dataclass → `event.text`). **Follow-up issues filed:**
    **#207** (general grab-based dismiss so user-attached menus also dismiss when a
    host widget returns `'break'`) · **#208** (persist DataTable selection by record
    id across pages — the "keep visible matches" interim shipped here).
- **Navigation API reshape — `AppShell` + `Workbench` (#200)** (this session; PR
  **#202**, MERGED to `main`) — split the one polymorphic `AppShell` into two
  honest classes along the **topology** axis: **`bs.AppShell`** = single-tier
  *sidebar host*; new **`bs.Workbench`** = two-tier *workspace host*
  (`add_workspace` + rail). Shared **`_SidebarHost`** mixin (on `AppShell` +
  `Workspace`); a private **`_ShellBase`** carries window/chrome/lifecycle. The
  **provider** axis is four parallel front doors — **`page_nav()`** (authored
  pages), **`list_nav()`** / **`tree_nav()`** (data-bound master-detail),
  **`custom_nav()`** (renamed from `panel()`); one per sidebar, only `page_nav`
  authored (`add_page`/`add_header`/`add_divider`). Provider options live on the
  provider: **`page_nav(variant='ghost'|'solid')`** (standalone-only; forced to the
  wash under a rail) and the full `PageStack.add` **layout kwargs on `add_page`**
  (a page IS a column — no inner wrapper). Footer = **`pin_to_footer=`** flag
  (dropped `add_footer_page`/`add_footer_workspace`). Shell kwargs keep only app-wide
  chrome (`nav_accent`, surfaces, `rail_*`). **Framework fix surfaced in review:
  `ContentHost` now FILLS its child** — master-detail/custom content was shrinking
  and centering (the apparent "extra padding"); detail panes left-aligned at
  `padding=(16, 10)`. Internal `Shell`/`Workspace` keep `add_page`/`add_workspace`/
  `panel`/`nav_selection` (public layer is the rename boundary). Built `Workbench`
  doc page + screenshot scenes; AppShell page gained a "Sidebars at a glance" card
  grid + ghost/solid + compact shots; Workbench compact is **not** a mode (rail is
  the icon tier → sidebar is expanded/hidden, documented). **#189 nav_variant
  (PR #199, MERGED) was folded in** — `nav_variant` ctor kwarg → `page_nav(variant=)`;
  its `test_nav_selection.py` removed (superseded by `test_appshell_reshape.py`).
  Tests: `test_appshell_reshape.py` (6) + `test_workbench.py` (2). Memory
  `project_navigation_api_reshape`. **Follow-up: #201 — SHIPPED (sidebar
  hamburger, see top of this list).**
- **Sidebar hamburger toggle — `Toolbar.add_sidebar_toggle()` (#201)** (this
  session; on `feat/nav-expandable-group`) — #201 was filed as an *expandable
  sub-item nav group*, but the maintainer **reinterpreted it** as a built-in
  **hamburger that collapses/expands the AppShell sidebar** (the accordion-style
  sub-items stay parked per the nav-spec Revision-4 cut — compose `bs.Accordion`
  in a `custom_nav`). The collapse machinery already existed (`toggle_sidebar()`/
  `show_sidebar()`/`hide_sidebar()`/`sidebar_mode`, Ctrl-B); what was missing was
  a control. Modeled on `ThemeToggle`/`add_theme_toggle()` but **NOT standalone**
  (a sidebar toggle is meaningless outside one shell): an internal
  `SidebarToggle(Button)` (`widgets/sidebar_toggle.py`, **not** in `bs.*`) built by
  **`Toolbar.add_sidebar_toggle(**kwargs)`**, which wires it to the owning shell.
  **AppShell-only** — the guard is `isinstance(host, AppShell)` (a `_SidebarHost`;
  `Workbench` inherits `toggle_sidebar` from `_ShellBase` so a `hasattr` check is
  too loose), raising `BootstackError` on `Workbench`/`App`/`Window`. Enabler:
  `add_toolbar()` (ChromeHostMixin) now passes `_host=self` into the `Toolbar`;
  `Toolbar.__init__` stores `self._host`. **Author places it wherever they want in
  the bar — no auto-injection.** `collapse='compact'` is the **default** (the
  desktop/Fluent convention: shrink to the icon rail, reusing the shell's
  `_can_compact_active()` so it **falls back to hidden** for non-compactable
  data-bound navs); `collapse='hidden'` always fully hides. **Mode-dependent
  default icon** (`icon=None` resolves to `layout-sidebar` for compact, `list` for
  hidden); single steady glyph unless the author passes a stateful pair
  (`collapse_icon` shown while expanded, `expand_icon` while collapsed, each
  falling back to `icon`). A ~6px toggle-vs-rail offset in compact is **left as-is
  by decision** (only visible compacted; aligning would couple toolbar padding to
  rail width). Tests `tests/widgets/public/test_sidebar_toggle.py` (8). Docs:
  "Sidebar toggle" section in `docs/widgets/toolbar.rst` (full detail) + the
  AppShell page's "Sidebar visibility" section (the user-facing control,
  cross-linked). StatusBar deliberately **not** given the method (scope creep — a
  hamburger belongs in a toolbar).
- **Gallery/Carousel height-floor cleanup (#160)** (PR **#185**, MERGED) — added the
  regression test + hardened two magic numbers into named constants; the floor itself
  shipped in #161. Memory `project_picture_suite`.
- **Tab overflow handling (#168)** (PR **#184**, MERGED) — clipped tabs scroll (wheel +
  selected-tab auto-scroll) with a trailing chevron overflow menu; `max_tabs=`; always-on
  (plain strip kept only for `tab_width='stretch'`). Three framework fixes: PackFrame
  no-repack when `gap==0`, PageStack pre-size-on-swap, deferred `_scroll_into_view`.
- **ContextMenu/Tooltip cover container children (#166)** (PR **#183**, MERGED) —
  `propagate_target_bindings()` adds the container's path bindtag to every descendant so
  the gesture fires anywhere inside. Memory `reference_bindtags_underused`.
- **Theme-repaint cleanup (#177) + docstring-backtick sweep** (PRs **#181**/**#182**,
  MERGED) — code-editor `StyleRegistry`/`SearchOverlay`/`IndentGuides` migrated onto
  `<<BsThemeChanged>>`; dead `FloodGauge` deleted; 754 RST double→single backticks across
  43 `src/` files. Memory `project_docstring_backticks`.
- **Undecorated window chrome (#162/#165) + theme-repaint perf (#167)** (PRs #175/#176/
  #178/#179/#180, MERGED) — undecorated App/Window/AppShell auto-inject titlebar+border;
  canvas widgets re-resolve colors via the STD publisher (post-rebuild), gated on
  visibility (gallery toggle ~2960ms→~580ms). Memories `project_undecorated_window_chrome`,
  `reference_theme_repaint_mechanisms`.
- **Pre-release `0.1.0a10` shipped + docs deploy fixed** (PRs #139/#140, MERGED) — Toast
  split into `toast()`/`Notification`/`Snackbar`; gallery/demo widget coverage; released to
  PyPI + GitHub Release; docs-deploy fixed (restored `docs/CNAME` + `html_extra_path`).
  Memories `project_prerelease_readiness`, `project_toast_notification_split`.
- **0.1.0 API-freeze pass — breaking changes drained + ThemeToggle + media floor** (PRs
  #141–#161, MERGED) — workflow action bump (#141), ttkbootstrap naming purge (#142),
  clipboard scope (#151), nav missing-key errors (#153), `Theme.from_existing` (#156),
  `Signal.subscribe` cancelable handle (#157), VariantToken retirement (#158), `ThemeToggle`
  (#159), media min-height floor (#161). Memories `project_clipboard_api_scope`,
  `project_variant_type_revisit`, `project_picture_suite`.
- **AppShell + navigation clean-slate rewrite** (PRs #133–#136, MERGED; later split into
  AppShell + Workbench by #200/#202 — see top) — VS Code-style rail + swappable sidebar +
  content; `bs.AppShell` swapped onto the new `Shell`, standalone `bs.SideNav` dropped.
  Companions: theme/Bootstrap-alignment v2 (#137), thin-scrollbar exposure (#138),
  nav-patterns docs (#136). Spec `docs/_dev/appshell-navigation-spec.md` (Revision 4).
  Memories `project_appshell_sidenav_refactor`, `project_theme_bootstrap_alignment`,
  `project_thin_scrollbar_initiative`, `project_nav_patterns_section`.
- **Media widget suite — Picture / Gallery / Carousel / Avatar** (PRs #126–#132, MERGED) —
  media-display widgets on the public `Image` handle: Picture (fit modes, animated GIF),
  Gallery (record-native thumbnail grid), Carousel (one-at-a-time stepper), Avatar
  (image-or-initials). Plus `on_select` rename (#130) + theme-aware demo videos (#131).
  Memories `project_picture_suite`, `project_avatar_widget`, `project_doc_demo_videos`.
- **Public Image/Icon API + AppIcon + field signals** (PR #125, MERGED) — `bootstack.images`
  (`Image` handle, `get_icon`/`list_icons`, `AppIcon` → `.ico`/`.icns`/`.png`); `App`/`Window`
  `icon=`; live `icon`/`image` setters; typed `signal=` on Number/Date/Time fields;
  `bootstack.toml` scoped to build/scaffold; public file-dialog verbs; ships `bootstack appicon`.
  Memories `project_image_icon_public_api`, `project_field_value_signal_dtype`.
- **Menu bar + command bar** (PR #124, MERGED) — cross-platform `app.menubar` (themed strip on
  Win/Linux, native `NSMenu` on macOS); `Toolbar`→`CommandBar`; legacy `bs.MenuBar` removed;
  `app.menu`→`app.menubar`, `app.toolbar`→`app.commandbar`. Memory `project_menu_redesign`;
  follow-up `project_macos_window_chrome`.
- **Widget detach/attach** (PR #123, MERGED) — `detach()`/`attach()`/`is_attached` across
  pack/grid/place; `on_attach`/`on_detach`; `attached=False` ctor; new `index=` pack knob.
  Memory `project_widget_attach_detach`; backlog `project_inherited_base_api_docs`.
- **Select grouping + popup height cap** (PR #122, MERGED) — `Select(group_by="field")` clusters
  the popup under verbatim headers (names any bag field, presentational only); `max_visible_items=N`.
  Memory `project_select_options_databag`.
- **Universal `.selection` on ListView/DataTable/Tree** (PR #120, MERGED) — polymorphic by
  `selection_mode` (dict/list, TreeNode handles); replaced `get_selected()`/`selected_rows`/
  `selected_nodes` (clean break); `ListView.select_items`/`deselect_items`. Memory `project_option_databag`.
- **Field value/text/label contract + option data bag** (PRs #113–#116, MERGED) — `label`=caption,
  `text`=formatted display (public read-only), `value`=raw datum (never derived from text); shared
  `Option = str | tuple | OptionDict` + `normalize_option` with a data bag; `.selection` accessor.
  Memories `project_field_value_text_model`, `project_option_databag`.
- **Widget API gap audit + documentation** (PR #111, MERGED) — audited ~49 widgets vs their
  `_impl/` internals; added lifecycle (`destroy`/`on_destroy`), `WindowControlsMixin` on
  App/AppShell/Window (AppShell is now a `PublicWidgetBase`), group management, live properties;
  new **Application** widget category with full-window screenshots. Brief `docs/_dev/widget-api-audit.md`.
- **Linked type aliases + widget-API consistency** (MERGED) — public aliases render as their
  short NAME, linked to a `.. py:type::` entry (dropped `sphinx_autodoc_typehints`;
  `autodoc_type_aliases` FQN map; `python_use_unqualified_type_names`; a `TypeAliasForwardRef`
  patch). Memories `project_enum_option_typing`, `reference_typed_alias_linking`.
- **Unified data bag** (PR #92) — non-scalar fields carried across Tree/DataTable/ListView
  (SQLite `_bs_data` JSON column; `bs.SerializationError` on non-JSON). Memory `project_data_bag`.
- **Large-file streaming** (PRs #93–#96) — chunked `load()`; pluggable reader/writer registries;
  `FileDataSource` → SQLite working store; `export_formats`. Memory `project_file_source_streaming`.
- **Tree public-API modernization** (PR #91) — recycle-view canvas Tree, `TreeNode` handles.
  Memories `project_tree_row_model`, `reference_treeview_perrow_indicator_state`.
- **Icon rendering + DataTable polish** — ink-metric icon renderer; `Table`→`DataTable` +
  DataSource decoupling. Memories `project_icon_rendering`, `project_table_datasource_coupling`.
- **Tree data-source backing** (PR #97) — `Tree(data_source=, parent_field=)` lazy hierarchy
  from a flat adjacency-list source. Memory `project_tree_datasource_backing`.
- **SqliteDataSource schema inference** (PR #98) — `load()` samples leading rows to infer column
  types (fixes the TEXT-affinity-from-leading-NULL bug).
- **Signal runtime cleanup** — `signal()` single getter; `is_signal()` duck-types. Memory
  `reference_signal_duck_typing`.
- **Preferences store `bs.Store`** — dict-like JSON file-backed prefs; shared `_core/paths.py`.
  Memory `project_persistent_kv_store`.
- **AppSettings flattening** (PR #101) — flat `App()`/`AppShell()` kwargs; `settings=`/`AppSettings`
  gone. See the "FLAT kwargs" gotcha. Memory `project_app_settings_flattening`.
- **Reference docs review pass** (PR #103) — enriched `docs/reference/*` + `localization.rst`;
  `compare` rule; `Form.validate()` runs all rules.
- **Top-level namespace curation + dialogs restructure** (PR #104) — `bootstack` slimmed to the
  compose surface (~85 names); dialog classes → `bootstack.dialogs`. Memory `project_toplevel_api_surface`.
- **Docs build warnings cleanup** (PR #106) — clean-build 40→0; keep it warning-free.
- **API Reference restructure — Stages 1–3** (PR #107) — Diátaxis split: narrative (Widgets +
  Guides) + by-module API Reference; templates/recipe in "## API Reference & Guide page pattern".
  Memory `project_api_reference_restructure`. (Stage 4 homing DONE — see "History".)

## Next up

> The big breaking changes for the **0.1.0 (stable) — API freeze** milestone are
> DRAINED this session (#141/#142/#151/#153/#156/#157/#158 merged; see the
> "0.1.0 API-freeze pass" pointer at the top of "Recently completed"). What's left
> below is the stable-cut closeout + the pre-ship polish backlog + the standing backlog.

### ★ NEXT — Pre-ship polish backlog (#186–#195, filed 2026-06-18)

Ten maintainer-requested items to resolve before shipping 0.1.0 — all filed as
tracked issues (each issue links the relevant impl file + has detail).
**Nine of ten SHIPPED:** #186/#190/#193/#194 (PR **#196**), #195 (PR **#197**),
#188 (PR **#198**), **#189 (PR #199 → folded into the nav reshape PR #202)**, **#187
(PR #203)**, **#191 (PR #204 — themed color tab + `ask_color(value=)` rename)** — all
merged to `main`. **One remains** (its own `feat/*` branch → PR → `main`):

- **#189 `solid` sidebar selection variant — DONE.** Shipped as **`nav_variant`**
  on `AppShell` (PR #199, gated to the standalone nav), then **superseded by the
  navigation reshape (#200, PR #202)**: the variant now lives on
  **`page_nav(variant='ghost'|'solid')`**, standalone-only. See the reshape pointer
  at the top of "Recently completed".
- **#187 StatusBar.add_widget class-only? — DONE (PR #203, MERGED).** Decision:
  **class-only** on BOTH `Toolbar` AND `StatusBar` (`add_widget(WidgetClass, **kwargs)`).
  The two were ALREADY polymorphic in lockstep (not StatusBar-only), so class-only on
  both keeps them consistent while dropping the redundant instance branch (couldn't
  inherit bar density/surface; required a manual attach). No flexibility lost — a
  self-built widget drops in via the container protocol (`parent=bar`, auto-attaches).
  `StatusBar` gained the `_apply_bar_defaults` helper it lacked. **NB the public param
  is annotated `widget_cls: Any` not `: type`** — the bare builtin `type` renders an
  ambiguous `ref.python` cross-ref under `python_use_unqualified_type_names` (collides
  with the many `.type` attrs); the precise `: type` stays only on the private
  `_apply_bar_defaults` (not rendered). Also fixed a stale `StatusBar(fill="x",
  side="bottom")` docstring (would raise under the grid engine) → `horizontal="stretch"`,
  and enriched `docs/tasks/composing-fields.rst` with a **"Subclassing for a reusable
  type"** section (`SearchField(bs.TextField)` via `insert_addon`, justified by exactly
  this change — a container can only build your field if it's a class). Test
  `tests/widgets/public/test_statusbar.py` (3).
- **#192 Color-swatch Select control (feature, larger)** — a `Select`-style
  dropdown rendering color swatches inline (complements `ask_color()`). New widget
  or Select variant — lock shape/naming with the maintainer first.

**SHIPPED detail (this session):** #195 (PR #197) — placeholder renders unmasked
under an input mask; `TextEntryPart` captures the mask char, clears `show` while
the placeholder shows, restores it for real input; PasswordEntry eye-toggle no-ops
while placeholder showing. Test `test_field_placeholder_mask.py`. NB `TextField`'s
public mask kwarg is **`mask=`** (not `show=`). #188 (PR #198) — accented Card
border now **`b.border(surface)`** (a soft stroke derived from the card's own
`{accent}[subtle]` tinted surface), NOT `{accent}_emphasis` (the issue's original
suggestion — rejected as too strong on review). Test `test_card_border.py`.

### Field-family review follow-ups (filed this session — OPEN)

The field family is fully reviewed (see the top "Recently completed" entry). These
additive follow-ups remain — none is a correctness bug:

- **#227 — `Signal` can't round-trip object values** (date/time). `Signal` picks its
  Tk var from the *initial* value's type, so a `date`/`time` lands in a StringVar →
  `Date/TimeField` `signal=` reads back a **string**, and field→signal doesn't fire
  on a programmatic `.value=`. So Date/Time docs deliberately keep `textsignal=`.
  Real fix = a type-aware/codec Signal (relates to the deferred dtype/codec field
  model). NumberField is unaffected (int/float are native Signal types).
- **#232 — PathField dialog-config options as live properties** (`mode`,
  `start_dir`, `file_filters`, `dialog_title`, `default_extension`/`_filename`) —
  construction-only on the wrapper though `PathEntry` supports them live via
  `@configure_delegate`.
- **#234 — SpinnerField↔NumberField parity** — live `min_value`/`max_value`/`step`
  props, `increment()`/`decrement()` methods, `on_increment`/`on_decrement` events.
  May be won't-do (SpinnerField is intentionally simpler) — decide first.

### Slider follow-ups — DONE

Slider `step=` snapping (#210, PR #213) and the RangeSlider `<Tab>` focus-trap
(#211, PR #215) both MERGED. Nothing open here.

### ✅ SHIPPED — Layout redesign (screen-axis grid engine) — MERGED #170

Replaced the Tk pack stack with a **screen-axis** vocabulary on the Tk grid manager:
`horizontal`/`vertical`/`grow` (bare = self, `*_items` = children); edge-name values
(`left`/`center`/`right`/`stretch`) + `space-between`/`-around`/`-evenly`; `HStack`/`VStack`
→ `Row`/`Column`, `Separator`→`Divider`, new `Spacer`; **cross-axis default `center`**;
legacy `fill`/`expand`/`anchor`/`sticky` now RAISE. Post-merge: #171 (GridFrame O(N) build),
#169 (deploy docs on release only), #172 (README/docs-home refresh), #173 (CLI icons on the
public layer + Gallery/MemoryDataSource fixes). Memories `project_layout_redesign`,
`feedback_layout_conversion_rules`, `project_layout_crossaxis_default`, `project_divider_rename`,
`project_dialog_content_builder_native`.

**Live follow-ups (not blockers):**
- **Gallery opt-in keyboard-focus ring** (future) + deferred Gallery perf (debounce
  `<Configure>`, bounded thumbnail-PhotoImage LRU, cache `_fit_caption`). Scope to keyboard
  focus, NOT hover. Memory `project_gallery_focus_ring`.
- **`add_spacer()`→public `Spacer`** still deferred — entangled with `feat/unified-toolbars`
  (internal `Toolbar` is pack-based). Memory `project_unified_toolbars`.

### ✅ SHIPPED — Undecorated window controls + border + maximized-drag — MERGED #175

Undecorated `App`/`Window`/`AppShell` auto-inject a draggable titlebar (min/max/close) +
1px border via `ChromeHostMixin._ensure_default_titlebar()` (layers on `add_toolbar()`, not
a dedicated band); `App` gained `undecorated=`, `Window` gained `window_controls=`; #165
maximized-drag re-anchors under the cursor. Memory `project_undecorated_window_chrome`.

### Toward the 0.1.0 stable release

- **#149** — final public-surface audit + **CHANGELOG** for the stable cut.
- **#150** — test-harness stabilization (the GUI suites need one `App` per process;
  the `.pytest_cache` perms warning on this machine is benign).
- **#155** — Topic-guide technical-writer review pass (the `/reference/*` pages get
  the same no-kitchen-sink edit the how-to guides already had; memory
  `project_user_guide_fleshout`). The maintainer is comfortable with the how-tos.

### Other candidates

- **Docs site fleshout — substantially DONE.** The how-to guides (`docs/tasks/*` —
  getting-input/handling-actions/displaying-data/building-forms/composing-fields/
  dialogs/layout/application-icons + the full `navigation/` set), `getting-started/
  app-structures`, and the production pages (`cli`/`debugging`/`distribution`) are all
  written and substantial. Remaining is only opportunistic: a review pass on
  `installation`/`quickstart` and enrichment of any still-thin page. Memory
  `project_docs_site_fleshout`.
- ~~**Docstring-backtick sweep**~~ — **DONE (PR #182):** 754 RST
  double-backticks → single across 43 `src/` files. Convention is Google + SINGLE
  backticks. Memory `project_docstring_backticks`.
- **Code-review follow-ups #4–#10** — cleanup/altitude items recorded in
  `docs/_dev/widget-api-audit.md` (SelectButton stale value after `options=`; screenshot
  Win64 HWND hardening; group/window/date duplication; Calendar batch-redraw).

**Throwaway demos `development/shell_*_demo.py` stay UNTRACKED** (scratch, not
framework code). Side note logged: a future `Tabs` `variant='secondary'` (top
indicator) — `project_secondary_tab_variant`, a standalone item.

### History — done initiatives

- **Public-API typing sweep — DONE** (branch `feat/api-reference-widgets`, merged via
  PR #109). All widget batches typed (Application → Overlays/Forms/Dialogs): real param
  types, per-widget `variant` Literals sourced from `style/builders/`, typed `on_*`
  payloads (impl signature, not `@overload`), thin docstrings, every public prop/method
  documented. Conventions live in the "API Reference & Guide page pattern" section +
  `docs/_dev/typing-review.md`. Memories `project_enum_option_typing`,
  `project_typed_event_payloads`, `project_variant_type_revisit`. Also shipped here:
  `Tree.find`/`find_all` (predicate or `col(...)` condition; memory `project_tree_find_filter`).
- **API Reference restructure — Stage 4 homing — DONE (PR #109).** The IA was re-cut to a
  semantic-category structure: one page per CONCEPT (Application · Widgets · Reactivity ·
  Events · Data · Validation · Theming · Localization · Scheduling · Shortcuts · Storage ·
  Errors), full-path stub titles, pandas-style card landing; every public name homed,
  guides converted to table-only API sections. Brief `docs/_dev/api-reference-restructure.md`;
  memory `project_api_reference_restructure`. **NEXT (follow-on): flesh out widget Guides
  with examples — the API Reference is a last resort; Guides carry teaching.**
- **Deferred file-streaming items** — background/progressive ingest, keyset pagination,
  auto-index (memory `project_file_source_streaming`).

## Carryover (deferred)

- **Reference docs examples** — LARGELY DONE in PR #103 (errors/scheduling/
  shortcuts/validation enriched; new `localization.rst`). `reference/store.rst`
  already carries the persistence patterns (`from_store`/`update(**kwargs)`,
  store hygiene, version skew, window-geometry-stays-a-flag) from the AppSettings
  work. Remaining: opportunistic enrichment of any still-thin reference page.
  Memories `project_docs_initiative`, `project_app_settings_flattening`.
- **Docs build is now warning-free** (PR #106). ⚠ Keep it that way: incremental
  Sphinx builds MASK warnings — always clean-build (`rm -rf docs/_build`, then
  `sphinx-build -W --keep-going`) to verify. When adding dataclass/attribute
  docstrings, follow the attribute-docstring pattern (NO `Attributes:`/`Args:`
  block for fields) and keep any colon OFF the first line of an attribute
  docstring (see the colon-space gotcha under PR #106 above).

---

## Prior initiative — Sphinx docs + public API audit (MERGED)

Branch `feat/docs-api-improvements`, merged to `main`. Shipped: the docs structure,
the public Table (`DataTable`), the typed-event redesign, the theming + font public
APIs, the DataSource verb rename + filtering DSL, and the observable-query layer.
Full detail lives in git history and memories; only the still-live conventions and
the open backlog are kept here.

### Still-live conventions

- **Docs structure** — top-level navbar is now **4 pillars** (numpy-style):
  **User Guide · Widgets · API Reference · Production** (`docs/index.rst`).
  - **User Guide** (`docs/user-guide/index.rst`) folds the old Getting Started +
    Tasks + Reference sections into ONE pillar with three `:caption:` toctree groups —
    **Getting started** (`/getting-started/*`), **How-to guides** (`/tasks/*`,
    goal-indexed recipes), **Topics** (`/reference/*`, subsystem-indexed usage guides;
    both how-to and topics are example-rich — the split is goal-vs-subsystem, NOT
    recipe-vs-theory, so do NOT call Topics "Concepts"/"Explanation"). The leaf pages
    STAY in their `getting-started/`/`tasks/`/`reference/` dirs (no URL churn); only the
    landing + top toctree changed. The three old section `index.rst` landings are DELETED.
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
  NOT topical nouns. **Topics (`/reference/*`) keep noun/subsystem titles** (`Events`,
  `Data Sources`) — that's correct, not a violation. Keep titles short enough to not
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
- **Public namespace is CURATED (PR #104)** — top-level `bootstack` (`bs.*`) holds
  ONLY what you compose a UI from: every widget, `App`/`AppShell`/`Window`,
  `Signal`, the dialog VERBS (`alert`/`confirm`/`ask_*`/`toast`), and
  `set_theme`/`toggle_theme`. Import everything else from its submodule —
  `from bootstack.data import SqliteDataSource, col`; `from bootstack.style import
  Theme, get_theme_color`; `from bootstack.i18n import L, LV`;
  `from bootstack.validation import ValidationRule`; `from bootstack.events import
  Event, Subscription`; `from bootstack.streams import Stream`;
  `from bootstack.scheduling import Schedule`; `from bootstack.shortcuts import
  get_shortcuts`; `from bootstack.store import Store`; `from bootstack.errors
  import ...`; `from bootstack.types import AccentToken`; dialog CLASSES
  `from bootstack.dialogs import FormDialog`. `MessageCatalog`/`IntlFormatter`/
  `get_current_app`/`Image` are INTERNAL (not public). Do NOT write `bs.Theme`/
  `bs.col`/`bs.SqliteDataSource`/`bs.FormDialog` etc. — they no longer exist at
  top level. Map: the `docs/api-reference/index.rst` landing (public-contract +
  submodule list; `api-overview` was retired into it); guard:
  `tests/test_public_surface.py`. Memory `project_toplevel_api_surface`.
- **Dialogs live in `bootstack.dialogs`** — impl under `bootstack/dialogs/_impl/`,
  public façade `bootstack/dialogs/__init__.py` (verbs + classes).
  `bootstack.widgets.dialogs` is GONE. Internal deep imports use
  `bootstack.dialogs._impl.<module>`.
- **`disabled` on Label** — not appropriate. Label is display-only.
- **`color=` / `background_color=`** — removed. Use `accent=` / `surface=`.
- **`bs.App` / `bs.AppShell` config is FLAT kwargs** (settings-flattening, branch
  `feat/app-settings-flatten`). All former `AppSettings` fields are direct
  constructor kwargs — `theme`, `light_theme`, `dark_theme`,
  `follow_system_appearance`, `available_themes`, `inherit_surface_color`,
  `locale`, `localize_mode`, `window_style`, `macos_quit_behavior`,
  `remember_window_state`, `state_path`, `app_author`, `app_version`. There is
  **NO public `settings=` / `AppSettings` / `app.settings`** (clean break, no
  shim — passing `settings=` raises `TypeError`). `AppSettings` survives only as
  an internal resolved-config holder; `get_app_settings()` is internal-only.
  Read/write config as symmetric `app.*` properties: `app.theme`/`app.locale`/
  `app.title` set live; locale-derived values are flat read-only props
  (`app.locale_date_format`, `app.locale_time_format`, `app.locale_decimal`,
  `app.locale_thousands`, `app.locale_language`). Config-change events:
  `app.on_theme_change(fn)` (→ theme name) and `app.on_locale_change(fn)`
  (→ locale code). Persistence: `bs.App.from_store(store)` (tolerant of version
  skew — filters to known kwargs) + `store.update(theme=...)` write-back. Shared
  impl in `widgets/_core/app_config.py` (`AppConfigMixin`, `APP_CONFIG_KWARGS`).
- **`bs.Signal()` crashes at module level** — must be inside `with bs.App():`.
- **`textsignal=`** — standard kwarg for text-bearing widgets. `signal=` for non-text
  (Slider, Checkbox, etc.). Never expose `textvariable=` / `variable=` publicly.
- **`TTKWrapperBase.__init__` overwrites `self._accent`** — store accent before `super().__init__()`,
  re-assign after.
- **`<<BsThemeChanged>>`** fires after full rebuild (use this). `<<ThemeChanged>>` fires before.
- **Canvas/imperatively-painted widgets — theme repaint:** NEVER bind ttk
  `<<ThemeChanged>>` on the **root/toplevel** — it re-fires **~1400× per rebuild**
  (once per style reconfigure); root-bound × instances = thousands of redraws (was
  the gallery's ~3s toggle lag, PR #180). Re-resolve colors via the **STD
  `Publisher`** (fires once, after rebuild) and **gate the redraw on visibility**.
  `Frame` subclasses: call `self._enable_theme_repaint(self._redraw)` (the shared
  hook — subscribes, gates on `winfo_viewable()`, defers off-screen to `<Map>`,
  releases on `<Destroy>`). Non-`Frame` (Slider/RangeSlider/chrome): publisher +
  own gate. Memory `reference_theme_repaint_mechanisms`. **#177 DONE (PR #181):**
  textarea/code-editor (`StyleRegistry`/`SearchOverlay`/`IndentGuides`) migrated onto
  `<<BsThemeChanged>>`; dead `FloodGauge` deleted. Nothing left on the racy event.
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
- **`content_builder`** fills a PUBLIC content `Column` set as the active parent —
  write the body parent-free (`def build(): bs.Label(...)`), like an App body;
  `Dialog(padding=, gap=)` configures it. `def build(content)` gets an explicit
  handle; old `def build(frame): with bs.Column(parent=frame)` still works (frame
  is the public Column, via the `_RawTkContainer` bridge in `_resolve_parent`).
  bootstack's own verb/Form dialogs render raw and opt out with `_raw_content=True`.
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
- **`Shortcuts` service** — public surface is `bootstack.shortcuts`: the `Shortcuts`
  class, the `Shortcut` dataclass, and the `get_shortcuts()` accessor.
  `register(key, "Mod+S", fn)` + `bind_to(app)` wires the keyboard handler.
  `format_shortcut(spec)` (in `_runtime/shortcuts.py`) resolves display text only
  (no binding side effect) — it is INTERNAL, not exported from `bootstack.shortcuts`.

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
    └── types.py AccentToken, WidgetDensity, SurfaceToken, per-widget variant Literals, etc.
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
with bs.AppShell(title="My App", theme="bootstrap-light") as shell:
    shell.commandbar.add_button(icon="sun", command=bs.toggle_theme)
    with shell.menubar.add_menu("File") as file:
        file.add_action("Quit", shortcut="Mod+Q", on_click=shell.close)
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

⚠ **No colon on the FIRST LINE of an attribute docstring.** napoleon splits the
first line at the first `:` and jams the pre-colon text into a bogus `:type:`
field — SILENTLY mangling the rendered type (it only *warns* when the split also
breaks a backtick pair). A colon on line 2+ is fine. Use an em-dash/period to
introduce an enum list: `"""Side to pack against — \`'top'\`, \`'bottom'\`..."""`,
not `"""Side to pack against: ..."""`. (PR #106 swept all existing offenders.)

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
