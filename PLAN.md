# PLAN — #453: `Select.read_only` is declared but never implemented

**Issue:** [#453](https://github.com/israel-dryer/bootstack/issues/453) — *Read-only `Select` not read-only*, reported by `@bLynnb2762` against `0.3.1` on Windows
**Branch:** `fix/select-read-only-453` (off `main`)
**Milestone:** `0.3.x — Patch line` *(maintainer, 2026-08-13 — no public surface added; the change makes documented behavior true)*
**Round cap:** **2** (patch line, per `REVIEW-PROTOCOL.md` gate 3)

---

## The report

> You are able to change a read-only `Select` widget by clicking in the text area vs. the drop-down arrow. […] The drop-down arrow seems to be inactive.

```python
import bootstack as bs

with bs.App() as app:
    sel = bs.Select(["A", "B", "C"], value="A", label="Read only", read_only=True)
    sel.on_change(lambda e: bs.toast(e))
app.run()
```

**Reproduced, both symptoms, one cause:**

```
read_only=True   arrow_dimmed=True   popup_opens=True
plain            arrow_dimmed=False  popup_opens=True
```

`read_only=True` sends `state="readonly"` into `Field._delegate_state`, whose only effect here is calling `_sync_addon_state()` (field.py:532) — which dims the arrow. Nothing guards the popup, and the entry-click binding installed at selectbox.py:161 stays live. **The greyed-out arrow the reporter noticed is the entire observable effect of the option**, and it is an accident rather than an implementation.

That is the visible tip of a larger conflation.

## Root cause

`read_only` exists **only on the public wrapper**. It appears nowhere in `selectbox.py` or `field.py` — verified with `grep -rn "read_only" src/bootstack/widgets/_impl/composites/selectbox.py src/bootstack/widgets/_impl/composites/field.py`, which returns nothing.

| | |
|---|---|
| `select.py:102` | `read_only: bool = False` — constructor kwarg |
| `select.py:62-63` | docstring: *"value is visible but the popup cannot be opened"* |
| `select.py:134-135` | `elif read_only: internal_kwargs["state"] = "readonly"` — the entire implementation |
| `select.py:283-290` | live property; getter and setter both read/write the ttk entry state |

So the public layer invents a feature, translates it into a toolkit state string, and hands it to a layer that has never heard of it. `SelectBox` already owns that same ttk state as the implementation of "no free typing" (the inverse of `allow_custom_values`/`enable_search`) and recomputes it unconditionally at line 156, discarding whatever the public layer asked for.

`_show_selection_options` (selectbox.py:352) guards only on `disabled`. Nothing anywhere guards the popup on read-only, because nothing downstream knows the concept exists.

## Pre-fix control table — MEASURED, keep for the reviewer

Measured on this branch at the plumbing commit (`_read_only` stored, nothing consuming it yet), `py -3.13`, probe `development/probe_select_read_only.py`:

| construction | `_readonly` | typeable | popup opens | `.read_only` |
|---|---|---|---|---|
| `Select()` | False | False | True | **True** ← false positive |
| `Select(read_only=True)` | True | False | **True** ← the report | True |
| `Select(read_only=True, allow_custom_values=True)` | True | **True** | True | **False** |
| `Select(read_only=True, searchable=True)` | True | **True** | True | **False** |
| `Select(disabled=True)` — CONTROL | — | False | **False** | — |

The `disabled` row is the control: it proves the probe can detect a blocked popup, so the `True`s above are real rather than a broken harness.

Runtime, on a `Select(allow_custom_values=True)`:

| step | typeable | popup | `.read_only` |
|---|---|---|---|
| initial | True | True | False |
| `.read_only = True` | False | **True** | True |
| `.read_only = False` | True | True | False |

So construction lets `allow_custom_values` win outright, while runtime lets `read_only` win over typing but not over the popup. Neither is a decision anyone made — both fall out of the ttk state being the only storage, written last by whoever ran last.

## Addon dimming — a second, latent defect found while scoping

`Field._sync_addon_state` (field.py:663-681) dims every addon when the entry is `readonly`, on the reasonable assumption that addons mutate the value. `SelectBox` uses `readonly` to mean "not typeable", where the dropdown is the *primary* interaction. Measured:

```
default Select         : entry_readonly=True   dropdown_addon=enabled
_readonly_active       : set()                 <- dropdown not registered read-only-safe
after <<StateChanged>> : dropdown_addon=disabled
after configure(state=): dropdown_addon=disabled
button click opens popup = True                <- still works while disabled
```

1. The dropdown survives on a default `Select` only **by accident** — line 161's direct `entry.state(['readonly'])` does not fire `<<StateChanged>>`, so the sync never runs at construction.
2. The first thing that does fire it dims the dropdown **permanently** on an ordinary `Select`.
3. Even dimmed, the button still opens the popup — `_show_selection_options` checks the entry's disabled state, not the button's.

## The contract

**Inputs** (stored): `_read_only`, `_allow_custom_values`, `_search_enabled`, disabled (ttk), `show_dropdown_button` (construction-only).

**Derived outputs** — nothing else may write these:

```
typeable      = not disabled and not read_only and (allow_custom_values or enable_search)
popup_opens   = not disabled and not read_only
dropdown_lit  = not disabled and not read_only
click_to_open = not typeable        # a typeable entry must place a cursor instead
```

**Precedence ladder**, extending the one already implicit at select.py:132-135:

```
disabled  >  read_only  >  allow_custom_values | enable_search
```

`read_only` **suppresses** `allow_custom_values`; it does not overwrite it. Clearing `read_only` must restore the field to *typeable*, not to plain. Today the runtime path only restores correctly by luck, because `allow_custom_values=True` happens to make `state="normal"` the right answer; the same code on a plain `Select` gets it wrong.

## Runtime writers — every one must route through the applier

| writer | where |
|---|---|
| `configure(allow_custom_values=)` | selectbox.py:955 |
| `configure(enable_search=)` | selectbox.py:968 |
| `configure(state=)` | field.py:514 — writes disabled/readonly/normal directly |
| `Field.enable()` / `.disable()` / `.readonly()` | field.py:489/495/501 — bypass the delegate entirely |
| `Select.disabled` setter | select.py:299 → `configure(state=...)` |
| `Select.read_only` setter | select.py:290 → to become `configure(read_only=)` |

**Covering them all at once:** override `_sync_addon_state()` in `SelectBox` to call `super()` and then apply the read-only rule. It is already bound to `<<StateChanged>>` (field.py:235) and called from all five internal sites, so every existing path picks up the new behavior with no new writers to track.

## Three things are construction-only and must not stay that way

- **Click-to-open** is bound once, in the `else` branch, via `after_idle` (selectbox.py:161). Flip `allow_custom_values` True→False at runtime and the entry becomes non-typeable with no binding — no entrance at all. **Bind unconditionally at construction and gate inside the handler.** Do *not* bind/unbind on transitions: that is the tkinter funcid-recycling trap that cost a critical defect in #392.
- **Button existence** is decided at selectbox.py:145 and never revisited, while both of its inputs are runtime-mutable. The delegates must insert the addon if it is missing and now needed (`insert_addon` works after construction).
- **`state`** — `Select.disabled = False` writes `state="normal"`, clearing `readonly` wholesale. It must re-derive instead of writing raw.

## Incomplete reachability guard — folded in deliberately

selectbox.py:145 reads `allow_custom_values or show_dropdown_button`; line 156 reads `allow_custom_values or enable_search`. The two conditions have drifted, and `enable_search` makes the entry typeable exactly as `allow_custom_values` does. Measured:

```
custom=F search=F btn=T   button=True   typeable=False  click_opens=True
custom=F search=F btn=F   button=False  typeable=False  click_opens=True
custom=T          btn=F   button=True   typeable=True   click_opens=False   <- 145 forces it
custom=F search=T btn=F   button=False  typeable=True   click_opens=False   <- no entrance
```

Latent only: public `Select` never passes `show_dropdown_button`, and neither internal caller does. **Folded into this branch rather than filed** because Step 1 rewrites those exact lines and the fix is hoisting the shared predicate — the same duplication that caused the primary bug. Called out here so the reviewer reads it as deliberate.

## Post-fix result — MEASURED, same probe as the control table above

| construction | typeable | popup opens | arrow dimmed | `.read_only` |
|---|---|---|---|---|
| `Select()` | False | True | False | **False** |
| `Select(read_only=True)` | False | **False** | **True** | True |
| `Select(read_only=True, allow_custom_values=True)` | **False** | **False** | **True** | **True** |
| `Select(read_only=True, searchable=True)` | **False** | **False** | **True** | **True** |
| `Select(disabled=True)` — CONTROL | False | False | True | False |

Runtime transitions, all four correct:

| scenario | result |
|---|---|
| custom-values select, `read_only` on then off | restores **typing**, not plain |
| plain select, `read_only` on then off | stays plain — does **not** grant typing |
| read-only select, `disabled` on then off | `read_only` survives |
| plain select, `allow_custom_values` on then off | click entrance returns |

Reachability, with `show_dropdown_button=False`: the `enable_search` row now gets a button like the `allow_custom_values` row already did.

## Verification result

- **Full suite: `py -3.12 tests/run_gui.py` → exit 0, all 20 legs.** Summed **1220 passed / 21 skipped**. Shared leg **1023 / 14**, up exactly **+12** from **1011 / 14** before this branch's tests — the 12 tests added here and nothing else.
- **Clean docs build `-W --keep-going` → exit 0.**
- ⚠ **The 1220/21 does NOT match this file's recorded baseline of 1250 / 22 at `288d2596`**, and neither does the shared leg (measured ceiling here is **1024** selected / 1099 collected / 75 deselected, and `1011 + 13 runtime skips = 1024` reconciles exactly; the table claims 1055 / 13 against a 1068 ceiling). This branch adds tests and touches none, so it cannot have shrunk collection. **Prefer the measured figure and reconcile the table separately — this would be the seventh wrong count.** The data leg reading **125 / 4** rather than **123 / 6** also indicates `pandas` is absent from 3.12 on this box today, which `CLAUDE.md` records as the environmental tell.

## Steps

0. ~~Branch, back up the working tree, write this plan.~~ **Done.**
1. ~~**Plumbing.** `readonly` param on `SelectBox`, default `False`, stored as `_readonly`, documented in the main `Args:` block. Public `Select` forwards `read_only` into it.~~ **Done.**
2. ~~**Derive the entry state.** Single `_apply_interaction_state()`; hoist the shared `typeable` predicate; fold in the reachability guard.~~ **Done.**
3. ~~**Route every writer** through it — both typing-mode delegates, an overridden `state` delegate, and a new `@configure_delegate('readonly')`.~~ **Done.**
4. ~~**Guard the popup** in `_show_selection_options`, and at both entrances.~~ **Done.**
5. ~~**Dropdown button.** Addon registered `active_when_readonly=True` so the ttk state stops dimming it; dimmed from an overridden `_sync_addon_state` on the real flag instead.~~ **Done** — fixes the two latent defects above as a side effect.
6. ~~**Click-to-open** bound unconditionally, gated in the handler.~~ **Done.**
7. ~~**Public wrapper.** Getter reads the setting via `configure("readonly")`. Setter → `configure(readonly=)`. The dead `elif read_only: state="readonly"` at construction is removed.~~ **Done** — the `disabled` setter needed no change once the `state` delegate re-derives.
8. ~~**Tests** — `tests/widgets/public/test_select_read_only.py`, 12 tests.~~ **Done.**
9. ~~**CHANGELOG** under `## [Unreleased]`.~~ **Done** — re-created, one `### Fixed` bullet, unwrapped.

## Control result — 12 tests, run against the unfixed source

**9 fail pre-fix, 3 pass, and each of the 3 is explained in the test itself.** Run by swapping the source files rather than `git stash` (this repo carries old stashes).

| passes pre-fix | why it is kept |
|---|---|
| `test_a_plain_select_still_opens_from_both_entrances` | the control — must pass on both sides, or the failures above it are harness noise |
| `test_the_arrow_is_dimmed_when_read_only` | dimming was the ONE thing `read_only` already did, as an accident; now pinned as intended |
| `test_clearing_read_only_restores_typing_when_custom_values_were_asked_for` | worked by luck pre-fix (`state="normal"` happened to be right); the mirror test is what caught it being wrong |

⚠ **The first control run was WRONG and looked right.** Three tests failed pre-fix with `AttributeError` because the helper called `_on_entry_click` by name — a method that only exists post-fix — which proves nothing. Rewritten to generate a real `<Button-1>`, so it drives whichever binding the widget installed.

⚠ **And that exposed a vacuity defect in the test for the reported bug itself.** `test_read_only_blocks_the_popup_from_an_entry_click` **passed** against the unfixed source: pre-fix the click binding is installed from `after_idle`, so a click generated before idle ran hit no binding, the popup stayed shut, and the test went green while the defect was fully present. It would never have caught #453. Fixed by settling idle work before the click. **A control that does not reach the path under test is indistinguishable from a fix that works.**

## Tests — each needs a pre-fix control

Run against unfixed source, each must fail for the **behavioral** reason, not an `AttributeError`:

- `read_only=True` blocks the popup from the button **and** from an entry click.
- `read_only=True, allow_custom_values=True` blocks both change paths.
- Clearing `read_only` on a custom-values `Select` restores **typeability**, not plain.
- A plain `Select` reports `.read_only is False`. *(Would pass vacuously today — needs the flag-backed getter to mean anything.)*
- The dropdown addon is **lit** on a plain `Select` after `<<StateChanged>>`, and **dim** under `read_only`.
- `sel.disabled = True` then `False` leaves `read_only` intact.
- Runtime `configure(allow_custom_values=)` in both directions keeps exactly one entrance to the popup.

## Verification

`py -3.12 tests/run_gui.py`, full suite, sum the legs by hand (no aggregate is printed). Redirect to a file and read `$LASTEXITCODE` on the next statement — never pipe to `tail`/`Select-String`. Baseline on `main` at `d6c90534`: **exit 0, 20 legs, 1250 passed / 22 skipped**.

Clean docs build: `rm -rf docs/_build && sphinx-build -b html docs docs/_build/html -W --keep-going`.

⚠ A green run is not evidence here — the behavior under test is currently *unguarded*, so several of these pass vacuously without the flag-backed getter. The pre-fix control is what carries the proof.

## Decisions taken (maintainer, 2026-08-13)

1. **Dim the dropdown arrow under `read_only`.** #453 argues for it on its own: the reporter read the dimmed arrow as *meaning* read-only, so dimming is the signal users already expect. It also preserves the invariant line 145 exists to maintain — a lit, inert entrance would be the only place in `SelectBox` that breaks it.
2. **Naming — `read_only` is the public spelling, `readonly` the internal one.** The impl layer already speaks ttk's spelling (`Field.readonly()`, the `'readonly'` state string) and `select.py` translates, as it already does for every other option. Verified there is no collision between the `configure` key `'readonly'` and `Field.readonly()`: `configure_delegate` stores keys on the function and builds a separate key→handler map (`configure_mixin.py:21-27`). The mixin also reads getters from `self._<key>`, so key `readonly` → `self._readonly`, which is what is already written. **No rename needed.**
3. **Patch line.** No public surface is added — `read_only` already exists on `Select`. Both observable changes correct behavior *toward* what is documented: `read_only=True` starts doing what select.py:62-63 always promised, and the getter starts returning a true answer instead of a false positive. Neither breaks expected behavior; each removes a defect. Same reasoning that put #430 on `0.2.x` and the four dialog fixes on `0.3.1`.

## Out of scope — file, do not fix here

- **`Field.readonly()` (field.py:501) never clears the readonly state.** All three branches set `['readonly']`; the `False` branch also disables the field. Pre-existing, reachable from internal callers only.
- **Public field widgets silently swallow unknown kwargs.** `bs.TextField(exportselection=False)` is indistinguishable from `bs.TextField(bogus_xyz=1)` — both construct, both do nothing — while the internal `Field` raises `TclError`. The public layer is the less strict of the two. Same class as `show_grid=True` on `Row`; belongs with **#383**.
- **`FieldOptions` (field.py:41-91) carries raw Tk vocabulary** — `exportselection`, `textvariable: Variable` with a link to the tkinter docs, `xscrollcommand`, `takefocus`, `show`, `cursor`, `foreground`. Internal only and never reaches the docs site (`grep -rn "FieldOptions\|composites.field\|SelectBox" docs/ --include=*.rst` → zero), but it is the declared kwarg contract of seven composites and it violates the standing no-tkinter-in-docstrings rule.
