# PLAN — #484: a signal the framework created for you can never be cleared

**Branch** `fix/widget-owned-signal-clear-484` off `main` (post-`0.4.0`, after the
#481/#482/#490 merges).
**Round cap: 2** (patch-shaped — no new public surface, and it makes `clear()`
succeed where it raised, which is the opposite direction from the patch line's
"raises where the framework accepts" exclusion).
Milestone: `0.4.x — Patch line`.

## The defect

Six public widgets expose a `.signal` the caller never constructed. All six get
`allow_empty=False` permanently, so `clear()` raises — and the message names a
constructor the caller cannot reach. Re-measured on `main` 2026-08-30, five
merges after the issue was filed; unchanged:

```
TextField      allows_empty=False  clear() TypeError: Expected str,   got NoneType. Pass allow_empty=True to Signal()...
PasswordField  allows_empty=False  clear() TypeError: Expected str,   got NoneType. ...
PathField      allows_empty=False  clear() TypeError: Expected str,   got NoneType. ...
SpinnerField   allows_empty=False  clear() TypeError: Expected str,   got NoneType. ...
Slider         allows_empty=False  clear() TypeError: Expected float, got NoneType. ...
Checkbox       allows_empty=False  clear() TypeError: Expected bool,  got NoneType. ...
```

`TextArea`, `NumberField` and `Select` return `None` for `.signal` while unbound,
so they never reach it.

There is no edit that follows the advice: `Signal()` is not in play, and no
keyword on `TextField(...)` reaches the creation either.

## Mechanism

Both lazy creation paths funnel through **one** function, `create_signal()` in
`_core/signal_binding.py`:

- `SignalMixin.textsignal` (`signal_mixin.py:103`) → `create_signal("")`
- `SignalMixin.signal` (`signal_mixin.py:223`) → `create_signal(infer_default_value_for_widget(...))`

`infer_default_value_for_widget` returns `False` for checkbuttons, `0` for
radiobuttons, `0.0` for scales, `0` for progressbars, `""` for everything else.
`create_signal` then calls a bare `Signal(default_value)`, which is
`allow_empty=False`.

⚠ **Neither path uses `Signal.from_variable`.** Gating `create_signal` reaches all
six widgets and nothing else.

## The issue's own text is stale in two places

- It points at `_core/capabilities/signals.py`. **PR #494 deleted that package**;
  both paths now live in `_core/signal_binding.py`.
- Its original body blames `Signal.from_variable()`. The correcting comment
  (2026-08-27) already overturned that: `RadioGroup`/`ToggleGroup`/`Tabs` are the
  only widgets built that way and **none exposes a public `.signal`**. Read the
  comment, not the body.

## Change 1 — the gate

`_core/signal_binding.py`, in `create_signal()`, currently
`signal = Signal(default_value)`. Declare empty when the type has an empty member:

```python
signal = Signal(default_value, allow_empty=isinstance(default_value, (str, set)))
```

Use `(str, set)`, not `str` alone, even though only `str` arrives here today — it
mirrors `Signal._empty_value()`'s own rule, and drift between *what may declare
empty* and *what empty means* is the class of bug #390 round 2 already paid for.
Put the reason in a `#` comment, not the docstring.

**This is the whole fix for the four text fields.** Their default is `""`, so they
get `allow_empty=True` and `clear()` works; `Slider`, `Checkbox`, radiobuttons and
progressbars keep `False` because their defaults are `0.0`, `False` and `0`.

### ⚠⚠ DO NOT make it an unconditional `allow_empty=True`

Measured — an empty-capable signal **cannot be bound** to the widgets whose
variable has no empty member:

```
Slider(signal=Signal(0.0, allow_empty=True))      -> BootstackError: cannot be bound to this widget
Checkbox(signal=Signal(False, allow_empty=True))  -> BootstackError: cannot be bound to this widget
TextField(textsignal=Signal('', allow_empty=True)) -> built
```

A blanket default has the framework hand those widgets a signal its own binding
guard rejects, making **every slider and checkbox fail on construction**. That is
#390's floor doing its job, not a bug to route around.

## Change 2 — the message, and why it cannot branch on type

After change 1 the only widget-owned signals still refusing are `Slider` and
`Checkbox`, and they *should* refuse. The sentence is still unactionable there.

⚠ **The discriminator is ownership, not type.** Measured: `allow_empty` is legal on
a `float`/`bool` signal on its own —

```
Signal(0.0, allow_empty=True)     -> constructs, .clear() reads None
Signal(False, allow_empty=True)   -> constructs, .clear() reads None
```

— so for a signal the **caller** built, "Pass `allow_empty=True` to `Signal()`" is
correct and actionable. The floor is at the binding, not the type. Branching the
message on `bool`/`float` would therefore make it wrong for callers to fix it for
widgets.

**Mechanism:** have `create_signal()` mark what it builds (`signal._widget_owned =
True`) and branch on that flag in `Signal.set()`'s `value is None` guard
(`signals/signal.py:378-382`). Private attribute, no public surface. The widget-owned
sentence should say the signal belongs to the widget, the widget's variable cannot
hold an empty value, and point at `widget.clear()`.

**Acceptable descope:** leave the message alone and ship change 1 only. That closes
the four cases anyone actually hits and leaves `Slider`/`Checkbox` pointing at a
constructor. Say so in the PR if you take it, rather than leaving it looking missed.

## Do not touch

`Signal.from_variable` keeps `allow_empty=False`. Its reasoning is documented at the
forcing site — *"the var already exists and is the widget's, so it decides what can
be stored"* — #484 explicitly is not questioning it, and no public widget exposes a
`.signal` built that way.

## Tests

New file, `tests/widgets/public/test_widget_owned_signal_clear.py`.

1. Each of the four text fields: `.signal.allows_empty is True`, `clear()` leaves the
   signal `''`, and the entry blanks.
2. `Slider` and `Checkbox`: `clear()` still raises, and the message does **not** name
   `Signal()`.
3. ⚠ **The control that matters most** — `bs.Slider()` and `bs.Checkbox("x")` still
   construct and `.signal` still reads. Without it, a later "simplification" to an
   unconditional `allow_empty=True` passes every other test in the file while making
   both widgets unconstructible.
4. Second control — a caller-made `bs.Signal(0.0, allow_empty=True)` still clears to
   `None` unbound, proving the gate did not leak into caller-owned signals.

Run the controls against the pre-fix commit *and* against a deliberately unguarded
version, the way #491's file was verified: no single wrong implementation should pass
the file.

## CHANGELOG

`### Fixed`. It is reachable — `.signal` and `clear()` are both public surface — so it
earns an entry. Lead with the reader's question: `clear()` on the signal a text field
made for you raised, advising a constructor you never called; it now empties the field
to `''`. Name that `Slider` and `Checkbox` still refuse, and why. One paragraph, one
line, no hard wrap.

## Settle before starting

⚠ **`field.value` reads `None` after a clear while the bound signal reads `''`.**
#484's correcting comment calls this "the known `TextField` value/signal divergence"
and says it is already filed — **but it names no issue number and I could not find
one.** Pin it down first: this change makes `clear()` reachable on four more widgets,
so the divergence will start showing up in places it could not before and will look
like this branch caused it.

## Out of scope

- **#482's residue** — a programmatic write while the field has focus still lags.
- **Near-dead code from #481.** `Signal.set()` still carries `self._type is not
  type(None)` with a comment explaining that `map()` produces `NoneType` signals.
  #481 closed that route; only an explicit `dtype=type(None)` reaches it now. Worth a
  follow-up issue, not this branch.
