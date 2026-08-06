"""Probe for #417 — DataTable.on_row_double_click never fires.

Hypothesis: the `<Double-1>` binding in TableView._build_tree is gated on
`self._editing['updating']`, which is False unless the user passes
`allow_edit=True`. The public `on_row_double_click` event is advertised
unconditionally, so with default kwargs nothing is ever bound.

Cases, so that a null result cannot be vacuous:
  RAW. a hand-bound <Double-Button-1> on the same tree widget -> proves the probe's
       two-press synthesis really does produce a double-click event. Without this
       control, "0 hits" would just as easily mean "the probe cannot click".
  A.   default table    -> expect double-click DEAD, right-click ALIVE (the report)
  B.   allow_edit=True  -> expect double-click ALIVE (it is the binding that differs)

The modal edit dialog and the grabbing row menu are stubbed out: both block the
event loop forever when driven synthetically, and neither is what is under test.

Run: py -3.13 development/probe_417_datatable_double_click.py
"""

import bootstack as bs

COLUMNS = [
    {"text": "First Name", "key": "first_name", "width": 120},
    {"text": "Last Name", "key": "last_name", "width": 120},
]
ROWS = [
    {"first_name": "Ada", "last_name": "Lovelace"},
    {"first_name": "Alan", "last_name": "Turing"},
]


class _NullMenu:
    def show(self, *a, **kw):
        pass


def run_case(label, **table_kwargs):
    hits = {"double": 0, "right": 0, "raw": 0}

    with bs.App(title=f"#417 {label}", size=(600, 300), padding=8) as app:
        table = bs.DataTable(columns=COLUMNS, rows=ROWS, horizontal="stretch", **table_kwargs)
        table.on_row_double_click(lambda e: hits.__setitem__("double", hits["double"] + 1))
        table.on_row_right_click(lambda e: hits.__setitem__("right", hits["right"] + 1))

    impl = table._internal
    # Neither of these is under test, and both block the loop when driven
    # synthetically (modal wait_window / menu grab).
    impl._open_form_dialog = lambda *a, **kw: None
    impl._ensure_row_menu = lambda *a, **kw: None
    impl._row_menu = _NullMenu()

    root = app.tk
    root.deiconify()
    root.update()

    tree = impl._tree
    mapped = bool(tree.winfo_ismapped())

    # Precondition: a real, hit-testable row. Without this the probe can pass
    # vacuously (bbox() returns '' on an unmapped window).
    iid = tree.get_children()[0]
    box = tree.bbox(iid)
    assert box != "", f"{label}: row bbox empty — window not mapped, probe would be vacuous"
    x, y = box[0] + box[2] // 2, box[1] + box[3] // 2
    assert tree.identify_row(y) == iid, f"{label}: hit test missed the row"

    # Read the binding table BEFORE adding the control binding below, or the
    # control pollutes the very thing being measured.
    has_double = any("Double" in b for b in tree.bind())

    # RAW control: our own double-click binding on the very same widget.
    tree.bind("<Double-Button-1>", lambda e: hits.__setitem__("raw", hits["raw"] + 1), add="+")

    # Tk refuses event_generate("<Double-1>") ("Double, Triple, or Quadruple
    # modifier not allowed"). Double-click is detected by the binding machinery
    # from two presses close in time and position, so synthesize those.
    for t in (100, 120):
        tree.event_generate("<ButtonPress-1>", x=x, y=y, time=t)
        tree.event_generate("<ButtonRelease-1>", x=x, y=y, time=t + 5)
    tree.event_generate("<Button-3>", x=x, y=y, rootx=x + 100, rooty=y + 100)
    root.update()

    print(f"  {label}", flush=True)
    print(f"    tree mapped ................. {mapped}", flush=True)
    print(f"    <Double-*> bound on tree .... {has_double}", flush=True)
    print(f"    RAW double-click hits ....... {hits['raw']}   <- control", flush=True)
    print(f"    on_row_double_click hits .... {hits['double']}", flush=True)
    print(f"    on_row_right_click hits ..... {hits['right']}", flush=True)

    root.destroy()
    return hits, has_double


print(f"bootstack {bs.__version__}\n", flush=True)
print("CASE A — default kwargs (the reporter's code):", flush=True)
a_hits, a_bound = run_case("default")
print(flush=True)
print("CASE B — allow_edit=True:", flush=True)
b_hits, b_bound = run_case("allow_edit=True", allow_edit=True)

print("\n" + "=" * 62, flush=True)
print(f"control: probe CAN synthesize a double-click ... {a_hits['raw'] > 0 and b_hits['raw'] > 0}", flush=True)
print(f"A: double-click dead while right-click alive ... {a_hits['double'] == 0 and a_hits['right'] > 0}", flush=True)
print(f"B: double-click alive with allow_edit=True ..... {b_hits['double'] > 0}", flush=True)
print(f"binding present ONLY when allow_edit=True ...... {(not a_bound) and b_bound}", flush=True)
