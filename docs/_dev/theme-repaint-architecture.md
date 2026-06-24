# Theme repaint — architecture

How widgets recolor when the theme changes (`set_theme` / `toggle_theme`). The
goal of this design is **one rule**, no per-widget visibility/`<Map>` bookkeeping.

## The one rule

- **A tree widget that needs to recolor defines `_bs_apply_theme(self)`.** It does
  *all* of that widget's imperative theme work in one place — re-resolve colors
  and redraw (canvas content, theme-colored PhotoImages, tag colors, etc.). The
  widget's plain background is handled separately (see "surfaces" below), so the
  hook owns only what the ttk/style engine doesn't.
- **A non-tree or cross-cutting reactor binds `<<BsThemeChanged>>` on the root.**
  Reserved for things that aren't tree widgets: the `Image` handle, the OS-level
  DWM window chrome, and the app-level `on_theme_change` callback. (CodeEditor's
  highlighting extensions also live here for now.)

That's it. There is no `_enable_theme_repaint`, no STD publisher subscription, no
per-widget `<Map>` deferral, and no widget registry.

## The walk

`Style.apply_theme_walk(root_widget, *, only_stale)` (in `style/style.py`) walks a
subtree and, for each themed widget, calls `Style._apply_theme_to_widget`, which:

1. re-applies the **surface background** for an autostyled Tk widget
   (`call_builder(w, surface=w._surface)`), then
2. calls the widget's **`_bs_apply_theme()`** hook if it has one, then
3. stamps `w._bs_theme_version = self._theme_version`.

Two triggers drive it — and **neither is `<Map>`**:

- **On a theme change** (`theme_use`): `apply_theme_walk(root, only_stale=False)` —
  recolor every *visible* widget now. Off-screen widgets are left stale.
- **On a container-show**: `apply_theme_walk(shown_subtree, only_stale=True)` —
  recolor every *stale* widget in the now-visible subtree, **ignoring
  `winfo_viewable()`** (it is unreliable for a widget embedded in a scrollable
  page's canvas — it can report `False` for an on-screen widget). Stale = the
  widget's `_bs_theme_version` is behind the current `_theme_version`, so a
  navigation *without* a theme change is a no-op (no flicker).

Visibility is resolved at apply time; nothing is deferred to a hoped-for event.

### Container-show triggers

Any container that hides/shows children by un/re-`pack`ing must call the walk on
show. Current call sites:

- `PageStack._navigate` → covers AppShell/Workbench pages **and** `Tabs` (Tabs
  routes its content through a `PageStack` — see `tabs/tabview.py`).
- `Expander.expand` → covers `Accordion` sections.

If you add another hide/show container, call
`get_style().apply_theme_walk(shown_subtree, only_stale=True)` after you pack the
content (deferred to `after_idle` so it is mapped first).

## Surfaces — the frozen-hex gotcha

The autostyle wrapper (`style/style_resolver.py`) stores a widget's `_surface`
**token** (e.g. `'card'`) and applies the initial background. On a theme change
the walk re-resolves that token. So a canvas widget must pass the **surface
token**, never a resolved color:

```python
# WRONG — freezes a hex; the walk re-applies the OLD color forever.
Canvas(self, background=self._resolved_surface)
# RIGHT — the walk re-resolves the token each theme.
Canvas(self, surface=self._surface_token)
```

This was the cause of the Meter canvas "background doesn't recolor" bug. (An
explicit `surface=` now wins over inheritance in both the ttk and Tk autostyle
paths.)

## Known limitations

- A widget hidden by `detach()` or sitting in a **withdrawn** Toplevel during a
  theme change won't recolor until it is re-shown through one of the container
  triggers (or the theme changes again while it is visible). These are rare; add
  a trigger if a real case appears.

## History

Replaced three overlapping mechanisms (the STD publisher + `_enable_theme_repaint`
for canvas content; a `register_tk_widget` WeakSet + `_rebuild_all_tk_widgets` +
`<Map>` registry for Tk surfaces; per-widget hacks). All shared one fragile
assumption — that an off-screen widget gets a usable `<Map>` when it reappears —
which is false for canvas-embedded widgets, so each grew its own workaround. The
walk + explicit container-show triggers removed that assumption (and the
"`_tk_widgets` grows forever" leak).
