"""Probe: does double-clicking a group header desync open-state vs chevron?

Control arm: a SINGLE click on the same header (must stay in sync on both refs).
Prints the branch it is running on so a "baseline" arm cannot silently be the
wrong ref.
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
COLS = ["id", "name", "role"]

results = []

with bs.App(title="probe", size=(600, 400)) as app:
    table = bs.DataTable(rows=ROWS, columns=COLS, grow=1)

impl = table._internal
tree = impl._tree


def chevron_state(iid):
    """Return (open_bool, chevron_says_open_bool)."""
    opened = bool(int(tree.item(iid, "open") or 0))
    img = tree.item(iid, "image")
    img = img[0] if isinstance(img, (list, tuple)) and img else img
    open_icon = impl._chevron_icon(True)
    shown_open = (str(img) == str(open_icon))
    return opened, shown_open


def press(iid, times):
    bbox = tree.bbox(iid)
    assert bbox, f"PRECONDITION FAILED: no bbox for {iid} (unmapped?)"
    x = bbox[0] + 40
    y = bbox[1] + bbox[3] // 2
    for _ in range(times):
        tree.event_generate("<Button-1>", x=x, y=y)
        tree.event_generate("<ButtonRelease-1>", x=x, y=y)
    app.tk.update()


def run():
    impl.set_grouping("role")
    app.tk.update()
    app.tk.update_idletasks()

    headers = list(impl._group_parents.values())
    assert headers, "PRECONDITION FAILED: no group headers"
    h_single, h_double = headers[0], headers[1] if len(headers) > 1 else headers[0]

    # ---- control: single click ----
    before = chevron_state(h_single)
    press(h_single, 1)
    after = chevron_state(h_single)
    results.append(("single-click control", before, after))

    # ---- test: double click ----
    before = chevron_state(h_double)
    press(h_double, 2)
    after = chevron_state(h_double)
    results.append(("double-click", before, after))

    # ---- keyboard arm: is the <<TreeviewOpen>> ordering bug pre-existing? ----
    # collapse then re-open a header with <space> only; never touches <Double-1>.
    tree.focus_set()
    tree.focus(h_single)
    tree.selection_set(h_single)
    app.tk.update()
    before = chevron_state(h_single)
    tree.event_generate("<space>")   # close
    app.tk.update()
    mid = chevron_state(h_single)
    tree.event_generate("<space>")   # open
    app.tk.update()
    after = chevron_state(h_single)
    results.append(("keyboard <space> close", before, mid))
    results.append(("keyboard <space> open", mid, after))

    app.tk.after(50, app.close)


app.tk.after(300, run)
app.run()

print(f"\n=== ref: {BRANCH} @ {SHA} ===")
for label, (o0, c0), (o1, c1) in results:
    verdict = "IN SYNC" if o1 == c1 else "*** DESYNC ***"
    print(f"{label:24s} before open={o0} chevron_open={c0} "
          f"-> after open={o1} chevron_open={c1}   {verdict}")
