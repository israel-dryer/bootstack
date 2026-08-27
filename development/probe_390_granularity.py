"""#390 -- does the VALUE TYPE decide nullability, or does the BINDING?

Arm A: two widgets whose value type is `str`, one realized, one not.
Arm B: two widgets whose value type is `date`, both unrealized -- type is constant,
       so if type decided, both arms would agree within themselves.
"""
import os
from datetime import date
import bootstack as bs

print("provenance:", os.path.dirname(bs.__file__))
print()


def probe(label, build, seed, nullable):
    sig = bs.Signal(seed, nullable=nullable) if nullable else bs.Signal(seed)
    try:
        w = build(sig)
    except Exception as exc:
        print(f"{label:32} nullable={nullable!s:5} BIND RAISES {type(exc).__name__}: {exc}")
        return
    realized = sig._var is not None
    try:
        sig.set(None)
        outcome = f"set(None) OK -> widget={w.value!r} signal={sig()!r}"
    except Exception as exc:
        outcome = f"set(None) RAISES {type(exc).__name__}"
    print(f"{label:32} nullable={nullable!s:5} realized={realized!s:5} {outcome}")


with bs.App(title="probe") as app:
    print("-- ARM A: value type is `str` in BOTH rows --")
    probe("TextField(textsignal=)", lambda s: bs.TextField(textsignal=s), "a", False)
    probe("TextField(textsignal=)", lambda s: bs.TextField(textsignal=s), "a", True)
    probe("Select(signal=) str keys", lambda s: bs.Select(options=["a", "b"], signal=s), "a", False)
    probe("Select(signal=) str keys", lambda s: bs.Select(options=["a", "b"], signal=s), "a", True)

    print()
    print("-- ARM B: value type is `date` in BOTH rows --")
    probe("DateField(signal=)", lambda s: bs.DateField(signal=s), date(2024, 5, 5), False)
    probe("DateField(signal=)", lambda s: bs.DateField(signal=s), date(2024, 5, 5), True)
    probe(
        "Select(signal=) date values",
        lambda s: bs.Select(options=[(date(2024, 5, 5), "May"), (date(2024, 6, 6), "Jun")], signal=s),
        date(2024, 5, 5),
        True,
    )
