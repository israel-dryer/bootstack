# REVIEW — `fix/datatable-context-menus-456`

**Round cap:** 2 (patch line, declared in `PLAN.md` before any findings existed).

---

## Round 1 — 2026-08-19

Reviewed `git diff main...HEAD` at `b88d03ac` — three commits (wire `context_menus` through the wrapper, then decouple `on_row_right_click` from it), plus `PLAN.md`, `CHANGELOG.md`, one probe and three test files.

Gate 1 was satisfied: `git diff main...HEAD -- src/` is non-empty (two files), so a round was warranted.

**Six findings — two medium, four low. Five acted on, one settled as a deliberate decision.** A seventh was found during the fix step rather than by the reviewer, and is recorded as F7 under the `0.3.2` precedent.

### What the round CONFIRMED as correct — do not re-derive

The production change is sound, and this was checked rather than assumed:

- `_context_iid = iid` being set when the row menu is off is harmless — `_context_iids()` is only reachable from row-menu commands.
- `_ensure_row_menu`'s own guard still prevents the `None.show()` path.
- `_build_tree` runs once and `bind_right_click` has no `add=`, so the now-unconditional bind cannot accumulate handlers.
- The default `'all'` path is byte-identical to `main` — the whole compatibility argument for the patch line.
- **The `#418`/`#420` invariant survived the gate move.** `_on_row_context`'s `if not iid or iid not in self._row_map` guard still sits *above* the emit, so group headers and empty space do not fire `<<RowRightClick>>` with an empty record. Read first, then measured live under F6's resolution.

---

### F1 — `CHANGELOG.md:15` — **medium** — FIXED

The release note claimed a misspelled `context_menus` value "previously turned both menus off silently". False for the public API.

**Measured.** `git show main:src/bootstack/widgets/datatable.py` contains zero occurrences of `context_menus` — it was not a parameter at all. A misspelled value fell into `**kwargs`, survived `_split_layout_kwargs` (it is not a layout key), and was discarded, so the internal kept its own `'all'` default and **both menus stayed ON**.

⚠ **The mechanism is worth stating precisely, because the first pass got it loose too.** The option *is* read — by `_impl/composites/tableview/tableview.py`, at `:288`/`:411`/`:1247`/`:1250`. What never happened is the wrapper *delivering* it: `internal_kwargs` is a closed dict built from named parameters only, and leftovers are never merged. So "not read at all" is wrong; "never reaches the widget" — the branch's own commit `933f55fe` — is right. Same mechanism as #383's third gap.

The same sentence also read "`on_row_right_click` fires whichever menus you turn off", missing "no matter".

**Resolution.** Rewritten to "A misspelled value is now reported instead of being ignored, so a typo reads as a typo rather than as an option that quietly does nothing", and "fires no matter which menus you turn off". Nothing else in the bullet changed.

⚠ **This is published text.** `0.3.1` and `0.3.2` each had their CHANGELOG reworded *after* the tag, forcing a `gh release edit` on the published body. Catching it before promotion is the cheap version of that.

---

### F2 — `src/bootstack/widgets/datatable.py:149` — **medium** — DECISION, NOT CHANGED

The new `validate_choice` turns previously-constructible calls into a construction-time `InvalidChoiceError` on a patch release.

**Measured.** `bs.DataTable(rows=[...], context_menus=None)` and `context_menus="None"` construct fine on `0.3.2` — silently, with both menus on — and raise here.

**`PLAN.md`'s justification was false.** It read *"Nothing can break: the argument is unreachable from public code today, so there is no caller to grandfather."* The argument was always **passable and accepted**; what was unreachable was its **effect**. That distinction is the whole finding.

✅ **DECIDED: keep the strict check, no CHANGELOG entry** (maintainer, 2026-08-19 — *"if None is not a valid argument and not specified as an option, then we should not care about it"*). Neither `None` nor `'None'` is in the documented `Literal`, so there is no supported behavior to preserve, and the rule covers every out-of-set value uniformly rather than special-casing `None`.

⚠ **Recorded because the reasoning, not the outcome, is what a later round needs.** The counter-argument raised and rejected was the SemVer precedent: #381 shipped in `0.2.0` as a **minor** explicitly because it raises where it used to accept, and #383/#369 are batched into `0.4.0` on the same grounds. The distinction that settles it — #381 tightened kwargs that were *documented and worked*; this tightens values that were never valid and never had effect.

**Resolution.** Source unchanged. `PLAN.md`'s invariant 3 rewritten so it states the true premise and the accepted consequence. **Do not re-file this.**

---

### F3 — `PLAN.md:133` — **low/medium** — FIXED

The `## Tests` table still asserted `'none'` → right-click bound: **no**, and the line under it called that row "the strongest observable and the closest to what the reporter sees". The decoupling decision ~30 lines above reverses exactly that, and the test enforcing it was removed.

**Cause.** `63d4cb2d` recorded the decision by **appending** (34 insertions, 1 deletion) without sweeping what it contradicted.

**Resolution.** Last column re-headed `on_row_right_click`, reading `fires` for all four values, with a note that the original column was reversed by the decision above. The `'none'` row is still called the strongest observable, for the now-correct reason: it is the one case where a table offers no menu at all yet must still report the gesture.

⚠ **`REVIEW-PROTOCOL.md` requires `PLAN.md` be handed to the reviewer.** A plan contradicting its own shipped decision is precisely how `0.3.1` round 3 spent a round re-litigating settled calls.

---

### F4 — `PLAN.md:195` — **low** — FIXED

The verification record claimed `main 53 → branch 61 = +8`, itemized as "4 parametrized gates + default + **unbound-handler** + 1 `BAD` + 1 `GOOD`". The unbound-handler test was removed by the decoupling commit.

**Re-measured today:** `pytest tests/widgets/public/test_datatable.py tests/widgets/public/test_choice_guards.py --collect-only -q` → **60**, i.e. **+7**. The removed test's intent moved into `test_datatable_right_click_event.py` (8 tests), so the real total across all three files is **+15**.

⚠ **`main`'s baseline of 53 is carried from `PLAN.md` and was NOT re-measured in this round.** Only the branch-side figures above were.

**Resolution.** Corrected to `+7 = 60` with the itemization fixed and the `+15` total stated. Given `CLAUDE.md` has been wrong about counts seven times, a stale delta in the branch's own verification record is exactly the input that produces the eighth.

---

### F5 — `src/bootstack/widgets/datatable.py:147` — **low** — FIXED

The comment justifying strict validation cited "the `!= 'none'` bind guard" — deleted by this same branch's third commit. `tableview.py:1159` binds unconditionally now.

The conclusion still held (`'nones'` fails **both** `_header_context_enabled()` and `_row_context_enabled()`, so every menu vanishes with no error); only the mechanism named was gone.

**Resolution.** Comment rewritten to cite the two predicates directly, with a "do not simplify this to match the internal's tolerance" line so the strictness decision in F2 is not quietly undone later.

---

### F6 — `tests/widgets/public/test_datatable.py:814` — **low** — NOTE, then CLOSED BY MEASUREMENT

Header-menu gating is pinned only by reading `_header_context_enabled()`, while the new `test_datatable_right_click_event.py` docstring argues that asserting on a gate "would restate the implementation instead of pinning the behavior". The row half got an end-to-end `<Button-3>` drive; the header half — newly reachable for `'rows'`/`'none'` — got none.

⚠ **Under gate 2 this is a NOTE, not a fix.** Test code is actionable only for **vacuity** or **false alarm**, and this is neither: the predicate read *is* the seam the click path consults (`_on_tree_context` is literally `if not self._header_context_enabled(): return`), so the uncovered glue is one line.

**Resolution — closed with evidence rather than filed as a survivor.** `PLAN.md` already flagged that nobody had watched a menu appear or fail to appear; nothing in the repo, automated or manual, had ever opened one. `probe_456_context_menus.py` reads gates only. So the gap was closed the way `#419`/`#427`/`#429`/`#453` closed theirs — a manual demo:

**`development/demo_456_context_menus.py`** — four tables, one per value, each captioned from a single `EXPECTED` map so the window cannot drift from the contract it checks; the `'all'` table is grouped so the group-header case has something to click.

**The instrument was proven before it was trusted**, driven headlessly:

```
data row right-click    -> events: 1
group header            -> unchanged
empty space below rows  -> unchanged
group_by("team")        -> {'Core': 'I004', 'Tools': 'I007'}
```

✅ **Run by the maintainer, 2026-08-19 — the menus behave.** That is the only evidence on the branch that a menu visually appears or fails to appear, and it gives the header half its first end-to-end check.

---

### F7 — `PLAN.md:207` — found during the fix step, not by the reviewer

The *reporter's script* verification block recorded:

```
right-click bound: False
```

**Measured at branch head: `True`.** `<Button-3>` is present on the tree for `context_menus='none'` — which is the entire point of the decoupling. The block was measured **before** the decoupling commit and never re-run, so the branch's own verification record displayed the behavior the branch had just reversed.

⚠ **This is worse than F3, and it is the one to carry forward.** A stale *table* reads as a plan that was not swept; a stale *measurement block* reads as proof. **Re-run a recorded measurement after any commit that changes what it measures.**

**Resolution.** Re-measured and corrected, with the correction labelled inline.

---

### Two defects in the working tree, neither a review finding

- ⚠ **A stray `u` byte was prepended before `datatable.py`'s BOM** (`75 ef bb bf`), left by a manual edit. The whole package was unimportable — `SyntaxError: invalid non-printable character U+FEFF`, every affected test file erroring at collection. Stripped; the header now matches `main`'s exactly. Committing it would have shipped an unimportable build.
- ⚠ **Line endings.** `.gitattributes` declares `eol: crlf`, and both `PLAN.md` and `probe_456_context_menus.py` were LF in the working tree — the probe already committed that way. Normalized in binary mode; `git diff` stayed content-only. This is the same trap `PLAN.md`'s own process note records for `test_datatable.py`, so it has now bitten this branch three times. `git diff` cannot see it; `file` and the stderr warning can.

---

### Verification

**Tests — measured 2026-08-19 after every change above:**

```
tests/widgets/public/test_datatable.py
tests/widgets/public/test_choice_guards.py
tests/widgets/public/test_datatable_right_click_event.py
-> 68 passed, 1 warning
```

`68 = 60 + 8`, which reconciles against F4's collection figure.

⚠ **The full suite was NOT re-run after this round's edits, and this is stated rather than implied.** The changes are one source *comment*, `CHANGELOG.md`, `PLAN.md` and one new file under `development/` — no production behavior moved, and the 68 above cover every test file the branch touches. `PLAN.md`'s recorded full run stands: exit 1, 33 legs, the single failure being **#449**, an already-filed flake at ~1 in 10 whose file the branch's one-file `src/` diff cannot reach.

**Not done, deliberately:**

- No CHANGELOG entry for F2's raise, per the decision recorded there.
- No test added for F6, per gate 2 — closed by the demo instead.

**Round 1 changed ZERO lines under `src/` except a comment.** Under gate 1 that does not trigger a round 2, so **the branch closes here at one round against a cap of two.**