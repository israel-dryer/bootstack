"""Round 3 -- every factual claim in the new signals.rst / checkbox.rst prose,
run rather than read. ASCII only."""
from datetime import date
import bootstack as bs

def show(claim, got, want):
    ok = "OK  " if got == want else "WRONG"
    print("  [%s] %-58s got=%r want=%r" % (ok, claim, got, want))

with bs.App(title="docs") as app:
    # signals.rst -- "Empty values"
    due = bs.Signal(date(2026, 1, 15), allow_empty=True)
    bs.DateField(signal=due)
    due.clear()
    show("due.clear() -> due() is None", due(), None)

    d2 = bs.Signal(None, allow_empty=True, dtype=date)
    show("Signal(None, allow_empty, dtype=date).type", d2.type, date)
    show("...and reads None", d2(), None)
    try:
        d2.set(7)
        show("due.set(7) raises", "no raise", "TypeError")
    except TypeError as e:
        show("due.set(7) raises TypeError", "TypeError", "TypeError")

    try:
        bs.Signal(5, allow_empty=True, dtype=str)
        show("Signal(5, allow_empty, dtype=str) raises", "no raise", "TypeError")
    except TypeError:
        show("Signal(5, allow_empty, dtype=str) raises", "TypeError", "TypeError")

    # "Clearing a bound field now reaches the signal, in both directions"
    d3 = bs.Signal(None, allow_empty=True, dtype=date)
    f3 = bs.DateField(signal=d3)
    d3.set(date(2026, 1, 15))
    f3.value = None
    show("field.value = None -> signal empty", d3(), None)
    d3.set(date(2026, 1, 15))
    d3.clear()
    show("signal.clear() -> field emptied", f3.value, None)

    # "What empty means"
    name = bs.Signal("Ada", allow_empty=True)
    bs.TextField(textsignal=name)
    name.clear()
    show('text signal clears to ""', name(), "")

    pick = bs.Signal("1", allow_empty=True)
    bs.Select(options=[("One", "1"), ("Two", "2")], signal=pick)
    pick.clear()
    show("Select signal clears to None", pick(), None)

    # "Bind that same pick signal to a bs.Label as well and it empties to '' too"
    pick.set("1")
    bs.Label(textsignal=pick)
    pick.clear()
    show('...also bound to a Label -> ""', pick(), "")

    # the map() guidance
    src = bs.Signal(date(2026, 1, 15), allow_empty=True)
    txt = src.map(lambda d: d.strftime("%b %d, %Y") if d else "")
    src.clear()
    show("guarded map survives a clear", txt(), "")

    # the set case the prose does not mention
    multi = bs.Signal({"a"}, allow_empty=True)
    bs.ToggleGroup(options=["a", "b"], mode="multi", signal=multi)
    multi.clear()
    show("multi ToggleGroup signal clears to set()", multi(), set())

    # checkbox.rst -- "a signal bound to an indeterminate checkbox reads False"
    agreed = bs.Signal(False)
    cb = bs.Checkbox("x", tristate=True, signal=agreed)
    cb.value = None
    show("indeterminate checkbox: widget.value", cb.value, None)
    show("indeterminate checkbox: signal reads False", agreed(), False)
app.destroy()
