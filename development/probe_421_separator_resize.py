"""Probe: can a column separator still be dragged when checkboxes are on?

Finding 1 of the #421 review. ``_on_header_click`` special-cases only
``region == "heading"``, so a press on a column *separator* falls into the
toggle-select branch, where ``identify_row(event.y)`` reports no row -- and the
branch returned ``"break"`` anyway, swallowing ttk's ``resize.press``. Column
resizing was therefore dead on every table showing selection checkboxes.

Both arms run in one process, in one root, so the numbers are comparable:

    plain table       control -- resizing has always worked here
    checkbox table    the arm under test

Run it against the fix, then against the unfixed source, e.g.::

    git stash push -- src/bootstack/widgets/_impl/composites/tableview/tableview.py

A probe that reports "resized" on both arms is measuring nothing -- the plain
arm is what proves the drag synthesis works at all.
"""
from __future__ import annotations

import bootstack as bs

ROWS = [
    {"id": 10, "name": "Ada", "role": "eng"},
    {"id": 20, "name": "Boole", "role": "math"},
    {"id": 30, "name": "Church", "role": "math"},
]


def find_separator(tree) -> tuple[int, int] | None:
    """Scan the heading strip for an x where ttk reports a column separator."""
    for y in (4, 8, 12):
        for x in range(2, int(tree.winfo_width()) - 2):
            if tree.identify_region(x, y) == "separator":
                return x, y
    return None


def drag(tree, x: int, y: int, dx: int) -> None:
    tree.event_generate("<ButtonPress-1>", x=x, y=y)
    tree.event_generate("<B1-Motion>", x=x + dx, y=y)
    tree.event_generate("<ButtonRelease-1>", x=x + dx, y=y)


def measure(label: str, table, pump) -> None:
    impl = table._internal
    tree = impl._tree
    print(f"\n=== {label} ===")
    print(f"  toggle-select active: {impl._toggle_select_active()}")

    hit = find_separator(tree)
    if hit is None:
        print("  NO SEPARATOR FOUND -- probe is vacuous, fix the hit test")
        return
    x, y = hit
    print(f"  separator at x={x} y={y}")

    cols = ("#0", "#1", "#2")
    before = {c: tree.column(c, "width") for c in cols}
    drag(tree, x, y, 36)
    pump()
    after = {c: tree.column(c, "width") for c in cols}

    moved = [c for c in cols if before[c] != after[c]]
    for c in cols:
        print(f"  {c}: {before[c]} -> {after[c]}")
    print(f"  RESULT: {'resized ' + str(moved) if moved else 'NOTHING MOVED'}")


with bs.App(title="#421 separator resize", size=(620, 620)) as app:
    plain = bs.DataTable(
        rows=[dict(r) for r in ROWS], columns=["name", "role"], page_size=10,
    )
    checkbox = bs.DataTable(
        rows=[dict(r) for r in ROWS], columns=["name", "role"], page_size=10,
        selection_mode="multi", show_selection_controls=True,
    )

    def run() -> None:
        root = app._tk_root

        def pump() -> None:
            root.update_idletasks()
            root.update()

        pump()
        measure("plain (control)", plain, pump)
        measure("checkboxes (under test)", checkbox, pump)
        app.close()

    app._tk_root.after(150, run)
app.run()