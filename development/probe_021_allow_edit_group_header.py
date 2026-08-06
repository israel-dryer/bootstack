"""Probe the two 0.2.1-reachable group-header defects, on an editable table.

Arm A: does double-clicking a group header desync open-state vs chevron?
Arm B: does it emit RowDoubleClick with an empty record AND open the edit dialog?

`_open_form_dialog` is stubbed — it is modal and blocks the loop forever when
driven synthetically. Control: a double-click on a real DATA row, which SHOULD
emit a populated record and open the dialog.
"""
import subprocess
import bootstack as bs

BRANCH = subprocess.run(["git", "rev-parse", "--abbrev-ref", "HEAD"],
                        capture_output=True, text=True).stdout.strip()
SHA = subprocess.run(["git", "rev-parse", "--short", "HEAD"],
                     capture_output=True, text=True).stdout.strip()

ROWS = [
    {"id": 1, "name": "Ada", "role": "eng"},
    {"id": 2, "name": "Bob", "role": "eng"},
    {"id": 3, "name": "Cy", "role": "ops"},
]

events = []
dialogs = []
out = []

with bs.App(title="probe", size=(600, 400)) as app:
    table = bs.DataTable(rows=ROWS, columns=["id", "name", "role"],
                         allow_edit=True, grow=1)

impl = table._internal
tree = impl._tree

table.on_row_double_click(lambda e: events.append((e.record, e.id)))
impl._open_form_dialog = lambda rec=None, *a, **k: dialogs.append(rec)


def chevron(iid):
    opened = bool(int(tree.item(iid, "open") or 0))
    img = tree.item(iid, "image")
    img = img[0] if isinstance(img, (list, tuple)) and img else img
    return opened, str(img) == str(impl._chevron_icon(True))


def dbl(iid):
    bbox = tree.bbox(iid)
    assert bbox, f"PRECONDITION FAILED: no bbox for {iid}"
    x, y = bbox[0] + 40, bbox[1] + bbox[3] // 2
    for _ in range(2):
        tree.event_generate("<Button-1>", x=x, y=y)
        tree.event_generate("<ButtonRelease-1>", x=x, y=y)
    app.tk.update()


def run():
    impl.set_grouping("role")
    app.tk.update()
    app.tk.update_idletasks()

    header = list(impl._group_parents.values())[0]

    events.clear(); dialogs.clear()
    before = chevron(header)
    dbl(header)
    after = chevron(header)
    out.append(("group header", before, after, list(events), list(dialogs)))

    # ---- control: a real data row ----
    data_iid = next(i for i in impl._row_map)
    if not tree.bbox(data_iid):          # row hidden under a collapsed group
        tree.item(header, open=True); app.tk.update()
    events.clear(); dialogs.clear()
    dbl(data_iid)
    out.append(("data row (control)", None, None, list(events), list(dialogs)))

    app.tk.after(50, app.close)


app.tk.after(300, run)
app.run()

print(f"\n=== ref: {BRANCH} @ {SHA} (allow_edit=True, grouped) ===")
for label, before, after, evs, dlgs in out:
    print(f"\n{label}:")
    if before is not None:
        sync = "IN SYNC" if after[0] == after[1] else "*** DESYNC ***"
        print(f"  open/chevron  {before} -> {after}   {sync}")
    print(f"  RowDoubleClick emitted: {evs}")
    print(f"  edit dialog opened with: {dlgs}")
