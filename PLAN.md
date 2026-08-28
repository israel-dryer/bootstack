# PLAN — #460: `.signal` is annotated `| None` on widgets that can never return `None`

**Branch:** `fix/signal-annotation-460` off `main` at `1fb13d7d`
**Milestone:** `0.4.0 — Signal binding on fields`
**Round cap: 2.** The diff is annotations and docstrings only — no behavior
change, no new surface. Patch-shaped work riding a minor, so the patch cap
applies rather than the minor's 3.

## What this fixes

Five public `signal` property definitions, covering seven widgets, are annotated
`Signal | None` and end their docstring with "or `None`". None of them can
return `None`. The annotation is wrong for every caller and for every type
checker, and the docstring text renders into the published API Reference.

Each of these wrappers forwards with `getattr(self._internal, 'signal', None)`,
so the `None` default fires only when the attribute is *absent*. It never is:
the internal `signal`/`textsignal` are properties that **lazily create on first
access** (`_impl/mixins/signal_mixin.py:92` and `:211`), both declared
`-> Signal[str]` / `-> Signal[Any]` with no `None`. Reading the attribute
manufactures a `Signal` if one does not exist yet, so the `getattr` default is
**dead code** and the `| None` half is unreachable, not merely unobserved.

## Scope — MEASURED on this branch's base, not taken from the issue

`development/probe_460_signal_never_none.py`, arms `scan` and `control`, run on
`main` at `1fb13d7d`. It constructs every widget exposing a public `signal`
property, reads the property, and compares the result against the declared
annotation.

| location | widgets | unbound `.signal` returns |
|---|---|---|
| `widgets/textfield.py:165` | `TextField` | `Signal('')` |
| `widgets/passwordfield.py:140` | `PasswordField` | `Signal('')` |
| `widgets/pathfield.py:218` | `PathField` | `Signal('')` |
| `widgets/spinnerfield.py:170` | `SpinnerField` | `Signal('')` |
| `widgets/boolean_controls.py:174` | `Checkbox`, `Switch`, `ToggleButton` | `Signal(False)` / `Signal('0')` |

⚠ **THE ISSUE'S TABLE IS STALE AND LISTS SIX LOCATIONS / EIGHT WIDGETS. IT IS
FIVE AND SEVEN.** `SelectButton` was the sixth; **#461 moved it onto
`ValueSignalMixin`** (`selectbutton.py:23`), whose `signal` property returns
`None` when unbound and is annotated correctly. The probe measures it as `ok`.
**Do not re-add it to the sweep.**

## Deliberately NOT touched

- **`TextArea` and `CodeEditor`** — see the finding below. Their `| None` is
  accurate; their problem is the opposite one and it is a behavior change.
- **`NumberField`, `DateField`, `TimeField`, `Select`, `SelectButton`** — all
  bind through `ValueSignalMixin`, whose `signal` returns `None` when nothing is
  bound. Annotation is correct. Measured `ok` on both arms.
- **`Slider`** — already annotates `Signal[float]` with no `None`, and delegates
  directly rather than through `getattr`. It is the exemplar this fix moves the
  five toward.

## A NEW DEFECT FOUND WHILE MEASURING — FILED, NOT FIXED HERE

**`TextArea.signal` and `CodeEditor.signal` are DEAD PROPERTIES: they return
`None` even when a signal IS bound.** The issue lists both as "correct — do not
fix", but it only ever checked the *unbound* case.

- `textarea.py:155` reads `getattr(self._internal, "signal", None)`; the impl
  composite has neither `signal` nor `textsignal`.
- `codeeditor.py:191` reads `getattr(self._internal.core, "signal", None)`; the
  core stores the bound signal at the **private** `self._signal`
  (`_impl/composites/textarea/core.py:55,284`) and exposes no public property.

So the `Signal[str]` half of *their* annotation is the unreachable one — the
exact mirror of #460. Measured with the probe's `control` arm: bound a
`Signal("hello")` via `textsignal=`, and both still report `None`.

**Out of scope here on purpose.** Repairing it makes a property that returned
`None` start returning an object, which is a behavior change, not a typing fix,
and it needs a decision about whether the public spelling is `.signal` or
`.textsignal` on these two. Filed separately; milestone is the maintainer's
call.

## The change

For each of the five locations, both halves together:

1. Drop `| None` from the return annotation and the trailing "or `None`" from
   the docstring.
2. Collapse the provably dead `getattr(self._internal, 'signal', None)` to a
   direct delegation, matching `Slider` (`widgets/slider.py:123`).

**Why both halves and not just the annotation.** The issue offers them as
independent. They are not, for this branch's purpose: leaving the `getattr` in
place keeps a `None`-producing default sitting under an annotation that now
promises it cannot happen, which is precisely the shape that drifts back. The
direct delegation makes the annotation checkable against the code rather than
against a measurement nobody re-runs.

## Invariants

- **No behavior change.** The property returns the identical object before and
  after; only the path it takes and what it claims change. The probe's `scan`
  arm is the before/after control — every row must report the same value on both
  arms of `git stash`.
- **The internal attribute must exist on every one of the five.** The whole fix
  rests on it; a direct delegation to an absent attribute is an `AttributeError`
  where the old code returned `None`. The probe proves existence by reading a
  live `Signal` back on all seven widgets, on both the unbound and bound arms.
- **`TextArea`/`CodeEditor` keep their `getattr`**, because for them the default
  is load-bearing — it is the only reason the property does not raise.

## Test plan

A new `tests/widgets/public/test_signal_property_contract.py`:

- For each of the seven widgets, constructed unbound: `.signal` is not `None`
  and is a `Signal`.
- For each, constructed with a signal bound: `.signal` **is** that same object
  (identity, not equality) — this is what would catch a delegation pointed at
  the wrong attribute, which an is-not-None assertion would not.
- For `TextArea`, `CodeEditor`, `NumberField`, `DateField`, `TimeField`,
  `Select`: `.signal` is `None` when unbound — pins the widgets the sweep must
  **not** touch, so a later "consistency" pass cannot quietly widen it.
- A structural test asserting no public `signal` property in `widgets/*.py`
  annotates `| None` while returning a live signal — the guard that makes the
  sweep's completeness checkable rather than asserted.

⚠ **The failure mode to avoid: a test that asserts `.signal is not None` passes
identically before and after**, since the property already returned a live
signal. These tests pin the *contract*, and the annotation itself is pinned by
the structural test. The behavior half genuinely cannot regress-test the fix —
say so rather than pretending otherwise.

## Verification

- `py -3.12 tests/run_gui.py` — expect `1638 + <new file>` / 22, exit 0.
- Clean docs build with `-W`: `rm -rf docs/_build && sphinx-build -b html docs
  docs/_build/html -W --keep-going`. The docstrings render into the API
  Reference, so this is the check that the published text moved.
- `grep -rn "or \`None\`" src/bootstack/widgets/` to bound the completeness
  claim by command rather than by conclusion.
- Re-run the probe on both arms and confirm every row's value is unchanged.

## CHANGELOG

`## [Unreleased]`, under `### Fixed`. It is user-visible: the published API
Reference text for seven widgets changes, and a type checker stops demanding a
`None` guard callers never needed.
