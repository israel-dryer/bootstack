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

---

## Round 3 — 2026-08-11

**Scope:** `git diff main...HEAD` at **`346d7f39`**. Working tree clean at review time.

**Reviewer:** a fresh agent via `/code-review`. ⚠ **It was NOT given `REVIEW.md`**, unlike round 2's reviewer, which is the whole story of this round.

### The headline: 3 of 4 findings were already-triaged items re-filed

**This round found one new thing.** The other three were re-reports:

| finding | status before this round |
|---|---|
| `_key_was_consumed` / `KP_Enter` | round 1 **F1** — refuted for Windows by a physical keypress, documented as a known limit with the remedy written into the docstring |
| `capture_grab` / unguarded `grab_current()` | round 1 **F4** — mechanism confirmed, reachability not established, **deferred by the maintainer** |
| `attach()`'s grid branch filters silently | round 2's own record — **filed there** as out of scope, "worth an issue on the `0.3.x` patch line" |

⚠ **The transferable rule: the review invocation has to carry the triage state forward, or every round re-litigates decisions that were already taken.** Round 2's reviewer was handed round 1's record and re-filed nothing; round 3's was not and re-filed three. This is a harness problem, not a reviewer problem — the cost is a round of maintainer attention spent re-reading its own deferrals.

⚠ **A re-report is not automatically noise, though, and F1 is the counter-example.** What changed since round 1 is not the evidence but the *price*: round 1 deferred it as an unmeasurable X11 case, and the reviewer pointed out the remedy is one argument. Weighed against shipping a branch that changes X11 behavior on a platform neither box can test, one argument is cheap. It is fixed below. F4's price did not change, so F4 stays deferred.

### H1 — `_runtime/toplevel.py:225`, a modal `bs.Window` never restores the grab — **FILED AS #444, NOT FIXED HERE**

**Real, reproduced independently**, and the only genuinely new finding this round:

```
outer holds grab:       True status= local
inner holds grab:       True
after inner closed:     None
outer still holds grab: False
```

**Out of this branch's scope on two counts, which is why it was filed rather than fixed.** #440 was scoped by the maintainer to `Dialog`, `MessageBox`, `QueryDialog`, `DateDialog`; and `toplevel.py` is **not in this branch's diff**, so the defect is pre-existing in `0.2.3` and `0.3.0` alike rather than a regression from the #440 work.

⚠ **The reviewer's sharpest claim — that the CHANGELOG says this is fixed — is WRONG, and was checked rather than accepted.** The #440 bullet scopes itself to "any dialog button command that shows an alert, a confirmation, or a second dialog," and its `modal="app"` sentence is about restoring a window's grab *kind* (F5a's fix), not about `bs.Window` restoring anyone else's. Nothing false ships. Agents over-flag; this is the shape it takes on a finding that is otherwise sound.

⚠ **But round 1's enumeration WAS one directory too tight**, and that is the third instance of this failure mode on this branch. Round 1 recorded *"no other `grab_set` exists in the package"* — where *the package* meant `dialogs/`. `grep -rn "grab_set" src/bootstack/` returns `_runtime/toplevel.py:228,230` as the only other real call site. Same shape as round 2's G1 (*"enumerate the CALL SITES, not the classes you can think of"*) and as `CLAUDE.md`'s standing "enumerate the producers" note. **The recurring error is not the enumeration — it is drawing the boundary silently.** Round 1 wrote a completeness claim whose scope word did the load-bearing work and was never stated as a limit.

### H2 — `base.py`, `attach()`'s grid branch — **FILED AS #445, NOT FIXED HERE**

Round 2 had already filed this in its own record. Reproduced before filing:

```
Column child  -> RAISED: Label: fill is not a valid layout option for a flex child
Grid child    -> ACCEPTED, placement options = {'sticky': 'ewns'}
```

Pre-existing, introduced by neither round, and a one-liner now that `kind` is required.

### H3 — `_key_was_consumed` asks about the widget, not the key — **FIXED**

Round 1's F1, reopened on cost rather than on new evidence. The rule now takes the **keysym**, required and positional — no default, per round 2's G1 lesson that a defaulted parameter *is* the defect.

**Measured against the live binding table before changing anything** — the asymmetry is real and it is one-sided:

```
TButton  <Key-Return> -> button_default_binding   <Key-KP_Enter> -> button_default_binding
Text     <Key-Return> -> tk::TextInsert           <Key-KP_Enter> -> '# nothing'
TEntry   <Key-Return> -> '# nothing'              <Key-KP_Enter> -> '# nothing'
```

A button answers both keys (bootstack binds both at `_runtime/app.py:150-153`); a text widget answers only `Return`. So the text branch stands down only for `Return`, and the button branch is unchanged.

⚠ **The polarity is `keysym != "KP_Enter"`, not `keysym == "Return"`, deliberately.** An unrecognized keysym then reads as CONSUMED. For a text widget that is the conservative answer: standing down wrongly costs a dead key, firing wrongly costs **#441 itself** — the dialog closing on top of a newline the user just typed. Pinned by its own test so it is not "simplified" into the equality form later.

**Windows behavior is unchanged**, because the platform folds the keypad key into `Return` and `keysym` is never `KP_Enter` there. **X11 is the case this exists for**, and it is the reason the fix is worth its argument: before it, this branch would have turned an X11 keypad Enter in a dialog `TextArea` from "submits the dialog" (the #441 bug) into "does nothing at all" (a dead key). Neither is right; only one of them is new.

**Tests added (4).** A precondition test pinning the two Tk binding scripts, so a Tk change reports itself by name rather than as an unexplained behavioral failure; a button arm proving the symmetry; the text arm that is the fix, carrying an in-test `Return` control so it cannot pass by the widget going unread; and the unknown-keysym arm pinning the conservative polarity.

⚠ **NOT REACHABLE END TO END ON WINDOWS, by either route** — synthesis yields keysym `??`/keycode 0 matching no binding, and the physical key folds. The tests drive the rule directly and say so; an end-to-end arm would pass vacuously here. `development/probe_441_kp_enter_platform.py` was updated to record that its job has changed from "decide whether to fix" to "be the arm someone runs on X11".

**Control, run both ways.** With the guard disabled, **exactly one test fails** — `assert True is False` on the text/`KP_Enter` arm — while the button arm, the precondition and the unknown-keysym arm all still pass. Behavioral failure, not a broken harness.

### Round 3 summary

| finding | severity | outcome |
|---|---|---|
| H1 — modal `bs.Window` never restores the grab | medium | **filed as #444** — real, reproduced, pre-existing and out of #440's scope |
| H2 — `attach()` drops legacy kwargs on a grid cell | low | **filed as #445** — already filed in round 2's record |
| H3 — `_key_was_consumed` ignores the keysym | low | **fixed** + 4 tests |
| H4 — unguarded `grab_current()` (round 1 F4) | low | **still deferred** — nothing changed |

**Verification at the handover commit.** Shared leg **1011 passed / 14 skipped / 75 deselected**, exit 0. Full `py -3.12 tests/run_gui.py`: **exit 0, all 20 legs passed, summed 1208 passed / 21 skipped** — round 2's 1204 plus exactly the 4 tests above, skips unchanged. Clean `-W` docs build succeeded (`CHANGELOG.md` is `include`d by `docs/release-notes.rst`, so a CHANGELOG edit can break the build).

⚠ **The selected-count ceiling reconciles, but not by the obvious sum.** Measured: `1024/1099 tests collected (75 deselected)`. The leg reports **1011 passed + 14 skipped = 1025**, which is one OVER the ceiling and looks impossible. It is not: **one of those skips happens at COLLECTION time** (`collected 1099 items / 75 deselected / 1 skipped / 1024 selected`) and is therefore not one of the 1024 items. `1011 + 13 runtime skips = 1024` exactly. Round 2's recorded "1021-selected ceiling" does not reconcile with its own `1007 + 14`; prefer the measurement over either recorded figure, per the standing rule.

⚠ **A CRLF flip was caused and repaired during this round.** Rewriting the six existing `_key_was_consumed` call sites with a `pathlib` `read_text`/`write_text` pass flipped `test_dialog_enter_key.py` entirely to LF — the exact trap `CLAUDE.md` records (`repo is core.autocrlf=true`). **The rule stands and was ignored: use the Edit tool, or write bytes.**

⚠ **The detection method is the part worth keeping, because the DIFF CANNOT SEE THIS.** The diffstat read 6 changed lines either way; git normalizes on read, so `git diff` is blind to a working-tree line-ending flip. The only signal is the *"LF will be replaced by CRLF the next time Git touches it"* **warning on stderr** — which is easy to skim past, and which no test or docs build would ever have surfaced. Both files were restored with a byte-level rewrite and `file` now reports CRLF for every touched file.

⚠ `probe_441_kp_enter_platform.py` was also LF in the working tree and was normalized alongside it. **Whether this round caused that one was NOT established** — it may have been written LF by the session that created it. Recorded as unknown rather than blamed on the `Edit` tool, which is not known to flip endings.

**Files touched:** `dialog.py`, `CHANGELOG.md`, `test_dialog_enter_key.py`, `probe_441_kp_enter_platform.py`.

**Recommendation: stop reviewing here.** Rounds 1 and 2 each found defects the tests structurally could not see. Round 3 returned one out-of-scope pre-existing bug and three settled questions — the yield has gone to noise, and the two real items are tracked as #444 and #445.

**Still open, unchanged since round 1:** `CLAUDE.md` quotes the wrong #426 message as a good error under Layout, and now needs to describe **two** messages. Its own commit on `main`, never on this branch; `git diff main...HEAD -- CLAUDE.md` must stay empty before merging.

---

## Round 4 — 2026-08-12 — **THE LAST ROUND. The branch closes here.**

Scope was `git diff 7ef64236..48dba181`, the #446 flake fixes. **`git diff 7ef64236..48dba181 -- src/` is empty**, verified, so the premise that both flakes were test defects holds.

### The headline: this round should not have existed, and that is now a written rule

Round 3 already ended with *"stop reviewing here."* Round 4 ran anyway, on a **test-only commit**, and returned five findings of which three are about how a probe reads. Reviewing it would have produced a round 5 reviewing the fixes to those tests, and so on: the loop had no termination condition, because a round was triggered by *a commit existing* rather than by production code changing.

**Four stopping rules were added to `REVIEW-PROTOCOL.md` as a result** (maintainer, 2026-08-12): a round is triggered by a non-empty `git diff -- src/` and by nothing else; test code is reviewed only for **vacuity** and **false alarm**, with everything else recorded as a note; a round cap goes in `PLAN.md` up front (2 for a patch, 3 for a minor) and survivors become issues; and probes are instruments, not reviewed code, with one fix attempt per flake before quarantine. Under gate 1 this round would not have opened. Under gate 2 it yields two findings, not five.

⚠ **The measurable cost, recorded so the trade is visible:** this branch is **~430 production lines** against ~1,300 test lines and ~750 lines of probes and review records, over 17 commits of which 4 are review records. The production work — #426, #439, #440, #441 — was complete and verified at round 3. Rounds 3 and 4 changed **zero** lines under `src/`.

### One mechanism check that VALIDATES the widened barrier

`Tk_MapWindow` dispatches a child's `MapNotify` **synchronously** through `Tk_HandleEvent` (Tk generates it itself for non-toplevels), and defers mapping children until the master maps — measured here, a child of a withdrawn toplevel reads `winfo_ismapped() == 0`. So `focus_target_is_up()` returning true genuinely implies `_focus_when_mapped`'s handler has already run. **The barrier is sound on every window system, not only the one it was measured on.** Recorded because it is the kind of thing a later round would otherwise re-derive.

### I1 — `test_dialog_nested_modality.py:152` — vacuity — **FIXED**

`_nest`'s barrier gave up **silently**: `run` had no `else` arm, unlike `_outer`. An inner dialog that never took the grab meant nothing nested, so the outer grab was never displaced and `test_a_nested_modal_hands_the_grab_back` and `test_two_levels_of_nesting_hand_the_grab_back` both passed measuring nothing — the exact vacuity the control test at the top of the module exists to catch, arriving by a different route. It reports into `_NEST_PROBLEMS` now, which `_outer` asserts on.

⚠ **The control matters more than the fix, and the FIRST control was wrong.** Disabling the retry budget (`attempt < 0`) left the test **passing**, because the inner dialog already held the grab on the very first check — the give-up path was never reached, so the control proved nothing. Forcing the condition itself (`if True:`, "pretend the grab never arrives") is what exercised it. **Measured both ways: pre-fix the test PASSES in 8.83s** — it sat through the entire 8-second fallback, nested nothing, and still reported success — **post-fix it fails naming both the exhausted barrier and the fallback.** A control that does not reach the code path under test is indistinguishable from a fix that works.

### I2 — `test_dialog_nested_modality.py:110` — vacuity — **FIXED**

`_outer`'s error path was unreachable in practice. The retry budget reached `attempt == 200` at t≈10050ms while `force_close` fired at t=10000ms, so the fallback always won: it destroyed the toplevel, `show()` returned, the `finally` cancelled the remaining retries, and `state` was left empty **with no `"error"` key** — so `assert "error" not in state` passed. Four tests then died with a bare `KeyError` and `test_no_grab_is_left_behind_once_every_dialog_has_closed`, which reads no state, passed vacuously. Both budgets now sit below their fallbacks (150 attempts / 7550ms under 10s; 120 / 6050ms under 8s) **and** `force_close` records the timeout with `setdefault`, so neither route can close quietly.

### I3 — `probe_446_disabled_button_enter.py:150` — **NOTED, NOT FIXED**

The probe for this round's open question counts a barrier timeout as a reproduction: a run where `act` never fires yields `calls == []` with no other keys, byte-identical to the flake being hunted — and the probe's own READING text would then send the reader at the guard ("a delivery problem") rather than at the harness. **Real, and correctly described.** Not fixed under gate 4: it is an instrument, and the flake it serves is being filed rather than chased further on this branch. **Whoever picks up that issue must fix this first, or the probe will lie to them.**

### I4 — `probe_446_leaked_after_jobs.py:92` — **NOTED, NOT FIXED**

The zero result has no positive control: if `_root()` returns `None` or `after info` raises, `_pending()` returns empty on both sides of every test and the output is indistinguishable from a clean result. This is the standing *"a probe that finds nothing must be proven able to find something"* rule, landing on the probe that backs a **refutation** the brief lists as settled. Under gate 4 the probe is not fixed, **but the claim it supports is downgraded here: "no test-scheduled timer survives a test" is now recorded as UNCONTROLLED, not settled.** That is the gate-4 exception — a claim about evidence, not about code quality.

### I5 — `test_dialog_initial_focus.py:94` — **NOTED, NOT FIXED**

The widened barrier adds a way to time out without a way to say so; exhaustion surfaces as `KeyError: 'focused'`, naming neither the barrier nor which of the three conditions never held, in the file whose stated aim is that a recurrence names its own cause. Diagnostic quality, so a note under gate 2. Worth doing if that file is opened for another reason; not worth a commit of its own.

### The third flake — **FILED, not chased**

`test_enter_on_a_disabled_button_still_reaches_the_default` failed once in 37 post-fix runs with `calls == []`. Filed as an issue with the full state: 0/12 pre-fix, 1/37 post-fix, 0/40 in a quiet process, 25 further instrumented runs clean, and the two candidate steps already separated by the probe. **Not chased here, under gate 4's one-attempt rule and the brief's own warning that a clean batch is the expected outcome either way.** ⚠ It is also why I3 must be fixed before that issue is worked.

### Round 4 summary

| finding | class | outcome |
|---|---|---|
| I1 — `_nest` gives up silently | vacuity | **fixed**, control measured both ways |
| I2 — `_outer`'s error path unreachable | vacuity | **fixed** |
| I3 — the probe counts a timeout as a reproduction | diagnostics | **noted** — blocks the flake issue, not this branch |
| I4 — the leaked-timer refutation has no positive control | evidence | **noted**, and the claim downgraded to uncontrolled |
| I5 — focus barrier cannot name its own timeout | diagnostics | **noted** |

**Verification.** Five-file reproduction **61 passed, exit 0** — the same 61 as before the fix, so no test was added or removed. `test_dialog_nested_modality.py` alone: **11 passed**. The fix is confined to one test file, 49 insertions and 2 deletions; `git diff -- src/` is empty for it.

**No round 5.** Gate 1 forbids it: this round's fix touches no production code.
