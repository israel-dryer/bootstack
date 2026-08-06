"""Probe for the #417 review — what does a double-click on a GROUP HEADER emit?

`_on_row_double_click` guards only with `if not iid: return`. A group-header
node IS a real tree item, so `identify_row` returns a truthy iid for it — but
group headers are never put in `_row_map` (see `_render_grouped`). Its sibling
`_on_row_click_event` guards with `if not iid or iid not in self._row_map`.

So the question this probe answers: does double-clicking a group header fire
`on_row_double_click` with an EMPTY record? Before the #417 fix that path only
existed on `allow_edit=True` tables; the fix binds it on every table, so if the
answer is yes, the fix widens the exposure of a latent defect.

Controls, so a null result cannot be vacuous:
  - a leaf row in the same grouped table is double-clicked too; it must fire
    with a real record, proving the probe's two-press synthesis works here.
  - the group-header iid is asserted to be genuinely absent from `_row_map`.

Run: py -3.13 development/probe_417_group_header_double_click.py
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


def _double_click(tree, iid):
    box = tree.bbox(iid)
    assert box != "", f"no bbox for {iid} — unmapped, probe would be vacuous"
    x, y = box[0] + box[2] // 2, box[1] + box[3] // 2
    assert tree.identify_row(y) == iid, f"hit test missed {iid}"
    for t in (100, 120):
        tree.event_generate("<ButtonPress-1>", x=x, y=y, time=t)
        tree.event_generate("<ButtonRelease-1>", x=x, y=y, time=t + 5)


def run(label, **table_kwargs):
    fired = []

    with bs.App(title=f"#417 group {label}", size=(640, 360), padding=8) as app:
        table = bs.DataTable(columns=COLUMNS, rows=ROWS, horizontal="stretch", **table_kwargs)
        table.on_row_double_click(lambda e: fired.append(e))

    impl = table._internal
    impl._open_form_dialog = lambda *a, **kw: None  # modal; blocks the loop

    root = app.tk
    root.deiconify()
    root.update()

    table.group_by("team")  # public API
    root.update()

    tree = impl._tree
    headers = tree.get_children("")
    assert headers, "no group headers rendered — group_by did not take effect"
    header_iid = headers[0]
    leaf_iid = tree.get_children(header_iid)[0]

    in_map_header = header_iid in impl._row_map
    in_map_leaf = leaf_iid in impl._row_map

    _double_click(tree, header_iid)
    root.update()
    header_events = list(fired)
    fired.clear()

    _double_click(tree, leaf_iid)
    root.update()
    leaf_events = list(fired)

    print(f"  {label}", flush=True)
    print(f"    group header in _row_map ......... {in_map_header}", flush=True)
    print(f"    leaf row in _row_map ............. {in_map_leaf}", flush=True)
    print(f"    header double-click fired ........ {len(header_events)}", flush=True)
    for e in header_events:
        print(f"      -> record={e.record!r} id={e.id!r}", flush=True)
    print(f"    leaf double-click fired .......... {len(leaf_events)}   <- control", flush=True)
    for e in leaf_events:
        print(f"      -> record={e.record!r} id={e.id!r}", flush=True)

    root.destroy()
    return header_events, leaf_events


print(f"bootstack {bs.__version__}\n", flush=True)
print("Grouped, read-only table (only reachable AFTER the #417 fix):", flush=True)
h, l = run("read-only")
print("\n" + "=" * 62, flush=True)
print(f"control: probe can double-click a real row ..... {len(l) == 1}", flush=True)
print(f"group header emits a row event ................. {len(h) > 0}", flush=True)
if h:
    print(f"...and its record is empty ..................... {not h[0].record}", flush=True)
