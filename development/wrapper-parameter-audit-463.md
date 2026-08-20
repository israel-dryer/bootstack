# Wrapper / internal parameter audit — the measurement pass (#463)

**Issue:** [#463](https://github.com/israel-dryer/bootstack/issues/463) · **Milestone:** `Wrapper and internal parity` (unnumbered)
**Branch:** `audit/wrapper-parameter-delta`, cut from `main` @ `22f045db`
**Run:** 2026-08-20, Windows box, `py -3.12`
**Ships no production code.** `git diff main...HEAD -- src/` is empty and stays empty.

**The instrument:** `development/probe_wrapper_parameter_delta.py`, four arms. Raw output is committed beside it as `wrapper-parameter-delta-{scan,control,leftovers,roundtrip}.txt`.

```
py -3.12 development/probe_wrapper_parameter_delta.py --arm scan -v
py -3.12 development/probe_wrapper_parameter_delta.py --arm control
py -3.12 development/probe_wrapper_parameter_delta.py --arm leftovers     # needs a display
py -3.12 development/probe_wrapper_parameter_delta.py --arm roundtrip     # needs a display
```

---

## Read this first: the result in three lines

1. **Modes 1 and 2 are essentially clean.** Zero never-forwarded parameters, and of 100 renamed destinations exactly **one** is a defect — **#461, already filed**. The wrapper layer's forwarding is in better shape than the recent defect run suggested.
2. **Mode 3 is the real exposure and it is broad: 40 of 52 wrappers silently accept a keyword they do not recognise.** Five wrappers already reject it, with a six-line guard that is in the codebase today. That is #383 gap 3, now measured and with its own precedent.
3. **Mode 5 is exactly #460 — eight widgets, no more and no fewer.** The scan reproduces that issue's population precisely, which is also the strongest evidence the tool is calibrated.

---

## Non-vacuity — run before believing any of the above

`--arm control`, all five checks **PASS**:

| control | mode | expected | found |
|---|---|---|---|
| #461 `SelectButton` `signal=` → `textsignal=` | 2 | present on `main` | ✅ found |
| #460 `.signal` annotated `\| None` it cannot return | 5 | present on `main` | ✅ found, and **exactly 8 widgets** |
| #383 gap 3 `TextField` accepts an unknown name silently | 3 | present on `main` | ✅ found |
| #458 `Select` `signal=` → `textsignal=` | 2 | **absent** on `main` | ✅ absent |
| #458 at `1f9a62d1^`, the pre-fix commit | 2 | **present** | ✅ found |

⚠ **The `main~` trap, worth keeping.** The first run of the #458 before/after arm used `main~` and failed. `main~` is two `docs(claude):` commits *after* the merge, so the defect was long gone. **The commit that bounds a control has to be the one the defect actually lived in** — here `1f9a62d1^`, the parent of the fix. The control is hardcoded to that SHA with a comment saying why.

**Parse integrity:** 58 files found, 58 parsed, 0 failures, and the report asserts `files_parsed + failures == files_found` rather than trusting it. Sources are read `utf-8-sig`; no bare `except` can swallow a parse failure. (This is the documented BOM trap that once made a completeness scan report zero hits.)

**Mode 3 is cross-checked against reality, not just read.** `--arm leftovers` constructs all 52 wrappers with an unknown keyword and compares the outcome to the static verdict: **51 agree, 0 disagree, 1 inconclusive.**

---

## Scope — the command, not the conclusion

```
scanned      src/bootstack/widgets/*.py        58 files, 65 public classes, 810 distinct params
NOT scanned  src/bootstack/dialogs/            (the probe accepts --src; this pass did not run it)
```

**Five classes the tool cannot speak about — do NOT read them as clean:**

| class | params | why |
|---|---|---|
| `AppShell` | 31 | builds no internal in its own `__init__` (`_init_shell` on `_ShellBase`) |
| `Workbench` | 34 | same |
| `ThemeToggle` | 5 | composes a `Button`, no internal of its own |
| `Notification` | 7 | toast host, no internal widget |
| `Snackbar` | 7 | same |

⚠ **`App`, `Window` and `Splash` were in this list and are now analysed** — they build the root first and alias it (`self._internal = self._tk_root`), which the first version of the tool could not follow. **The PLAN's warning was right and it was worth 84 parameters.**

**Forwarding idioms understood** (a wrapper using one not on this list is reported UNANALYZED, never clean):

- `internal_kwargs` / `kw` / `frame_kwargs` / `lf_kwargs` / `ps_kwargs` / `pw_kwargs` / `init_kwargs` dict splat
- direct keyword arguments on the construction call
- one alias hop (`self._tk_root = Internal(...)` … `self._internal = self._tk_root`)
- `super().__init__()` composition, including positional-to-name mapping
- pass-through slots (`_internal_options=options` merged wholesale by the base)
- `internal_kwargs.update(kwargs)`, `for k, v in kwargs.items(): internal_kwargs[k] = v`
- `for k, v in {"padding": padding, ...}.items(): frame_kwargs[k] = v`

---

## Results by mode

| mode | what | count | verdict |
|---|---|---|---|
| 1 | never forwarded | **0** | clean |
| 2 | wrong destination | 100 rows → **35 rank A / 65 rank B** | **1 defect (#461)**; the rest are internal naming |
| 3 | swallowed as a layout key | **40 of 52** wrappers | **the finding** |
| 4 | accepted then ignored | not statically decidable | 1 weak candidate, see below |
| 5 | the type lies | **8** | **= #460 exactly** |

### Mode 2 — how 100 rows became 1

A rename on its own says nothing (`max_value` → `maxvalue` is ordinary). The ranking signal is **divergence**: a public parameter name that lands on a **different** internal key in some other wrapper means the family disagrees with itself, and that is where both #458 and #461 lived. Sixteen names diverge; all sixteen were read.

| public name | destinations | verdict |
|---|---|---|
| **`signal`** | `signal` (9) · `signals` (Chart) · **`textsignal` (SelectButton)** | ⚠ **#461.** Chart normalizes one-or-many into a list — deliberate |
| `accent` | `accent` (39) · `surface` (Card) | ✅ deliberate — an accented Card is `accent[subtle]` surface *and* accent |
| `undecorated` | `override_redirect` (App) · `overrideredirect` (Window) | ✅ both correct — the two internals spell it differently |
| `read_only` | `read_only` · `readonly` · (`state` by guard) | ✅ three internals, three spellings; all work |
| `options` | `items` · `options` · `values` | ✅ internal naming only |
| `label` / `title` / `theme` / `variant` / `step` / `max_value` / `show_separators` / `data_source` / `icon` / `width` / `height` | see scan output | ✅ internal naming only |

**So: mode 2 produces no new defect.** ⚠ **That is a negative result and it is only worth something because the controls pass** — the same scan finds #461 on `main` and finds #458 at the pre-fix commit.

⚠ **A note that is real but OUT OF SCOPE by the PLAN's own boundary:** the *internal* layer spells the same concept a dozen ways (`readonly`/`read_only`, `maxvalue`/`maximum`, `items`/`options`/`values`, `override_redirect`/`overrideredirect`). No user can see it. It is an `_impl` defect and the PLAN says those get filed, not chased.

### Mode 3 — 40 wrappers accept anything

`_split_layout_kwargs()` strips the layout keys in place and **nothing reads what is left**, so `bs.TextField(bogus_xyz=1)` constructs silently while the internal `Field(master, bogus_xyz=1)` raises. **The public layer is the less strict of the two.**

| policy | count | wrappers |
|---|---|---|
| **DROPPED — silently accepted** | **40** | Accordion, Avatar, Badge, Button, ButtonGroup, Calendar, Card, Carousel, CodeEditor, Column, DataTable, DateField, Divider, Form, Gallery, Gauge, Grid, GroupBox, Label, ListView, NumberField, PageStack, PasswordField, PathField, ProgressBar, RadioGroup, RangeSlider, Row, ScrollView, Select, SelectButton, Slider, SpinnerField, SplitView, Tabs, TextArea, TextField, TimeField, ToggleGroup, Tree |
| REJECTED — raises `TypeError` naming the key | 5 | Checkbox, Radio, RadioToggleButton, Switch, ToggleButton |
| FORWARDED — reaches the internal, which raises | 5 | Chart, MenuButton, Picture, StatusBar, Toolbar |
| no split | 2 | App, Window |

⚠ **`Select`, `DateField`, `NumberField` and `TimeField` look like they reject and do not.** They carry an `if "textsignal" in kwargs: raise` guard, which rejects **one known name** and says nothing about the rest. A first version of the tool credited all four with rejecting; `--arm leftovers` caught it by construction. **A specific-key guard is not a leftover guard**, and the four are the wrappers most likely to be mistaken for strict.

✅ **The fix already exists in this codebase.** `_BooleanControlBase.__init__`:

```python
layout_kw = self._split_layout_kwargs(kwargs)
if kwargs:
    raise TypeError(
        f"{type(self).__name__}() got unexpected keyword argument(s): "
        f"{', '.join(sorted(kwargs))}"
    )
```

Six lines, already shipped, already covering five public widgets. **#383 gap 3 does not need a design — it needs this pasted at the shared split seam**, which is what that issue's open question ("the obvious home … needs the wrappers that legitimately forward `**kwargs` counted first") was waiting on. **They are now counted: five forward legitimately, two do not split.**

### Mode 5 — exactly #460

Eight widgets annotate `.signal` as `Signal | None` and return `getattr(self._internal, 'signal', None)` where the internal defines `signal` as a lazily-creating property with **no `None` path** — the default is unreachable:

`Checkbox`, `Switch`, `ToggleButton` (via `_BooleanControlBase`), `PasswordField`, `PathField`, `SelectButton`, `SpinnerField`, `TextField`

**`TextArea` was checked and CLEARED** — its internal has no class-level `signal`, so the attribute genuinely can be absent. That matches CLAUDE.md's standing warning not to "fix" TextArea, CodeEditor or the `ValueSignalMixin` trio, and the tool arrives at it independently.

### Mode 4 — one weak candidate, and an honest limit

`--arm roundtrip` constructs each wrapper with a non-default value for a parameter that has a same-named property and reads it back: **80 checked, 1 mismatch, 72 skipped.**

- `Carousel(index=7).index` reads back `0`. **Probably benign** — with no slides loaded there is nothing at index 7 to clamp to. Worth one look, not an issue on its own.

⚠ **This arm would NOT have caught #453**, the defect mode 4 is named for. `Select.read_only` answered `True` for every Select; the only honest observable was the inner entry's ttk state. **A property that echoes the stored setting cannot witness the setting being ignored.** The arm prints this limit before its results so a null is not over-read.

---

## Findings, ranked

| # | finding | mode | evidence | proposed |
|---|---|---|---|---|
| **1** | **40 of 52 wrappers silently accept an unrecognised keyword**, while 5 reject it with a guard that already exists | 3 | measured statically, cross-checked by construction (51/51 agree) | **fold the measurement into #383** — it is that issue's gap 3 with the counts it was blocked on |
| **2** | Eight widgets annotate `.signal` as `\| None` and cannot return it | 5 | scan reproduces #460's population exactly | **already #460**; this pass confirms the list is complete and that `TextArea` is correctly excluded |
| **3** | `SelectButton` `signal=` → `textsignal=` | 2 | scan rank A | **already #461** |
| 4 | The `_impl` layer spells one concept several ways | — | divergence table | **note only** — no user impact, out of the PLAN's scope |
| 5 | `Carousel(index=7).index == 0` | 4? | roundtrip arm | **note only** until someone reproduces it with slides loaded |

**No new issue needs filing.** Every real finding lands on an issue that already exists. The audit's product is the *measurement* those issues were missing — particularly #383 gap 3, which now has its population (40), its precedent (5), and its exclusions (5 forward, 2 no-split).

---

## Tool defects found and fixed during the run

Recorded because a probe whose conclusion will be cited has to show its own error history.

1. **Stopped at the subclass.** 19 classes read as unanalysable because the internal is built in a shared private base (`Checkbox`, `Row`, `Radio`, …). Fixed by composing through `super().__init__()`; ⚠ **without it the tool reported 40-odd parameters as unspeakable and would have looked thorough doing it.**
2. **Read only the leaf's vocabulary.** Reported `TimeField(read_only=True)` as writing a key nothing accepts. **It works** — `TimeEntry` delegates to `Field`. Fixed by unioning `Unpack[TypedDict]` over the internal's whole MRO. Caught by construction, not by reading.
3. **Counted a specific-key guard as a leftover guard.** Credited `Select`, `DateField`, `NumberField`, `TimeField` with strictness they do not have. Caught by `--arm leftovers`.
4. **Missed two merge idioms** — `for k, v in kwargs.items()` (MenuButton) and `for k, v in {...}.items()` (Grid) — producing one false "dropped" and two false "never forwarded".
5. **Pointed the before/after control at `main~`**, which is after the fix.

⚠ **Four of these five were caught by running something, not by reading something**, and three of them were false alarms pointing at working code. **A static wrapper audit that is not cross-checked against construction will ship false findings** — that is the transferable lesson, and it is why `--arm leftovers` exists.

---

## The durable guard — deliberately not built here

A one-time audit decays. The valuable half is a `test_public_surface.py`-style test at the **parameter** level, designed to these five modes. It is a separate branch and needs this taxonomy to exist first, which it now does.

⚠ The existing `tests/test_public_surface.py` has a blind spot of exactly this kind — it gates the top-level *name set* but never asserts a submodule is unreachable as `bs.*`, which is why the `bs.events.X` drift went uncaught for two months. **Design the new guard to the modes, or it inherits the same shape.**
