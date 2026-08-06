"""Probe for the #417 review — two follow-on questions the fix raises.

PART 1. Does the SAME missing guard affect right-click? `_on_row_context` carries
the comment "empty space or a group-header row — no row menu" but only tests
`if not iid`, exactly like `_on_row_double_click`. Group headers are real tree
items absent from `_row_map`, so the comment may be describing an intent the
code does not implement. Right-click is bound by default (`context_menus='all'`),
so unlike the double-click case this would be a defect already live on `main`.

PART 2. Is `"_on_row_double_click" in tree.bind("<Double-1>")` a usable
geometry-free invariant? Tkinter's `Misc._register` names the Tcl command
`repr(id(bound_method)) + func.__name__`, so the bound script should carry the
handler's name. If so it is a strictly stronger assertion than "some <Double-*>
sequence is bound", which any unrelated double-click binding satisfies.

Controls, so neither part can read vacuously:
  - PART 1 clicks a LEAF row as well; it must emit a real record, proving the
    synthesis and the stubs work.
  - PART 2 prints the raw bound script for both <Double-1> and <ButtonRelease-1>,
    so a "name present" result can be seen rather than trusted.

Run: py -3.13 development/probe_417_row_event_guards.py
"""

import bootstack as bs

COLUMNS = [
    {"text": "Name", "key": "name", "width": 140},
    {"text": "Team", "key": "team", "width": 140},
]
ROWS = [
    {"name": "Ada", "team": "eng"},
    {"name": "Alan", "team": "eng"},
    {"name": "Grace", "team": "math"},
]


class _NullMenu:
    def show(self, *a, **kw):
        pass


def _center(tree, iid):
    box = tree.bbox(iid)
    assert box != "", f"no bbox for {iid} — unmapped, the probe would be vacuous"
    x, y = box[0] + box[2] // 2, box[1] + box[3] // 2
    assert tree.identify_row(y) == iid, f"hit test missed {iid}"
    return x, y


print(f"bootstack {bs.__version__}\n", flush=True)

double_events, right_events = [], []

with bs.App(title="#417 guards", size=(640, 380), padding=8) as app:
    table = bs.DataTable(columns=COLUMNS, rows=ROWS, horizontal="stretch")
    table.on_row_double_click(lambda e: double_events.append(("dbl", e)))
    table.on_row_right_click(lambda e: right_events.append(("right", e)))

impl = table._internal
impl._open_form_dialog = lambda *a, **kw: None   # modal; blocks the loop
impl._ensure_row_menu = lambda *a, **kw: None    # grabs; blocks the loop
impl._row_menu = _NullMenu()

root = app.tk
root.deiconify()
root.update()
table.group_by("team")
root.update()

tree = impl._tree
header_iid = tree.get_children("")[0]
leaf_iid = tree.get_children(header_iid)[0]

# ------------------------------------------------------------------ PART 2 first
# Read the binding scripts before anything perturbs them.
dbl_script = tree.bind("<Double-1>")
rel_script = tree.bind("<ButtonRelease-1>")

print("PART 2 — is the handler name visible in the bound script?", flush=True)
print(f"    <Double-1>        -> {dbl_script}", flush=True)
print(f"    <ButtonRelease-1> -> {rel_script}   <- control, a different handler", flush=True)
print(f"    '_on_row_double_click' in <Double-1> script .... "
      f"{'_on_row_double_click' in dbl_script}", flush=True)
print(f"    ...and NOT in the <ButtonRelease-1> script ..... "
      f"{'_on_row_double_click' not in rel_script}", flush=True)

# ------------------------------------------------------------------ PART 1
print("\nPART 1 — do the row events guard against group headers?", flush=True)
print(f"    group header in _row_map ... {header_iid in impl._row_map}", flush=True)

for label, iid in (("GROUP HEADER", header_iid), ("leaf row (control)", leaf_iid)):
    double_events.clear()
    right_events.clear()
    x, y = _center(tree, iid)
    for t in (100, 120):
        tree.event_generate("<ButtonPress-1>", x=x, y=y, time=t)
        tree.event_generate("<ButtonRelease-1>", x=x, y=y, time=t + 5)
    tree.event_generate("<Button-3>", x=x, y=y, rootx=x + 200, rooty=y + 200)
    root.update()

    print(f"    {label}", flush=True)
    print(f"      on_row_double_click ... {len(double_events)}"
          + (f"  record={double_events[0][1].record!r} id={double_events[0][1].id!r}"
             if double_events else ""), flush=True)
    print(f"      on_row_right_click .... {len(right_events)}"
          + (f"  record={right_events[0][1].record!r} id={right_events[0][1].id!r}"
             if right_events else ""), flush=True)

root.destroy()
