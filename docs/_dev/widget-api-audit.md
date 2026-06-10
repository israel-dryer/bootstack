# Widget public-API gap audit

**Date:** 2026-06-10 · **Branch:** `feat/widget-api-gap-audit` (off `main`)

## Purpose

Before fleshing out the widget Guides, audit every public widget wrapper
(`src/bootstack/widgets/*.py`) against its internal implementation
(`_impl/...`) to find **user-facing capabilities the wrapper fails to expose** —
so we don't document an incomplete API. Triggered by the ContextMenu finding
last session (a 247-line wrapper over a 1941-line impl that was missing ~7
positioning/sizing params and ~4 item methods — since fixed on `main` via the
`feat/typed-alias-links` merge, commit `05add8fc`).

**Method:** 9 parallel agents, one rubric. For each widget: enumerate the public
wrapper's params/methods/properties/events, follow its `_Internal*` import to the
impl (+ widget-specific mixins/parts), enumerate the internal public-ish surface,
and diff. Excluded by design: raw Tk options, `.tk`/`.var` escape hatches,
private members, `PublicWidgetBase` framework methods, and capability already
exposed under a renamed public name.

**Severity:** `high` = clearly useful + user-facing, fix before docs · `med` =
useful, worth a decision · `low` = niche / plausibly opinionated.
**Rec:** `expose` · `omit-by-design` · `needs-decision` (maintainer call).

> This is a findings document, not a change set. Nothing here is implemented yet.
> The maintainer should triage the cross-cutting decisions (§2) first, since they
> set the pattern for many individual findings.

---

## 0. Impact summary — and what's likely *intentional*

**Read this first.** A "gap" here means *the impl can do X, the wrapper can't* —
which is **not** the same as a defect. bootstack is deliberately opinionated and
hides Tk, so under-exposure is often the *correct* design. The audit deliberately
sorted findings into `expose` / `needs-decision` / `omit-by-design` precisely so
this distinction is explicit. Rough shape of the ~65 findings:

- **~10 are real incompleteness / bugs** (recommend fix): the App/AppShell window
  lifecycle, the ToggleGroup/RadioGroup management API, and the three
  correctness gaps (RangeSlider clamp, NumberField `clear()`→0, Form Tk leak).
  These would make a Guide *wrong*, not just terse.
- **~25 are judgment calls** (`needs-decision`): mostly the §2a "construction-only
  vs live property" pattern. Exposing them adds runtime surface — which the
  framework may *deliberately* not want. **Fewer knobs is a valid choice.** The
  right lens: only promote to a live property if a real user would bind a control
  to it (the App/AppShell rule). Many of these can stay construction-only.
- **~30 are correctly hidden** (`omit-by-design`) or already tracked elsewhere:
  raw Tk options, escape hatches, low-level color/state, niche styling
  (`arc_range`, `underline`, `striped_background`), simplified single-shot
  patterns (Toast/Form-as-fresh-instance), the demoted `EditFilter`, and the
  items already owned by other initiatives (icons, window hardening,
  `show_indicator` removal, the Select option-databag).

### The line between "opinionated minimalism" and "incomplete"

The useful test the audit applied: **does the omission prevent a task the widget
is *for*?**

- Hiding `ttk.Button.underline` or a scrollbar `variant` → opinionated, **keep
  hidden**. The widget's job isn't affected.
- Not being able to `close()` the app from code, `remove()`/`disable()` one option
  in a ToggleGroup, or change a Calendar's available dates as data loads → that
  blocks the widget's *core* job. **Real gap.**

So the impact isn't "65 things to fix." It's: **~10 to fix, ~25 to rule on (and
"leave hidden" is a fine ruling for most), ~30 already settled.** The docs risk is
concentrated in the ~10 — those are the ones where a Guide written today would
teach an API that hits a wall.

### Impact by dimension

| Dimension | What's affected | Severity |
|---|---|---|
| **Docs correctness** | App/AppShell (no `close`/lifecycle), ToggleGroup/RadioGroup (no item mgmt), DataTable (no programmatic column/row view-ops), CodeEditor (no find/replace API) — a "complete" Guide would overstate | high — the reason we audited first |
| **Behavioral bugs** | RangeSlider clamp bypass, NumberField `clear()`→0, Form raw-Tk `Variable` leak | med — independent of docs |
| **Consistency** | §2d family asymmetries (`wrap`, `value_format`, `select_on_click`, `font=`, `textsignal=` naming) | med — cheap, a sibling proves the shape |
| **Surface-area risk** | The §2a live-property question — exposing *adds* permanent public API | this is where "intentionally hiding" most applies; bias toward NOT exposing unless clearly needed |
| **Change cost** | Almost all fixes are additive (new property/method) and low-risk; only AppShell façades (§1.2) and CodeEditor find/replace are larger | low–med |

---

## Status — implemented on `feat/widget-api-gap-audit` (2026-06-10)

The §1 headline fixes + §2e behavioral bugs are **done** (pending review):

- **Lifecycle on `PublicWidgetBase`** (all widgets): `destroy()` + `on_destroy`
  (Tk `<Destroy>`, wired via a `"destroy"` entry in the global event map). The
  `<Map>`/`<Unmap>` visibility events are **deferred** to the widget
  attach/detach initiative below — see "Deferred".
- **Window controls** via a shared `WindowControlsMixin` on App / AppShell /
  Window: `close()`, `hide`/`minimize`/`maximize`/`set_fullscreen`/`set_topmost`,
  `on_close`/`add_close_handler`/`remove_close_handler`. App + AppShell gained a
  typed `on_close=` constructor kwarg; **AppShell is now a `PublicWidgetBase`**
  (so it also gets `destroy`/`schedule`/`on`/`emit`); Window gained a live
  `title`.
- **Group management** (leak-free, curated): `ToggleGroup` gained
  `remove`/`configure_item`/`__len__`/`__contains__`; `RadioGroup` gained
  `configure_item`/`__len__`/`__contains__` + a live `title`. `configure_item`
  takes friendly kwargs (`label=`, `disabled=`), not raw Tk options.
- **Behavioral bugs:** RangeSlider `low_value`/`high_value` now route through the
  clamping `set_lo`/`set_hi`; NumberField `clear()` empties to `None` (not `0`);
  Form `field_variable()` (raw Tk `Variable` leak) **removed** —
  `field_signal()`/`field_textsignal()` are the Tk-free path.

**Consciously deferred (need decisions, not mechanical):**

- **§1.2 — AppShell's raw `toolbar`/`nav`/`pages` leak.** Still returns internal
  composites. Wrapping them in public façades vs documenting the internal surface
  is a design call; bundles with the broader "add-only wrappers should return
  public handles" theme (§2b). **Open for §2 review.**
- **Group `item`/`items`/`keys`/`values` enumerators.** The internal `item`/
  `items` return raw internal button widgets (a leak), and `keys`/`values` naming
  collides with the pending `project_select_options_databag` initiative (value vs
  label vs key). Deferred there so the option-shape vocabulary is settled once.

Verified: clean `-W` build, `test_public_surface` (137), `test_slider_events`
(5), `test_app_config` (8), and a runtime smoke of every item above.

---

## 1. Headline (highest-value, recommend fixing before the docs pass)

1. **App / AppShell have almost no window-lifecycle surface.** The public `App`
   exposes only `run()` + config props — none of `BaseWindow`/`App`'s window
   verbs. Missing **`close()`**, the veto-able **`on_close` / `add_close_handler`**
   chain (`base_window.py:341/355`; also the dropped `App(on_close=)` kwarg
   `app.py:428`), and `hide`/`minimize`/`maximize`/`set_fullscreen`/`set_topmost`
   (`base_window.py:591–635`). `Window` already surfaces `close()`; `App` doesn't.
   Programmatic quit + confirm-before-quit are table-stakes. **AppShell inherits
   the entire gap** (it uses `AppConfigMixin` but doesn't subclass public `App`).
   · **high · expose** (share a window-controls mixin between App/AppShell/Window).

2. **AppShell leaks raw internal composites.** `shell.toolbar` / `.nav` / `.pages`
   return the *internal* `Toolbar`/`SideNav`/`PageStack` (`appshell.py:355/365/373`),
   not public wrappers — so the shell's own toolbar wants `command=` not
   `on_click=`, etc. (the docstrings admit this). · **high · needs-decision**
   (wrap in public façades, or explicitly document the internal surface).

3. **ToggleGroup is missing the management API its own impl and sibling expose.**
   Public `ToggleGroup` surfaces only `value`/`disabled`/`add()`/`on_change` —
   but the internal has `remove` (`togglegroup.py:290`), `item`/`items`
   (`:305/:297`), `keys` (`:337`), `configure_item` (`:321`). RadioGroup's wrapper
   already exposes `remove`; ToggleGroup's doesn't. Clear family asymmetry.
   · **high · expose**.

4. **RadioGroup is missing item-level query/config.** No public `item`/`items`
   (`radiogroup.py:331/:323`), `configure_item` (`:347`, enable/disable/relabel one
   option), `keys`/`values` (`:467/:475`), `__len__`/`__contains__` (`:483/:487`),
   or live `title`/`labelanchor` (`:426/:413`). · **high (item/configure) /
   med (rest) · expose**.

These four are the gaps that would most embarrass a Guide that claimed to teach
the widget completely. Everything else is medium/low.

---

## 2. Cross-cutting themes — decide these once, apply widely

These patterns recur across the whole widget set. A single maintainer decision on
each resolves dozens of individual findings below.

### 2a. "Construction-only, but the impl supports it live" (the dominant pattern)

By far the most common finding. The internal widgets have working
`@configure_delegate` setters (live reconfigure + redraw), but the public wrapper
freezes the value at construction. Candidates for promotion to **live properties**
(apply the App/AppShell rule: *a property is live only if changing it has a
complete effect a user would bind a control to* — most of these DO take full
effect):

| Area | Construction-only today, live internally |
|---|---|
| Fields | `PathField` dialog opts (`start_dir`/`mode`/title/filters), `DateField` picker bounds (`min_date`/`max_date`/`disabled_dates`/`show_picker_button`), `SpinnerField` numeric bounds (`min_value`/`max_value`/`step`/`wrap`), `value_format` (all fields) |
| Select family | `Select` `searchable`/`allow_custom_values` (`selectbox.py:505/:492`); `SelectButton` `options` (`optionmenu.py:197`, rebuilds menu) |
| Slider | `tick_step`/`tick_format`/`minor_ticks`/`tick_labels` (`slider.py:701–729`, both Slider + RangeSlider); live `accent` |
| Data display | `Gauge` `min_value`/`max_value` (`meter.py:235–251`), `value_template`/prefix/suffix |
| Calendar | `disabled_dates`/`min_date`/`max_date` (consulted live on redraw, but **no internal mutator exists** — needs a small `set_disabled_dates`+`_refresh` too) |
| Containers | live `gap` on VStack/HStack/Grid/Card/GroupBox (`PackFrame._delegate_gap` `packframe.py:97`, `GridFrame` `gridframe.py:141`); `padding`; ScrollView scroll-config trio (`scrollview.py:124/151/190`) |
| Accordion | `allow_multiple`/`allow_collapse_all`/`show_separators` (`accordion.py:339/347/355`) |

**Recommended decision:** pick a tier. Highest user value: container `gap`, Gauge
range, Slider ticks, Select `searchable`/`allow_custom_values`, SelectButton
`options`, Calendar `disabled_dates`. Lowest: format strings, scrollbar variants.

### 2b. Add-only / fire-and-forget wrappers drop return handles

`MenuBar.add_button`/`add_menu`/`add_label` and every `Toolbar.add_*` return
`None`, while the internal adders return the created widget (`menubar.py:185/245`,
`toolbar.py:215–343`). Users can't reference an item later to update/disable it.
**Recommended decision:** return a handle (or key) from add-methods, matching the
MenuButton/ContextMenu/Tree pattern that already does. · **med · expose**.

### 2c. `**kwargs` leaks raw Tk options (convention violation)

`Spinbox` (`spinbox.py:86`), `Scrollbar` (`scrollbar.py:43`), and `SizeGrip`
(`sizegrip.py:35`) do `internal_kwargs.update(kwargs)`, passing the catch-all
straight into the ttk constructor — contra the curated layout-only `**kwargs`
convention every other wrapper follows. `Spinbox` is the worst (it's a full field
sibling). · **med (Spinbox) / low · expose** (fix the leak; promote any genuinely
useful option, e.g. Scrollbar `variant`, to a typed param).

### 2d. Cross-family consistency gaps (a sibling exposes it, this one doesn't)

| Gap | Has it | Missing it |
|---|---|---|
| `wrap` (numeric edge-wrap) | SpinnerField | **NumberField** (`numberentry_part.py:32`) |
| `value_format` | Text/Number/Date/Time | **SpinnerField** |
| `select_on_click` | Tree | **ListView** (`listview.py:50`) |
| `show_separator(s)` | ListView | **Tree** (`treeview.py:43`) |
| `textsignal=` naming | every field | **Spinbox** uses `text_signal=` |
| `icon_position`/`show_indicator` | Radio | **RadioToggleButton** (`__init__` drops them — `radio_variants.py:223`) |
| `font=` | inputs, Label | **all 6 boolean/radio controls** (inherit `FontMixin._delegate_font` but surface none) |
| live `title`/`icon` setter | AccordionSection | **Expander** |
| live `label` setter | (none) | all 3 boolean controls (`label`/`text` construction-only) |

These are cheap, high-confidence fixes — a sibling already proves the shape.
· mostly **med · expose**.

### 2e. Behavioral-correctness gaps (not just missing surface)

- **RangeSlider** `low_value`/`high_value` public setters write the signal
  directly, **bypassing the clamping** in `set_lo`/`set_hi` (`rangeslider.py:695/703`)
  — so `low_value = 90` can exceed `high_value`. Route setters through the
  clamping methods. · **med · fix**.
- **NumberField** `clear()` sets the value to **`0`**, not empty
  (`numberfield.py:243`), even though the field supports a blank/`None` state — a
  cleared required field would pass the empty check. · **med · needs-decision**.
- **Form** `field_variable()` returns a raw Tk `Variable` (`form.py:387`) — a Tk
  leak into the public surface; `field_signal()`/`field_textsignal()` already
  provide the Tk-free path. · **med · needs-decision** (demote/drop).
- **Window** modal grab is never released on close (`toplevel.py:205` `grab_set`,
  no `grab_release`) — already tracked in memory `project_window_api_hardening`.

---

## 3. Medium findings by group (beyond the cross-cutting themes)

**Buttons & menus**
- `ButtonGroup.add(widget_type=)` — internal accepts Button/CheckToggle/RadioButton/
  RadioToggle members (`buttongroup.py:97`); public hardcodes `Button`.
  **RESOLVED — omit-by-design (maintainer, 2026-06-10): `ButtonGroup` is for
  ACTION buttons only; toggle/radio/check selection belongs in `ToggleGroup` /
  `RadioGroup`. The internal flexibility stays internal.**
- `MenuBar` region frames `before`/`center`/`after` (`menubar.py:155/163/171`) — no
  way to add an arbitrary widget to a region. · needs-decision.
- `Toolbar.content` frame (`toolbar.py:347`) — `add_widget` requires a toolbar-parented
  widget but gives no way to *get* that parent; the docstring's own workflow is unusable
  without it. · expose. Plus window-control button accessors (`:369–382`).
- `ContextMenu` (just completed) — remaining: live reconfigure delegates (re-`target`,
  swap `on_select`) `contextmenu.py:1523–1599`; `shift-click`/`ctrl-click` triggers
  (`:1740`). · needs-decision.

**Fields** — see §2a/§2d. Plus `PathField.dialog_button` accessor (parallels
`DateField.picker_button`); `TimeField` (a `SelectBox` subclass) exposes no
dropdown knobs and its `read_only` doc claim doesn't match `allow_custom_values`.

**Text editors**
- `CodeEditor`: no programmatic **find/replace** API despite a complete internal
  search engine (`search_overlay.py` `_run_search`/`_replace_all`/…) — only the UI
  bar is reachable. Live `wrap` + `show_line_numbers` toggles (one-line on the live
  text / sidebar add-remove). `get_selection`/`replace_selection`/cursor read
  (`on_cursor_move` fires but the position isn't readable). · med · expose/needs-decision.

**Select / slider / calendar** — see §2a/§2e.

**Data display**
- `Gauge.step()` (`meter.py:807`, auto-bounce) — sibling `ProgressBar.step()` exists,
  Gauge omits it. · expose.
- `ListView`: `on_item_drag` (continuous; only start/end surfaced),
  `on_item_delete_fail` (`<<ItemDeleteFail>>` `listview.py:677`), `select_on_click`. · expose.
- `DataTable` (largest medium cluster): programmatic `move_rows`/`hide_rows`,
  `move_columns`/`hide_columns`/`unhide_columns` (`tableview.py:650–708`);
  `show_hscrollbar`+`column_auto_width` (`:266/:289`, no horizontal scroll today);
  `search_mode='advanced'`/`search_trigger='input'` (`:259`); `context_menus`
  gate (`:287`); `first_page`/`last_page` (`:751/:754`). · med · expose/needs-decision.

**Navigation & overlays**
- `Tabs`: `on_tab_activate`/`on_tab_deactivate` — payload types `TabActivateEvent`/
  `TabDeactivateEvent` are already in `bootstack.events.__all__` and the internal
  emits them (`tabview.py:185/191`), but no shorthand delivers them. · med · expose.
- `Tooltip`: live `text` setter (toplevel rebuilds each hover, so it's trivial —
  `tooltip.py:96`). · med · expose.

---

## 4. Low / deferred / already-tracked (do not action here)

- `App.icon=`/`Window.icon=` — **deferred** to the Image/Icon initiative
  (memory `project_image_icon_public_api`).
- `Window` live geometry (`size`/`position`/`state`) + modal-grab release —
  tracked in memory `project_window_api_hardening`.
- `show_indicator=` on the radio family — **slated for removal**
  (`project_show_indicator_removal`); the RadioToggleButton asymmetry folds into that.
- Decoupled value≠label for Select/SelectButton — **confirmed no hidden capability**:
  `SelectBox._items` is `list[str]`, `OptionMenu` coerces to `str`. The planned
  `project_select_options_databag` initiative genuinely needs new internal work, not
  wrapper plumbing. (Useful negative result.)
- Tree `filter`/`search` — deliberately deferred (`project_tree_find_filter`).
- Niche params left as omit-by-design: Button `underline`/`anchor`, Meter
  `arc_range`/`indicator_width`, container `width`/`height` live, Toast/Form
  reuse-via-`configure` (the documented pattern is a fresh instance), `EditFilter`
  (demoted, Tk-coupled), various `striped_background`/`enable_hover` theme knobs.
- **Verify:** does the public `AutoFlow` alias include `'row-dense'`/`'column-dense'`/
  `'none'` (Grid's impl supports them)? If not, the dense pack modes are unreachable.

---

## 5. Clean (no gaps found)

`Label`, `Badge`, `Separator`, `SizeGrip`, `PasswordField`, `PageStack` — wrappers
are complete relative to their impls. (Layout batch overall is much tighter than
the ContextMenu calibration; no widget there has a 7-param/4-method hole.)

---

## 6. Suggested sequencing

1. **Maintainer triages §2** (the five cross-cutting decisions) — this is the gate;
   it determines the shape of most fixes.
2. **Fix §1 + §2e** (window lifecycle, group management, behavioral bugs) on this
   branch — highest value, lowest ambiguity.
3. **Apply the §2 decisions** widget-by-widget, *in the Stage-4 homing batch order*,
   so each widget is gap-fixed at the moment its Guide is written (matches the
   standing "clean up the API while documenting" pattern,
   memory `feedback_cleanup_api_while_documenting`).
4. Per batch: `python -m pytest tests/test_public_surface.py -q` + a clean `-W`
   docs build (wipe `docs/api-reference/generated/` first — stale stubs there
   produce false "not in any toctree" / "duplicate object" warnings).

Full per-widget findings are preserved in the agent transcripts for this audit.
