"""Is 'a signal whose type does not suit the widget' a NEW hole, or pre-existing?

If Signal('yes') already realizes as a StringVar under a Checkbox today, then a
deferred-type empty-able signal doing the same is the SAME pre-existing gap, not
something the widening introduces.
"""
import os
import bootstack as bs

print("provenance:", os.path.dirname(bs.__file__))
print("branch check: allow_empty exists?",
      "nullable" in bs.Signal.__init__.__code__.co_varnames)
print()

with bs.App(title="probe") as app:
    for label, seed in (("Signal('yes')", "yes"), ("Signal(0)", 0), ("Signal(False)", False)):
        sig = bs.Signal(seed)
        try:
            cb = bs.Checkbox("Opt", signal=sig)
            var = type(sig._var).__name__
            print(f"   Checkbox + {label:15} var={var:11} widget={cb.value!r} sig={sig()!r}")
        except Exception as exc:
            print(f"   Checkbox + {label:15} RAISES {type(exc).__name__}: {exc}")
