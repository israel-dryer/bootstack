# Review brief — #453, round 2

**For a FRESH session.** A session that has written code never reviews code, so
whoever wrote `937b0aa2` must not be the one to read it.

---

## Scope — the FIX diff only

```
git diff 545e98f4..872aa862
```

Two commits:

| SHA | Kind | In scope? |
|---|---|---|
| `937b0aa2` | `src/` + tests — the round-1 fixes | **YES, this is the round** |
| `872aa862` | `REVIEW.md` only | record, not reviewed code |

**Round 1 already reviewed the whole branch.** Do not re-review `b65ca66d`
(the original #453 fix), the probes, the demo, or `PLAN.md`. Re-reviewing
settled code is what produced `0.3.1`'s round 3, where three of four findings
were items already triaged.

The round opens legitimately under `REVIEW-PROTOCOL.md` gate 1: `937b0aa2` has
a non-empty `git diff -- src/`.

---

## This is the LAST round

`PLAN.md` declares a **round cap of 2** (patch line, gate 3). Anything that
survives this round is **filed as an issue, not fixed here**.

---

## Read first, so nothing is re-filed

- **`REVIEW.md` at the repo root** — round 1's three findings, their root
  causes, and what the fix step actually changed. This is the triage state.
  Round 2 of `0.3.1` was handed its predecessor's record and re-filed nothing;
  round 3 was not, and re-filed three settled items. That is a harness failure,
  not a reviewer failure.
- **`PLAN.md`** for the contract and the precedence rule. Read it for
  requirements, not for the implementer's argument that the approach was sound
  — rationale is what produces "yes, that seems right" instead of scrutiny.

---

## Settled — do not re-litigate

1. **Dropdown-button membership is decided ONCE, at construction.** This is a
   **maintainer decision** (2026-08-13), not an implementation convenience:
   building a button and later un-building it makes no sense, and a runtime
   insert adds a button the caller explicitly refused. Do not propose a removal
   arm, and do not propose restoring the insert arm.
   - **The consequence is KNOWN AND ACCEPTED**, and is in `REVIEW.md`: a box
     built `readonly=True, allow_custom_values=True, show_dropdown_button=False`
     has no button, and clearing `readonly` later leaves it typeable with no
     entrance to the list. There is no keyboard entrance either — the
     `<Down>`/`<Up>`/`<Return>` bindings are created inside the popup-open
     routine and torn down on close. **This is `main`'s behavior today**, so the
     change restores it rather than regressing it. Re-raising it is only useful
     if the *evidence* changed, not the *judgment*.
2. **F1 was fixed in `timefield.py`, not `selectbox.py`, deliberately.** Mapping
   an incoming ttk `state="readonly"` onto `self._readonly` was considered and
   rejected: a plain select is already untypeable while its list still opens, so
   that mapping would suppress the popup for every select that asked only for
   "no typing". `_delegate_readonly`'s docstring draws that distinction.
3. **F3 is LATENT, not live.** `SelectBox` resolves `TTKWrapperBase.configure`,
   which returns the bare value — measured, `configure("readonly")` → `True`.
   The `cget` change is hardening against an MRO shift. Do not report it as a
   bug that was shipping.

---

## Measured — do not re-derive

- **Full suite at `872aa862`:** `py -3.12 tests/run_gui.py`, **exit 0, 20 legs,
  1225 passed / 21 skipped**. Shared leg **1028 / 14**, collection line
  `collected 1116 / 75 deselected / 1 skipped / 1041 selected`, and
  `1028 + 13 = 1041`.
- **`main` is 1208 / 21**, shared leg **1011 / 14** against **1024**. ⚠ The
  `1250 / 22` and `1055 / 13 / 1068` that `CLAUDE.md` carried were **wrong** and
  were corrected on `main` at `7ff25930`. If a stale copy is in context, prefer
  the corrected table.
- **Control, run the required way:** `src/` reverted, the 5 new tests run against
  the unfixed source. **4 of 5 fail behaviorally** — `assert False is True` on
  the TimeField getter, `assert True is False` on the popup gate, and
  `assert 'dropdown' not in {'dropdown': <Button ...>}` on the runtime flip. The
  fifth pins an end state rather than a transition, passes pre-fix, and says so
  in place.
- **`pandas` is ABSENT on this box**, so the data leg reads `125 / 4`. That is
  the documented environmental pair, not a discrepancy.

---

## Gate 2 — how to review the test half

`937b0aa2` is roughly a third production, two thirds tests. Test code is
reviewed on **ONE axis: what defect can it let through.** Only two things are
actionable:

- **vacuity** — it passes while the behavior is broken;
- **false alarm** — it fails while the behavior is fine.

Diagnostics, wording, symmetry and ergonomics are **notes in the record, never
fixes**. Under this gate `0.3.1`'s round 4 yields 2 findings instead of 5.

The specific vacuity question worth asking here: `test_select_read_only.py` now
has 17 tests across two concerns (`Select` and `TimeField`) sharing helpers
written for the first. Does any `TimeField` assertion read a path the helpers
were not built for?

---

## Environment

- **`py -3.12` for tests and docs.** pytest is installed ONLY on 3.12. `py -3.13`
  fails every leg with *"No module named pytest"* while still printing a
  plausible harness summary.
- **Never pipe a build or test command to `tail`** — you capture `tail`'s exit 0.
  In PowerShell, `| Select-String` leaves `$LASTEXITCODE` from the pipeline.
  Redirect to a file, capture the code on the next statement, then grep it.
- **A worktree runs against `main`'s source unless `PYTHONPATH` is set** — and
  setting `PYTHONPATH` while passing the PRIMARY checkout's test paths runs the
  new tests against the old source, which reads as a real result. Pass the
  worktree's absolute test paths too, and print
  `os.path.dirname(bootstack.__file__)` before trusting a number.
- Probe output must be **ASCII** — this box's console is cp1252.
