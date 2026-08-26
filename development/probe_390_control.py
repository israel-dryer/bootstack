"""Control for #390 — makes the baseline fail BEHAVIORALLY, not on a missing kwarg.

Run against the PRE-FIX src. A plain run of the new tests there dies on
`TypeError: unexpected keyword argument 'nullable'`, which only proves the
parameter does not exist yet. This stubs `nullable=` into the baseline Signal as
an inert flag, so every assertion below reaches the real behavior and the
failures are the ones the fix is meant to remove.

ASCII only.
"""
from datetime import date

import bootstack as bs
from bootstack.signals.signal import Signal

STUBBED = not hasattr(Signal, "nullable")
if STUBBED:
    _orig = Signal.__init__

    def _init(self, value, name=None, master=None, *, nullable=False):
        _orig(self, value, name, master)
        self._nullable = nullable

    Signal.__init__ = _init
    Signal.nullable = property(lambda self: getattr(self, "_nullable", False))

print("ARM:", "BASELINE (nullable= stubbed inert)" if STUBBED else "FIXED (real nullable=)")

app = bs.App(title="c390")
app.__enter__()
fails = []


def check(label, got, want):
    ok = got == want
    if not ok:
        fails.append(label)
    print(f"{'ok ' if ok else 'FAIL'} {label:<46} got={got!r} want={want!r}")


# 1. set(None) on a nullable signal
sig = bs.Signal(date(2024, 5, 5), nullable=True)
try:
    sig.set(None)
    check("nullable set(None) stores None", sig(), None)
except TypeError as e:
    check("nullable set(None) stores None", f"TypeError: {e}", None)

# 2. seeded-empty signal has a deferred type
u = bs.Signal(None, nullable=True)
check("Signal(None, nullable=True).type", u.type, None)

# 3. clearing a bound field reaches the signal
s2 = bs.Signal(date(2024, 5, 5), nullable=True)
fld = bs.DateField(signal=s2, parent=app)
app.tk.update()
seen = []
s2.subscribe(lambda v: seen.append(v))
fld.value = None
app.tk.update()
check("DateField cleared -> signal", s2(), None)
check("DateField cleared -> subscribers", seen, [None])

# 4. a non-nullable signal keeps skipping (decision 3 — must hold on BOTH arms)
s3 = bs.Signal(date(2024, 5, 5))
f3 = bs.DateField(signal=s3, parent=app)
app.tk.update()
f3.value = None
app.tk.update()
check("non-nullable stays stale (both arms)", s3(), date(2024, 5, 5))

# 5. binding a nullable signal to a text field is refused
try:
    bs.TextField(textsignal=bs.Signal("hi", nullable=True), parent=app)
    check("TextField(nullable) refused", "constructed", "BootstackError")
except Exception as e:
    check("TextField(nullable) refused", type(e).__name__, "BootstackError")

print()
print(f"{len(fails)} behavioral failure(s): {fails}")
