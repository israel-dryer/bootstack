"""Measure whether emit() on a NATIVE-sequence event drives the widget (#396).

Three states matter:
  pre-#396  emit() fired at the outer frame  -> inert
  on-branch emit() fired at the inner entry  -> drives _handle_focus_out etc.
  fixed     emit() fires at the outer frame for native sequences only -> inert
            while emit("change") still reaches on_change().
"""
import bootstack as bs
from bootstack.events import ChangeEvent

results = {}

with bs.App(title="probe") as app:
    field = bs.TextField(placeholder="type here")
    plain = bs.TextField()
    changes = []
    field.on_change(lambda e: changes.append(e.value))

app._tk_root.update_idletasks()

# --- 1. emit("focus") must not touch the placeholder ---------------------
before = field._internal._entry.get()
field.emit("focus")
app._tk_root.update()
after = field._internal._entry.get()
results["focus_inert"] = (before == after, f"{before!r} -> {after!r}")

# --- 2. emit("blur") must not commit / fire a spurious ChangeEvent -------
changes.clear()
field.emit("blur")
app._tk_root.update()
results["blur_no_spurious_change"] = (changes == [], f"changes={changes!r}")

# --- 3. emit("submit") must not run the field's Return handling ----------
changes.clear()
field.emit("submit")
app._tk_root.update()
results["submit_no_spurious_change"] = (changes == [], f"changes={changes!r}")

# --- 4. the real #396 fix must still hold: emit("change") -> on_change ---
changes.clear()
field.emit("change", data=ChangeEvent(value="reached"))
app._tk_root.update()
results["change_reaches_on_change"] = (changes == ["reached"], f"changes={changes!r}")

# --- 5. control: a field with no placeholder behaves the same -----------
pchanges = []
plain.on_change(lambda e: pchanges.append(e.value))
plain.emit("blur")
app._tk_root.update()
results["plain_blur_inert"] = (pchanges == [], f"changes={pchanges!r}")

ok = sum(1 for passed, _ in results.values() if passed)
for name, (passed, detail) in results.items():
    print(f"{'PASS' if passed else 'FAIL'}  {name:32} {detail}")
print(f"\n{ok}/{len(results)}")
