# PLAN — collapse `_core/capabilities` (the Tk-surface veneer)

Unmilestoned, unfiled. **Written from a measurement pass, 2026-08-28.** No issue exists yet; file
one before cutting the branch if you want it tracked.

⚠ **Read this whole file before editing.** The pass found **three latent defects** in the code it
proposes to delete. Two of them change what "removal" means: they are not removals, they are fixes.

---

## Why

`_core/capabilities/` was written when `_impl` widgets were the product and the mixins gave Tk a
typed, documented surface. The public layer now wraps those widgets, public widgets are plain Python
objects that never inherit any of this, and `_core` is private — so the docstrings have no reader
and the annotations describe a layer no user touches.

⚠ **The package is THREE things wearing one name, and only the first has lost its purpose:**

| group | files | verdict |
|---|---|---|
| Tk-surface mixins | 12 modules, 91 methods | the veneer — this is what collapses |
| `busy.py` | 1 module, 5 methods | **dead**: `BusyMixin` is imported by nobody, not even the aggregator |
| `signals.py`, `localization.py` | 2 modules, 11 functions | **real, live, widely imported — LEAVE ALONE** |

The package's own `__init__.py` already admits this: it exports only `signals` and `localization`
and its docstring lists only those two as "Capabilities". The other thirteen modules are exported
by nothing.

---

## What the measurement says

An AST pass over all 91 methods classified each as a pure pass-through (a single statement
delegating to `super().<same_name>(...)`) or as carrying real logic:

```
module          methods  passthru  real
after.py              4         3     1   after_repeat
bind.py               7         7     0
bindtags.py           5         0     5
busy.py               5         3     2
clipboard.py          5         3     2
focus.py              7         7     0
grab.py               5         5     0
grid.py              10         3     7
pack.py               6         3     3
place.py              5         2     3
selection.py          5         4     1
winfo.py             27        26     1
-----------------------------------------
TOTAL                91        66    25
```

**66 of 91 are pure pass-throughs.** Of the 25 with a body, most only re-derive a default the
native method already has. Measured against real `tkinter` signatures:

```
bindtags               (self, tagList=None)          <- mixin re-implements the None branch
grid_rowconfigure      (self, index, cnf={}, **kw)   <- same
grid_columnconfigure   (self, index, cnf={}, **kw)   <- same
grid_slaves            (self, row=None, column=None) <- mixin expands into 4 identical branches
winfo_pathname         (self, id, displayof=0)       <- same
selection_handle       (self, command, **kw)         <- mixin only coerces None -> ''
clipboard_get          (self, **kw)                  <- clipboard_get_text is a pure alias
place_configure        (self, cnf={}, **kw)          <- and tkinter already aliases these:
                                                        tk.Grid.grid  is grid_configure  == True
                                                        tk.Pack.pack  is pack_configure  == True
                                                        tk.Place.place is place_configure == True
```

**Revised tally: ~66 pass-through + ~12 re-deriving-native = ~78 removable; 13 genuinely additive.**

⚠ **And 12 of those 13 have ZERO call sites.** Measured across `src/` and `tests/`:

```
after_repeat 0 | bindtags_prepend 0 | bindtags_append 0 | bindtags_remove 0 | bindtags_replace 0
clipboard_get_text 0 | selection_own_set 0 | busy_hold 0 | busy_forget 0
clipboard_set 1   <- src/bootstack/clipboard.py:35
```

The only additive code that is actually exercised is `clipboard_set` (one caller) and the
`_on_child_*` layout interception in `grid.py` / `pack.py`.

⚠ **The fluent `return self` chaining is NOT a reason to keep anything.** Searching `src`, `tests`
and `docs` for a chained `.pack(...).x` / `.grid(...).x` / `.place(...).x` returns **zero** hits.

---

## The three defects this pass found

⚠⚠ **All three sit in code the checklist deletes. Deleting them IS the fix — but each one changes
behavior, so none of this is a pure no-op refactor. Decide each deliberately.**

### 1. `grid_propagate()` / `pack_propagate()` are broken as GETTERS

Native tkinter distinguishes query from set with a sentinel, `flag=Misc._noarg_`. The mixin
re-declares the parameter as `flag: bool | None = None` and forwards `None` straight through, so a
no-arg call takes native's **setter** branch and pushes `None` into Tcl. Measured, with a control:

```
plain tkinter    frame.grid_propagate() -> True   (getter works)
bootstack Frame  frame.grid_propagate() -> None   (silently broken)
                 frame.grid_propagate(False) -> ok (setter still fine)
```

The mixin's own docstring promises *"If None, acts as a getter."* It does not. **Deleting the two
methods restores the native sentinel and fixes this.**

### 2. `forget()` destroys `ttk.Panedwindow.forget(child)`

Not a capability module — it is in the aggregator, `_core/mixins/widget.py`. Measured:

```
ttk.Panedwindow.forget       : (self, child)
PanedWindow.forget resolves on: WidgetCapabilitiesMixin
its signature                : (self) -> None
pw.forget(0) -> TypeError: WidgetCapabilitiesMixin.forget() takes 1 positional argument but 2 were given
```

`widgets/splitview.py:379` already works around this by dropping to
`tk.call(str(w), "forget", pane)`, with a comment naming the collision. **That is a correct
workaround for broken inheritance, not caller misuse.**

⚠⚠ **AND THE CONVENIENCE IT SHADOWS WITH HAS NO CALLERS AT ALL — measured, so this is a plain
deletion and not a trade-off.** `grep -rn "\.forget()" --include="*.py" src tests docs` returns
**one line: the comment above.** Every real forget in the package reaches past the mixin to the
native class explicitly — `tk.Grid.forget(widget)` at `flexframe.py:244`, `gridframe.py:356,475,479`
and `tk.Pack.forget(widget)` at `packframe.py:147,215,219` — or uses `grid_forget`/`pack_forget`.
**bootstack's own layout frames already route around it.**

⚠ **`ttk.PanedWindow` is never used directly either**: it is subclassed once
(`_impl/primitives/panedwindow.py:23`) and instantiated once (`splitview.py:201`). So the blast
radius of deleting `forget()` is exactly one file — the one already working around it.

### 3. `selection_own_set()` raises unconditionally

```python
return super().selection_own(owner, command=command, selection=selection)
```

Native is `tk.Misc.selection_own(self, **kw)` — keyword-only. Measured:

```
f.selection_own_set(f) -> TypeError: Misc.selection_own() takes 1 positional argument but 2 were given
```

Zero callers, which is why nobody noticed. **It is the only "new API" in `selection.py` and it has
never worked.**

---

## Checklist

### Phase 0 — preconditions

- [ ] **Commit or park the uncommitted `colorutils` change first.** As of writing, `main` has an
      uncommitted working tree (the `_core/colorutils` removal). Do not start this on top of it.
- [ ] **Cut a branch.** `chore/collapse-capabilities-veneer` off `main`. Never on `main`.
- [ ] **`git mv` this file to `PLAN.md`** at the branch root, per `REVIEW-PROTOCOL.md` — a plan is
      written up front, lives at the root during the branch, and is archived back to `development/`
      **in the branch, before the PR opens**. ⚠ `git mv` stages the *indexed* blob; `git add` the
      moved file afterwards.
- [ ] **Set the round cap here, in this file, before writing code.** Suggest **2**.
- [ ] **Measure `main`'s suite on this box first**, so the after-figure means something.
      `.venv/bin/python tests/run_gui.py`. ⚠ The `1661 / 22` in `CLAUDE.md` is a **Windows** figure
      under `py -3.12` and is not comparable.

### Phase 1 — delete what nothing imports

- [ ] Delete `src/bootstack/_core/capabilities/busy.py` (72 lines, 5 methods). `BusyMixin` appears
      in no import anywhere — verify once more with
      `grep -rn "BusyMixin\|capabilities.busy" --include="*.py" src tests`.

### Phase 2 — delete the modules that are pure pass-through

Each of these is 100% (or 26-of-27) delegation. Removing them lets the identical `tkinter`/`ttk`
method resolve one step further down the MRO.

- [ ] Delete `capabilities/bind.py` (7/7 pass-through).
- [ ] Delete `capabilities/focus.py` (7/7). ⚠ `focus_set`/`focus_force` look additive because of
      `visual_focus=`, but that is **implemented by a monkey-patch on `tk.Misc`** in
      `_runtime/visual_focus.py:150-151`. After the patch installs, the native signature is
      byte-identical to the mixin's. The mixin only documents it.
- [ ] Delete `capabilities/grab.py` (5/5).
- [ ] Delete `capabilities/winfo.py` (26/27). ⚠ The one non-pass-through, `winfo_pathname`, only
      re-derives native's `displayof=0`. ⚠ **`winfo_containing` is a genuine narrowing** — the
      mixin drops `displayof` and renames `rootX/rootY` to `rootx/rooty`, so a keyword caller
      breaks. Grep for it before deleting; deleting restores the native signature.
- [ ] Delete `capabilities/place.py` (5 methods). No `_on_child_*` hooks exist for place — the only
      addition is the unused `return self`.
- [ ] Remove each deleted name from the imports and the class bases in
      `src/bootstack/_core/mixins/widget.py`.

### Phase 3 — reduce the partial modules

Keep only the methods with no native equivalent; delete the rest.

- [ ] `capabilities/after.py` — **keep `after_repeat`**; delete `after`, `after_cancel`,
      `after_idle`. ⚠ `after` and `after_idle` currently **drop native's `**kw`** — deleting them
      restores it.
- [ ] `capabilities/bindtags.py` — **keep the four helpers** (`bindtags_prepend`, `_append`,
      `_remove`, `_replace`); delete `bindtags`, which only re-implements native's `tagList=None`.
      ⚠ It also **renames the parameter** (`tags` vs `tagList`), so any keyword caller is already
      broken against native — grep before deleting.
- [ ] `capabilities/clipboard.py` — **keep `clipboard_set`** (its one caller is
      `src/bootstack/clipboard.py:35`); delete `clipboard_append`, `clipboard_clear`,
      `clipboard_get`, and `clipboard_get_text` (a pure alias for `clipboard_get`).
- [ ] `capabilities/selection.py` — delete the whole module. Its four pass-throughs are native, and
      `selection_own_set` is **defect 3** above: it has never worked and has no callers.
- [ ] `capabilities/grid.py` — **keep `grid`, `grid_configure`, `grid_forget`, `grid_remove`** (the
      `_on_child_*` interception); delete `grid_rowconfigure`, `grid_columnconfigure`,
      `grid_slaves`, `grid_info`, `grid_size`, and **`grid_propagate` (defect 1)**.
- [ ] `capabilities/pack.py` — **keep `pack`, `pack_configure`, `pack_forget`**; delete
      `pack_info`, `pack_slaves`, and **`pack_propagate` (defect 1)**.

⚠ **The `_on_child_*` hooks are load-bearing and must survive.** They are defined at
`_impl/primitives/packframe.py:177,207` and `_impl/primitives/gridframe.py:400,467,484`. Confirm
with `grep -rn "_on_child_" --include="*.py" src` before and after.

### Phase 4 — the aggregator and the `forget()` collision

- [ ] **Delete `forget()` from `_core/mixins/widget.py`** (**defect 2**). ⚠ **This was written as a
      three-option maintainer call and it is not one** — the method has **zero callers**
      (`grep -rn "\.forget()" --include="*.py" src tests docs` returns only the splitview comment),
      so there is no convenience to preserve and nothing to weigh it against.
- [ ] Then revert the workaround at `widgets/splitview.py:379-381` to the natural
      `self._internal.forget(pane._frame)` and **delete the two-line comment**, which states the
      collision as a standing fact that this deletion falsifies. ⚠ **This is the only file
      affected** — `ttk.PanedWindow` is subclassed once and instantiated once, both in that path.
- [ ] Leave `destroy`, `configure`/`config`, `cget`, `lift`/`tkraise`, `lower` alone for now — they
      are pass-throughs too, but they are on the aggregator rather than in `capabilities/`, and
      `configure` is overridden widely. Out of scope; see follow-ups.

### Phase 5 — consolidate what is left

After phases 1-4, `capabilities/` holds ~13 methods across 5 shrunken mixin modules plus the two
real function modules.

- [ ] **Fold the ~13 survivors directly into `_core/mixins/widget.py`.** It already holds the
      aggregator's own methods, so one file replaces five, and `WidgetCapabilitiesMixin` stops
      being an aggregate of near-empty bases. Delete `after.py`, `bindtags.py`, `clipboard.py`,
      `grid.py`, `pack.py` once emptied.
- [ ] **Reconsider the class name.** `WidgetCapabilitiesMixin` at that point means "the five layout
      hooks plus four bindtags helpers" — `WidgetLayoutMixin` or similar is honest. ⚠ It is
      referenced in **20 files**; a rename is mechanical but wide.
- [ ] **Leave `signals.py` and `localization.py` where they are.** They are imported by
      `widgets/_impl/mixins/localization_mixin.py`, `signal_mixin.py`, `expander.py`,
      `tabitem.py`, `widgets/_core/base.py` and `tests/signals/test_signal.py`. ⚠ **Moving them is
      a separate change** — and note `_core/capabilities/signals.py` is easy to confuse with the
      public `bootstack/signals/` package, so any rename needs care.
- [ ] ⚠ **The package name is then wrong** — `capabilities/` holding only `signals` + `localization`
      describes nothing. Renaming to `_core/support/` (or moving both files up to `_core/`) is the
      honest end state, but it touches 6 importers. **Do it as its own commit, or file it.**

### Phase 6 — the dangling documentation

- [ ] Three class docstrings tell readers the standard widget API "is documented under bootstack
      capabilities": `_runtime/app.py:385`, `_runtime/toplevel.py:21`, `_runtime/base_window.py:8`.
      ⚠ **There is no such documentation.** `grep -rn capabilities docs --include="*.rst"` returns
      nothing outside `docs/_dev/`. Either write the section or delete the three sentences —
      **deleting is the honest option**, since `_core` is private and users cannot reach it.
- [ ] Update `CLAUDE.md`'s source-structure tree if `_core/capabilities` moves or is renamed.
- [ ] Update the `project_capabilities_relevance` memory entry — it says the module "may be
      redundant". This pass settles it; record the measurement, not the suspicion.

---

## Verification

- [ ] `.venv/bin/python -c "import bootstack; print(bootstack.__file__)"`
- [ ] `.venv/bin/python tests/run_gui.py` — compare against the Phase 0 baseline **taken on this
      box**, not against `CLAUDE.md`'s Windows figure.
- [ ] **Assert the defects are actually fixed, with the control:**
      plain-`tkinter` `frame.grid_propagate()` returns `True`; a bootstack `Frame` must now return
      `True` too (it returns `None` today).
- [ ] **Check line endings** — every touched file must stay **CRLF**. `git diff` cannot see a flip.
      `file src/bootstack/_core/mixins/widget.py` must say `CRLF line terminators`.
- [ ] `grep -rn "capabilities\." --include="*.py" src tests` — no import of a deleted module.
- [ ] Run the docs build clean, since three docstrings change:
      `rm -rf docs/_build && sphinx-build -b html docs docs/_build/html -W --keep-going`.

---

## CHANGELOG

**Probably none for the deletions** — `_core` is private, none of it is reachable from public API,
and the standing rule is that an entry earns its place by being reachable. ⚠ **But the three
defects may be reachable**: `grid_propagate()`/`pack_propagate()` resolve on every `_impl` widget,
and `.tk` is a documented public escape hatch. **Check whether a public widget exposes either
before deciding**, and say in the commit message why an entry was omitted if it is.

---

## What this pass did NOT verify

⚠ **State these boundaries rather than letting the plan read as complete.**

- **Nothing was run with the mixins removed.** The classification is by signature and body only. A
  pass-through can still matter if something depends on its MRO position — and `forget()` proves
  this hierarchy already has one collision, so **there may be others not enumerated**.
- **`mypy` was never run.** Nearly every pass-through carries `# type: ignore[misc]`, which suggests
  the type checker was never satisfied by them anyway — but that is an inference, not a measurement.
  **Run it before claiming the annotations cost nothing.**
- **The 8 `self.winsys` cache sites were not traced.** Unrelated to this plan, but they came out of
  the same reading — see the `_windowingsystem` duplication note (2 private twins,
  `_runtime/wheel.py:38` and `widgets/toast.py:25`, plus 18 raw `tk.call` sites) which belongs on
  **#477**, not here.
- **No issue is filed.** File one before the PR, or this lands unmilestoned and untracked.
