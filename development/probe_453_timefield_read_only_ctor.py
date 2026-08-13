"""Does `TimeField(read_only=True)` survive construction? (#453, round-2 F1)

Round 1 fixed the `read_only` SETTER on `TimeField` and left the constructor
sending `state="readonly"`. A `TimeEntry` is always built with
`allow_custom_values=True, enable_search=True`, so `_apply_interaction_state()`
at the end of `SelectBox.__init__` recomputes `typeable=True` and writes
`['!readonly']` straight over it -- the field a caller asked to lock came back
freely typeable, with its time list still opening.

Run it on both sides of the fix. Arms 2-4 are the controls: they must read the
same either way, so an arm-1 difference is behavioral rather than a broken
harness. Output is ASCII (this box's console is cp1252).

    py -3.12 development/probe_453_timefield_read_only_ctor.py

Pre-fix  arm 1: read_only=False typeable=True  popup=True   states=()
Post-fix arm 1: read_only=True  typeable=False popup=False  states=('readonly',)
"""
import bootstack as bs

app = bs.App(title="probe 453")


def report(name, f):
    entry = f._internal._entry
    print(
        "%-28s read_only=%-5s _readonly=%-5s typeable=%-5s popup=%-5s states=%s"
        % (
            name,
            f.read_only,
            f._internal._readonly,
            not entry.instate(["readonly"]),
            f._internal._popup_allowed(),
            tuple(str(s) for s in entry.state()),
        )
    )


# The defect under test.
report("1 ctor read_only=True", bs.TimeField(read_only=True, parent=app))

# Control: the setter path, fixed in round 1. Must stay fixed.
f2 = bs.TimeField(parent=app)
f2.read_only = True
report("2 setter read_only=True", f2)

# Control: a plain field must stay typeable, or arm 1 could not come out the
# other way and would be pinning nothing.
report("3 plain", bs.TimeField(parent=app))

# Control: `disabled` used to shadow `read_only` in an elif. Both are set now.
report("4 disabled", bs.TimeField(disabled=True, parent=app))
report("5 disabled+read_only", bs.TimeField(disabled=True, read_only=True, parent=app))

app.tk.update_idletasks()
print()
print("EXPECT post-fix: arms 1, 2, 5 read_only=True typeable=False popup=False")
print("EXPECT both ways: arm 3 read_only=False typeable=True popup=True")
print("EXPECT both ways: arms 4, 5 carry 'disabled'")
