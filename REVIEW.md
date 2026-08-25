# REVIEW — round 1 of 3 · `fix/unknown-kwarg-strictness-383` (#472, #383 gap 3)

## ★ PICK UP HERE

**Round 1 is CLOSED. There were NO BLOCKING findings.** The three should-fixes were held for the maintainer, who took all three; **F1, F2 and F3 are FIXED at `1d674f41`, and that fix diff touches no `src/`** — see *Fix step* at the bottom. F4 and F5 are nits with no action proposed and are still open. **Nothing has been pushed.**

**The branch is `02b9ee3d` (the implementer) + `1d674f41` (round 1's fix) + this record.** ⚠ **A row cannot name its own SHA** — `git log --oneline origin/main..HEAD` settles it rather than trusting any SHA written here.

⚠⚠ **F1's SEVERITY WAS OVERSTATED IN THE ORIGINAL RECORD AND THE SENTENCE IS CORRECTED BELOW.** I wrote that deleting `Chart._forwards_kwargs` *"would not fail CI"*. **It would** — via `test_declared_forwarders_are_exactly_the_five`, which never constructs a widget and is therefore untouched by the missing dependency. I checked the vacuous test in isolation and did not check whether a sibling covered the same regression. **The vacuity was real and the fix stands; the consequence I drew from it did not.**

**Reviewed:** `git diff origin/main...HEAD -- src/` at base **`339177f5`** (confirmed with `git merge-base origin/main HEAD`, not read from PLAN.md), branch tip `02b9ee3d`, 74 insertions across 11 files. Gate 1 opens the round: the production diff is non-empty. **Round cap 3, SPENT 1.**

**The production change is correct and is the strongest-evidenced part of the branch.** The guard is in the right place, the four crafted `textsignal` messages are the complete set and all four survive, the one production fold-in outside the stated scope is load-bearing and pinned by an existing test, and the before/after is a real measurement with a working control. Every finding below is fallout the branch created *around* the fix — a test that cannot fail on CI, two repo scripts nobody ran, and one over-claiming sentence in the CHANGELOG.

**⚠ The single most useful thing to carry forward: the guard's blast radius was measured over `src/` and `tests/` and never over `docs/`.** Both of F2's sites were silent no-ops that the guard correctly turned into hard failures — which is the fix working — but nothing in the suite or the docs build executes them, so they would have reached `main` broken.

---

## Verification performed by this review — commands, not conclusions

Recorded so a later round does not repeat it, and so each claim below has a stated boundary.

| what | how | result |
|---|---|---|
| Base SHA | `git merge-base origin/main HEAD` | **`339177f5`**, matching PLAN.md. `origin/main` has since moved to `6b080ac8` (a `docs(claude):` commit); the merge-base is unchanged |
| Probe, on the branch | `py -3.12 development/probe_383_unknown_kwarg_policy.py` | **`dropped=0 rejected=50 other=0`** — matches PLAN's target |
| **Probe CAPABILITY** (gate 4's exception) | worktree at `339177f5`, `PYTHONPATH=$W/src`, provenance printed, probe copied in, `--arm control` | **`dropped=40 rejected=10 other=0`**, *"OK -- both outcomes are observable"*. The 40 named are PLAN's 40 exactly. **So the post-fix zero is a measurement, not a blind probe** |
| Full suite | `py -3.12 tests/run_gui.py`, Windows box, `matplotlib` and `pandas` both confirmed present | **1552 passed / 22 skipped, 33 legs, exit 0** |
| Is `+28` accounted for? | `main` = 1524; the new file collects 25 (12+1+1+1+5+1+4), `test_base_layer.py` adds 3 | **28, exact.** `git diff --stat` over `tests/` bounds it |
| Is the `form.py` fold-in load-bearing? | worktree at `HEAD` with **only** `form.py` reverted to base, `PYTHONPATH` + absolute test paths, provenance printed | `test_select_items_alias_wins_over_values` **FAILS** with `TypeError: Select() got unexpected keyword argument(s): values`; the other 28 in that file pass. **The branch cannot ship without it, and an existing test pins it** |
| Are the four `textsignal` guards the complete set? | `grep -n "in kwargs" src/bootstack/widgets/*.py` | Exactly four in constructor scope — `datefield:104`, `numberfield:127`, `select:125`, `timefield:94`. **All four re-ordered. No fifth was missed** |
| Is the `@staticmethod` → instance conversion source-compatible? | `grep -rn "_split_layout_kwargs(" src/ tests/ tools/ development/ \| grep -v "self\._split"` | **No non-`self` call site anywhere.** `development/flexlayout_proto.py:45` already spells it `self.` |
| Does anything still silently accept? | constructed every top-level class carrying a `**kwargs` catch-all outside the probe's 50 — `App`, `AppShell`, `Workbench`, `Window`, `ThemeToggle` | **Nothing accepts silently.** See F3 for the message shapes |
| Does `_forwards_kwargs` leak into the docs? | `docs/conf.py:87` `autodoc_default_options`; `grep -rl` over `docs/_build/html` | No `private-members`, no occurrence in the built HTML. The `#:` prefix on its comment is inert here. **Not a finding** |
| Hygiene | `git diff origin/main...HEAD -- CLAUDE.md`; `file` on every changed file | Diff **empty**; every changed file **CRLF** |

**⚠ Boundary of my over-rejection sweep, stated because a completeness claim whose scope was never written down reads as global.** I AST-scanned every `docs/**/*.py` for `bs.<Widget>(kw=...)` whose `kw` is neither a named parameter nor a layout key, skipping `App`/`Window`/`AppShell`/`Workbench` (they never call the split) and the five forwarders — **2 hits, both real, both in F2.** I then ran the same scan over python code-blocks extracted from `docs/**/*.rst` and `README.md`: **797 blocks parsed, 0 hits, and 47 blocks unparseable and therefore UNSCANNED.** The `.py` arm finding two is the only reason the `.rst` zero means anything. **Not scanned at all: `development/`, `tools/`.**

---

## Findings

### F1 — `test_declared_forwarders_still_forward[Chart]` is vacuous wherever matplotlib is absent · **note, fixed** · gate 2: vacuity

`tests/widgets/public/test_unknown_kwarg_strictness.py:66`

**Root cause.** The assertion is only *reachable* when the widget can construct. `bs.Chart(bogus=1)` raises `BootstackError: Chart requires matplotlib, which is not installed…` **before `__init__` reaches the split**, and that message does not contain `"got unexpected keyword argument"` — so the test passes for a reason unrelated to forwarding. `.github/workflows/ci.yml:56` installs `-e .` and `pytest` only, so on every CI leg this row is green without testing anything. The defect is a **missing optional-dependency gate**, not a wrong assertion.

**Measured.** Blocked `matplotlib` with a `meta_path` finder, asserted the block worked as a control, then constructed: `Chart: BootstackError | Chart requires matplotlib…` → `test would PASS`.

⚠ **CORRECTION to this finding's original severity.** It first said *"deleting `Chart._forwards_kwargs` would not fail CI"*. **That was wrong.** Measured afterwards by deleting the attribute in-process (a pytest plugin, no file edit) and running both ways:

| regression injected | matplotlib present | matplotlib blocked (= CI) |
|---|---|---|
| `del Chart._forwards_kwargs` | `still_forward[Chart]` **and** `are_exactly_the_five` fail | **`are_exactly_the_five` fails** — caught |
| seam stops honoring the flag (all flags still declared) | — | **`still_forward[MenuButton/Picture/StatusBar/Toolbar]` fail** — caught |

**Every regression I could construct is caught on CI by a sibling test**, because the enumeration test never constructs and the other four forwarders carry no optional dependency. **So the vacuity was real but had no unguarded regression behind it.** The error was reviewing the one test in isolation instead of asking what else covers the same defect — worth remembering, because a vacuous test inside a suite that covers the behavior elsewhere is a very different finding from a coverage hole.

**Fix applied anyway, and it still earns its place:** a skip is honest where a vacuous pass is not, and a green `Chart` row that proves nothing is exactly the thing a later session reads as coverage.

### F2 — two repo scripts now raise `TypeError`, and nothing executes them · **should-fix** · production fallout

- `docs/examples/chart_data_source.py:47` — `bs.DataTable(enable_search=False, …)`. **`enable_search` is the INTERNAL key**; the wrapper's parameter is `searchable`, and `datatable.py:162` is where one is mapped to the other. The example's own comment says search is disabled *"on purpose"* — **it never was.**
- `docs/screenshots/home-hero.py:164` — `bs.DataTable(paginated=False, …)`, two lines below a correct `searchable=False`. There is no `paginated` parameter; the nearest real one is `paging_mode` (`'standard'` / `'virtual'`).

**Root cause.** Both were silent no-ops that the guard correctly promotes to hard failures — this is the fix doing exactly its job. But the suite does not run `docs/examples/`, Sphinx `literalinclude` does not execute what it includes, and CI runs neither, so the branch turned two working-looking scripts into crashing ones with nothing to report it. `home-hero.py` is the generator for the site's promo hero image, so the breakage surfaces at the next regeneration, not now.

**Minimal change.** `enable_search=False` → `searchable=False`; `paginated=False` → either `paging_mode="virtual"` or delete it. **⚠ Neither is a mechanical rename — `paginated=False` never had a meaning, so what it *should* say is a judgment call about the hero, and the maintainer art-directs that image.** Also worth knowing: `chart_data_source.py` is **not** `literalinclude`d by any `.rst` (73 example files, 74 include directives, this one is not among them), so it does not reach the docs site; `home-hero.py` does, via the image it produces.

### F3 — the CHANGELOG's central claim is checkable and is not true as written · **should-fix**

`CHANGELOG.md`, the new `### Changed` bullet: *"Every widget now raises `TypeError` naming itself and the keyword it did not recognize."*

**Measured on the branch:**

| | what actually happens |
|---|---|
| `bs.App(bogus=1)` · `bs.AppShell(…)` · `bs.Workbench(…)` | `TypeError: Tk.__init__() got an unexpected keyword argument 'bogus_xyz_383'` — a `TypeError`, but it names **`Tk.__init__`**, not the widget |
| `bs.Window(bogus=1)` | `TclError: unknown option "-bogus_xyz_383"` — **not a `TypeError`** |
| the five forwarders | `TclError` from the internal, by design |

**Root cause.** The sentence generalizes from the 45 wrappers the seam covers to "every widget". The bullet already carves the forwarders out of the *forwarding* behavior one sentence later, but not out of the *message shape*, and it says nothing about the top-level windows, which are the four classes a reader is most likely to try first.

**What is true and worth keeping:** nothing silently accepts any more — the headline promise ("reported instead of ignored") holds universally. It is only the second sentence that over-claims.

**Minimal change.** Narrow it to the widgets the seam covers and say the windows and the five forwarders report through the toolkit instead. **⚠ Precedent: the #456 bullet had to be corrected for this same class of error — a sentence written from the fix's point of view and read as authoritative — and this project has reworded two CHANGELOGs *after* tagging.** Cheap now, expensive after `0.4.0` ships.

### F4 — the duplicated guards are now dead code · **nit**

`src/bootstack/widgets/boolean_controls.py:47-52` and `src/bootstack/widgets/radio_variants.py:49-53`

The six-line guard PLAN.md cites as the shipped prior art still sits immediately after each `self._split_layout_kwargs(kwargs)` call, where the seam has already raised. Harmless, and leaving it is defensible under minimal-diff — but a reader will mistake it for the live guard, and if a boolean control ever declared `_forwards_kwargs = True` the two would flatly contradict each other. Deleting it, or replacing it with a one-line comment pointing at the seam, is a judgment call, not a defect.

### F5 — in place mode the crafted legacy-migration message is bypassed · **nit**

`src/bootstack/widgets/_core/base.py:135-138`

**Measured** (`bs.Label` inside a `bs.Row`):

```
{'side': 'left'}             -> BootstackError: Row: side is not a valid layout option for a flex child. Use grow= ...
{'side': 'left', 'x': 5}     -> TypeError: Label() got unexpected keyword argument(s): side
{'anchor': 'center', 'x': 5} -> accepted (Label declares `anchor`, so it never reaches **kwargs)
```

A `PLACE_TRIGGER_KEY` flips `layout_keys` to the place set, so `side` is no longer popped into `layout_kw`, never reaches `_reject_legacy_child_kwargs`, and gets the generic message instead of the migration advice. **PLAN.md §3 checked this for the non-place path and is correct there** — this is the path it did not enumerate. Place mode is undocumented (`docs/tasks/layout.rst` never mentions `x=`/`relx=`) and mixing pack keys with place keys is a user error either way, so **note, not fix.** `test_legacy_child_kwargs_keep_their_own_message` covers only the non-place path, which is the right scope for it.

---

## Notes — record only, no fix (gate 2: not vacuity, not false alarm)

- **The `_seam()` helper is sound.** `object.__new__(cls)` skips `__init__`, and `_split_layout_kwargs` reads only `type(self).__name__` and the class flag, so the tests exercise the real code path with no Tk dependency. Not a shortcut.
- **`test_declared_forwarders_are_exactly_the_five` enumerates `dir(bs)` only.** A widget that sets the flag without being exported at top level would not be caught. Every public widget is exported today, so this is a boundary, not a hole — but it is the same shape as `test_public_surface.py`'s known blind spot, and #466 should not inherit it.
- **`test_unknown_keyword_is_rejected_and_named` would also pass if a wrapper lost its `**kwargs` entirely** — Python's own `TypeError` names both the class and the key. That outcome is still correct behavior, so this is not actionable.
- **`test_legacy_child_kwargs_keep_their_own_message` uses `pytest.raises(Exception)`** and would pass if the `with bs.Row():` block failed for an unrelated reason. Narrow mechanism, low risk; noted so a later round does not re-derive it.
- **Population arithmetic, three places, all cosmetic.** The probe's docstring says *"The 52 public wrappers"* and lists **50** — the two absent are `App` and `Window`, which never call the split, exactly as PLAN.md says. The commit message repeats *"all 52 wrappers"* and separately says *"all 50 call sites"* where the source comment at `base.py:145` says **51**. Numbers in prose, not behavior.
- **⚠ `development/probe_wrapper_parameter_delta.py` and `development/wrapper-parameter-audit-463.md` now describe behavior that no longer exists.** Mode 3's *"40 of 52 wrappers drop an unknown keyword"* is historical from this commit onward, and the `--arm leftovers` arm will report DISAGREEs under a banner calling a disagreement a probe defect — which is precisely why the implementer swapped instruments, and that call was right. **#466 is designed against those five modes and should be read with this in mind.** No action on this branch.
- **The four `textsignal` re-orderings sit below `self._parent = self._resolve_parent(parent)`**, so a widget built outside any container still reports the container error first. Unchanged from before the branch and correct.
- **The five forwarders all genuinely forward** — `internal_kwargs.update(kwargs)` at `chart.py:163`, `picture.py:101`, `statusbar.py:79`, `toolbar.py:95`, and the merge loop at `menubutton.py:167-168`. The exemption preserves the status quo rather than inventing one. **⚠ But PLAN.md §4's question is still open and untouched: whether those five deserve a real error instead of an exemption.** Related and also out of scope: `App`/`AppShell`/`Workbench` leaking `Tk.__init__()` and `Window` leaking `TclError` is **#383's other gap** (args that raise but leak a raw toolkit error), which stays on `0.5.0`.
- **Three things the implementation says it did not verify remain unverified here**, deliberately — they are scope calls, not defects: whether the five forwarders *need* the opt-out, where `_forwards_kwargs` should live, and anything about #383's gaps 1 and 2.
- **On merge:** `PLAN.md` was moved from `development/plan-383-unknown-kwarg-strictness.md` to the repo root when the branch was cut, so both it and this file need re-archiving under `development/` and a fresh `PLAN.md` created, per the working agreement.

---

## Fix step — applied 2026-08-25, at the maintainer's instruction

**Severity was re-ranked before any edit, as the protocol requires.** There were no blockers; the maintainer asked for F1–F3, so those three were taken and F4/F5 were left alone. **`git diff HEAD -- src/` is EMPTY** — the fix is one test guard, two repo scripts and one CHANGELOG sentence.

| # | file | change | verified by |
|---|---|---|---|
| F1 | `tests/widgets/public/test_unknown_kwarg_strictness.py` | new `OPTIONAL_DEP = {"Chart": "matplotlib"}` and a `pytest.importorskip` in `test_declared_forwarders_still_forward`. **The map is deliberately separate from `FORWARDERS`** — that constant is the expected set for `test_declared_forwarders_are_exactly_the_five`, so removing `Chart` from it would have weakened the enumeration guard | matplotlib blocked: **24 passed, 1 skipped** (`SKIPPED … could not import 'matplotlib'`) where it previously passed vacuously. matplotlib present: **25 passed**. Both regression controls above still fail as they should |
| F2 | `docs/examples/chart_data_source.py:47` | `enable_search=False` → `searchable=False` — `enable_search` is the internal key, mapped from `searchable` at `datatable.py:162` | AST re-scan of `docs/**/*.py`: the two real hits are gone, and the 119 remaining are all `bs.App(minsize=…)`, confirmed noise (`App` never calls the split, and `bs.App(minsize=(400,300))` constructs fine) |
| F2 | `docs/screenshots/home-hero.py:164` | **deleted** `paginated=False`, with a comment naming the real switch | Both fixed spellings constructed directly. ⚠ **Deletion, not `paging_mode="virtual"`, and the reason is not laziness:** the keyword was always inert, so the published hero was rendered with the default `paging_mode="standard"`. **Removing it keeps that rendering byte-identical; switching to `"virtual"` would change a published image**, which is an art-direction call and not a reviewer's to make. The comment records the real switch so nobody re-adds the dead one |
| F3 | `CHANGELOG.md` | *"Every widget now raises `TypeError` naming itself…"* → *"Every widget you place in a layout…"*, plus a new sentence: nothing accepts an unknown keyword in silence, but `App`, `AppShell`, `Workbench` and `Window` report it through the toolkit, so their message names that rather than the window | Re-read the whole bullet as its audience reads it, not just the edited clause. The existing forwarder sentence already covers the other five |

**Full suite after the fix, Windows box, `py -3.12 tests/run_gui.py`, matplotlib and pandas both present: 1552 passed / 22 skipped, 33 legs, exit 0** — unchanged, as a production-free diff should be.

**No regression test was added, deliberately.** F1 *is* a test change; F2 and F3 touch a docs example, a screenshot generator and a CHANGELOG line, none of which a test can assert against. The nearest durable guard is **#466**, and the F2 sweep suggests a shape for it that the issue does not currently carry: **an AST check that every `bs.<Widget>(kw=…)` in `docs/**/*.py` names a real parameter or a layout key.** It would have caught both sites before the branch existed. Worth adding to #466 rather than building here.

---

## Round 1 resolutions

| # | severity | status |
|---|---|---|
| F1 | ~~should-fix~~ → **note** (see the correction) | ✅ **FIXED** — dependency gate added; the regression it guards was already covered on CI by two sibling tests |
| F2 | should-fix | ✅ **FIXED** — both sites; the hero keeps its exact published rendering |
| F3 | should-fix | ✅ **FIXED** — sentence narrowed and the windows carved out |
| F4 | nit | **OPEN** — dead duplicate guards left in place; judgment call, no action proposed |
| F5 | nit | **NOTE ONLY** — place-mode legacy message, no action proposed |

**⏭ GATE 1 OPENS NO ROUND 2.** `git diff HEAD -- src/` is empty: the fix step changed no production code, so it is self-checked by the session that wrote it and goes no further. **The cap is 3 and 1 is spent; rounds 2 and 3 are unspent and unneeded on present evidence.** The branch is ready for the maintainer.

**On merge:** archive `PLAN.md` and this file into `development/` and create `PLAN.md` fresh — finding a stale one describing shipped work is worse than finding none.
