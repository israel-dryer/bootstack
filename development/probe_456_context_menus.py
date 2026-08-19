"""#456 — does `DataTable(context_menus=...)` reach the widget?

The report: `bs.DataTable(context_menus="none")` still shows both right-click
menus. The reporter's own diagnosis was that the argument never lands in
`internal_kwargs`.

Two arms, and the second is the one that makes the first mean anything:

    ARM 1  the public wrapper  -- reads the resolved gate after construction
    ARM 2  CONTROL, the internal TableView constructed directly with the same
           argument -- proves the feature itself works, which is what scopes
           the defect to the wrapper rather than to `tableview.py`

Pre-fix, arm 1 reports 'all' for every input while arm 2 reports the value
asked for. Post-fix the two columns agree.

Run:  .venv/bin/python development/probe_456_context_menus.py
ASCII output only (cp1252 consoles -- see CLAUDE.md).
"""
from __future__ import annotations

import bootstack as bs
from bootstack.widgets._impl.composites.tableview.tableview import TableView

COLUMNS = ["name"]
ROWS = [{"name": "Ada"}]
VALUES = ["all", "headers", "rows", "none"]


def _gates(internal) -> str:
    """The seams the click path actually consults, not the raw attribute."""
    return (
        f"resolved={internal._context_menus!r:10} "
        f"header={internal._header_context_enabled()!s:5} "
        f"row={internal._row_context_enabled()!s:5}"
    )


def main() -> None:
    with bs.App(title="probe 456") as app:
        print("ARM 1 -- public wrapper (the reported path)")
        for value in VALUES:
            table = bs.DataTable(columns=COLUMNS, rows=list(ROWS), context_menus=value)
            print(f"  asked={value!r:10} {_gates(table._internal)}")

        print()
        print("ARM 2 -- CONTROL: internal constructed directly")
        master = app._tk_root
        for value in VALUES:
            internal = TableView(master, columns=COLUMNS, rows=list(ROWS), context_menus=value)
            print(f"  asked={value!r:10} {_gates(internal)}")

    print()
    print("READING: arm 1 matching arm 2 means the wrapper forwards the argument.")
    print("Arm 1 stuck on 'all' while arm 2 varies is the #456 defect.")
    print("Arm 2 failing to vary means the probe is broken, not the wrapper.")


if __name__ == "__main__":
    main()