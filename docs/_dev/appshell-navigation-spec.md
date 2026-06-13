# AppShell + Navigation — implementation spec

Status: **DRAFT for review** (2026-06-13). Actionable spec derived from
`appshell-design.md` (the rationale/north-star) + the locked decisions from the
2026-06-13 design discussion. This supersedes the *API shapes* in the design doc
where they conflict (e.g. `shell.toolbar` → `shell.commandbar`); the design doc
remains the source for *why*.

Clean-slate rewrite of `AppShell` + the shell's navigation. Pre-release →
clean breaking changes, no compat shims.

---

## 1. Locked decisions (from discussion)

1. **Single-tier is two-tier with one workspace.** The rail (workspace switcher)
   is always in the *model*; it only *renders* when `len(workspaces) > 1`. The
   switcher is therefore optional with zero app-code branching.
2. **Nested page-stack cascade.** `rail selection → sidebar panel` and
   `sidebar selection → content page` are both page-stack swaps. Off-screen
   panels stay alive (per-workspace memory: selection + scroll survive).
3. **One provider per workspace, mutually exclusive.** A workspace's sidebar is
   filled by exactly one of `add_page` (static), `list_nav`, `tree_nav`, or a
   custom panel. Mixing is an error, not a merge.
4. **Two modes per workspace.** *Provider mode* (blessed: cascade +
   collapse-to-rail + per-workspace memory) vs *custom mode* (blank container,
   user owns content-switching, **hides but does not compact to a rail**).
5. **Collapse-to-rail requires icon-representable content.** Inherent constraint,
   not a bug — only provider-mode panels compact; custom panels only hide.
6. **VS Code rail gesture.** Click the **active** rail icon → hide the sidebar.
   Click a **different** rail icon → switch workspace + show the sidebar.
7. **Three independent layout axes; rail→sidebar content-coupled.** Visibility of
   rail / sidebar / detail-dock toggle independently. Rail *drives* sidebar
   content (the cascade); the detail dock answers to neither.
8. **Detail/inspector dock reserved, not built this round.** Right-side region +
   independent `dock_visible` axis are reserved in the layout and the nav model;
   no rendering work now.
8b. **Status bar built minimal this round.** Full-width bottom band, shell-global,
    home for *passive* status; reuses the CommandBar strip primitive; left/right
    clusters; content-driven presence. Per-view status segments deferred.
9. **§3 of the design doc ("menubar is a toolbar") is dead.** Use the shipped
   two-surface split (`menubar` + `commandbar`, PR #124). The rail/sidebar sit
   *below* that chrome row.
10. **Detail payload normalized to one shape** (resolves design-doc open
    decision #2): both `list_nav` and `tree_nav` detail builders receive the
    universal `.selection` **record dict**, not dict-vs-node.
11. **`SideNav` stays standalone, and is simplified.** It remains a public widget
    usable outside a shell (the seed-brief renames land on it: `on_toggle`/
    `on_display_change`), and the AppShell static (`add_page`) provider renders
    the *same* primitive. **Collapsible groups (`SideNavGroup` expandability) are
    removed** — accordions in the primary nav break collapse-to-rail and conflate
    content-hierarchy with navigation (design doc §4). What survives: single-select
    nav items (radio semantics, nav rendering), **static** group headers (inline
    markers that chunk the list and hide on collapse), separators, footer items,
    and the `hidden → compact → expanded` axis. Grouping survives *without*
    collapsibility — a header + its items may indent and highlight the active child.
12. **The sidebar owns ONE selection language; providers adopt it by role.** The
    nav-item visual treatment — subtle accent wash (`b.subtle(accent, surface)`) +
    an optional **left indicator bar** + accent foreground, **no hover-when-selected**
    — is a *sidebar* affordance, theme-token driven (flips light/dark). All three
    providers (`add_page`/`list_nav`/`tree_nav`) render rows in this language, so
    switching a workspace's provider never makes the rows jump. This is independent
    of ListView's *content-area* selection style (which dropped the bar for a
    simpler wash) — a ListView in `list_nav` *role* takes the sidebar language, not
    its data-grid styling ("a widget exposes capabilities; a provider exposes a
    role"). Implementation reuses the existing pattern: the `navitem_{density}`
    nine-patch (with the baked indicator-bar channel) + the shared **button-family
    sizing helpers** (`toolbutton_layout`/`button_padding`/`button_font`/
    `icon_size`/`normalize_button_density`) — exactly how `ToggleGroup` reuses
    `ButtonGroup`'s baked shapes with a role-specific builder. Cleanup: drop the
    unused `variant`/`VariantToken` kwarg from `SideNavItem`
    (`project_variant_type_revisit`).
13. **Per-tier visual hierarchy (rail vs sidebar vs content).** Three reinforcing
    axes of distinction so two icon columns never compete and *"the eye lands on
    exactly one high-contrast item per tier"* (design doc §6):
    - **Elevation:** rail = 0, sidebar = 1, content = 2 — **named elevation
      tokens** (light themes darken with depth; dark themes often lighten — the
      token lets it flip correctly per theme).
    - **Active markers differ by tier — the bar is sidebar-only:**
      - **Rail active** = a **subtle accent-tinted wash** (`b.subtle(accent,
        surface)`, resolved against the *rail* surface — it must be tuned against
        elevation 0, not the sidebar's surface) + glyph at **full neutral
        foreground**; inactive glyphs **muted**; **no bar, no accent on the glyph**
        (accent appears once, as the wash tint — accent-wash + accent-glyph is "too
        much"). The rail must carry its active state independently because the hide
        gesture can remove the sidebar entirely.
      - **Sidebar active** = subtle wash + **accent foreground** + **left indicator
        bar** (decision #12); the wash carries selection through compact mode where
        the bar matches the fill and disappears.
    - **Icon scale — two tokens:** `inline_icon_size` (small, ~16–18px
      density-scaled — expanded item beside a label) vs `rail_icon_size` (larger,
      ~20–24px — standalone categorical glyph). Size alone signals the tier.
    - **The seam rule (load-bearing):** a compacted *single* sidebar adopts the
      **rail paradigm wholesale** — `rail_icon_size`, the rail wash+neutral-glyph
      marker (NOT the bar), and `rail_width` — so collapsing a one-workspace
      sidebar is visually identical to a two-tier rail (collapse never reveals a
      seam). Net: only two icon sizes system-wide (inline, rail/compact), and
      "compact" ≡ "rail".

---

## 2. Three-layer architecture

Layout, navigation logic, and content-population are separated so they don't bleed
into each other (today's `AppShell` mixes all three).

### Layer 1 — Region layout (dumb)
The band layout. Full-width top (`menubar`/`commandbar`) and bottom (`statusbar`)
bands; a body row that is a paned arrangement of `rail · sidebar · content · dock`.
Each region is a **toggleable slot**. Knows nothing about navigation — just
shows/hides/sizes regions. The `dock` slot is reserved (not rendered this round);
the `statusbar` band is built minimal.

```
┌─────────────────────────────────────────────┐
│ menubar / commandbar  (full width)           │
├──┬──────────────┬──────────────────┬─────────┤
│r │ sidebar      │                  │  dock   │
│a │ (swaps per   │     content      │ (resv'd)│
│i │  workspace)  │                  │         │
│l │              │                  │         │
├──┴──────────────┴──────────────────┴─────────┤
│ statusbar  (full width, minimal — passive)   │
└─────────────────────────────────────────────┘
```

### Layer 2 — `NavModel` (the brain): single observable state
**Tk-free, headless-testable.** One source of truth; controls dispatch into it,
regions subscribe.

```python
SidebarMode = Literal["hidden", "compact", "expanded"]

@dataclass
class WorkspaceState:
    key: str
    text: str = ""
    icon: str | dict | None = None
    is_footer: bool = False          # pinned to rail bottom
    provider: ProviderKind = "pages" # pages | list | tree | custom

class NavModel:
    workspaces: list[WorkspaceState]      # insertion order
    active_workspace: str | None
    active_page: dict[str, str]           # workspace_key -> page_key (per-ws memory)
    sidebar_mode: SidebarMode             # the ONE linear axis
    dock_visible: bool                    # independent axis (reserved)

    # transitions (the only ways state changes)
    def add_workspace(self, key, **meta) -> WorkspaceState: ...
    def select_workspace(self, key) -> None: ...      # rail click (different icon)
    def select_page(self, key, *, workspace=None) -> None:
    def activate_rail(self, key) -> None:             # VS Code gesture dispatcher:
        # if key == active_workspace and sidebar visible -> hide
        # else -> select_workspace(key) + show
    def toggle_sidebar(self) -> None:                 # hamburger/shortcut: visibility
    def set_sidebar_mode(self, mode) -> None:         # chevron: compact<->expanded
    def toggle_dock(self) -> None:

    def subscribe(self, listener) -> Subscription: ...  # regions observe
```

Invariant: `sidebar_mode` is a single linear axis (`hidden → compact → expanded`),
so "hidden but expanded" is unrepresentable. In two-tier the rail is the
always-present tier-1, so the secondary panel uses only `hidden ↔ expanded`
(no own compact — two icon-rails side by side is noise).

`rail_renders == len([w for w in workspaces if not w.is_footer]) + footers > 1`
(i.e. more than one workspace total). Pure function of workspace count.

### Layer 3 — Providers (Strategy + Adapter)
What *fills* a workspace panel, behind one contract: **emit a selection → swap
content**. The sidebar region holds *a provider* and doesn't know which kind.

```python
class NavProvider(Protocol):
    def mount(self, panel: Container) -> None: ...   # build the sidebar widget
    def on_select(self, handler) -> Subscription: ...# emits the selected record
    def selection: dict | None                        # universal record shape
    def supports_compact: bool                        # pages/list/tree True; custom False
```

- `add_page` → **static** provider (authored items + authored bodies).
- `list_nav(source=)` → **flat data-bound** (a `ListView` in nav role: single-select,
  no multi/export). Adapts `DataSourceProtocol` (pagination/`where`/`order`).
- `tree_nav(...)` → **hierarchical data-bound** (a `Tree` in nav role; same source
  viewed through a parent column).
- custom → no provider; raw container, `supports_compact = False`.

Providers *consume* the widget/source; they don't subclass it, so widgets keep
gaining capability without it leaking into the narrow nav contract.

---

## 3. Public API surface

### 3.1 `AppShell` (the shell == the implicit default workspace)

Constructor keeps the existing flat-kwargs path (`theme`/`size`/`locale`/window
placement/window-state/etc. via `AppConfigMixin`), plus navigation options.
**New/changed nav kwargs:**

| kwarg | type | default | meaning |
|---|---|---|---|
| `show_sidebar` | `bool` | `True` | render the sidebar region |
| `sidebar_mode` | `'expanded'\|'compact'\|'hidden'` | `'expanded'` | initial sidebar state |
| `sidebar_width` | `int \| None` | token | expanded width |
| `rail_width` | `int \| None` | token | rail / compact width (shared token — collapse is seamless) |
| `collapsible` | `bool` | `True` | show the in-sidebar chevron + bind Ctrl/Cmd-B |
| `nav_accent` | `AccentToken \| str` | `'primary'` | active-item accent |
| `remember_nav_state` | `bool` | `False` | persist sidebar_mode + per-workspace page across sessions |
| `show_statusbar` | `bool` | `False` | force the status band on (else content-driven) |
| `show_dock` *(reserved)* | `bool` | `False` | render the detail/inspector dock |

**Region accessors (public handles — NOT internal composites):**

| accessor | returns | notes |
|---|---|---|
| `shell.commandbar` | `CommandBar` | public handle (fixes today's leak) |
| `shell.menubar` | menubar handle | already public (PR #124) |
| `shell.rail` | `Rail` | workspace switcher; methods no-op when not rendered |
| `shell.content` | content region handle | active page container |
| `shell.statusbar` | `StatusBar` | full-width bottom band (see §3.5) |
| `shell.dock` *(reserved)* | dock handle | right-side detail/inspector region |

**Workspace API on the shell** — sugar that targets the **implicit default
workspace**:

| method | returns | effect |
|---|---|---|
| `add_page(key, *, text, icon, group, scrollable)` | `Page` (context mgr) | static authored page |
| `add_footer_page(key, ...)` | `Page` | page pinned to sidebar bottom |
| `add_header(text)` | `NavHeader` | static (non-collapsible) group label |
| `add_separator()` | `NavSeparator` | divider |
| `list_nav(source=, *, image_field=, caption_field=, where=, order=)` | `ListNav` | claim default ws as flat data-bound |
| `tree_nav(source=None, *, parent_field=, ...)` | `TreeNav` | claim default ws as hierarchical |
| `detail` | decorator | the parameterized body for a data-bound provider |
| `panel()` | `Container` (context mgr) | claim default ws as **custom mode** |

**Two-tier API:**

| method | returns | effect |
|---|---|---|
| `add_workspace(key, *, text, icon)` | `Workspace` (context mgr) | adds a rail icon → a sidebar panel |
| `add_footer_workspace(key, ...)` | `Workspace` | rail icon pinned to rail bottom |

**Navigation + lifecycle:**

| method/prop | meaning |
|---|---|
| `navigate(page)` / `navigate(workspace, page)` | set active workspace and/or page |
| `current` | active page key (single-tier) |
| `current_workspace` | active workspace key (two-tier) |
| `toggle_sidebar()` / `show_sidebar()` / `hide_sidebar()` | visibility (hamburger) |
| `sidebar_mode` (rw prop) | `'hidden'\|'compact'\|'expanded'` |
| window controls | `close`/`minimize`/`maximize`/… via `WindowControlsMixin` |
| `run()` | show + mainloop |

**Mutual-exclusivity rule (locked):** shell-level page methods
(`add_page`/`list_nav`/`tree_nav`/`panel`) are sugar for the implicit default
workspace and are **mutually exclusive with `add_workspace`**. Call one style or
the other. Calling `add_workspace` after a shell-level page method (or vice-versa)
raises — this keeps "simple stays simple" and "complex is explicit" without an
implicit workspace that has no rail icon/text.

### 3.2 `Workspace` (returned by `add_workspace`; the shell *is* the default one)

Exposes the **same page API the shell has** — `add_page`, `add_footer_page`,
`add_header`, `add_separator`, `list_nav`, `tree_nav`, `detail`, `panel`,
`navigate(page)`, `current`, and `content` (the workspace's content-region handle,
for hand-driven swapping in custom mode). This literal symmetry is what makes
single→two-tier purely additive.

### 3.3 `Rail` (the workspace switcher)
Mostly framework-driven (built from workspaces). Public surface is small:
`rail.select(key)`, `rail.current`, `rail.on_change(handler)` (→ a workspace-change
event). Footer workspaces render at the rail bottom.

### 3.5 `StatusBar` (full-width bottom band)

Shell-global, the home for **passive** status (indicators, counts, sync state) —
*interactive* controls stay on the `commandbar`. Reuses the CommandBar strip
primitive with a `statusbar` style role (thinner, muted surface), so the
left/right-cluster mental model carries over.

| method | effect |
|---|---|
| `add_widget(widget, *, side='left')` | add a passive widget to the left/right cluster |
| `add_spacer()` | push subsequent items to the right cluster |
| `add_text(text, *, side='left')` | convenience label segment |
| `clear()` | remove all segments |

**Content-driven presence:** the band renders only if items were added *or*
`show_statusbar=True`. A one-screen utility never sees an empty strip.
Shell-global only this round — per-workspace/per-view status segments are deferred
(the band itself is global; segments can be added later without re-cutting it).

### 3.4 Events (`bootstack.events`)

| shorthand | payload | fires |
|---|---|---|
| `shell.on_page_change(h)` | `PageChangeEvent(key, prev_key, data)` | active page changes |
| `shell.on_workspace_change(h)` | `WorkspaceChangeEvent(key, prev_key)` *(new)* | rail switches workspace |
| `shell.on_sidebar_toggle(h)` | `PaneToggleEvent(is_open)` | sidebar shown/hidden |
| `shell.on_sidebar_mode_change(h)` | `DisplayModeEvent(mode)` | compact ↔ expanded |

All follow the `@overload` no-arg→`Stream` / handler→`Subscription` convention.
Present-tense names throughout (`project_event_naming_revisit`).

---

## 4. Usage patterns

### 4.1 Single-tier, static pages (the default — rail never appears)

```python
import bootstack as bs

with bs.AppShell(title="My App", size=(800, 540)) as shell:
    shell.commandbar.add_spacer()
    shell.commandbar.add_button(icon="circle-half", on_click=bs.toggle_theme)

    with shell.add_page("dashboard", text="Dashboard", icon="speedometer2"):
        with bs.VStack(fill="x", gap=12, padding=24):
            bs.Label("Dashboard", font="heading-lg")
            bs.Label("Welcome back.")

    with shell.add_page("inbox", text="Inbox", icon="inbox"):
        bs.Label("Inbox", font="heading-lg")

    shell.add_separator()
    shell.add_header("Documents")

    with shell.add_page("files", text="Files", icon="folder"):
        bs.Label("Files", font="heading-lg")

    with shell.add_footer_page("settings", text="Settings", icon="gear"):
        bs.Label("Settings", font="heading-lg")

    shell.navigate("dashboard")
shell.run()
```

### 4.2 Single-tier, data-bound list (master–detail, still no rail)

```python
from bootstack.data import MemoryDataSource

devices = MemoryDataSource().load([...])

with bs.AppShell(title="Devices") as shell:
    shell.list_nav(source=devices)          # claims the implicit workspace

    @shell.detail
    def show(record):                        # re-rendered per selection
        with bs.VStack(fill="both", gap=12, padding=24):
            bs.Label(record["title"], font="heading-lg")
            bs.Label(record["text"])
    # no navigate() needed — first record auto-selected
shell.run()
```

### 4.3 Two-tier (rail appears — one provider per workspace)

```python
with bs.AppShell(title="Instrument Console", size=(960, 600)) as shell:
    shell.commandbar.add_spacer()
    shell.commandbar.add_button(icon="circle-half", on_click=bs.toggle_theme)

    # WS 1 — static authored pages
    with shell.add_workspace("acquire", text="Acquire", icon="cpu") as ws:
        with ws.add_page("sensors", text="Sensors", icon="thermometer-half"):
            bs.Label("Sensors", font="heading-lg")
        ws.add_separator()
        ws.add_header("Hardware")
        with ws.add_page("ports", text="Ports", icon="usb-symbol"):
            bs.Label("Ports", font="heading-lg")

    # WS 2 — flat data-bound master–detail
    with shell.add_workspace("devices", text="Devices", icon="hdd-stack") as ws:
        ws.list_nav(source=devices)
        @ws.detail
        def show_device(record):
            bs.Label(record["title"], font="heading-lg")

    # WS 3 — hierarchical data-bound
    with shell.add_workspace("library", text="Library", icon="folder") as ws:
        with ws.tree_nav() as tree:
            tree.add_nodes([...])
        @ws.detail
        def show_node(record):               # normalized: record dict, not node obj
            bs.Label(record["text"], font="heading-lg")

    # global Settings pinned to the rail bottom
    with shell.add_footer_workspace("settings", text="Settings", icon="gear") as ws:
        with ws.add_page("general", text="General", icon="sliders"):
            bs.Label("Settings", font="heading-lg")

    # passive global status in the bottom band (interactive controls stay on the
    # commandbar). Renders because items were added.
    shell.statusbar.add_widget(bs.Badge("0 devices", accent="primary"))
    shell.statusbar.add_spacer()
    shell.statusbar.add_text("Ready")

    shell.navigate("acquire", "sensors")     # workspace first, then page
shell.run()
```

### 4.4 Custom panel (escape hatch — hides but does not compact)

```python
with shell.add_workspace("tools", text="Tools", icon="tools") as ws:
    with ws.panel():                         # blank sidebar container; custom mode
        bs.Label("Filters", font="heading-md")
        with bs.Accordion():                 # allowed here (not in provider mode)
            ...
    # you drive the content region yourself (register pages + navigate, or swap frames)
```

---

## 5. Implementation plan (each step leaves a working shell)

1. **`NavModel` (headless)** — state machine, transitions, per-workspace memory,
   the VS Code `activate_rail` gesture, `subscribe`. Full unit tests, no Tk.
2. **Region layout (Layer 1)** — band grid + body paned slots + show/hide/size.
   Dumb, no nav semantics. Build the `statusbar` band (minimal, reusing the
   CommandBar strip primitive); reserve the `dock` slot.
3. **Wire model ↔ regions, single-tier path** — rail hidden; `add_page` works;
   `navigate`/`on_page_change`. Public handles for `commandbar`/`content`.
4. **Provider abstraction + static provider** — `NavProvider` Protocol;
   `add_page` as the first provider; selection→content swap.
5. **Data-bound providers** — `list_nav` then `tree_nav`; `@detail` master-detail;
   normalize payload to the record dict (open-decision #2).
6. **Two-tier rail** — `add_workspace`/`add_footer_workspace`; `Rail` widget; VS
   Code gesture; per-workspace panel deck; `on_workspace_change`.
7. **Sidebar collapse** — chevron (compact↔expanded) + hamburger/Ctrl-B
   (visibility); shared `rail_width`/`sidebar_width` tokens so single-collapse and
   two-tier rail look identical; `remember_nav_state` persistence.
8. **Custom panel mode** — `ws.panel()`; `supports_compact = False`.
9. **Elevation tokens** — rail/sidebar/content as named elevation tokens
   (light/dark flip).
10. **Detail dock** *(reserved — likely a follow-on)* — wire the slot + axis.
11. **Polish** — window-control accessors, fold `menu_layout`/`chrome_surface`,
    `bootstack.events` additions, docs (clean `-W` build), `test_public_surface`.

---

## 6. Open questions — RESOLVED (2026-06-13)

1. **SideNav standalone vs absorbed.** **Resolved:** stays standalone *and*
   simplified — collapsible groups removed. See locked decision #11.
2. **Custom-mode content wiring.** **Resolved:** expose **both** — `ws.panel()`
   for the sidebar container and `ws.content` for hand-driven content swapping.
3. **Status bar scope.** **Resolved:** build minimal, shell-global, reusing the
   CommandBar primitive (see §3.5). Per-view segments deferred.
4. **`navigate` signature overload.** **Resolved:** positional overload —
   `navigate(page)` (single-tier) / `navigate(workspace, page)` (two-tier).
5. **Auto-select first item** for data-bound providers. **Resolved:** on by
   default — `list_nav`/`tree_nav` auto-select the first item so the detail body
   renders without an explicit `navigate`.
```
