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
- **Gallery/Carousel height-floor cleanup (#160)** (this session; PR **#185**,
  MERGED to `main`) — closed out #160 (Gallery/Carousel collapse to ~0 height in a
  non-expanding/scrollable parent). The floor itself shipped in **PR #161** and is
  **sound** (`pack_propagate(False)` on the frame + `configure(height=floor)`, inner
  canvas `fill="both", expand=True` → a true minimum `grow`/`expand` still grows
  past) — left untouched. This PR added the **regression test the issue asked for**
  (`tests/widgets/public/test_media_height_floor.py`, 8: non-zero floor reqheight —
  Gallery `360`, Carousel `267`; no collapse inside a `ScrollView`; floor-is-a
  -minimum-not-a-freeze via the expand-packed inner canvas; `rows`/`height`/
  `aspect_ratio` move the floor) + **hardened two magic numbers** into named
  constants (`carousel._FLOOR_STAGE_WIDTH=400`, `gallery._CAPTION_H=24`;
  value-preserving) + clarified the `aspect_ratio` docstring (larger ratio →
  shorter floor). **Deliberately NOT changed:** the Gallery `rows=` vs Carousel
  `aspect_ratio=`/`height=` API asymmetry (each is the natural knob; a unified
  `min_height=` would be scope creep). Memory `project_picture_suite`.
- **Tab overflow handling (#168)** (this session; PR **#184**, MERGED to `main`)
  — tabs that exceed the strip now stay
  in a **scrollbar-less scrolling line** (wheel scrolls along the axis; the
  selected tab auto-scrolls into view) with a trailing **chevron overflow menu**
  listing the off-screen tabs (with icons) that scrolls the picked one into view.
  `⌄`/`+` are pinned outside the scroll region (`+` outermost, `⌄` next), ghost
  buttons with a gap before them: horizontal = compact icon-only `⌄`; vertical =
  full-width left-aligned **`⌄ More`** matching the rows + **`+ New`**.
  **Always-on — NO `overflow=` option** (clipped tabs are never desirable; the
  plain non-scrolling strip is kept ONLY for `tab_width='stretch'`, which always
  fits). New **`max_tabs=`** disables the add button at the limit (re-enables on
  removal). Axis-aware (both orientations); built on the existing `ScrollView`
  (`scrollbar_visibility='never'`). **Three framework fixes surfaced while
  building:** (a) **`PackFrame` skips the full forget/repack on child removal
  when `gap==0`** (Tk keeps sibling order on its own) — kills a tab-close
  **flash**; a win for any gap-less PackFrame. (b) **`PageStack.navigate`
  pre-sizes the target page before a SWAP** (`update_idletasks`, guarded to
  `self._current is not None` so the initial build — all first-mounts — isn't
  serialized into a visible **slow-motion** render) — kills the add+select
  content-area **jump** (a pre-existing PageStack quirk, reproduced in the old
  non-scrolling path too). (c) **`_scroll_into_view` defers via retry** until the
  new tab is positioned (winfo_x ready) instead of a forced synchronous flush.
  Demo Navigation page wires `+` to add+select and showcases H/V overflow + the
  `max_tabs` limit. Tests `tests/widgets/public/test_tabs_overflow.py` (10). The
  `+` only fires a `tab_add` event — the app supplies the new tab (it never
  "did nothing"; the demo simply hadn't wired a handler).
- **ContextMenu/Tooltip cover container children (#166)** (this session; PR
  **#183**, MERGED to `main`) — Tk events don't bubble, so a gesture bound to a
  **container** target (e.g. a `Card`) only fired over the container's bare area,
  never over its children. Fix = new shared helper **`propagate_target_bindings(target)`**
  in `_runtime/utility.py`: adds the container's own **path-name bindtag** (the tag
  `widget.bind(...)` registers under) to every descendant in the same toplevel, so the
  trigger/hover fires anywhere inside. Inserted **after** each child's own path tag
  (child bindings keep precedence); **idempotent**; **skips nested toplevels** (the
  menu's own popup is parented under the target). Wired into
  `ContextMenu._bind_trigger` (covers all platform gesture variants at once — it's
  tag-based) + `Tooltip.__init__`. `Tooltip` also gained a **crossing-aware `<Leave>`**
  (`_pointer_within_target` via `winfo_containing`) so moving container→child doesn't
  flicker the tip; `<ButtonPress>` split into its own unconditional-hide handler.
  **Limitation:** children added *after* attach aren't auto-tagged (re-attach covers
  it). Tests `tests/widgets/public/test_overlay_container_coverage.py` (5). Memory
  `reference_bindtags_underused` — **bindtags are underused in the architecture;
  TODO: an eval pass to find recursive/duplicated `.bind()` a shared bindtag could
  simplify** (a `BindtagsMixin` already exists, barely used).
- **Theme-repaint cleanup (#177) + docstring-backtick sweep** (this session; PRs
  **#181**/**#182**, both MERGED to `main`) — **#181**
  (`fix/theme-repaint-cleanup`, closes #177): migrated the code-editor's
  `StyleRegistry`/`SearchOverlay`/`IndentGuides` off the racy ttk `<<ThemeChanged>>`
  (fires mid-rebuild → stale colors) onto **`<<BsThemeChanged>>`** (fires once,
  post-rebuild) — the pattern `pygments_highlighter`/`sidebar` already use; kept the
  deliberate `<<EditorBgChanged>>` notify. Cleanup uses the repaint-hook convention
  (**NO `is self` guard, idempotent unbind on any `<Destroy>`**) — GOTCHA: in this
  widget tree a container's OWN `<Destroy>` is not delivered to its instance binding
  (only a descendant's is), so an `is self` guard silently skips cleanup. Also
  deleted dead **`FloodGauge`** (zero imports) + its `tools/gen_api_docs.py` entry.
  **#182** (`chore/docstring-backticks`): swept **754** RST double-backtick literals
  → single backticks across **43** `src/` files. Reusable approach: a Python regex
  matching **runs of exactly two backticks** (`(?<!`)``(?!`)`) — leaves ```` ``` ````
  fences AND `:class:`/`:doc:`/`:ref:` cross-ref roles intact (roles are DELIBERATE
  links, not stray); byte-safe write preserves CRLF+BOM. **NB ripgrep/Grep can't do
  this** (Rust regex has no lookbehind → silently 0 matches); use Python. Verified
  warning-free `-W` docs build. Memory `project_docstring_backticks`.
- **Undecorated window chrome + theme-repaint perf** (prior session, all merged) —
  **#162/#165** (PR #175): undecorated `App`/`Window`/`AppShell` auto-inject a
  draggable title bar (controls) + border; `App` gained `undecorated=`, `Window`
  gained `window_controls=`; maximized-drag re-anchors under the cursor. (The #162
  handoff plan was stale — the dedicated band had been retired + `menubar`/
  `commandbar` removed in favor of `add_toolbar()`.) **Theme-repaint perf**
  (#167 → PRs #176/#178/#179/#180): canvas widgets kept the old theme's colors /
  toggling was slow. Root causes + fixes — (a) Gauge/Meter bound the early ttk
  `<<ThemeChanged>>` → STD publisher (post-rebuild); (b) Slider/RangeSlider +
  window chrome bound ttk `<<ThemeChanged>>` on the **root/toplevel**, which
  re-fires ~1400× per rebuild × instances → **gallery toggle ~2960ms → ~580ms**;
  (c) new `Frame._enable_theme_repaint` hook gates 8 canvas widgets to on-screen
  repaints (off-screen defers to `<Map>`) + fixed 4 widgets that self-bound
  `<<BsThemeChanged>>` and never recolored; (d) Gauge supersample capped on HiDPI;
  (e) calendar reuses weekday-header labels (nav 5.8→2.7ms). **RULE in gotchas.**
  Memories `project_undecorated_window_chrome`, `reference_theme_repaint_mechanisms`.
  **#177 DONE (PR #181):** textarea/code-editor migrated off the racy
  event + dead `FloodGauge` deleted — see the top entry.
- **Pre-release `0.1.0a10` shipped + docs deploy fixed** (PRs #139–#140 merged;
  release built from `main`) — **Toast split** (PR #139): the kitchen-sink Toast
  became three public widgets over one engine — `toast()` (single-line, icon
  opt-in, corner-stacked on the current monitor), `Notification` (titled card),
  `Snackbar`/`snackbar()` (neutral surface, window-bottom anchored, accent only on
  the action); emphasis-shade text (`{accent}_emphasis`), `on_color` light-mode
  contrast fix (info cyan → black text). **Pre-release readiness** (PR #140): full
  **gallery/demo-app widget coverage** (Media/MenuButton/SelectButton/ToggleButton/
  RadioToggleButton/RangeSlider/ListView/ScrollView/PageStack/Notification/Snackbar/
  ContextMenu/shell chrome) + a **`ToggleButton(icon=)`** framework add (fallback for
  both states; `on_icon`/`off_icon` override); `installation.rst` rewrite (`pip
  install --pre`, Tk-install checks, version pin); a **pre-release announcement
  banner** (conf.py `html_theme_options`); **README** refresh (banner, `--pre`,
  hero swap, Table→DataTable / Toolbar→CommandBar fixes); `requirements.txt` /
  `requirements-dev.txt` / `pyproject.toml` deps + description sync; app-settings
  doc review. Release via `bump-my-version` (a9→**a10**, tag `v0.1.0a10`) → PyPI
  trusted-publish + GitHub Release (both ✓). **Docs deploy fix** (commit `5959e7b3`,
  direct to `main`): `docs/CNAME` (`bootstack.org`) had been deleted in `13c01d4d`
  (old mkdocs copied `docs/` to the site root; **Sphinx does not**) — restored it +
  `html_extra_path = ["CNAME"]`; also reverted the docs trigger `tags:v*`→`branches:
  [main]` because the `github-pages` environment protection **rejects tag
  deployments**. `bootstack.org` now serves HTTP 200 with the CNAME at root.
  Memory `project_prerelease_readiness`, `project_toast_notification_split`.
  **FOLLOW-UPS:** (1) workflow action versions bumped to the Node-24 majors ahead of
  the 2026-06-16 cutoff — **DONE**, PR #141 (`checkout@v6`/`setup-python@v6`/
  `upload-artifact@v7`/`download-artifact@v8`/`upload-pages-artifact@v5`/
  `deploy-pages@v5`/`action-gh-release@v3`). (2) legacy ttkbootstrap naming purge —
  **DONE** (branch `chore/cleanse-ttkbootstrap`): `bootstyle*.py`→`style_resolver.py`/
  `style_builder_*.py`, `Bootstyle`→`StyleResolver`, `BootstyleBuilder*`→`StyleBuilder*`,
  dead dash-string parser + `bootstyle` config-key path deleted, exceptions unified onto
  the public `bootstack.errors.BootstackError` (Navigation/Theme/StyleBuilder now public;
  Tabs aligned to `NavigationError`), `TTKBOOTSTRAP_DEBUG`→`BOOTSTACK_DEBUG`. (3)
  docstring-backtick sweep — **DONE (PR #182)**, see top entry. (Toast
  woven into the user-guide how-tos — **DONE**, PR #140 commit `d95d298a`.)
- **0.1.0 API-freeze pass — breaking changes drained + ThemeToggle + media floor**
  (this session; PRs #141–#161, all merged except #161 in review) — cleared the
  "0.1.0 (stable) — API freeze" milestone of breaking changes ahead of the stable
  cut: **workflow action bump** (#141, Node-24 majors) · **ttkbootstrap naming purge**
  (#142, `chore/cleanse-ttkbootstrap` — see prerelease pointer) · **clipboard scope**
  (#151 — moved the global clipboard helpers off `PublicWidgetBase` to a lean
  `bootstack.clipboard` module; memory `project_clipboard_api_scope`) · **nav
  missing-key errors** (#153 — `NavigationError` raised uniformly on a missing/
  duplicate key across Tabs + AppShell nav) · **`Theme.from_existing(base, …)`**
  (#156 — derive a theme/family from an existing base; required `base=`) · **Signal
  subscribe handle** (#157 — `Signal.subscribe()` now returns a cancelable
  `streams.Handle`, unifying with events/streams; memory
  `project_signal_subscribe_subscription`) · **VariantToken retirement** (#158 —
  the universal `VariantToken` is gone; each widget uses its own per-widget `variant`
  Literal; memory `project_variant_type_revisit`). Then **`ThemeToggle`** (#159,
  merged) — a stateless sun/moon `Button` that flips the theme on click and re-syncs
  its icon on `<<BsThemeChanged>>` (so programmatic theme changes update it too);
  `light_icon`/`dark_icon`/`variant`/`density`/`accent`; added to `bootstack.*`;
  `CommandBar.add_theme_toggle()` + container protocol (`_child_master`/`guide_layout`)
  on CommandBar & StatusBar, both `add_widget(Class, **kwargs)`-polymorphic; swept
  hand-wired toggles across docs/examples/CLI. Last, **media min-height** (#161,
  `feat/media-min-height`, in review) — `Gallery`/`Carousel` collapsed to ~1px in a
  non-height-imposing parent (ScrollView/auto-fit window) because the public wrappers
  freeze the frame with `pack_propagate(False)`; fix configures a content-derived
  height floor on the frame itself (Carousel: `height=`/`400÷aspect_ratio`; Gallery:
  `rows×row_h`). New params `Carousel(aspect_ratio=1.5, height=None)`, `Gallery(rows=2)`;
  demo Media page reordered (Carousel above Gallery — Gallery swallows the wheel event).
  Memory `project_picture_suite`.
- **AppShell + navigation clean-slate rewrite SHIPPED** (PRs #133–#136, all merged;
  in `0.1.0a10`) — the VS Code-style **rail + swappable sidebar + content** rewrite
  landed and the public **`bs.AppShell` was swapped onto the new `Shell`** (#135),
  **dropping the standalone `bs.SideNav`** (`SideNavHeader`/`SideNavSeparator` stay,
  used by `NavPanel`). Sidebar = three shapes: flat-static (`add_page`) ·
  grouped-static (`add_header` muted label) · data-bound (`list_nav`/`tree_nav`); the
  Revision-3 accordion was built then **cut** (spec Revision 4). Scrollable `NavPanel`
  (footer pinned, overflow-gated thin scrollbar), neutral selection + `accent_selection`
  opt-in, pixel-ellipsis truncation. Statusbar + menubar/command bar wired + styled;
  `Workspace` context-manager; public façade (`commandbar`/`nav`/`pages` + window
  controls). **Companions in the same release:** **theme/Bootstrap-alignment v2**
  (#137 — v2 theme-family model, Bootstrap-aligned colors, color-independent sidebar
  selection, accent defaults) · **thin-scrollbar public exposure** (#138 —
  `ScrollbarVariant` alias, list widgets default to thin) · **nav-patterns docs**
  (#136 — standalone `StatusBar` guide + AppShell nav-pattern articles). Spec
  `docs/_dev/appshell-navigation-spec.md` (Revision 4). Memories
  `project_appshell_sidenav_refactor`, `project_theme_bootstrap_alignment`,
  `project_thin_scrollbar_initiative`, `project_nav_patterns_section`.
- **Media widget suite — Picture / Gallery / Carousel / Avatar** (PRs #126–#132,
  all merged) — a family of media-display widgets built on the public `Image`
  handle, in a new **Media** docs category. **`Picture`** (#126) is the display
  atom: object-fit modes (`contain`/`cover`/`fill`/`none`/`scale-down`),
  responsive resize, antialiased rounded corners, animated-GIF playback (via
  `Schedule`), typed `on_load`/`on_error` + `on_click`; the shared
  `widgets/_impl/composites/_image_fit.py` helper (fit/round/`resolve_pil`) was
  extracted here. **`Gallery`** (#127) is a **record-native recycling thumbnail
  grid** (reuses `items=`/`data_source=`, the universal `.selection`,
  `select_items`/…; `image_field`/`caption_field`; responsive auto-columns;
  accent selection ring). **`Carousel`** (#128) is a one-at-a-time stepper —
  slide/fade transitions (own canvas, two-image `canvas.move` / `Image.blend`),
  `corner_radius` rounds the **container** (a fixed corner-mask), **neutral** dots
  auto-switching to a count past 8 slides, `data_source`/`reload`,
  `on_change`/`on_item_click`. **`Avatar`** (#132) is an image-or-initials
  identity badge (circle/rounded/square; initials via Tk text in the app UI font;
  image-load fallback). Plus: an **image-subsystem review** (#129 — fixed a
  Gallery global-cache leak, added Gallery theme handling, Carousel
  parity/edge-cases); the **`on_select` rename** (#130 — `on_selection_changed`
  (ListView/DataTable/Tree) + `on_date_selected` (Calendar) → `on_select`,
  present-tense convention); and **theme-aware demo videos** (#131 — PageStack +
  Carousel heroes are now `bs-video-light/dark` MP4s, with a `.gitignore`
  exception). Memories: `project_picture_suite`, `project_avatar_widget`,
  `project_doc_demo_videos`, `project_image_subsystem_review`,
  `project_event_naming_revisit`. Brief `docs/_dev/picture-suite.md`. **Deferred**
  (in the brief/memories): `Image.from_url()` + async/off-thread load (Phase 1.5),
  a silent video source via `bootstack[video]` (Phase 2), a splash screen, an
  `_ImageService._cache` LRU cap, animated-GIF carousel slides, more demo videos
  (Toast/Tooltip/Tabs/Accordion are the Tier-1 candidates).
- **Public Image/Icon API + AppIcon + field signals + toml cleanup** (PR #125,
  merged; reviewed) — new public
  **`bootstack.images`**: a toolkit-free **`Image`** handle (`open`/`from_bytes`/`from_pil`,
  lazy materialize, theme-following), **`get_icon`/`list_icons`**, and **`AppIcon`** (a
  glyph on a rounded tile) that **`App`/`Window` accept as `icon=`** and that exports
  **`.ico`/`.icns`/`.png`** via `save()` for packaging. Live **`icon`/`image` property
  setters** on Label/Button/MenuButton/SelectButton; the icon **spec** `{name,size,color}`
  is public via `bootstack.types` (**`Icon`/`IconSpec`**, color resolves theme tokens).
  **AppIcon render** is the hard-won part: size-aware `shape="auto"` (glyph-only at small
  title-bar sizes, **tile** from taskbar size up), **integer-ratio tile supersampling**,
  glyph drawn at **native display size + pixel-aligned** (`_render_icon(align=)`),
  size-dependent padding, and **DPI-matched sizes baked into the `.ico`** (the small-size
  crispness fix — true per-size sharpness still needs hand-drawn grid-aligned art).
  Ships the **`bootstack appicon`** GUI designer and **`[build.icon]`** glyph generation.
  Also: **`Window(parent=)`** + anchored **`Window.show(anchor_to=, anchor_point=, …)`**;
  **reveal-after-settle** window show (no open-time shift); **typed `signal=`** on
  Number/Date/Time fields (binds the parsed value, not text; committed separately);
  **`bootstack.toml` scoped to a build/scaffold manifest** (runtime **`[settings]`**
  removed — runtime config is `App()` kwargs + `Store`); framework lifecycle fixes
  (scheduler descendant-destroy guard, grid prune-on-destroy, clipboard helpers); public
  **file-dialog verbs** (`ask_save_file`/`ask_open_file`/`ask_open_files`/`ask_directory`).
  Docs: `reference/images` guide, `api-reference/images`, the **Application Icons** how-to
  (`tasks/application-icons` — runtime-vs-build-icon distinction + glyph/color tips). A
  **pre-commit review (5 agents)** found+fixed 2 HIGH (field-Signal leak; Signal type-
  mismatch crash) + 2 MEDIUM (image-clear theme-binding leak; `show()` alpha-not-in-finally)
  + nits. Memories `project_image_icon_public_api`, `project_field_value_signal_dtype`,
  `project_app_settings_flattening`. Follow-up: a `Picture` display widget
  (animated GIF / splash) on a separate branch.
- **Menu bar + command bar** (PR #124, merged) — cross-platform **`app.menubar`**
  (also `window.menubar` / `shell.menubar`): a single-layer menu model with two
  renderers — a themed in-window strip on **Win/Linux** and the **native global menu
  bar** (`NSMenu`) on **macOS** — behind one API. Build imperatively
  (`with app.menubar.add_menu("File") as f: f.add_action(...)`) or declaratively
  (`app.menubar.load([...])`); item types `action`/`check`/`radio`/`separator`;
  `shortcut=` displays AND binds (patterns auto-register via the `Shortcuts` service;
  macOS uses word-form accelerators). Plus **`app.commandbar`** (the widget renamed
  `Toolbar`→**`CommandBar`**) sharing the top chrome row, with **`menu_layout`**
  (`'fused'` default/`'stacked'`), **`chrome_surface`** (blend via `'background'` /
  brand via an accent — NOT `'content'`, see memory), **`chrome_divider`**. **Breaking
  (pre-release):** legacy region-bar **`bs.MenuBar` REMOVED**; **`Toolbar`→`CommandBar`**;
  accessors **`app.menu`→`app.menubar`**, **`app.toolbar`→`app.commandbar`**
  (`shell.toolbar`→`shell.commandbar`); `MenuManager`/`create_menu` retired;
  `MenuHostMixin`→`ChromeHostMixin`. **macOS menus are text-only** (icons mismatch the
  system hover foreground). Internal composite + ttk style stay `Toolbar`. Tests under
  `tests/widgets/public/test_menu_*` + `test_window_chrome` (run GUI modules one at a
  time — one `App` per process). Memory `project_menu_redesign`; brief
  `docs/_dev/menu-redesign.md`. Follow-up: `project_macos_window_chrome` /
  `docs/_dev/macos-window-chrome.md` (native window chrome — not started).
- **Widget detach/attach** (PR #123, merged) — public **`detach()` / `attach()` /
  `is_attached`** on every widget: pull a placed widget out of its layout and put it
  back **without destroying it**, across all three geometry managers (pack/grid/place).
  Revives the deferred `<Map>`/`<Unmap>` lifecycle as **`on_attach` / `on_detach`** (now
  earned by a real control pair; they propagate through ancestors). `guide_layout` records
  a **`Placement(method, master, options, index)`** snapshot on each child
  (`widgets/_core/container.py`); `is_attached` is backed by `winfo_manager()` (no flag).
  **pack ordering:** `detach()` snapshots the index among currently-attached siblings,
  `attach()` translates via new `resolve_pack_order` → `before=slaves[index]`; new public
  **`index=`** pack knob (works at construction too), `before=`/`after=` accept public refs.
  **grid gotcha:** uses `grid_forget` + full reconstruct from stored options — `grid_remove`'s
  "remembered" state rejects an explicit re-grid. Also shipped **`attached=False`** ctor arg
  (build a widget hidden in place — records placement, skips mapping, no flicker; a later
  `attach()` lands it in its declared slot). **Docs:** new "Detaching and reattaching" section
  in `reference/events.rst`; the inert placement API is **hidden on the top-level window
  classes** (App/AppShell/Window are `_auto_place=False`, never placed → detach no-ops,
  attach raises) via a shared `_templates/autosummary/toplevel.rst` excluding the 5 members.
  Tests `test_attach_detach.py` (20 cases; ONE module-scoped App — multi-App-per-process
  crashes). Memories `project_widget_attach_detach`; backlog `project_inherited_base_api_docs`
  (every widget page repeats the inherited base surface — consolidate onto one shared page).
- **Select grouping + popup height cap** (PR #122, merged) — the LAST piece of the
  option-databag orbit. Opt-in **`Select(group_by="field")`** clusters the popup
  under **bold, verbatim** section headers + separators (none above the top group;
  leading dividers suppressed during search). **Key design (maintainer-chosen over a
  reserved `"group"` key):** `group_by` NAMES any field already in the option's flat
  record (a bag key, or `text`/`value`) — like `Tree(parent_field=)` / pandas
  `groupby`, reusing data the options carry instead of duplicating it. Nothing is
  reserved; `normalize_option` is untouched. **Presentational only** —
  `value`/`.selection`/`.options` unaffected; the field rides in the bag. Clusters by
  first-appearance order; an option missing the field renders headerless. Also shipped
  **`max_visible_items=N`** (cap the popup at ~N rows before it scrolls); both have
  symmetric read/write props. New `cluster_records`/`record_field` in
  `widgets/_core/options.py`; the search filter was extracted to a testable
  `_apply_search_filter`. Fixes found along the way: popup auto-scrolled past the first
  header on open (render-order-aware highlight + a header-reveal scroll) and a negative
  popup geometry when opened before layout (width clamp). DEFERRED: a `group_by`
  callable + grouping for SelectButton/RadioGroup/ToggleGroup (Select-only this pass).
  Tests in `test_select_options.py`; Select guide + example + screenshots updated.
  Memory `project_select_options_databag`.
- **Universal `.selection` on the record-native widgets** (PR #120, merged) —
  extends the option family's polymorphic `.selection` accessor (PRs #114–#118) to
  **ListView / DataTable / Tree**, which carried records but exposed them under
  divergent names of divergent kinds (`get_selected()` method / `selected_rows` /
  `selected_nodes`). **Breaking, clean break (no shim):** those three are GONE;
  `.selection` is now universal and **polymorphic by `selection_mode`** — single →
  `dict | None` (Tree: `TreeNode | None`), multi → `list[dict]` (Tree:
  `list[TreeNode]`), none → `None`. ListView/DataTable return record dicts (the
  bag, indexed by key); Tree returns node **handles** (bag at `node.data`). Each
  wrapper stores `self._selection_mode` and collapses the internal's always-list to
  the singular shape. **Behavior note:** DataTable defaults to
  `selection_mode='single'`, so `table.selection` is a `dict | None` by default (the
  old `selected_rows` was always a list). Also closed the symmetric **write-side
  gap**: new **`ListView.select_items(ids)` / `deselect_items(ids)`** (by record id,
  single-mode replace / multi-mode add) mirroring `DataTable.select_rows` /
  `deselect_rows` — ListView previously had only `select_all`/`clear_selection`.
  Both wrap source mutations in `_silence_source()` and emit ONE `<<SelectionChange>>`
  (a single-mode replace does `deselect_all()` + `select()` but must not double-fire
  — regression-tested). Verb+noun naming stays per-widget vocabulary (rows/items/
  nodes) **by design** — not a divergence to reconcile. Tree needed nothing
  (`select(node)`/`deselect(node)` is the right node-handle primitive). Tests in
  `test_listview.py`/`test_datatable.py`/`test_tree.py`; guides updated. Memory
  `project_option_databag`; brief `docs/_dev/option-databag.md`.
- **Field value/text/label contract + selection data bag** (PRs #113–#116, all
  merged) — a framework-wide field-widget contract and a shared, extensible option
  shape, built across four PRs:
  - **#113** code-review follow-ups #4–#10 (SelectButton value reconcile, ctypes HWND
    types, shared `SelectionGroupMixin`, uniform `BaseWindow.close`, shared
    `coerce_date`, Calendar redraw coalescing).
  - **#114** the **value/text/label** model: `label` = caption beside a control,
    `text` = formatted display (new public **read-only `.text`** across the field
    family — TextField/NumberField/…/Select/CodeEditor), `value` = raw datum.
    LOAD-BEARING RULE: **never derive value from text** (doing so broke
    `TimeField.value` → returned the formatted string instead of `datetime.time`;
    `SelectBox.value` now defers to `Field.value` and the option map only layers on
    for *decoupled* options). Shared `Option = str | tuple | OptionDict` shape +
    `normalize_option`; `SelectBox.strict_value` flag (public `Select` strict,
    embedded SelectBoxes lenient). Catalog is `.options` (`.texts`/`.values` dropped).
  - **#115** `.text` (selected label) on RadioGroup/ToggleGroup (mirrors `value`:
    str | set in multi); `text_for(value)` on the internal composites.
  - **#116** the **option data bag**: `normalize_option` no longer rejects unknown
    dict keys (recognized = `text`/`value`/`icon`/`disabled`; everything else is
    carried data); a universal polymorphic **`.selection`** accessor returns the
    selected option's full record dict (`dict | None`, or `list[dict]` for
    ToggleGroup multi). RadioGroup/ToggleGroup keep records via `SelectionGroupMixin`.
  Memories `project_field_value_text_model`, `project_option_databag`. Briefs:
  `docs/_dev/option-databag.md` (+ the value/text model in the memory).
- **Widget API gap audit + documentation** (PR #111, merged; review follow-ups
  #4–#10 shipped in PR #113) — audited
  all ~49 public widgets vs their `_impl/` internals for unexposed capability and fixed
  the high-value gaps: widget lifecycle (`destroy`/`on_destroy` on `PublicWidgetBase`,
  `<Destroy>` mapping); a `WindowControlsMixin` (`close`/`show`/`hide`/`minimize`/
  `maximize`/`set_fullscreen`/`set_topmost`/`on_close`) on App/AppShell/Window — **AppShell
  is now a `PublicWidgetBase`**, Window gained a live `title`; RadioGroup/ToggleGroup
  management (`remove`/`configure_item`/`__len__`/`__contains__`, RadioGroup live `title`);
  live properties (Gauge `min/max_value`, SelectButton `options`, Calendar/DateField date
  constraints — internal `set_*` mutators); §2c/§2d param + kwargs-leak fixes; 3 behavioral
  bugs (RangeSlider low/high clamp, NumberField `clear()`→`None`, Form `field_variable()`
  removed). Plus dark-mode window-border theming (`change_border_color`) and the new
  **Application** widget category with full-window DWM screenshots (`bs-window-screenshot`
  CSS; `take_screenshots.py` `_capture_full_window`). A high-effort `/code-review` fixed 3
  more correctness bugs. Brief: `docs/_dev/widget-api-audit.md`. DEFERRED (recorded in the
  brief): Toolbar/MenuBar return-handle rework + AppShell façades, option-databag
  enumerators, review follow-ups #4–#10. Memories `project_widget_attach_detach`,
  `project_docs_site_fleshout`.
- **Linked type aliases + widget-API consistency** (merged to `main` this session
  via rebase) — public type aliases now render as their short NAME, **linked** to a
  `.. py:type::` entry on the API-ref page, framework-wide (was: inline-expanded
  Literals, or empty `autosummary` summaries). The recipe, after a long debugging arc:
  (1) **source consistency** — promote recurring inline Literals to named aliases
  (`Orient` reused; new `IconPosition`/`SelectionMode`/`ExportScope`/`ExportFormat`;
  `ButtonVariant` for the whole button family — which fixed Button/ButtonGroup *missing*
  `'default'`); export `AccordionVariant`/`Region`/`ThemeMode`/`SeverityToken`. (2)
  **conf.py** — DROP `sphinx_autodoc_typehints` (it printed alias values as inert text,
  blocking linking) → core autodoc; `autodoc_type_aliases` maps each alias to its FQN;
  `python_use_unqualified_type_names = True` (short display, keeps link); and a 4-line
  `TypeAliasForwardRef.__init__` patch giving it `__module__`/`__qualname__` (Sphinx
  9.1 leaked its `repr` when the alias was nested in a union — this was the one real
  Sphinx gap). 6 API-ref pages converted to `py:type` catalogs. Verify: `-W` clean +
  `python_use_unqualified_type_names` keeps names short + grep built pages for
  `TypeAliasForwardRef` (must be 0). Memory `project_enum_option_typing`.
  Widget-API fixes bundled in: MenuButton/ContextMenu `command` Tk-leak (item dicts now
  take clean `on_click`, translated); MenuButton/ToggleButton button text `label`→`text`
  (controls keep `label`); `ColumnSpec.editor` `str`→`EditorType`; ContextMenu
  completeness pass (+7 positioning/sizing params, +4 item methods). DEFERRED: rename the
  menu item *type* `'command'`→`'action'` (Tk-ism, but a deliberate public name).
- **Unified data bag** (PR #92) — undisplayed/non-scalar fields carried across
  Tree/DataTable/ListView; SQLite hides non-scalars in a `_bs_data` JSON column;
  `bs.SerializationError` on non-JSON values. Memory `project_data_bag`.
- **Large-file streaming** (PRs #93–#96) — chunked `load()`; pluggable
  reader/writer registries (CSV/TSV/JSON/JSONL/XML built in; Parquet/Feather/HDF5
  via extras); `FileDataSource` ingests a file into a SQLite working store; source
  `save()` + DataTable `export_formats`. Memory `project_file_source_streaming`
  (deferred: background ingest, keyset pagination, auto-index).
- **Tree public-API modernization** (PR #91) — recycle-view canvas Tree, `TreeNode`
  handles (icon+label rows). Memories `project_tree_row_model`,
  `reference_listrow_button_focus_stick`, `reference_treeview_perrow_indicator_state`.
- **Icon rendering + DataTable polish** — ink-metric icon renderer; `Table`→
  `DataTable` rename + DataSource decoupling. Memories `project_icon_rendering`,
  `project_table_datasource_coupling`.
- **Tree data-source backing** (PR #97) — `Tree(data_source=, parent_field=, ...)`
  projects a flat adjacency-list source as a lazy hierarchy (per-node loaders via
  `src._query`, batched has-children chevrons; mutually exclusive with `nodes=`).
  Impl `widgets/_impl/composites/tree/source_binding.py`. Memory
  `project_tree_datasource_backing` (deferred: child pagination, tree filtering,
  auto-refresh, native protocol, doc page).
- **SqliteDataSource schema inference** (PR #98) — `load()` samples leading rows
  (`_SCHEMA_SAMPLE_SIZE=1000`) to infer column types, fixing the
  TEXT-affinity-from-leading-NULL bug surfaced by Tree backing. Tests
  `tests/data/test_schema_inference.py`. (`_ensure_table` still infers from one
  record — inherent.)
- **Signal runtime cleanup** (`feat/signal-cleanup`) — `signal()` is the single
  getter; removed `.get()` + the `__getattr__` Tk proxy; `set()` widens int→float;
  `subscribe(immediate=)` propagates errors. `is_signal()` now duck-types on
  `var`/`subscribe`/`set`/callable. Memory `reference_signal_duck_typing`.
- **Preferences store `bs.Store`** (`feat/store`) — public dict-like JSON
  file-backed prefs store; write-through atomic saves, JSON-only values, no App
  required; lives at `<config>/<app>/<name>.json` via shared `_core/paths.py`.
  Memory `project_persistent_kv_store`.
- **AppSettings flattening** (PR #101) — all settings are flat `App(...)`/
  `AppShell(...)` kwargs; `settings=`/`AppSettings`/`app.settings` GONE (raises
  `TypeError`); symmetric `app.*` properties via `AppConfigMixin`; `from_store` +
  `Store.update(**kwargs)`. See the "FLAT kwargs" gotcha. Memory
  `project_app_settings_flattening`.
- **Reference docs review pass** (PR #103) — enriched `docs/reference/*` + new
  `localization.rst`; implemented the `compare` validation rule, made
  `Form.validate()` run ALL rules on submit, fixed two `IntlFormatter` bugs. Tests
  `tests/test_validation_rules.py`, `tests/test_intl_format.py`.
- **Top-level namespace curation + dialogs restructure** (PR #104) — top-level
  `bootstack` slimmed to the compose surface (~85 names); primitives moved to
  submodules; dialog classes → `bootstack.dialogs`; clean break. See the "Public
  namespace is CURATED" gotcha. Memory `project_toplevel_api_surface`.
- **Docs build warnings cleanup + global-items/verb audit** (PR #106) — clean-build
  39 warnings+1 error → 0 (attribute docstrings; colon-on-first-line root cause —
  see Code standards; docutils nits); renamed `supported_extensions`→
  `supported_read_extensions`; demoted internal style accessors. Keep clean-build
  warning-free.
- **API Reference restructure — Stages 1–3** (PR #107 + `feat/api-reference-stage2`,
  merged) — Diátaxis split: narrative (Widgets + Guides) + unified by-module **API
  Reference** (autosummary mirroring each `__all__`). All 10 subsystem API-ref pages
  built (each the autodoc home); all 11 `reference/*` pages converted to Guides.
  Templates + recipe locked in "## API Reference & Guide page pattern" below. Brief:
  `docs/_dev/api-reference-restructure.md`; memory `project_api_reference_restructure`.
  **NEXT: Stage 4 (in progress — see below).**

## Next up

> The big breaking changes for the **0.1.0 (stable) — API freeze** milestone are
> DRAINED this session (#141/#142/#151/#153/#156/#157/#158 merged; see the
> "0.1.0 API-freeze pass" pointer at the top of "Recently completed"). What's left
> below is the stable-cut closeout + the pre-ship polish backlog + the standing backlog.

### ★ NEXT — Pre-ship polish backlog (#186–#195, filed 2026-06-18)

Ten maintainer-requested items to resolve before shipping 0.1.0 — all filed as
tracked issues (each issue links the relevant impl file + has detail).
**Eight of ten SHIPPED:** #186/#190/#193/#194 (PR **#196**), #195 (PR **#197**),
#188 (PR **#198**), **#189 (PR #199 → folded into the nav reshape PR #202)**, **#187
(PR #203)** — all merged to `main`. **Two remain** (each its own `fix/*`/`feat/*`
branch → PR → `main`):

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
- **#191 Theme colors in the color picker (feature)** — add a swatch row of the
  active theme's semantic colors (via `get_theme_color`) to
  `dialogs/_impl/colorchooser.py`. NB the color dropper was removed in #190, so the
  footer is OK/Cancel-only now.
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

### ✅ SHIPPED — Layout redesign (screen-axis vocabulary on a grid engine) — MERGED #170

Replaced the Tk pack stack layout with a **screen-axis** vocabulary on the Tk **grid**
geometry manager. Merged to `main` via **PR #170** (the long-running
`feat/grid-layout-engine`). Memories `project_layout_redesign`,
`feedback_layout_conversion_rules`, `project_layout_crossaxis_default`,
`project_divider_rename`, `project_dialog_content_builder_native`.

- **Vocabulary (shipped):** axes fixed to the SCREEN (`horizontal`=x, `vertical`=y; no
  main/cross flip). **Bare = self, `_items` = children** (a container is also a widget):
  self → `horizontal`/`vertical`/`grow`; container → `horizontal_items`/`vertical_items`/
  `grow_items`. Edge-name values (`left`/`center`/`right`/`stretch`; `top`/`center`/
  `bottom`/`stretch`) + `space-between`/`-around`/`-evenly` on the stacking axis.
  `HStack`/`VStack`→**`Row`/`Column`**; `Separator`→**`Divider`**; new **`Spacer`**;
  `layout=` values `column`/`row`/`grid`. `weights=` kept (positional `grow` shorthand).
- **Cross-axis default = `center`**, uniform across all stacks; the stacking (main) axis
  starts top/left; grid stays `stretch`. **Legacy child kwargs (`fill`/`expand`/`anchor`/
  `sticky`) now RAISE** a clear error instead of silently collapsing a child.
- **Conversion rules** (memory `feedback_layout_conversion_rules`): axis-aware
  (`fill="x"`→`horizontal` stretch in a Column, `grow` in a Row); HOIST uniform child
  alignment to the parent `*_items`; NEVER write a default. Data/canvas widgets
  (ListView/Tree/DataTable/Gallery/Carousel) collapse without `grow`/`stretch`.
- **Engine fixes shipped in #170:** undefined grid rows default `weight=0` (no more rows
  spreading down a `layout="grid"` page); `Grid` honors `width=`/`height=` (propagation
  bug); `FlexFrame` prunes children destroyed out-of-band (no more `bad window path
  name`); O(1) append fast-path for plain stacks (build O(N²)→O(N), N=1000 ~7.4s→~0.5s).
- **Docs shipped:** Row/Column guides rewritten for teaching quality, new **Spacer**
  page, Divider hero redesigned, `tasks/layout.rst` ("Arranging Widgets") tightened, all
  examples/screenshots/CLI scaffold/`cli/demo.py` converted; `-W` build clean. README +
  docs-home install refreshed to the new vocabulary + `--pre`.

**Shipped post-merge (all merged to `main`):**
- **#171** `perf(layout)` — GridFrame O(N) build (gate the per-add prune scan on a
  `<Destroy>`-set flag; N=1000 grid 827ms→501ms; destroy-recreate correctness preserved).
- **#169** `ci(docs)` — deploy docs only on a new release (`workflow_run` after the
  Release workflow; runs in the `main` context so it passes the github-pages branch
  protection a tag-ref deploy would fail). In effect now.
- **#172** `docs` — README + docs-home refreshed to the layout vocabulary + `--pre`.
- **#173** `refactor(cli)` + Gallery/image fixes — rebuilt `bootstack icons` on the public
  layer (App/Row/`Gallery`, 326→94 lines, no raw Tk). Plus framework fixes (surfaced by
  dogfooding) that benefit every scroll-query widget: icon handles render+cache to PIL so
  Picture/Gallery can display `get_icon()` images; Gallery uniform tiles (`_fit_caption`),
  row-fill column weighting, `_resolve_columns` off-by-one, caption scroll-binding;
  `MemoryDataSource` filter+sort view memoization (O(1) `count`, O(window) `page_slice`).
  This closed the last `cli/icons.py` raw-Tk follow-up.

**Follow-ups (not blockers):**
- **Gallery opt-in keyboard-focus ring** (future) + deferred Gallery perf (debounce the
  `<Configure>` relayout, bounded thumbnail-PhotoImage LRU, cache `_fit_caption`). Scope to
  keyboard focus, NOT hover. Memory `project_gallery_focus_ring`.
- **`add_spacer()`→public `Spacer`** still deferred — entangled with
  `feat/unified-toolbars` (internal `Toolbar` is pack-based). Memory `project_unified_toolbars`.
- Demo bugs (pre-existing, NOT layout-caused): ~~#166 ContextMenu/Tooltip don't
  cover container children~~ (DONE, PR #183 — see top of "Recently completed") ·
  ~~#167 Gauge theme repaint~~ (resolved by the theme-repaint perf work, PR #180) ·
  ~~#168 Tabs overflow~~ (DONE, PR #184, MERGED; see top of "Recently completed").

### ✅ SHIPPED — Undecorated window controls + border + maximized-drag (#162, #165) — MERGED #175

An `undecorated` `App`/`Window`/`AppShell` is no longer stranded (the `Shell`
rewrite had dropped the controls/drag the OLD region AppShell got from the internal
`Toolbar`). **NB the #162 plan in this handoff was STALE** — by the time it was
tackled, the unified-toolbars sweep had already (a) implemented + then *retired* a
dedicated titlebar band (`7dbab5a6`→`375e1458`) and (b) **removed `menubar`/
`commandbar` framework-wide in favor of `add_toolbar()`** (`351d2409`). So the fix
layers on `add_toolbar()`, not a band:
- `ChromeHostMixin._ensure_default_titlebar()` (shared) — undecorated + no
  author-added chrome toolbar → injects one `add_toolbar(show_window_controls=True)`
  (min/max/close, draggable, dbl-click-maximize) labeled with the window title.
  No-op when decorated / macOS / author owns chrome. Called from `App.run()` /
  `AppShell.run()` / `Window.show()` / `Window.block_until_closed()`.
- 1px themed **border** via a `_region_root` wrapper (mirrors `ShellLayout`).
- **`App` gained `undecorated`** (it had none); **`Window` gained
  `window_controls=True`** (`False` = fully chromeless splash — no controls, no
  border). `App`/`AppShell` always get controls+border when undecorated.
- **#165** fixed in the same PR: dragging a maximized undecorated window now restores
  it *under the cursor* (`toolbar.py:_on_drag_motion` re-anchors on the cursor's
  horizontal fraction). Tests: `test_undecorated_titlebar.py`, `test_toolbar_drag.py`,
  AppShell case in `test_shell_toolbar.py`. Memory `project_undecorated_window_chrome`.

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

- **✅ DONE — Public-API typing sweep** (branch `feat/api-reference-widgets`, NOT
  pushed). Grew out of Stage 4's "clean up each widget's API as it is homed". Goes
  widget-by-widget in Stage-4 batch order fixing param TYPES + docstrings. **ALL widget
  batches complete** (Application → Overlays/Forms/Dialogs). **DECISION (2026-06-09):
  the standalone sweep is finished; any remaining/future typing now folds into the
  Stage-4 API-Reference *homing* below — each module gets typed at the moment it is
  homed, not in a separate pass.** Full brief + per-widget checklist + every convention:
  `docs/_dev/typing-review.md`.
  - **DONE:** Application (App/AppShell/Window), Actions (Button/ButtonGroup), Menus &
    Toolbars (Toolbar/MenuButton/MenuBar/ContextMenu), Label, Inputs (all 11 — committed
    `4a9609ff`), Selection (all 10 — Checkbox/Switch/ToggleButton/ToggleGroup/Radio/
    RadioToggleButton/RadioGroup/Select/SelectButton/Calendar), Data Display (all 7 —
    Label/Badge/ProgressBar/Gauge/ListView/DataTable/Tree). Selection included a
    maintainer-approved STRUCTURAL cleanup: removed dead `variant` (Switch/Checkbox) +
    unsupported `density` (Checkbox/Switch/Radio) via per-subclass `__init__`s + an
    `_internal_options` engine that rejects unknown kwargs. **Layout** (all 9 —
    committed `5fbbc0a7`: Separator/Card/GroupBox/VStack/HStack/Grid/ScrollView/
    Accordion/SplitView; added `LayoutKind`/`AutoFlow` aliases; enriched
    `AccordionSection` + full `SplitView` pane management + dropped the broken
    `min_size=`; HStack/VStack own `__init__` so params render). **Navigation** (all 3
    — committed `22baa3c7`: PageStack/Tabs/SideNav; enriched `StackPage`/`TabPage`
    handles; `item()`/`items()` return handles, not leaked internals).
    **Overlays/Forms/Dialogs** (final batch — committed `aee08c78`: Tooltip/Toast/Form +
    the dialog verbs/classes). **FOLD INTO HOMING (not done in the sweep):** convert
    `ColorChoice`/`FontChoice` from bare `namedtuple`s → typed `NamedTuple`s with field
    docstrings + single-backtick prose when the `bootstack.dialogs` API-Reference page is
    built; surface the `bootstack.types` aliases (`LayoutKind`/`AutoFlow`/`Padding`/…)
    when that page is built (both modules are flagged "pending" in
    `api-reference/index.rst`). STILL DEFERRED (separate initiatives): the holistic
    `guide_layout`→`_guide_layout` demotion on the 4 handle classes (AccordionSection/
    SplitPane/StackPage/TabPage) and a public `on_destroy` lifecycle hook. (Retiring
    the universal `VariantToken` is **DONE** — #158, per-widget `variant` Literals now.)
  - **Conventions (full in brief):** public type aliases render as their short NAME,
    LINKED to a `.. py:type::` entry (the linked-alias docs work — see "Linked type
    aliases" below; this REVERSES the old "literals expand inline" rule). NO
    `_drop_overloads_field` hook and NO `sphinx_autodoc_typehints` anymore (core
    autodoc renders overloads natively). Under-typed `Any`/`str` →
    real types; per-widget `variant` Literals **sourced from `style/builders/`** (NOT
    docstrings — they under-report, e.g. MenuButton/Toolbar have a `'default'` variant);
    `accent`/`surface` = `Token | str | None`; `padding` → `Padding`; closed sets →
    `Literal`. THIN docstrings (drop value enumerations the type shows; keep the
    default). `on_*` overloads: document `handler` + `:class:`-link the payload. Open
    sets with an authority → curated examples + `str` + a `:doc:`/`:ref:` link:
    `**kwargs`→`/tasks/layout`, `value_format`→`/reference/localization` (`:ref:`
    `value-formats`), `font`→`/reference/typography`, `window_style`/`language`/`theme`→
    pywinstyles/Pygments.
  - **New this session:** public aliases `Padding`/`WindowStyle` (`bootstack.types`),
    `RuleType` (`bootstack.validation`); `AccentToken` trimmed to the 6 semantic accents;
    `Fill` widened to its real set. `MenuSelectEvent` payload — MenuButton/ContextMenu
    `on_select` now typed (was a raw dict). CodeEditor `on_change`/`on_input` now emit
    typed `ChangeEvent`/`InputEvent` (was a raw `{op,index}` dict). Gauge `value_format`→
    `value_template`. New `docs/tasks/layout.rst` (placement-options page) + enriched
    `reference/localization.rst` formats section. Memories: `project_enum_option_typing`
    (the hub), `project_variant_type_revisit` (now covers accent + variant per-widget),
    `project_show_indicator_removal` (deferred behavior change), `project_image_icon_public_api`.
  - **Data Display batch (this session):** `accent`→`AccentToken|str|None` everywhere;
    removed `internal_kwargs.update(kwargs)` leaks (`**kwargs` is layout-only); documented
    `**kwargs`; promoted under-typed params (ProgressBar `signal`→`Signal`; ListView/Tree
    `data_source`→`DataSourceProtocol`; ListView `items`→`list[dict]`; Tree `nodes`→
    `list[str|dict]`, `order`→`str|Column|SortKey|Sequence|None`; DataTable
    `export_formats`→`list[Literal[...]]`); completed `on_*` payload docs. **TreeNode**
    (public) got typed annotations + attribute docstrings for its 9 `__slots__` fields.
    **CRITICAL convention learned (maintainer review):** with `autodoc_typehints="description"`,
    the rendered param type comes from the **IMPL signature**, not the `@overload`s (those
    are stripped) — so `on_*`/`on` IMPLS must be typed `handler: Callable[[Payload],Any]|None
    =None) -> Stream|Subscription`, AND every public `@property` + method needs a docstring,
    or they render bare. Swept this gap across ALL prior batches too (an AST scan found +
    fixed: DateField/TimeField `disabled`/`read_only`, Radio `disabled`; the generic `.on()`
    impl on 10 input/select widgets). Remaining gap (FLAGGED, not an on_*): `guide_layout`
    on the page-frame handles (AccordionSection/StackPage/SplitPane/TabPage) — likely
    DEMOTE to `_guide_layout` (internal layout hook) rather than document. Internal-only
    `Spinbox`/`Expander` props left as-is.
  - **Tree feature (this session, maintainer-requested):** `Tree.find(matcher)` +
    `find_all(matcher)` — `matcher` is a predicate OR a `col(...)` condition; a condition
    pushes down to a data-source-backed tree (reaching unexpanded branches) and loads the
    path to each hit non-destructively. `filter()`/`search()` view-pruning DEFERRED (open
    decisions in memory). Memory `project_tree_find_filter`; tests in `test_tree.py`.
  - **Verify each batch:** `python -m pytest tests/test_public_surface.py -q` + a CLEAN
    build — build to a FRESH temp dir when `docs/_build` is locked by an open browser:
    `sphinx-build -b html docs /tmp/bsdocs -W --keep-going` (must be warning-free).
    **Also run the doc-gap AST scan** (undocumented public props/methods + untyped `on_*`
    impls) per batch — see the convention above.
- **★ API Reference restructure — Stage 4 *homing* (docs), IN PROGRESS** (the autosummary
  homing thread — interleaved with the typing sweep above; NOT yet advanced this session).
  Branch **`feat/api-reference-widgets`** (off main; Stages 1–3 merged to main).
  Building the single top-level `bootstack` category-grouped API page + converting
  widget guides to table-only summaries, **cleaning up each widget's public API as it
  is homed** (per-widget recipe under "## Widget documentation pattern"). Within-group
  entries are **alphabetical** (lookup layer; Guides keep curated order).
  **DONE so far (committed on the branch — NOT pushed/PR'd yet):**
  - Foundation: top-level `api-reference/bootstack.rst`; relocated re-exports
    `Signal`/`set_theme`/`toggle_theme` up (subsystem pages table-link via `~bootstack.X`).
  - Batch 1 — Application (App/AppShell/Window) + Actions (Button/ButtonGroup) +
    full **App/AppShell/Window constructor curation** (dropped `app_author`/`app_version`/
    `inherit_surface_color`[hardwired]/`name`/`mainloop`; demoted `localize_mode`/
    `macos_quit_behavior`/`state_path`/`available_themes` → construction-only; promoted
    `position`/`min_size`/`max_size`/`resizable`/`hdpi`/`scaling`; removed the `tk.Tk`
    docstring leak; fleshed out `emit`). Memories `project_window_api_hardening`.
  - Batch 2 — Inputs (11) + Selection (10, incl `Radio`/`RadioToggleButton` first home).
    Completed the typed-payload `on_*` audit for boolean/selection controls (`on_change`
    → `ChangeEvent(value, prev_value)`; `on_check`/`on_uncheck` stay data-free `Event`).
    Memory `project_typed_event_payloads`.
  - Set **`default_role = "code"`** (single backticks → inline code, colon-safe) +
    converted the 6 Selection widgets' docstrings double→single — de-risks the
    framework-wide `project_docstring_backticks` sweep (now safe everywhere).
  **✅ Batch 3 — Data Display DONE** (uncommitted on the branch): homed Label/Badge/
  ProgressBar/Gauge/ListView/DataTable/Tree/TreeNode (Data Display section on
  `bootstack.rst`, alphabetical); 7 guides converted bottom-`autoclass`→table-only API
  section; **`ColumnSpec`/`EditorType`/`FormOptions` defs relocated to `widgets/types.py`
  + re-exported from `bootstack.types`** (`EditorType` dropped from top-level `__all__`,
  the only one there). `ExportJob` kept local in `datatable.py` (return-handle Protocol,
  prose-only in guide — maintainer call 2026-06-09). `on_*` payloads were already typed
  in the typing sweep (`a6d6d496`) — audit confirmed clean.
  **✅ Batch 4 — Layout + Navigation DONE**, then **the whole API-Reference IA was
  RE-CUT** to a semantic-category structure (2026-06-09, with the maintainer) —
  see the new "## IA re-cut" section + the deletions list in
  `docs/_dev/api-reference-restructure.md`. In brief: the single `bootstack` page is
  GONE; the reference is now **one page per CONCEPT** (Application · Widgets ·
  Reactivity · Events · Data · Validation · Theming · Localization · Scheduling ·
  Shortcuts · Storage · Errors — build-flow order, flat 2-level, collapsed by
  default via `show_nav_level:1`), groups may **cross namespaces** (Reactivity =
  Signal+streams; Theming = top-level verbs + `bootstack.style`), **stub titles show
  the FULL path** (all 5 templates flipped to `{{ fullname }}`), and the landing is a
  pandas-style public-contract + submodule list + `sphinx-design` card grid (secondary
  TOC removed). `api-overview` RETIRED (folded into the landing). All clean-build
  warning-free; uncommitted until the "IA restructure" commit.
  **✅ IA migration COMPLETE** (2026-06-09) — every public name is now homed: added
  the **Dialogs** group (verbs at `bootstack.*`, classes at `bootstack.dialogs.*`; gave
  `bootstack.dialogs` an `__all__`) + the **Types** group (`bootstack.types.__all__`),
  homed Menus/Overlays/Forms into **Widgets**, converted the ~13 remaining guides to
  table-only, converted `ColorChoice`/`FontChoice` → typed `NamedTuple`s, enriched the
  4 Form item dataclasses, and added `autosummary_filename_map` for the `Toast`/`toast`
  case collision. **All 14 reference groups built, clean-build warning-free.**
  **NEXT (Stage 4 done; this is the follow-on):** flesh out widget Guides
  with examples (**API Reference is a last resort; Guides carry teaching**). `EditFilter`
  already demoted (memory `project_editfilter_public_api`). **Full brief + decisions in
  `docs/_dev/api-reference-restructure.md`**; memory `project_api_reference_restructure`.
- **Public Image/Icon API** (initiative, designed 2026-06-08) — three stacked
  pieces: `Image` (Tk-free image handle; re-promote, internal since PR #104),
  `get_icon(name, ...) -> Image` (public factory over the internal font-glyph
  renderer), and `AppIcon(icon=, background=, foreground=)` (generates the
  platform app-icon assets — `.ico`/`.png` — for `App`/`Window`). `App`/`Window`
  `icon=` (type `str | AppIcon | Image`) is DEFERRED to this. Memory
  `project_image_icon_public_api`.
- **Decoupled option shape for the selection family** (initiative, designed
  2026-06-09) — let `Select`/`SelectButton` options carry a value distinct from
  their label, via ONE shared `Option = str | tuple[str, Any] | OptionDict` shape
  (dict = the extensible "data bag" member: `{"text", "value", …icon/disabled}`)
  normalized once and consumed by all four selection widgets (RadioGroup/ToggleGroup
  already do `(label,value)` tuples — fold them into the shared normalizer + widen to
  the dict). Bulk of the work is giving the entry-backed `SelectBox` a real text↔value
  map (search-on-text, value-space `value`, custom-value semantics). Full brief +
  open decisions (`text` vs `label` key; `.options` return shape; unknown-value setter
  behavior): `docs/_dev/select-options-databag.md`. Behavior feature — do AFTER the
  typing sweep's Data Display batch; lock shape/naming before touching internals.
- **Deferred file-streaming items** — background/progressive ingest, keyset
  pagination, auto-index (memory `project_file_source_streaming`).

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

## Widget documentation pattern (established — follow exactly)

> ⚠ Stage 4 of the API Reference restructure will modify this pattern: the bottom
> `autoclass` gets DROPPED (the autodoc home moves to the single top-level
> `bootstack` API Reference page) and replaced with a table-only `autosummary`
> summary + cross-links, per the Guide-page recipe above. Until then, in-flight
> widget pages keep the autoclass.
>
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
