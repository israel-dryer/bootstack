"""Probe: what ORDER does a double-click deliver row events in?

The 0.2.2 notes claim a double-click "runs your `on_row_click` handler twice
before `on_row_double_click`". The counts were measured (2 clicks + 1 double);
the ORDER was not. The binding types suggest the claim is wrong:

    on_row_click        <ButtonRelease-1>   -- fires on release
    on_row_double_click <Double-1>          -- a ButtonPress pattern

which would interleave as click, double, click rather than click, click,
double. This records the actual sequence.

Control: a single click must report exactly one `click` and no `double`, or the
synthesis is not producing what a real double-click produces.
"""
from __future__ import annotations

import bootstack as bs

ROWS = [
    {"id": 10, "name": "Ada", "role": "eng"},
    {"id": 20, "name": "Boole", "role": "math"},
    {"id": 30, "name": "Church", "role": "math"},
]

log: list[str] = []

with bs.App(title="#421 click order", size=(560, 260)) as app:
    table = bs.DataTable(rows=[dict(r) for r in ROWS], columns=["name", "role"], page_size=10)
    table.on_row_click(lambda e: log.append("click"))
    table.on_row_double_click(lambda e: log.append("double"))

    def run() -> None:
        root = app._tk_root

        def pump() -> None:
            root.update_idletasks()
            root.update()

        pump()
        tree = table._internal._tree
        iid = tree.get_children("")[0]
        box = tree.bbox(iid)
        assert box != "", "row has no bbox -- unmapped, probe cannot click"
        x, y = box[0] + box[2] // 2, box[1] + box[3] // 2

        # Tk decides Double from the event's `time` field. Synthesized events
        # default to time=0, so without an explicit clock every press looks
        # like a continuation of the last one -- which reports `double` on the
        # very first press and makes the whole measurement junk.
        clock = {"t": 100_000}

        def press_release(gap_ms: int) -> None:
            clock["t"] += gap_ms
            tree.event_generate("<ButtonPress-1>", x=x, y=y, time=clock["t"])
            clock["t"] += 20
            tree.event_generate("<ButtonRelease-1>", x=x, y=y, time=clock["t"])

        # Control: one click, well clear of any previous one.
        log.clear()
        press_release(2000)
        pump()
        print(f"  single click            -> {log}")
        assert log == ["click"], f"control failed -- a lone click reported {log}"

        # Two presses inside the double-click interval. Tk REJECTS
        # event_generate("<Double-1>") -- Double is a binding pattern, not an
        # event type -- so two timed presses is the only synthesis.
        log.clear()
        press_release(2000)   # first press, clear of the control
        press_release(80)     # second press, inside the interval
        pump()
        print(f"  double click            -> {log}")
        print()
        print(f"  0.2.2 notes claim:  ['click', 'click', 'double']")
        print(f"  actual:             {log}")

        app.close()

    app._tk_root.after(150, run)
app.run()
