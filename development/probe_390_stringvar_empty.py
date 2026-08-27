"""#390 -- if '' were accepted as the empty for StringVar-backed bindings, which
widgets would that actually serve?

The review's gate 1 refuses all 16 realized bindings.  But 11 of them are StringVar,
where '' IS representable.  Does '' mean 'empty' to those widgets, or is it junk?
"""
import os
import bootstack as bs

print("provenance:", os.path.dirname(bs.__file__))
print()

with bs.App(title="probe") as app:
    print("-- RadioGroup: does '' read as 'nothing selected'? --")
    rsig = bs.Signal("a")
    rg = bs.RadioGroup(options=[("a", "Apple"), ("b", "Banana")], signal=rsig)
    print(f"   seeded 'a'      value={rg.value!r}  selection={rg.selection!r}")
    rsig.set("")
    print(f"   signal.set('')  value={rg.value!r}  selection={rg.selection!r}")

    print()
    print("-- ToggleGroup: same question --")
    tsig = bs.Signal("a")
    tg = bs.ToggleGroup(options=[("a", "Apple"), ("b", "Banana")], signal=tsig)
    print(f"   seeded 'a'      value={tg.value!r}")
    tsig.set("")
    print(f"   signal.set('')  value={tg.value!r}")

    print()
    print("-- Label / Button: is '' a sensible empty for display text? --")
    lsig = bs.Signal("hi")
    lb = bs.Label(textsignal=lsig)
    lsig.set("")
    print(f"   Label after ''  text={lb.text!r}")
