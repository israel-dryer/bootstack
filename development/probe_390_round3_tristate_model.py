"""Is tristate an INITIAL state only, or reachable at runtime? ASCII only."""
import bootstack as bs

with bs.App(title="t") as app:
    print("=== what tristate=True alone does at construction ===")
    a = bs.Checkbox("a", tristate=True)
    print("  Checkbox(tristate=True).value        =", repr(a.value))
    b = bs.Checkbox("b")
    print("  Checkbox().value                     =", repr(b.value))
    c = bs.Checkbox("c", tristate=True, value=False)
    print("  Checkbox(tristate=True, value=False) =", repr(c.value))

    print("\n=== can a USER click reach indeterminate? cycle from each state ===")
    d = bs.Checkbox("d", tristate=True)
    seq = [d.value]
    for _ in range(5):
        d.tk.invoke()          # what a real click runs
        seq.append(d.value)
    print("  invoke() cycle from indeterminate:", seq)

    e = bs.Checkbox("e", tristate=True, value=False)
    seq2 = [e.value]
    for _ in range(5):
        e.tk.invoke()
        seq2.append(e.value)
    print("  invoke() cycle from False:        ", seq2)

    print("\n=== can CODE return to indeterminate at runtime? ===")
    f = bs.Checkbox("f", tristate=True, value=True)
    print("  start          =", repr(f.value))
    f.value = None
    print("  after value=None =", repr(f.value))
    f.value = True
    f.value = None
    print("  and again        =", repr(f.value))

    print("\n=== non-tristate checkbox asked for None ===")
    g = bs.Checkbox("g")
    try:
        g.value = None
        print("  Checkbox(tristate=False).value = None ->", repr(g.value))
    except Exception as ex:
        print("  raised:", type(ex).__name__, ex)
app.destroy()
