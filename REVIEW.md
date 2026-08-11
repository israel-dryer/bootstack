# REVIEW.md — `fix/dialog-keyboard-modality`

## Round 1 — 2026-08-11

**Scope:** `git diff main...HEAD` at **`76173410`** — four fix commits (#426, #439, #440, #441) plus `PLAN.md`. Touched `dialog.py`, `datedialog.py`, `query.py`, `container.py`, tests and CHANGELOG. Working tree clean at review time.

**Reviewer:** a fresh agent via `/code-review`, run before this session had written any code. Per the protocol it did not read `PLAN.md`.

**Fix step:** same session as the verification, at the maintainer's instruction to verify each finding before fixing anything. Pre-fix SHA for round 2 scoping is **`76173410`**.

### The headline: two of five findings did not survive verification

This is the part worth carrying. The review produced five findings; **F1 and F5b were refuted by measurement**, F4 was deferred on reachability grounds, and only F2, F3 and F5a were real. Both refutations came from running the thing rather than reasoning about it, and in F1's case from a **human keypress** that no automated arm could have supplied.

The standing note in `CLAUDE.md` is that agents over-flag. That held here at 2-in-5. But note the reverse also happened inside the same round: the *existing* test suite under-flagged twice, in exactly the areas it appeared to cover (see F2 and F5a).

### Verification the review ran

- **Suite at HEAD before any fix:** shared leg **991 passed / 14 skipped / 75 deselected**, exit 0 (`main` was 962/14 — the branch's 29 new tests all pass).
- **After all fixes:** shared leg **1000 / 14 / 75**, exit 0. The +9 is exactly the nine tests added below.
- **Full suite at the commit being handed over**, `py -3.12 tests/run_gui.py`: **exit 0, all 20 legs passed, summed 1197 passed / 21 skipped**. Reconciles against `PLAN.md`'s baseline exactly — `main`'s 1159 + the branch's 29 + this round's 9 = 1197, with skips unchanged at 21 (shared 14, data 125/4, `test_pagestack.py` 1/3).

⚠ **A first reading of that run reported 22 skipped.** The sum had counted pytest's *collection* line (`collected 1088 items / 75 deselected / 1 skipped / 1013 selected`) as if it were a leg result. `run_gui.py` prints no aggregate, so the sum is hand-rolled and the collection lines have to be excluded — this file has been wrong about counts five times and that is one more way to do it.
- **`git diff main...HEAD -- CLAUDE.md` is empty**, per `PLAN.md`'s pre-merge invariant.
- **Cleared, so it is not re-derived:** `unbind("<Map>", bind_id)` does not wipe sibling `<Map>` bindings (`_patched_unbind` rewrites the script line-wise, and `bind_all` lives on the `all` tag); the `TButton` polarity is right (`not instate(["disabled"])` is True when enabled — not the `!disabled` double-negative trap); the `horizontal=`/`vertical=` value lists match `grid_sticky` and `FlexFrame`; `QueryDialog`'s `_focus_target` hand-off lands on the inner `TEntry` for both the entry and `items=` paths; `MessageBox` and `FormDialog` inherit the grab handling through `Dialog.show()` and no other `grab_set` exists in the package.

---

### F1 — `dialog.py:271` (`_key_was_consumed`) — reported MEDIUM — **REFUTED**

**Claim.** `_key_was_consumed` decides from the widget class, not the key, but `press_default` is bound to `<Return>` **and** `<KP_Enter>`. Tk binds `Text <KP_Enter>` to the literal script `# nothing` (`tk8.6/text.tcl:308`, unconditional), so on keypad Enter the guard reports "consumed" while the Text inserted nothing — leaving the key completely dead in a dialog `TextArea`.

**Why it looked confirmed.** A probe generated `<KP_Enter>` at a focused `Text` and observed no newline. That measurement was **invalid**: on win32 `event_generate("<KP_Enter>")` cannot be synthesized at all — it delivers keysym `'??'`, keycode 0, matching no binding. The empty Text was the dead synthetic event, not `# nothing` running.

**What settled it.** A physical keypress, alternating keypad Enter against the main Enter key as an interleaved control. All four presses were byte-identical:

```
arm B: toplevel binding <Return> FIRED
arm A: keysym='Return' keycode=13 char='\r' -> Text inserted newline: True
```

**Windows FOLDS the keypad key into `Return`.** The `<KP_Enter>` binding at `dialog.py:704` is unreachable on this platform, the Text genuinely consumes the key, and standing down is correct. #441 works as designed.

**What survives, unmeasured.** `text.tcl:308` is not platform-guarded and X11 reports `KP_Enter` as a distinct keysym, so the defect may be real there — turning a Linux keypad Enter from "submits" into "does nothing". Neither box can test it: Windows folds the keysym and the macOS box is Aqua, not X11. Same bucket as #376.

**Resolved as documentation, not code.** No behavior changed. `dialog.py:701` had asserted the keypad key reports `KP_Enter` "on Windows, X11 and Aqua alike", which is measurably false; it now records the folding, the synthesis gap, and that Aqua is unmeasured. `_key_was_consumed`'s docstring gained a `⚠ KNOWN LIMIT, UNMEASURED` block naming the X11 case and the fix if it is ever confirmed (thread the keysym in, scope the text stand-down to `Return`).

**Probe added:** `development/probe_441_kp_enter_platform.py`. Arm 1 is automatic and runs anywhere with a display; arm 2 needs the human keypress and skips under `--auto`, per `PLAN.md`'s rule that a probe must be runnable on every box it informs.

⚠ **The transferable lesson: no automated test on Windows can cover any `<KP_Enter>` path, by two independent mechanisms** — synthesis produces a dead event, and physical presses fold. That applies to the `<KP_Enter>` bindings in `colorchooser.py`, `dropdownbutton.py` and `optionmenu.py` too.

---

### F2 — `container.py:229` — should-fix — **FIXED**

**The new #426 message tells `Grid` users to use `grow=`, which a `Grid` child silently drops.** The message covers "a Row/Column/Grid child" and recommends `grow=`, but `Grid._merge_layout_options` filters child options to `GRID_KEYS`, which has no `grow`.

**Root cause.** The remedy depends on how the container places its children, and the message did not. Flex containers honor `grow=`; grid cells filter it away. Measured:

```
arm1 raised: Grid: expand is not a valid layout option for a Row/Column/Grid child. Use grow= ...
arm2 grow=1  -> placement options: {'sticky': 'ewns'}      <- the kwarg vanished
control (Column) grow=1 -> options: {'grow': 1}            <- honored
```

The `sticky` in arm 2 comes from the container default, not from `grow=`. So following the message's advice produced **no error and no effect** — the same silent no-op #426 exists to remove, one step further along. The old text at least raised a second time.

**Which containers are affected** — measured rather than read: `Row`, `Column`, `Card`, `GroupBox` place with `method=flex` and honor `grow`; `Grid`, plus the page/pane containers (`AppShell page`, `StackPage`, `SplitPane`, `TabPage`), place with `method=grid` and drop it. Five call sites filter to `GRID_KEYS`.

**Resolved.** `_reject_legacy_child_kwargs` gained an `advice` parameter with two module constants — `FLEX_CHILD_ADVICE` (unchanged text) and `GRID_CHILD_ADVICE`, which drops `grow=` and points at `horizontal=`/`vertical=` plus the container's `columns`/`rows` weighting. The five grid-cell callers pass the latter. A new `GRID_CHILD_KEYS` records what a grid cell actually honors.

⚠ **A `kind=` flag with a default was considered and rejected**: a defaulted `kind="local"`-style parameter means any caller who forgets gets the bug, silently — the default *is* the defect. The advice travels explicitly instead. Container-level options are deliberately named **without** a trailing `=` in the message so the per-child regex in the test cannot mistake them for child kwargs; that is commented at the constant.

⚠ **Deviates from `PLAN.md`, which scoped #426 as "Message-only."** The message cannot be correct for both placement kinds without knowing which one it is speaking to, so the parameter is the minimum that makes the text true. No public surface added.

**Why the existing test missed it.** `test_layout_migration_error.py` checked every recommended kwarg against `FLEX_CHILD_KEYS` — and `grow` **is** in that set, so a message aimed at a grid cell passed while `Grid` dropped the kwarg. The invariant was one notch weaker than the property that mattered.

**Tests added (3).** The invariant is now per-container: a grid arm checked against `GRID_CHILD_KEYS`, an explicit "the grid message does not say `grow=`" test, and a **behavioral** test pinning why — `grow=1` on a `Grid` child is not recorded while the same kwarg on a `Column` is, with the `Column` arm as an in-test control so the `Grid` assertion cannot pass for the wrong reason. Control run: the old advice fails the new invariant on exactly `grow`.

---

### F3 — `datedialog.py:82` — nit — **FIXED**

**The duplicated focus block is inert for `ask_date()`, and its comment asserted the opposite.** The comment said the duplication was required "or `ask_date()` would open with nothing focused".

**Root cause.** `DateDialog.__init__` builds footer buttons only when `selection_mode == "range"`, so single-date mode has no default button, and nothing sets `_focus_target` for the raw calendar content. Measured:

```
single  _focus_target=None _default_button=None                  -> _focus_when_mapped runs: False
range   _focus_target=None _default_button=<... Button ...>      -> _focus_when_mapped runs: True
```

Only `ask_date_range()` gains anything. `ask_date()` still opens with focus on the toplevel, exactly as before.

**Resolved.** The comment now states the range-only reach and says the single-date case is unchanged, with a note that giving the calendar a real focus target is a separate change (it would put a focus ring on a day cell and make the arrow keys move the selection).

**CHANGELOG corrected on the same basis.** The #439 entry claimed "the other `ask_*` prompts … now focus their field". Only `query.py` sets `_focus_target`, so the claim is true of exactly `ask_string()`, `ask_integer()`, `ask_float()` and `ask_item()`. It now names those four and states that `ask_date()` is unchanged.

---

### F4 — `dialog.py:484` (and `datedialog.py:126`) — should-fix — **DEFERRED (maintainer)**

**The grab capture is unguarded while the restore is guarded.** `Misc.grab_current()` ends in `_nametowidget`, which raises `KeyError` when the grab holder is not in tkinter's widget map.

**Mechanism CONFIRMED:**

```
grab holder per Tcl: .tclmade
grab_current() RAISED KeyError: 'tclmade'
```

**Why it would matter.** The call sits *after* `_position_dialog` has deiconified and positioned the window, and *before* the `try` block — so the exception escapes `show()` with the dialog visible, holding no grab, and never waited on. Worse than the #440 symptom being fixed, where the dialog at least still blocked its caller.

**Reachability NOT established, and an earlier claim here was overstated.** What was measured is that a `ttk.Combobox` popdown is Tcl-created and outside tkinter's map (`.!combobox.popdown` → `KeyError: 'popdown'`). That is a fact about ttk, not about bootstack. Checking the actual call sites: `SelectBox` builds a Python `Toplevel`, `_NativeContextMenu` uses a tkinter `tk.Menu` (both registered), and while the `Combobox` primitive **is** a `ttk.Combobox` subclass, nothing in `widgets/` instantiates it. The remaining candidates — Tk's menu clones, and user code reaching through `.tk` — are untested; a posted menu blocks the event loop and holds a grab, which hung a probe and had to be killed.

**Deferred by the maintainer** as out of scope, to revisit if it comes up. Recorded here rather than fixed. The suggested change, if revisited, is a `try/except (KeyError, TclError)` inside `capture_grab` degrading to `None` — which F5a's refactor has now made a one-place edit rather than a per-call-site one.

---

### F5a — `dialog.py:210` (`restore_grab`) — should-fix — **FIXED**

**A global grab is restored as a local one.** `restore_grab` called `previous.grab_set()` unconditionally, with no branch on grab kind.

**Reachability is a public API**, unlike F4: `bs.Window(modal="app")` takes a global grab (`_runtime/toplevel.py:228`, the only `grab_set_global` in the tree). A dialog opened from inside such a window silently narrows its modality on the way out.

**The ordering trap, measured** — and the reason the fix is a paired function rather than an extra parameter:

```
outer holds:        grab_status = local
after inner grabs:  outer.grab_status = None   <- the trap
```

The kind must be read **before** the dialog takes the grab; afterwards the previous holder reports `None`. Putting the read inside `capture_grab` makes that unforgettable.

**Resolved.** New `capture_grab(widget)` returns `None` or `(holder, kind)`; `restore_grab(token)` branches on the kind. Both call sites (`dialog.py`, `datedialog.py`) collapse to one line.

⚠ **No `winsys` branch, deliberately.** The fix *removes* a platform assumption rather than adding one: the old code hardcoded "local", which is wrong wherever a global grab exists, while reading `grab_status()` echoes back Tk's own answer and is self-consistent on every window system. The `local`/`global`/`none` strings come from Tcl's shared `tkGrab.c`, not from a platform port. The existing platform branches nearby (`dialog.py:843`, `formdialog.py:345`, Aqua sheets, the context-menu backend) earn their place because a specific API differs; grab kind does not.

⚠ **The one way this is riskier than the status quo, and how it is handled.** `grab set -global` can fail where a local grab cannot — it is the call Tk's viewability rule guards, and on X11 it can also lose to another client. A failed global restore therefore **degrades to local** rather than to nothing: modal within the application is imperfect, but it is not the #440 symptom. Both the fallback and the outer swallow now log through `debug_log_exception`, so a failed restore is observable under `BOOTSTACK_DEBUG` instead of vanishing — it still never raises, which matters on a teardown path.

**Why the existing tests missed it.** Every assertion in `test_dialog_nested_modality.py` was about **who** holds the grab (`grab_current() is top`), never what kind. A downgraded grab passes all of them: the right window holds it, just more weakly. Same shape as F2 — the invariant was one notch weaker than the property.

**Tests added (6).** `test_the_restored_grab_is_the_same_KIND_it_was` closes that gap on the public path. The global-grab cases use a `_StubHolder` recording which call `restore_grab` made.

⚠ **The stub is deliberate and breaks "test PUBLIC paths".** A real global grab confines mouse and keyboard at the window-system level, so a test failing between take and release locks the machine running the suite out of every other application. The logic being pinned is entirely ours — that the captured kind selects the matching restore call. What a global grab then *means* is Tk's and differs by window system; asserting on that would be testing the toolkit. Under `xvfb` in CI (#380) a true end-to-end arm becomes available; the reason for the omission is written into the test file rather than left silent.

**Controls, run both ways.** Against the pre-fix implementation the global test fails with `['local']` vs `['global']` while the local control still passes, so the failure is behavioral rather than a broken harness. ⚠ **`test_a_failed_global_restore_degrades_to_local_rather_than_to_nothing` passes against the OLD code too** — both land on `['local']`, for different reasons — so it guards the fallback (removing it yields `[]`) but does **not** pin the transition. That is recorded in its own docstring rather than left to be discovered.

**CHANGELOG.** Extended the existing #440 bullet rather than adding a second entry for the same issue.

---

### F5b — `dialog.py:210` — reported LOW — **REFUTED**

**Claim.** Tk requires a viewable window for `grab set`, so an outer dialog iconified while the inner modal is up makes `grab_set()` raise *"grab failed: window not viewable"*, which the bare `except … pass` eats — silently reproducing #440.

**Measured on Windows, and it does not hold for either grab kind:**

```
withdraw      viewable=False mapped=False  -> grab_set OK, status = local
iconify       viewable=False mapped=False  -> grab_set OK, status = local
never-mapped  viewable=False               -> grab_set OK, status = local
grab_set_global on withdrawn: SUCCEEDED status = global
```

No viewability enforcement here at all, so the scenario cannot arise on this platform. X11 is unverified as usual.

**Not fixed as reported — but it became live as a consequence of F5a.** Restoring a *global* grab is the case Tk's viewability check actually guards, so the fix introduced the failure mode the finding described. That is why F5a ships the local fallback and the `debug_log_exception` rather than treating them as optional polish.

---

## Round 1 fix summary

| finding | severity | outcome |
|---|---|---|
| F1 — `KP_Enter` dead in a dialog `TextArea` | medium | **refuted** — Windows folds the keysym; documented, X11 left as a known limit |
| F2 — `Grid` child told to use `grow=` | should-fix | **fixed** + 3 tests |
| F3 — inert focus block in `datedialog` | nit | **fixed** (comment + CHANGELOG) |
| F4 — unguarded `grab_current()` | should-fix | **deferred** by the maintainer; mechanism confirmed, reachability not |
| F5a — global grab restored as local | should-fix | **fixed** + 6 tests |
| F5b — swallowed "not viewable" failure | low | **refuted**; its mechanism folded into F5a's fallback |

**Files touched by the fix step:** `container.py`, `grid.py`, `appshell.py`, `pagestack.py`, `splitview.py`, `tabs.py`, `dialog.py`, `datedialog.py`, `CHANGELOG.md`, `test_layout_migration_error.py`, `test_dialog_nested_modality.py`, and a new `development/probe_441_kp_enter_platform.py`.

**Still open from `PLAN.md`, unchanged by this round:** `CLAUDE.md` still quotes the wrong #426 message as a good error under Layout. It must be fixed as its own commit on `main`, never on this branch — `git diff main...HEAD -- CLAUDE.md` is currently empty and must stay that way before merging.

**Suggested strengthening of a `PLAN.md` invariant, for whoever picks this up:** the plan states "after any dialog closes, `grab_current()` is whatever it was before". F5a shows identity is not sufficient — the invariant should read *the same holder **and the same kind***, which is exactly what the old tests could not distinguish.

---

## Round 2 — 2026-08-11

**Scope:** `git diff 76173410` — the five commits round 1's fix step produced, ending at **`d4f2d127`**. Working tree clean at review time; the shared leg re-measured at **1000 passed / 14 skipped / 75 deselected**, matching round 1's recorded figure.

**Reviewer:** a fresh agent via `/code-review`, run before this session had written any code. It read round 1's record so it would not re-file F1–F5.

**Fix step:** same session as the verification, at the maintainer's instruction to prove each finding before fixing it. Every finding below was verified — none was refuted this round, which is worth noting after round 1's 2-in-5.

### The headline: round 1's own fix left the defect in four containers

**F2 shipped a parameter with a default, and four of the nine call sites did not pass it.** Round 1's record explicitly rejected a defaulted flag — *"a defaulted `kind="local"`-style parameter means any caller who forgets gets the bug, silently — the default IS the defect"* — and then shipped exactly that, one keyword over. Four callers forgot within the same commit.

The enumeration is what went wrong, not the reasoning. F2 measured which containers honor `grow=` and recorded *"`Row`, `Column`, `Card`, `GroupBox` place with `method=flex`"*. True — in `Card` and `GroupBox`'s **default** mode. Both are dual-mode: under `layout="grid"` they take a separate branch that grids the child and filters to `GRID_KEYS`. `Expander` and `AccordionSection` are the same shape. So the measurement classified four containers by the mode they happened to be constructed in, and "five call sites filter to `GRID_KEYS`" undercounted by four.

⚠ **The transferable rule: enumerate the CALL SITES of the thing you changed, not the classes you can think of.** `grep -n '_reject_legacy_child_kwargs' src/` returns nine lines and takes one second; it was never run. Same shape as the standing "enumerate the producers, don't reason about the consumer" note in `CLAUDE.md`.

### Verification

Pre-fix, at `d4f2d127`, via `development/probe_426_grid_cell_advice.py` — **2 of 5 arms passed**:

```
[PASS] CONTROL Grid(columns=2)                    kind='grid cell'  advises grow=? False
[PASS] CONTROL Card() default column              kind='flex child' advises grow=? True   grow honored? True
[FAIL] Card(layout='grid')      kind='flex child' advises grow=? True  placement=grid options={'sticky': 'ewns'}
[FAIL] GroupBox(layout='grid')  kind='flex child' advises grow=? True  placement=grid options={'sticky': 'ewns'}
[FAIL] Accordion.add(layout='grid')  ...same
```

Post-fix: **5 of 5**. The two control arms pin both ends — a real `Grid` (already correct before this round) and a `Card` in its default column mode, where `grow=` genuinely is the remedy, so a fix that hard-wired everything to the grid advice would fail the control rather than pass silently.

`Expander` has no arm: it is not in the public namespace (`'Expander' in dir(bs)` is `False`), so its call site is reachable only internally. Fixed for consistency, unmeasured by choice.

---

### G1 — `container.py:255`, four missed call sites — medium — **FIXED**

`_reject_legacy_child_kwargs(layout_kw, where, *, advice=FLEX_CHILD_ADVICE)`, with `card.py:147`, `groupbox.py:139`, `expander.py:169` and `expander.py:287` passing no advice. All four sit inside an unambiguous grid branch — two of them under a comment reading *"Only reached for grid layout"* — and filter to `GRID_KEYS` on the next line. A user in `bs.Card(layout="grid")` was told to write `grow=` and then had it dropped.

**Resolved by making the kind required**, which is what round 1's own reasoning called for: `_reject_legacy_child_kwargs(layout_kw, where, kind)` where `kind` is `'flex child'` or `'grid cell'`, positional and mandatory. A caller who forgets now gets a `TypeError` at the call, not a wrong message at the user. The advice is looked up in `_CHILD_ADVICE`, so an unknown kind raises `KeyError` rather than quietly selecting the other engine's remedy.

The kind names the child's **placement**, not its parent class — deliberately, because that is the distinction the round-1 enumeration lost.

### G2 — `container.py:270`, advice matched by identity — low — **FIXED**

`kind = "grid cell" if advice is GRID_CHILD_ADVICE else "flex child"` derived the user-visible noun with `is` on a module constant. Any equal-but-distinct string — a formatted variant, a reloaded module under `bootstack.dev`, a future per-container advice — would have been labelled "flex child" while filtering to `GRID_KEYS`. Dissolved by G1: the kind is now the input and the advice the lookup, so the two cannot disagree.

### G3 — `GRID_CHILD_ADVICE` named a class the user never constructed — low — **FIXED**

The text ended *"weighting the row or column on the container (the Grid's columns/rows argument)"*, but it is emitted for `TabPage`, `StackPage`, `SplitPane` and `AppShell page` too — measured:

```
TabPage: fill is not a valid layout option for a grid cell. ... (the Grid's columns/rows argument)
```

A user who hit it from `tabs.add("tab", layout="grid")` was pointed at an argument on a class not in their code; the real argument is `columns=`/`rows=` on `add()`. Now reads *"(its columns/rows arguments)"*. Still written without a trailing `=`, per round 1's note that container-level options must not look like per-child remedies to the test's regex.

### G4 — `docs/tasks/layout.rst:254` contradicted the new message — low — **FIXED**

Every message ends *"see the layout guide"*, and the guide told *"a Row/Column/Grid child"* to use *"`grow` / `horizontal` / `vertical`"*. A grid-cell user got a message that deliberately withheld `grow=`, followed the link, and was told to use `grow` — landing back on the silent no-op the message had just steered them off. The bullet now splits by placement kind.

### G5 — `CHANGELOG.md:21` re-asserted the advice the fix removed — low — **FIXED**

The #426 bullet said the message *"now names `grow=` for claiming leftover space"* for a child of *"a `Row`, `Column` or `Grid`"*. False for `Grid` and for the page/pane containers after round 1. Rewritten to state both forms and why they differ.

---

## Round 2 fix summary

| finding | severity | outcome |
|---|---|---|
| G1 — four grid call sites still emitting the flex advice | medium | **fixed** — kind is required now, + 7 tests |
| G2 — advice matched by `is` identity | low | **fixed** — dissolved by G1 |
| G3 — grid advice named "the Grid's" to non-Grid containers | low | **fixed** |
| G4 — layout guide contradicted the new message | low | **fixed** |
| G5 — CHANGELOG re-asserted the removed advice | low | **fixed** |

**Tests added (7).** Round 1's tests drove the helper directly, so they said nothing about whether a real container asks it for the right remedy — which is precisely how four containers kept the defect. The new arms go through the public constructors: a parametrization over `Card`/`GroupBox`/`AccordionSection`/`Grid` in grid mode asserting the message says "grid cell", never says `grow=`, and recommends only `GRID_CHILD_KEYS`; a two-arm control over `Card`/`GroupBox` in **column** mode asserting the opposite, so the advice must follow the `layout=` rather than the class; and a structural test that the kind is required — `TypeError` when omitted, `KeyError` on a mistyped one. That last one is the invariant rather than the symptom, per the standing rule: it fails every time, where a behavioral test only fails for whichever container someone forgot.

**Verification at the handover commit.** Shared leg **1007 passed / 14 skipped / 75 deselected**, exit 0 — 1000 plus exactly the 7 tests above, and below the 1021-selected ceiling. Full `py -3.12 tests/run_gui.py`: **exit 0, all 20 legs passed, summed 1204 passed / 21 skipped**, which is round 1's 1197 plus the same 7, skips unchanged. Clean `-W` docs build succeeded. The sum excludes pytest's collection lines, which is the arithmetic round 1 got wrong on its first reading.

**Files touched:** `container.py`, `base.py`, `card.py`, `groupbox.py`, `expander.py`, `grid.py`, `appshell.py`, `pagestack.py`, `splitview.py`, `tabs.py`, `CHANGELOG.md`, `docs/tasks/layout.rst`, `test_layout_migration_error.py`, and a new `development/probe_426_grid_cell_advice.py`.

**Filed rather than fixed — out of this branch's scope.** `base.py:515`: `attach()`'s grid branch filters re-attach kwargs to `GRID_KEYS` with **no** rejection at all, so `widget.attach(fill="x")` on a grid child is silently dropped, while the flex branch one line above rejects it. Same class as #426 on a different path, pre-existing, introduced by neither round. Worth an issue on the `0.3.x` patch line.

**Unchanged from round 1 and still open:** `CLAUDE.md` quotes the wrong #426 message as a good error under Layout. It needs its own commit on `main`, never on this branch — and it now needs to describe **two** messages, not one corrected one. `git diff main...HEAD -- CLAUDE.md` must stay empty before merging.
