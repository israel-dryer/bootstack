# PLAN — #390 (Signals cannot represent an empty value)

Branch `fix/signal-nullable-390`, off `main` at `028b8392`. Milestone `0.4.0`.
**Round cap: 3, spent 3 — the cap is reached and round 3's record is `REVIEW.md`.**

⚠ **RE-SCOPED 2026-08-27 BY MAINTAINER DECISION. THIS SUPERSEDES THE PLAN AT `14ea913f`**,
which designed a `nullable=` parameter that refused every widget-attached binding. Two things
changed: the concept is now **empty**, not **null**, and the **11 `StringVar`-backed bindings
accept** instead of refusing. Round 1 (`REVIEW.md`, commit `725b3990`) reviewed the superseded
design — its findings 1 and 9 carry forward and are folded in below; the rest are moot.

⚠ **Round 1's spend was against code this plan replaces.** The cap is left at 3 rather than
reset, so there are two rounds for substantially new code. If a third is needed on top, that is
a maintainer call, not this plan's to take.

## The decisions

Decisions 1–4 were answered by the maintainer 2026-08-26 in a **comment** on #390 (the body
still reads as an open design question — read the comment). Decisions 5 and 6 were answered
2026-08-27, in session, and are what re-scoped the branch.

1. **Do it at all?** YES.
2. **Declared, not automatic.** Now spelled **`Signal(v, allow_empty=True)`**. Automatic-by-mode
   cannot cover `int`: `Signal(0)` is Python-authoritative only while unrealized.
3. **A field bound to a signal that does NOT allow empty is cleared:** keep skipping, silently.
   Status quo; needs no code.
4. **`map()` is unchanged** — the transform is called with the source's empty and the author
   guards. Docs-only.
5. **A signal that allows empty, bound to a widget that stores the value directly:** accept
   where the backing variable has an empty member, refuse where it does not. **Replaces the
   superseded plan's blanket refusal.**
6. **The eligible set widens now**, in this branch, to all 11 `StringVar`-backed bindings.

## Why "empty" and not "null"

**Not a naming preference — `empty` is the vocabulary the framework already speaks, and
`nullable` was the odd one out.** `clear()` ships on nine field widgets today and already means
one verb with a type-dependent spelling:

```
TextField.clear()    ->  value = ""
NumberField.clear()  ->  value = None   # docstring: "not 0 - so a cleared required field still reads as blank"
DateField.clear()    ->  value = None
```

So the widgets already agree that *empty* is a single concept realized differently per type.
`nullable=True` invented a second, narrower one — "can hold `None`" — and three measurements
say that narrower promise was never keepable across the surface:

**The value type does not decide what can be empty; the binding does.**
`development/probe_390_granularity.py`, arm A — both rows are `str`:

```
TextField(textsignal=)     str  realized=True   allow_empty -> BIND RAISES
Select(signal=) str keys   str  realized=False  allow_empty -> set(None) OK, widget=None
```

**`None` cannot round-trip a realized native-mode binding.** `__call__` reads the var back
(`signal.py:188`), so `set(None)` must come back as something the var can hold. The one escape —
forcing object mode so `_last` stays authoritative — severs the widget→signal direction outright.
`development/probe_390_object_mode_text.py`:

```
control (native mode)  user types -> call='typed by the user'  subscriber saw it
object mode            user types -> call='seed'               subscriber told 'seed'
```

**And the framework already conflates the two spellings.** `TextField.value` returns `None` for
an empty field while its bound signal returns `''` — measured, today, with no `allow_empty`
anywhere (`development/probe_390_empty_string_null.py`, Q1).

Under `nullable=`, a text signal going to `''` on `set(None)` is a lie. Under `allow_empty=`, it
is exactly what was promised.

⚠ **This is NOT the per-type-empties proposal #390 rejected.** That one was `empty(int) = 0` and
`empty(bool) = False`, which contradict the shipped `NumberField.clear()` decision and collapse
tristate. Here the empty is `None` everywhere **except** where the toolkit can only hold a
string, and `''` is a real member of `str` rather than a repurposed in-band value. **Do not read
the rejection as covering this.**

## The floor that does not move — three types have no empty member

Measured in plain tkinter, `development/probe_390_no_empty_member.py`:

```
StringVar   set('')   OK    raw ''      -> ''            <- a real, legal value
BooleanVar  set('')   RAISES TclError: expected boolean value but got ""
BooleanVar  set(None) RAISES TypeError
DoubleVar   set('')   OK    raw ''      -> get() RAISES TclError
DoubleVar   set(None) OK    raw 'None'  -> get() RAISES TclError
IntVar      set('')   OK    raw ''      -> get() RAISES TclError
```

⚠ **The `DoubleVar`/`IntVar` rows are the dangerous ones and they are why this must raise rather
than degrade.** No error at the write, then a `TclError` at an arbitrary later `.get()` — a
repaint, another widget's callback — **fired inside a Tk trace, where Python cannot see it.**
That is the invisible-failure channel, not a crash anyone would find in testing.

And the Python types have nothing to fall back on: `str` has `''`; `bool` has only `True`/`False`,
where `False` means *off*, not *unset* (collapsing them is #358's tristate); `float` has none,
since `0.0` is a real slider position.

**So `Checkbox`, `Switch`, `ToggleButton`, `Slider` and `ProgressBar` refuse, under every option
considered.** This is a property of the toolkit, not a policy. The only real fix is to bind them
Python-side the way `ValueSignalMixin` does, which changes what `signal=` means on boolean
controls — out of scope, and it is round 1's finding 9.

## Where emptiness lands — the census

`development/probe_390_signal_census.py`: **24 public widgets take a signal. 16 realize** (the
Signal *is* the widget's Tk variable), **8 stay pure Python.**

| group | count | disposition |
|---|---|---|
| pure-Python bindings (`ValueSignalMixin`) | 8 | `NumberField`, `DateField`, `TimeField`, `Select`, `SelectButton` **accept** — the five #390 was moved onto `0.4.0` for. `TextArea`, `CodeEditor` accept trivially (their empty is `''` and always was). `Chart` undecided, out of scope |
| realized, `StringVar`-backed | 11 | **ACCEPT — this is the widening.** `TextField`, `PasswordField`, `PathField`, `SpinnerField`, `RadioGroup`, `ToggleGroup`, `Radio`, `RadioToggleButton`, `Label`, `Button`, `MenuButton` |
| realized, `BooleanVar`/`DoubleVar`-backed | 5 | **REFUSE.** `Checkbox`, `Switch`, `ToggleButton`, `Slider`, `ProgressBar` — the floor above |

⚠ **`RadioGroup` and `ToggleGroup` were the superseded plan's named near-miss, shelved onto
#369.** They come in for free here: measured, `signal.set('')` leaves them with nothing selected
and does not raise (`development/probe_390_stringvar_empty.py`). **#369 no longer needs to hold
them.**

## The change

### 1. `src/bootstack/signals/signal.py`

- **`__init__(self, value, name=None, master=None, *, allow_empty=False)`.** Keyword-only, so no
  positional call site can be affected.
- **`Signal.allows_empty`** — read-only property. Spelled as a question because it is read in
  conditions (`if signal.allows_empty:`), while the keyword is spelled as an instruction. The
  mismatch is deliberate; it is recorded here so a review does not "harmonize" it.
- **`Signal.clear()`** — sets the signal to its type's empty, through **`self.set(None)`**.
  ⚠⚠ **SUPERSEDED IN ROUND 2. THIS BULLET USED TO SPECIFY `self.set(self._empty_value())` AND
  CALL THE RESULTING ASYMMETRY "THE DESIGN, NOT AN OVERSIGHT". IT WAS AN OVERSIGHT.** Passing the
  empty in means a realized `str` signal receives `''`, a valid `str`, so `set()`'s `value is
  None` check never runs and **any realized text signal could be cleared with no declaration at
  all** — round 2's finding 3. Worse, the asymmetry that shipped was not even the one described:
  it keyed on **realization**, not on type, so `bs.Signal('x').clear()` raised before a binding
  and succeeded after one. `set(None)` routes through the check, and the rule is now uniform —
  a signal empties only if it was declared able to.
- **`_empty_value()`** — `set()` for a `set`-typed signal (the empty set is legal in both stores,
  so it needs no proxy); otherwise `''` where the value lives in a realized native-mode variable,
  and `None` elsewhere. Internal. ⚠ **The old spelling `'' if self._type is str else None` is
  wrong twice** — it misses that the `''` answer belongs to the *binding* rather than the type,
  and it sent a `set`-typed signal to `''`, which `SetVar` refuses (round 2's finding 4).
- **`set()`** — `None` is accepted when `allow_empty`, **or when `_type is NoneType`** (round 1's
  finding 1, kept verbatim: `map()` makes a `NoneType`-typed signal whenever the transform
  returns `None` for the first value it sees, and `set(None)` there has always been a no-op).
  An accepted `None` is then **normalized to `_empty_value()`**, so a `str` signal stores `''`.
- **`_realize()`** — refuse with `BootstackError` **only** when `allow_empty` and the type is
  `bool`, `int` or `float`, **tested with `issubclass`** (`1040a62d` — the identity spelling let a
  declared `IntEnum` past into an `IntVar`). The message names the type and says its variable
  cannot represent an empty value. ⚠ **"Every other type realizes as `StringVar` (or `SetVar`),
  which can" WAS WRONG about `SetVar`:** `SetVar.set('')` raises `Expected set or frozenset, got
  str`, which is round 2's finding 4. A `set` signal's empty is `set()`, not `''`.
- **Writing the empty into a realized var writes `''`, never `str(None)`.** Without this an
  object-mode `Label` displays the four characters `None` instead of going blank, which is the
  exact corruption #390 exists to remove.
- ⚠ **DEFERRED TYPE IS GONE — REPLACED IN ROUND 2 BY A DECLARED `dtype=`.** The superseded
  design gave `Signal(None, allow_empty=True)` a `_type` of `None` until the first non-empty
  `set()`. **That window was reachable from a widget binding, and round 2 measured what got
  through it** (findings 1 and 2): `self._type in (bool, int, float)` is False while the type is
  deferred, so `bs.Slider(signal=bs.Signal(None, allow_empty=True))` **built** and then raised
  `TypeError: unsupported operand type(s) for -: 'str' and 'float'` inside `slider.py:_on_var_write`
  — the exact invisible-in-a-Tk-trace failure `_realize()`'s comment says the guard prevents, and
  reached by the spelling the CHANGELOG advertises. Second, `_create_variable` dispatched on the
  **seed**, so a signal that started empty was a `StringVar` for life: after `set(5)` it reported
  `type is int` while `__call__` returned `'5'` and `clear()` raised out of its own setter.
- **The rule now: `dtype` is required when the seed is `None` and `allow_empty=True`, honored
  whenever it is given, and the seed is checked against it.** So `_type` is a real type from
  construction, always. ⚠ **Honored-not-ignored is deliberate and was decided against both
  alternatives** — *rejecting* `dtype` beside a value seed breaks the case it exists for
  (`bs.Signal(record.get('due'), allow_empty=True, dtype=date)`, where whether the seed is `None`
  is **data**, not a different spelling), and *ignoring* it silently makes `Signal(5, dtype=str)`
  an `int` signal, which is the audit's mode 5 and the `MenuButton` silent-skip this file already
  says not to copy into new code.
- **The seed goes through the same check every later write does.** `_reconcile()` is the one type
  rule — exact match, or an `int` widened into a `float` signal — called by both `__init__` and
  `set()`. ⚠ **Coercing at construction was rejected**: it would accept `Signal('5', dtype=int)`
  at birth while `sig.set('5')` raised for the rest of the signal's life, which is two type
  policies on one object. The two call sites differ only in the message — construction names both
  inputs, a bare write has only one.
- **`_create_variable` dispatches on `self._type`**, and `_is_tk_native_type()` is its type-level
  companion (`_is_tk_native` takes a *value*, and a signal that starts empty has none).
  ⚠ **BOTH ASK `issubclass`, NOT IDENTITY, AND SO DOES `_realize()`'s REFUSAL — the identity
  spelling shipped first and was wrong three times over** (`baacc48f`, `1040a62d`): an `IntEnum`
  is an `int` to `isinstance`, so identity sent it to a `StringVar`, made a declared `IntEnum`
  object-mode while a seeded one was native, and let it walk straight past the empty guard into
  an `IntVar`. **`grep -n "_type is \|_type in (" src/bootstack/signals/signal.py` bounds this**;
  the one survivor is `from_variable`'s recovery chain, left on purpose.
- **`Signal.type` stays `Type[T]`.** The deferred design retyped it to `Type[T] | None`, which is
  `0.5.0`'s rule; **with a declared `dtype` that retype disappears from the branch entirely**, so
  the public surface change is now `allow_empty=`, `dtype=`, `allows_empty` and `clear()`.
- ⚠ **`bs.Signal(None, dtype=date)` without `allow_empty=True` RAISES** — it would otherwise be a
  fresh instance of #481 reached through the new parameter. **`bs.Signal(None)` bare is
  untouched** and stays #481's, on `0.5.0`.
- **`dtype` takes the type itself, not `Form`'s string spelling.** `FieldItem.dtype` accepts both
  `'date'` and `date`; a signal's takes only the type, and the message says so. Unifying them
  belongs to the `dtype`/codec follow-up, not here.

### 2. `src/bootstack/widgets/_core/field_mixin.py`

The three seams are unchanged in shape; the predicate is renamed. Push the empty through when
the bound signal allows it, keep skipping silently when it does not (decision 3).

- `_to_signal` (`:297`), `_from_signal` (`:285`), `_sync_value_set`.

### 3. Docs

- `docs/reference/signals.rst:109` — the unguarded `due.map(lambda d: d.strftime(...))` is the
  only shipped example that breaks on an empty source. Guard it and state the rule beside it.
- The nullability section becomes an **emptiness** section: what `allow_empty=True` is for, that
  the empty is `''` for text and `None` otherwise, that `clear()` is the verb, and that the three
  types with no empty member raise at the binding.

### 4. CHANGELOG

One bullet under `### Added`, rewritten for `allow_empty=`.

⚠⚠ **THE PROMOTION TRAP STILL FIRES.** The `0.4.0` bullets for **#458 and #461** were qualified
in round 1 to say *"Declare the signal `nullable=True` and the clear reaches it"*. **Both now
name a parameter that will not exist** — they must be swept to `allow_empty=True` in this branch,
not at promotion time.

## Tests — `tests/widgets/public/test_signal_empty.py`

Renamed from `test_signal_nullable.py`. Carried over, renamed: the five value-space widgets
(round 1's finding 3 added `Select` and `SelectButton` to the parametrize — keep both), the
non-empty-able skip (decision 3), the deferred-type lock, `Form`-shaped `form.set({k: None})`,
and round 1's `test_a_none_typed_signal_still_no_ops_on_none`, **which must keep passing against
`main`'s `signal.py` as well as this branch's** — it pins the baseline, not the fix.

New, for the widening:

1. `test_clear_on_a_text_signal_stores_the_empty_string` — `Signal('x', allow_empty=True).clear()`
   gives `''`, not `None`; a bound `TextField` goes blank; the subscriber saw `''`.
2. `test_set_none_on_a_text_signal_normalizes_to_the_empty_string` — the uniform-clearing path.
3. `test_clearing_a_radiogroup_signal_selects_nothing` — the #369 near-miss, pinned.
4. `test_an_empty_text_signal_renders_blank_not_the_word_none` — asserts the **var contents**, the
   thing a user would see. This is the corruption test; it is the reason `''` is written rather
   than `str(None)`.
5. `test_binding_an_empty_signal_to_a_checkbox_raises` / `..._to_a_slider_raises` — the floor,
   pinned with its message and naming the type.
6. `test_clear_needs_no_declaration_on_a_text_signal` — `Signal('x').clear()` works;
   `Signal(date(...)).clear()` raises naming `allow_empty`. The asymmetry, pinned so it is not
   "simplified" away.

**Control, before committing:** revert `src/bootstack/widgets/_core/field_mixin.py` **only** (not
all of `src/`, which fails every test at the constructor and proves nothing), confirm the
field-clearing tests fail **on the behavior** — a stale value, or `''` where the empty was
expected — and not on `unexpected keyword argument 'allow_empty'`. Run the signal-level tests
against `main`'s `signal.py` the same way.

## Boundary of the completeness claim

Each of these is run and recorded in the review, not asserted from here.

- `grep -rn "nullable" src/bootstack tests/ docs/` must return **nothing** when the rename is
  done — the old name has no reason to survive anywhere.
- `grep -rn "allow_empty\|allows_empty" src/bootstack` bounds the new surface.
- `grep -rn "_object_mode\|_realize()" src/bootstack` bounds who is affected by the deferred type.
- `grep -rn "_bind_value_signal" src/bootstack` enumerates the value-space bindings.
- The census probe is re-run after the change, so the three-way table above is a measurement at
  the shipped commit rather than at the planned one.

## Out of scope — file, do not fix

- **#481, already filed** — `Signal(None)` without the flag constructs a signal that can never
  hold a value.
- **Round 1 finding 7** — `_push_to_signal`'s `except TypeError: pass` (`field_mixin.py:352`)
  swallows the mismatch once a deferred type locks to `int`: the field shows `5.5` while the
  signal stays `5`. Pre-existing (identical with `bs.Signal(0)`); the branch widens its reach.
  ⚠ **NOT FILED — maintainer decision 2026-08-27. Recorded here only. Do not file it as a
  drive-by.**
- **Round 1 finding 9's behavior half — FILED AS #483, and DISPOSITIONED AS DOCUMENTATION rather
  than a production fix (maintainer, 2026-08-27), "for now at least".** ⚠⚠ **THE CAUSE IS THE
  TOOLKIT, MEASURED IN PLAIN `tkinter` WITH NO FRAMEWORK INVOLVED**
  (`development/probe_483_ttk_alternate_variable.py`): the underlying checkbutton has **no tristate
  or indeterminate option at all**, and its indeterminate paint is a widget state that is fully
  orthogonal to the bound variable — it can be set while the variable reads `1`. **So the third
  state was never a variable concept to lose.** bootstack already surfaces MORE than the toolkit
  does, because `cb.value` reads the widget and returns `None`. **Do not re-open this as a defect.**
  The code change that would transcend it — binding boolean controls Python-side the way
  `ValueSignalMixin` does — is a redesign of what `signal=` means, belongs with #477, and carries
  the standing *"`value=` ignored when `signal=` is passed"* bug with it. **Shipped docs cover the
  gotcha:** `docs/widgets/checkbox.rst` and the note in `docs/reference/signals.rst`. A tristate
  `Checkbox` bound to a `Signal` cannot report indeterminate. ⚠ **Measured 2026-08-27, and it
  refines the floor above rather than being covered by it: `bool` DOES have an empty in this
  framework** — `Checkbox(tristate=True).value` is `None` — but the variable reads `'0'` for
  indeterminate and for off *identically*, because the third state lives in the ttk `alternate`
  widget state (ttk has no tristate option at all). **So the cause is the binding model, not the
  type**, and the real fix is to bind boolean controls Python-side the way `ValueSignalMixin`
  does. That fix also carries the missing half of the standing *"`value=` silently ignored when
  `signal=` is passed"* bug: honoring `value=` alone would start a checkbox indeterminate while
  its signal said `False`. ⚠ **`Switch` and `ToggleButton` reject `tristate=` outright, so this
  is about ONE widget, not about `bool`.**
- ⚠⚠ **THE CONSTRUCTION `bs.Checkbox(tristate=True, signal=bs.Signal(False))` IS CORRECT, AND AN
  EARLIER VERSION OF THIS BULLET CALLED IT A SILENT DEFECT. IT IS NOT.** Measured 2026-08-27: it
  shows unchecked, `widget.value` is `False` and the signal is `False` — all three surfaces agree,
  which is exactly what a reader expects. `tristate=True` grants the third state *and* defaults the
  start to it; a seed — `value=` or `signal=` — overrides the start and keeps the capability,
  precisely as `bs.Checkbox(tristate=True, value=False)` does. **Do not re-file the construction.**
  ⚠ **The residue is the RUNTIME step, not the seed:** after `cb.value = None` the checkbox paints
  indeterminate and reports `None` while the bound signal still says `False`. That is #483's
  mechanism, and it is where the "select all" pattern lives. Rejecting the combination outright was
  considered and **declined** — it breaks apps that pass both today and only use `True`/`False`,
  which is a strictness change and `0.5.0`'s rule.
- **NEW, measured 2026-08-27, NOT filed:** a signal whose *type* does not suit the widget is accepted
  silently. `bs.Checkbox(signal=bs.Signal('yes'))` realizes a `StringVar` and the two surfaces
  disagree — `widget=False sig='yes'` — today, on `main`, with no `allow_empty` involved
  (`development/probe_390_type_mismatch.py`). **Pre-existing and NOT introduced by the widening**;
  it is why a deferred-type signal reaching a `Checkbox` is the same known gap rather than a new
  hole. Belongs with #369/#383's family.
- **NEW, FILED AS #482:** a field's `value` lags a programmatic signal write until the next
  commit. `bs.TextField(textsignal=sig)`, `sig.set('world')` — the entry shows `world` while
  `field.value` still reports `hello`, resyncing only on blur. Pre-existing, not empty-specific
  (it lags a non-empty write identically) and reproduces with an ordinary `bs.Signal`. Same
  shape as #458, which was treated as a defect.
- **NEW, FILED AS #484 (round 3's one survivor):** every signal the framework creates for the
  caller is `allow_empty=False` permanently, so `clear()` on one raises *"Pass `allow_empty=True`
  to `Signal()`"* — a call that is not in the caller's code. ⚠ **Not pre-existing — `clear()`
  arrives in this branch.** ⚠⚠ **THE FIRST FILING BLAMED `Signal.from_variable()` AND THAT ROUTE
  IS NOT PUBLICLY REACHABLE** — `RadioGroup`/`ToggleGroup`/`Tabs` use it and expose no public
  `.signal`. **The reachable population is six widgets** (`TextField`, `PasswordField`,
  `PathField`, `SpinnerField`, `Slider`, `Checkbox`); the issue is retitled and carries the
  measurement. `field.clear()` and `signal.set('')` both work, so it is a message defect plus a
  small verb gap — and for `Slider`/`Checkbox` the refusal itself is right, only the text is wrong.
- **`Chart`** — the one gate-2 survivor left undecided. Out of scope either way.
- **#389** (`Form.reset()` / `Form.clear()`). This unblocks it; it does not implement it.
- **Widening `map()`** (decision 4).
