"""Adversarial verification of #390 round 2's seven findings.

Each arm reproduces ONE claim from the report and prints PASS (claim holds) or
REFUTED (claim does not reproduce). Run: py -3.12 development/probe_390_review_round2_verify.py
"""
import traceback
from datetime import date

import bootstack as bs
from bootstack.errors import BootstackError

results = []


def record(n, claim, holds, detail):
    results.append((n, claim, holds, detail))
    print(f"[{n}] {'HOLDS  ' if holds else 'REFUTED'} {claim}")
    print(f"      {detail}")


def arm1(app):
    """F1: realize guard misses an empty-SEEDED signal, so bool/int/float bind."""
    out = []
    for name, factory in (
        ("Slider", lambda s: bs.Slider(signal=s)),
        ("Checkbox", lambda s: bs.Checkbox("x", signal=s)),
        ("ProgressBar", lambda s: bs.ProgressBar(signal=s)),
    ):
        sig = bs.Signal(None, allow_empty=True, dtype=float)
        try:
            factory(sig)
            out.append(f"{name}: built, var={type(sig.var).__name__}")
        except BootstackError as e:
            out.append(f"{name}: REFUSED ({type(e).__name__})")
        except Exception as e:
            out.append(f"{name}: {type(e).__name__}: {e}")
    # control: the value-seeded spelling the guard was written for
    ctl = bs.Signal(False, allow_empty=True)
    try:
        bs.Checkbox("c", signal=ctl)
        ctl_msg = "control Checkbox(Signal(False, allow_empty=True)): BUILT (guard missed)"
        ctl_ok = False
    except BootstackError:
        ctl_msg = "control Checkbox(Signal(False, allow_empty=True)): refused (guard fires)"
        ctl_ok = True
    holds = any("built" in o for o in out) and ctl_ok
    record(1, "empty-seeded signal slips the bool/int/float realize guard",
           holds, "; ".join(out) + " | " + ctl_msg)


def arm2(app):
    """F2: a signal that starts empty must get the variable its type calls for."""
    parts = []
    # int + allow_empty cannot be realized at all now -- the guard reaches it.
    sig = bs.Signal(None, allow_empty=True, dtype=int)
    try:
        _ = sig.var
        parts.append(f"dtype=int: REALIZED (var={type(sig.var).__name__})")
        wrong = True
    except BootstackError:
        parts.append("dtype=int: refused at realize")
        wrong = False
    # the types that can hold an empty get the right var and their own type back
    for dt, expect in ((str, "StringVar"), (date, "StringVar"), (set, "SetVar")):
        s = bs.Signal(None, allow_empty=True, dtype=dt)
        got = type(s.var).__name__
        parts.append(f"dtype={dt.__name__}: var={got} type={s.type.__name__}")
        wrong = wrong or got != expect
    record(2, "a signal that starts empty realizes as a StringVar whatever its type",
           wrong, "; ".join(parts))


def arm3(app):
    """F3: clear() bypasses the allow_empty declaration once realized."""
    sig = bs.Signal("hello")  # NOT allow_empty
    fld = bs.TextField(textsignal=sig)
    try:
        sig.clear()
        holds = True
        detail = f"clear() SUCCEEDED on allow_empty=False: sig()={sig()!r} field.value={fld.value!r}"
    except TypeError as e:
        holds = False
        detail = f"clear() raised TypeError as documented: {e}"
    # control: unrealized signal of the same type
    ctl = bs.Signal("hello")
    try:
        ctl.clear()
        ctl_msg = "control (unrealized): clear() SUCCEEDED too"
    except TypeError:
        ctl_msg = "control (unrealized): clear() raised, as documented"
    record(3, "clear() ignores allow_empty=False once the signal is realized",
           holds, detail + " | " + ctl_msg)


def arm4(app):
    """F4: set-typed signal has no empty member and is not in the realize guard."""
    sig = bs.Signal({"a"}, allow_empty=True)
    built = None
    try:
        bs.ToggleGroup(options=["a", "b"], mode="multi", signal=sig)
        built = f"built, var={type(sig.var).__name__}"
    except BootstackError as e:
        built = f"REFUSED at realize: {e}"
    except Exception as e:
        built = f"{type(e).__name__}: {e}"
    err = None
    try:
        sig.clear()
        err = f"clear() ok, sig()={sig()!r}"
        raised = False
    except TypeError as e:
        err = f"clear() raised TypeError: {e}"
        raised = True
    record(4, "set-typed signal: clear() raises out of the caller",
           raised and "built" in built, built + " | " + err)


def arm5(app):
    """F5: a second binding flips what empty means for the first."""
    sig = bs.Signal("1", allow_empty=True)
    sel = bs.Select(options=[("One", "1"), ("Two", "2")], signal=sig)
    sig.clear()
    a = f"Select only: sig()={sig()!r} select.value={sel.value!r} realized={sig._var is not None}"

    sig2 = bs.Signal("1", allow_empty=True)
    sel2 = bs.Select(options=[("One", "1"), ("Two", "2")], signal=sig2)
    bs.Label(textsignal=sig2)  # realizes it
    sig2.clear()
    b = f"Select+Label: sig()={sig2()!r} select.value={sel2.value!r} realized={sig2._var is not None}"
    holds = sig() != sig2()
    record(5, "adding a second binding changes the first binding's empty",
           holds, a + " | " + b)


def arm6(app):
    """F6: map() does not propagate allow_empty."""
    src = bs.Signal(date(2024, 5, 5), allow_empty=True)
    derived = src.map(lambda x: x.isoformat() if x else None)
    detail = f"derived.allows_empty={derived.allows_empty} derived()={derived()!r}"
    try:
        src.clear()
        detail += f" | clear() ok, src()={src()!r} derived()={derived()!r}"
        raised = False
    except TypeError as e:
        detail += f" | clear() raised TypeError: {e}"
        raised = True
    # the swallowed variant, through a bound field
    src2 = bs.Signal(date(2024, 5, 5), allow_empty=True)
    d2 = src2.map(lambda x: x.isoformat() if x else None)
    fld = bs.DateField(signal=src2)
    fld.value = None
    detail += f" || via field: src2()={src2()!r} derived2()={d2()!r} (stale={d2() == '2024-05-05'})"
    record(6, "map() drops allow_empty: clear() raises unactionably or goes stale",
           raised or d2() == "2024-05-05", detail)


def arm7(app):
    """F7: a push the signal's type cannot take is swallowed (round 1 finding 7)."""
    sig = bs.Signal(None, allow_empty=True, dtype=int)
    fld = bs.NumberField(signal=sig)
    fld.value = 5
    t1 = sig.type
    fld.value = 2.5
    detail = (f"after value=5: sig.type={t1} sig()={sig()!r} | "
              f"after value=2.5: field.value={fld.value!r} sig()={sig()!r}")
    holds = fld.value != sig()
    record(7, "a float pushed into an int signal is swallowed and the signal goes stale",
           holds, detail)


with bs.App(title="probe-390-r2") as app:
    for fn in (arm1, arm2, arm3, arm4, arm5, arm6, arm7):
        try:
            fn(app)
        except Exception:
            print(f"[{fn.__name__}] ARM CRASHED:")
            traceback.print_exc()
        print()

print("=" * 70)
for n, claim, holds, _ in results:
    print(f"F{n}: {'HOLDS' if holds else 'REFUTED'} -- {claim}")
