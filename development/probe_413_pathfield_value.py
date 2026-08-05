"""Probe for discussion #413 — should PathField.value return pathlib.Path?

Checks the two claims in the post (value is a str; PathField can't be used in
auto-generated Form fields) and the two wrinkles a Path return type has to
survive: the empty state, and 'open_multiple' mode.

Run: py -3.12 development/probe_413_pathfield_value.py
"""
from pathlib import Path

import bootstack as bs
from bootstack.widgets._impl.composites.form import Form as _InternalForm
from bootstack.widgets.types import EditorType
from typing import get_args

checks: list[tuple[str, bool, object]] = []


def check(label: str, ok: bool, got: object) -> None:
    checks.append((label, ok, got))


app = bs.App(title="probe 413")

# --- A: what value returns today -------------------------------------------
pf = bs.PathField(value="C:/tmp/report.csv", parent=app)
v = pf.value
check("A  PathField.value is a str, not a Path", isinstance(v, str) and not isinstance(v, Path), f"{type(v).__name__}={v!r}")

# --- B: the empty state ------------------------------------------------------
empty = bs.PathField(parent=app)
ev = empty.value
check("B  empty PathField.value is '' (Path('') would become Path('.'))", ev == "", repr(ev))

# --- C: open_multiple is a joined string, and the join is lossy --------------
multi = bs.PathField(mode="open_multiple", parent=app)
multi.value = "C:/a.txt, C:/b.txt"
check("C1 open_multiple stores one joined string, not a sequence", isinstance(multi.value, str), repr(multi.value))

# a filename legitimately containing the separator round-trips wrong
tricky = "C:/my, notes.txt"
multi.value = tricky
check("C2 ', ' join is ambiguous — a name containing it cannot be split back",
      len(multi.value.split(", ")) == 2 and multi.value == tricky,
      f"{multi.value!r} -> split gives {multi.value.split(', ')!r}")

# --- D: is 'pathfield' even a Form editor? ----------------------------------
editors = get_args(EditorType)
check("D1 'pathfield' is NOT in EditorType", "pathfield" not in editors, list(editors))

# --- E: what a Path in Form data infers to ----------------------------------
inferred = _InternalForm._infer_dtype_from_value(Path("C:/tmp/report.csv"))
check("E1 a Path value infers dtype 'str'", inferred == "str", repr(inferred))

form = bs.Form(data={"outfile": Path("C:/tmp/report.csv")}, parent=app)
untouched = form.get()["outfile"]
check("E2 an UNTOUCHED Path survives Form.get() -- it is never coerced on the way out",
      isinstance(untouched, Path), f"{type(untouched).__name__}={untouched!r}")

# ...but the editor is a TextField, so the moment anything writes the field the
# Path is replaced by a plain string. The type of a Form value therefore depends
# on whether the field was touched, which is the deeper reason #415 matters.
form.set({"outfile": "C:/tmp/other.csv"})
touched = form.get()["outfile"]
check("E3 any set() replaces it with a str -- value type depends on whether the field was touched",
      isinstance(touched, str) and not isinstance(touched, Path),
      f"{type(touched).__name__}={touched!r}")

# --- F: forcing editor='pathfield' silently degrades -------------------------
f2 = bs.Form(items=[{"key": "outfile", "label": "Out", "editor": "pathfield"}], parent=app)
widget = f2.field("outfile")
check("F  editor='pathfield' silently builds a TextField (no error, no browse button)",
      type(widget).__name__ == "TextField", type(widget).__name__)

print()
failed = 0
for label, ok, got in checks:
    print(f"[{'PASS' if ok else 'FAIL'}] {label}")
    print(f"       got={got}")
    if not ok:
        failed += 1
print()
print(f"{len(checks) - failed}/{len(checks)} checks matched expectations.")
raise SystemExit(1 if failed else 0)