# AppShell + Navigation — implementation spec

Status: **DRAFT for review** (2026-06-13). Actionable spec derived from
`appshell-design.md` (the rationale/north-star) + the locked decisions from the
2026-06-13 design discussion. This supersedes the *API shapes* in the design doc
where they conflict (e.g. `shell.toolbar` → `shell.commandbar`); the design doc
remains the source for *why*.

Clean-slate rewrite of `AppShell` + the shell's navigation. Pre-release →
clean breaking changes, no compat shims.

---

## Revision 2 — model finalization (2026-06-13, with maintainer)

A design conversation (driven by VS Code pattern analysis) refined the navigation
model. The decisions below **supersede** parts of §1 where they conflict (marked
inline). Net: the model is *simpler* — one strong icon tier (the rail), one quiet
panel tier (the sidebar), **tier-relative** styling, and collapsible groups
restored.

**R1 — Drop the *seam rule*, not `compact` itself.** Compact (icon-only) stays a
real sidebar state, but **only for a standalone static sidebar** (no rail) — the
primary nav narrowing to an icon strip (Gmail / admin-dashboard style). What is
removed is the **seam rule**: the mandate that a compacted single sidebar adopt the
rail's exact paradigm + `rail_width` so it looks indistinguishable from a two-tier
rail (decisions #1/#5/#13). Compact is just the static pills rendered icon-only at
an icon-fitting width — it is *not* pretending to be a workspace rail (there is no
rail when it's standalone, so no confusion). Specifics:
- **Sidebar axis stays `hidden ↔ compact ↔ expanded`** — NavModel `SidebarMode`
  is unchanged (`compact` retained).
- **Compact is static-only.** `list_nav` / `tree_nav` are **`hidden ↔ expanded`**
  only — a label-less data list / icon-only hierarchy is meaningless ("a list nav
  can be hidden, but not compact, whatever that even means"). So
  `supports_compact` = `True` for the static provider, `False` for list/tree.
- **Under a rail, every tier-2 sidebar is `hidden ↔ expanded`** regardless of
  provider — an icon-only panel beside the icon rail is two icon columns = noise
  (the §2.2 invariant). So compact applies only to the *standalone* static case.

Icon-compaction-into-a-rail-lookalike is what's gone; "want a real rail" → add
workspaces (the rail is a first-class tier you opt into, not an emergent state of a
collapsed sidebar).

**R2 — Collapsible accordion groups are restored (reverses decision #11's
removal).** "A static sidenav with collapsible section headers" and "a 1-level
accordion" are the *same widget* — a non-collapsible header is just a group pinned
open. So this is **folded into the static provider** (optional `collapsible`
groups), not a 4th provider. Hard rule: **accordions are 1 level** (collapsible
section → flat items, no nesting). Depth → `tree_nav`. This is what fills real
two-tier sidebars (VS Code Explorer/Extensions, Slack/Discord channels).

**R3 — Sidebar styling is tier-relative, not provider-absolute.** Prominence
tracks whether a rail outranks the sidebar:
- **Static, standalone (no rail) = the primary nav** → **button-like, rounded
  "pill" items** (macOS System Settings vibe). Reuses the rounded `button` asset
  family.
- **Static, under a rail = tier-2** → **quiet flat full-width list rows** (the
  rail is now the strong tier; the sidebar recedes).
- **`list_nav` / `tree_nav` keep their list/tree row language in *all* contexts**
  — a data list reads as a list (Mail's sidebar), never as pills. *("You'd never
  see a pill sidebar next to a list nav — that's the wrong navigation structure.")*
- **Rail** → the VS Code **activity-bar** treatment: muted unselected glyph →
  **full-strength glyph + accent indicator bar**, **FLAT (not rounded)**, on its
  **own chrome/elevation color**. The rail is built on the `navitem` **bar** asset,
  **not** the rounded `button` asset. The rounded "pill" is the *standalone-static*
  look ONLY — do not give it to the rail (a previous draft conflated the two).

Because shell-level `add_page` (no rail) and workspace `add_page` (rail present)
are mutually exclusive, a provider always knows its tier at mount — no runtime
flipping between pills and flat rows.

**R4 — Static `add_page` stays on both shell and workspace.** It is the
single-tier idiom, but valid under a rail (e.g. a footer "Settings" workspace with
General/Appearance sub-pages), rendered in the tier-2 quiet language per R3.

**R5 — One sidebar selection language *per tier*.** All providers in the same tier
render rows alike (decision #12's spirit): tier-2 (under-rail) = quiet wash, no
bar, no accent text; tier-1 standalone static = rounded pill. The rail owns the
bar.

**R6 — Ctrl-B collapses the sidebar as far as is *useful*, context-dependently.**
VS Code's Ctrl-B fully hides the side panel because the activity bar (rail) stays
as a fallback nav. A **standalone static sidebar is the only nav**, so hiding it
strands the user — there, Ctrl-B = **expanded ↔ compact** (shrink to icons, never
strand). For a **data-bound** sidebar (can't compact) or **any sidebar under a
rail** (rail remains as nav), Ctrl-B = **expanded ↔ hidden** (VS Code behavior).
So: compact-toggle when `not rail_visible and provider.supports_compact`, else
visibility-toggle. The explicit verbs `toggle_sidebar()`/`show_sidebar()`/
`hide_sidebar()` stay **pure visibility** (the hamburger primitive); only the
keyboard shortcut is context-smart. The step-9 chevron does expanded↔compact, so
chevron and Ctrl-B agree for the static case.

**Re-scoped build order** (supersedes §5 steps 7–11):
- **7 — Sidebar visibility/compaction + persistence** (slimmed): wire
  `hidden ↔ compact ↔ expanded` → view, where **compact = icon-only + narrower
  width, gated to the standalone static case** (no rail, `supports_compact`);
  `toggle_sidebar`/`show_sidebar`/`hide_sidebar` (pure visibility) + `sidebar_mode`
  rw prop + context-smart **Ctrl/Cmd-B** (compact-toggle for standalone static,
  else hide — R6); `remember_nav_state` (sidebar_mode + per-workspace page). **No
  visible chevron control** (the trigger for compact↔expanded is folded into step
  9). **No PanedWindow sash** (deferred to a separate 7b follow-up).
- **8 — Collapsible groups (accordion) + custom panel.** 1-level collapsible
  groups in the static provider; `ws.panel()` custom mode.
- **9 — Visual hierarchy (the big styling pass — discuss before implementing).**
  Tier-relative styling per R3: rail = FLAT VS Code bar treatment (`navitem`
  asset: muted→full-strength glyph + accent bar, NOT rounded) + own chrome color;
  tier-2 sidebar quiet list rows; tier-1 standalone static rounded pills;
  `list_nav` → real `ListView`, tree aligned to the quiet wash; named elevation
  tokens (rail/sidebar/content); tree empty-state placeholder.
  - **Collapsible groups (step 8):** **indent/nest** grouped items under their
    header so grouped vs ungrouped reads clearly (the unindented look in step 8 is
    why a mixed sidebar jars); style the chevron (size/weight/placement) and the
    collapsible-header treatment (distinct from a plain static label); quiet the
    per-item accent fg/icon coloring per R3.
  - **Sidebar nav-item style variants (native Toolbutton variants):** the items
    are `RadioToggle`s styled by native variants — `nav-quiet` (under-rail: square
    `navitem` wash + neutral fg), `nav-pill`/`nav-pill-compact` (standalone:
    rounded `card` pill + accent fg). The pill is currently a **ghost** treatment
    (subtle accent tint + accent fg). **FOLLOW-UP:** add a **`solid`** pill variant
    — fill the pill with the solid accent token and use the on-color foreground
    (e.g. white-on-accent); ghost stays the default. This generalizes to offering
    the button-family variants (ghost/solid/outline) for sidebar items.
  - **Composition guideline (docs, not enforced):** use grouping *consistently* —
    a flat list, or everything under collapsible sections (VS Code Explorer); a
    single primary item *above* groups is acceptable, but don't sprinkle loose
    top-level items among collapsible groups. The pinned footer is conventionally
    standalone and exempt. The API allows the mix (flexibility); examples/docs
    model the consistent idiom.
- **10 — Dock** (reserved, deferred). **11 — Polish** + swap public AppShell.
  Includes the deferred **rail follow-ups**: (a) **footer actions/menus** — a
  non-radio path for plain icon buttons + icon menu buttons pinned to the rail
  footer (VS Code's gear/accounts), styled to match the rail (muted→hover, no
  selection bar); (b) **rail item tooltips** — the rail is icon-only, so each
  item wants a tooltip (built into the per-item `RadioToggle`). Both designed
  with the `shell.rail` public façade in this step.

---

## Revision 3 — accordion sections vs. static groups (2026-06-13, with maintainer)

Step 8 shipped "1-level collapsible groups" as a **flat run** — a header plus the
sibling items following it, where collapse just *hides the run*. That model
conflated two different primitives and can't express "an accordion containing a
list" (the body isn't a container, just later siblings). Revision 3 corrects the
model. **Supersedes Revision 2 / R2** (the flat-accordion restoration).

### The three sidebar archetypes

The grouping element is the tell. A static **header is a label**; an accordion
**header is a control**. They look different by design.

| archetype | grouping element | items | collapse |
|---|---|---|---|
| **Flat static** | none | quiet/pill nav rows | compact → icons |
| **Grouped static** | `add_header()` — a quiet label | quiet nav rows | hidden ↔ expanded |
| **Accordion** | `add_group()` — an interactive bar (`Expander`) | *anything* (rows / list / tree / custom) | hidden ↔ expanded |

### Accordion — `add_group()` returns a `NavGroup` (context manager + content host)

A `NavGroup` exposes the **same content verbs as the workspace** (`add_page`,
`list_nav`, `tree_nav`, `panel()`, `@detail`) plus `expand`/`collapse`/`toggle`/
`expanded`/`title`. Each section owns its content; selecting anything in any
section drives the **one shared content/detail region** (the VS Code editor-area
model). Backed by the existing `Expander` (header is a `CompositeFrame` with
hover/press/selected — *configured*, not hand-styled); reuses the existing
providers mounted into the section body (sidebar side) + the shared content region
(detail side).

```python
ws = shell.add_workspace("explorer", text="Explorer", icon="files")

with ws.add_group("Folders", icon="folder") as g:   # section of nav pages
    g.add_page("src",   text="src",   icon="folder")
    g.add_page("tests", text="tests", icon="folder")

with ws.add_group("Outline") as g:                   # section that IS a tree
    g.tree_nav(nodes=outline_nodes)
    @g.detail
    def show(node): ...

with ws.add_group("Timeline", expanded=False) as g:  # section that IS a list
    g.list_nav(source=timeline)
    @g.detail
    def show(record): ...
```

- `ws.add_group(title, *, icon=None, expanded=True)` → `NavGroup`.
- Detail is **per-section** for data-bound sections (`@g.detail`); `add_page`
  sections render their page. All feed the shared content region (one active at a
  time, via a content deck keyed by active item).
- `ws.expand_all()`/`collapse_all()` retarget to the sections.

### Grouped-static — `add_header()` is now a pure label

`collapsible=` is **removed** from `add_header` (and from `SideNavHeader`). A
static header is a non-interactive small-caps secondary label; the items after it
are ordinary quiet nav rows, **flush** under the label (the label's color + top
margin carry the hierarchy — no indentation). *Decision: grouped-static items keep
the button/quiet-row language, NOT list-item rows* — row style encodes what the
row is (nav rows = pages; list rows = records). The header label is what makes
grouped-static "its own thing"; the items don't diverge. Genuinely list-dense
grouped rows are the signal to use an accordion section containing a `list_nav`.

### Model implications

1. **Workspace = a container of content-hosts.** Today one `_provider`. New: a
   workspace is *either* a single provider (flat/grouped static, list, tree,
   custom) *or* a set of accordion sections. First `add_group()` claims accordion
   mode; mixing top-level `add_page` with groups is disallowed (the consistency
   guideline).
2. **Key aggregation.** Each section reports its keys up; the workspace aggregates
   (keys unique within a workspace). `NavModel` still holds one `(workspace,
   page)` truth.
3. **Navigate-to-reveal.** `navigate(ws, key)` finds the owning section, expands
   it, shows + visually selects there, and clears the visual selection in sibling
   sections.
4. **Compact.** Flat-static stays compactable; grouped-static and accordion are
   `supports_compact=False` (hidden ↔ expanded) — VS Code "collapses completely":
   Ctrl-B hides the whole sidebar, only the rail remains. No icon-flattened
   accordion.

### Implementation steps (step 8 redesign)

1. **Revert the flat-run hack** — drop `collapsible=`/chevron/`_toggle_group` from
   `SideNavHeader` + `NavPanel` + `add_header`; header is a label again.
2. **`NavGroup`** — an `Expander`-backed content host exposing the workspace
   content verbs; mounts its provider into the `Expander.content` (sidebar) +
   shared content region (detail). Context manager.
3. **Workspace accordion mode** — `add_group()`; aggregate keys/selection across
   sections; route `show`/`select_visual` to the owning section; nested content
   deck. `expand_all`/`collapse_all` retarget.
4. **Styling** — configure the `Expander` header to the workspace nav language
   (quiet vs pill); section body inherits the sidebar surface.
5. **Tests** — rewrite `test_shell_groups`; add accordion-section + heterogeneous-
   body + navigate-to-reveal cases.

### Side note (unrelated, logged for later)

Create a **`'secondary'` Tabs variant** that draws the selection indicator at the
**top** of the tab instead of the bottom. Not part of the appshell work.

---

## Revision 4 — accordion CUT (2026-06-13, with maintainer)

After building the Revision-3 accordion (`add_group` → `NavGroup` over `Expander`,
heterogeneous list/tree/page section bodies, shared content region, navigate-to-
reveal), the maintainer pulled the plug: **the accordion is not worth the
trouble.** The heavy, bug-prone part was "a section that *is* a list/tree" — the
shared content deck across sections, reveal into a collapsed data view, sibling-
selection clearing, the no-intrinsic-height fix, the header highlight wash. It also
conflated content-hierarchy with navigation, exactly what the design doc warns
against. **Supersedes Revision 2 / R2 and Revision 3.**

**Decision: drop the built-in accordion.** The sidebar has three authored shapes:

| shape | how | scroll |
|---|---|---|
| **flat-static** | `add_page` | compact → icons; item area scrolls |
| **grouped-static** | `add_page` + `add_header` (a plain **muted** label, flush items, larger top gap for the group break) | item area scrolls |
| **data-bound** | `list_nav` / `tree_nav` | the recycling widget scrolls itself |

A collapsible section that hides/reveals a sub-list is a **content** concern —
compose `bs.Accordion` inside a custom `panel()`. `NavGroup` / `ProviderHost` were
deleted; `Workspace` is back to a single provider; `add_group` / `expand_all` /
`collapse_all` are gone from `Shell`/`Workspace`; `SideNavHeader` is a plain label.

**Also shipped this pass (the grouped-static finish):**
- **Muted section headers** — `SideNavHeader.DEFAULT_ACCENT='muted'` (was full-
  strength); a header is quiet chrome, the clickable rows carry the contrast.
- **Bigger group break** — `NavPanel.add_header` top padding `10→16` (bottom stays
  `4`, so the header still hugs its own items).
- **Scrollable static nav** — `NavPanel` wraps its item area in a `ScrollView`
  (mousewheel + auto-hiding bar) with the **footer pinned** outside it. Overflow-
  gated: when content fits → `scrollbar_visibility='never'` (no gutter, no bar,
  no footer divider, items full-width); when it overflows → `'scroll'` (gutter +
  bar) and a `SideNavSeparator` divider appears above the footer. The 8px-vs-bar-
  width difference + a 4px epsilon gives stable hysteresis (no flicker). Canvas
  background is painted to the sidebar surface (repaint on `<<BsThemeChanged>>`).
- **Square (`nav-quiet`) under a rail, `nav-pill` standalone stays** — confirmed:
  under a rail you have mixed-provider workspaces (static + list + tree) that must
  share one row language, so the pill is single-tier-only.

**Also shipped after the cut (sidebar styling round, committed):**
- **Scrollable static nav** — `NavPanel` item area in a `ScrollView`; footer
  pinned outside. Overflow-gated: fits → no gutter/bar/divider, items full-width;
  overflows → bar + footer divider. The scrollbar gutter is **absorbed into the
  right inset** (right margin stays even, not inset+gutter) and the footer
  re-aligns to the scrolled rows — both adapt to the live bar width.
- **Thin scrollbar** — new reusable **`'thin'`** scrollbar variant (4px solid
  square thumb via `create_box_image`, track painted to the surface); `ScrollView`
  threads its surface to its scrollbars. `NavPanel` uses it. (The 8/17px confusion
  earlier was a stale-read artifact — the bar was always thin; it's now 4px.)
- **Muted section headers** (`SideNavHeader.DEFAULT_ACCENT='muted'`) + a larger
  group break (header top padding `10→16`).
- **Empty-state placeholders** — `tree_nav` (opens unselected) and an empty
  `list_nav` show a centered muted placeholder until a row is picked
  (`placeholder=` on both).

**Deferred → step 11 (the public-AppShell swap):**
- **Drop the standalone `bs.SideNav`.** Decided (its unique value is thin — app
  nav = AppShell, in-dialog nav = vertical `Tabs`; and it duplicates `NavPanel`).
  Coupled to removing the old AppShell: the current public `bs.AppShell` is still
  the OLD sidenav-based one, so SideNav can't be removed until the new `Shell` is
  swapped on. `SideNavHeader`/`SideNavSeparator` stay (used by `NavPanel`).
- **Wire + style the statusbar and menubar/command bar** into the new shell — the
  `chrome` band is an empty `Frame` and the `statusbar` is a bare `Toolbar`; the
  public `commandbar`/`menubar`/`statusbar` APIs aren't on the new `Shell` yet.
- **`Workspace` context-manager support** (`with shell.add_workspace(...) as ws:`).
- Public AppShell façade (`commandbar`/`nav`/`pages` + window-control accessors).

**Separate initiative:** expose/document the `'thin'` scrollbar variant publicly +
audit other scrollable widgets for narrow bars (memory
`project_thin_scrollbar_initiative`).

Tests: `test_shell_groups` rewritten for grouped-static. Throwaway demos
`development/shell_*_demo.py` stay untracked.

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
5. **Collapse-to-rail requires icon-representable content.** *(REVISED by Revision
   2 / R1 — `compact` (icon-only) is retained but applies ONLY to a standalone
   static sidebar; the seam rule "compact looks like the rail" is removed. Nothing
   compacts *into a rail*.)* Inherent constraint, not a bug — only the static
   provider compacts (icon-only); list/tree and custom panels only hide.
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
11. **`SideNav` stays standalone, and is simplified.** *(PARTLY SUPERSEDED by
    Revision 2 / R2 — collapsible groups are RESTORED as 1-level accordions folded
    into the static provider. The rest of this decision stands.)* It remains a public widget
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
13. **Per-tier visual hierarchy (rail vs sidebar vs content).** *(REVISED by
    Revision 2 / R3 — the per-tier hierarchy stands; the seam rule is removed and
    sidebar styling is now tier-relative: standalone static = rounded pills
    (compact = those pills icon-only), under-rail static = quiet list rows. The
    RAIL uses the FLAT `navitem` bar treatment (muted→full-strength glyph + accent
    bar), NOT the rounded `button` asset — rounded is the standalone-static pill
    ONLY. The "reuse ToggleButton + rounded button asset for the rail" wording
    below is the conflation R3 corrects.)* Three reinforcing
    axes of distinction so two icon columns never compete and *"the eye lands on
    exactly one high-contrast item per tier"* (design doc §6):
    - **Elevation:** rail = 0, sidebar = 1, content = 2 — **named elevation
      tokens** (light themes darken with depth; dark themes often lighten — the
      token lets it flip correctly per theme).
    - **Active markers (REVISED 2026-06-13 to the maintainer's VS Code model —
      this supersedes the earlier "bar is sidebar-only" of decision #12):**
      - **Rail (workspace) = the STRONG tier.** Unselected glyphs **muted**;
        selected glyph **full color** (the **toggle-button** muted→full-color
        treatment — *reuse the existing ToggleButton/toggle styling + rounded
        `button` asset*, NOT the flat `navitem` asset), **plus the indicator bar**
        (accent OR just foreground). The rail owns the bar.
      - **Sidebar list (page) = the QUIET tier.** **Subtle wash only** —
        `subtle(accent)`, **no bar, no muted/full-color, no accent text**. Just a
        quiet selection wash.
      - Rationale: one bar (on the rail) + a quiet list resolves the accent-overload
        the maintainer flagged (rail accent + sidebar bar + sidebar accent text was
        "too much"). VS Code: activity bar = bar + muted/full-color; side list =
        subtle wash.
    - **Icon scale — two tokens:** `inline_icon_size` (small, ~16–18px
      density-scaled — expanded item beside a label) vs `rail_icon_size` (larger,
      ~28px — standalone categorical glyph). Size alone signals the tier.
    - **List rendering:** `list_nav` should use the **real `ListView` widget**
      (recycling for large/live lists + the subtle-wash selection it already does);
      static `add_page` keeps `NavPanel` (ListView is overkill — can't do
      interspersed headers/separators/footer, and recycling is wasted on a few
      authored items). The `tree` uses the `Tree` widget; align its selected wash
      to the sidebar's subtle wash (no accent text), per decision #12.
    - **The seam rule:** a compacted *single* sidebar adopts the rail paradigm
      (rail treatment + `rail_width`), so collapsing a one-workspace sidebar looks
      like a two-tier rail. With the revised model the rail = toggle-button +
      muted/full-color + bar, so the compacted sidebar shows that.
    - **Interim state (step 6):** the rail is built from compact `SideNavItem`
      (flat navitem asset, ~28px icon, no bar, accent-glyph-on-select) — a
      placeholder; step 9 rebuilds it on the toggle-button treatment above. The
      tree opens **unselected** by default (correct for a hierarchy); add an
      empty-state placeholder in the content area so a fresh tree isn't blank.

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
SidebarMode = Literal["hidden", "compact", "expanded"]  # compact = static-only (R1)

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
so "hidden but expanded" is unrepresentable. *(Revision 2 / R1: `compact` is
retained but applies ONLY to a standalone static sidebar — `list_nav`/`tree_nav`
and any under-rail tier-2 sidebar use `hidden ↔ expanded` only. A single sidebar
never morphs into a rail-lookalike; "want a rail" → add workspaces.)* In two-tier
the rail is the always-present tier-1, so the secondary panel uses only
`hidden ↔ expanded` (no own compact — two icon-rails side by side is noise).

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
| `collapsible` | `bool` | `True` | show the in-sidebar chevron + bind Ctrl/Cmd-B (collapse: compact for a standalone static sidebar, else hide — see R6) |
| `nav_accent` | `AccentToken \| str` | `'primary'` | active-item accent |
| `rail_labels` | `bool` | `False` | show a caption under each rail icon (widens the rail); icon-only otherwise |
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
9. **Elevation + selection tokens** — the visual hierarchy per the REVISED
   decision #13 (the authoritative model). Concretely:
   - **Rail:** rebuild on the **toggle-button treatment** (muted unselected →
     full-color selected, rounded `button` asset) **+ the indicator bar** (accent
     or foreground); replace the interim compact-`SideNavItem` rail. ~28px glyph.
   - **Sidebar list:** reduce to **subtle wash only** — strip the bar + accent
     text from the `NavPanel` nav items (currently flat `navitem` asset has the
     bar).
   - **`list_nav` → real `ListView`** (recycling + subtle wash); static keeps
     `NavPanel`. **Tree** selected wash → align to the sidebar subtle wash
     (role-scoped; don't touch content-area grids), no accent text.
   - Rail/sidebar/content as named **elevation tokens** (light/dark flip).
   - **Tree empty-state placeholder** in the content area (tree opens unselected).
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
