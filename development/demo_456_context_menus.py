"""Manual visual check for #456 -- `context_menus` gates the MENUS, not the EVENT.

Run it:  .venv/bin/python development/demo_456_context_menus.py
   or:   py -3.13 development/demo_456_conte
   xt_menus.py

Nothing else on this branch opens a menu. Every automated check -- the tests,
`probe_456_context_menus.py` -- asserts on the two gate predicates or on the
`<<RowRightClick>>` dispatch. Whether a menu actually APPEARS has only ever been
inferred. That is what this closes, so work the checklist with your eyes.

WHAT TO DO -- four tables, one per `context_menus` value, each captioned with
what it must do. Right-click a COLUMN HEADER and then a DATA ROW in each.

  step 1  HEADER right-click  -> menu appears for 'all' and 'headers' only
  step 2  ROW right-click     -> menu appears for 'all' and 'rows' only
  step 3  the "events" counter under EVERY table increments on a row
          right-click, including 'none'. That is the #456 decoupling: the
          option chooses which menus the table offers, not whether the
          right-click reaches your code
  step 4  on the grouped 'all' table, right-click the GROUP HEADER row and
          then the EMPTY SPACE below the rows -- no menu, and the counter must
          NOT move. Group headers hold no record, so they are not rows

Pre-fix behavior, for comparison while testing:
  steps 1-2  every table shows both menus; the argument never reached the widget
  step 3     the counter stays at 0 for 'none' and for 'headers', because the
             event used to sit behind the row-menu gate -- the bug this branch
             split apart
"""
from __future__ import annotations

import bootstack as bs
from bootstack.events import RowEvent

COLUMNS = ["name", "team"]
ROWS = [
    {"id": 1, "name": "Ada", "team": "Core"},
    {"id": 2, "name": "Linus", "team": "Core"},
    {"id": 3, "name": "Grace", "team": "Tools"},
]

# value -> (header menu, row menu). The captions are written from these so the
# window cannot drift from the contract it is checking.
EXPECTED = {
    "all": (True, True),
    "headers": (True, False),
    "rows": (False, True),
    "none": (False, False),
}

last = bs.Signal("(no right-click reported yet)")


def _caption(value: str) -> str:
    header, row = EXPECTED[value]
    return (
        f"header menu: {'YES' if header else 'no '}    "
        f"row menu: {'YES' if row else 'no '}    "
        f"event: YES"
    )


def _build(value: str, *, grouped: bool = False) -> None:
    """One captioned table with its own right-click counter."""
    seen = [0]

    with bs.Card(padding=10, gap=6):
        bs.Label(f"context_menus={value!r}", font="heading-md")
        bs.Label(_caption(value), font="code")
        if grouped:
            bs.Label("grouped -- use this one for step 4", font="caption")

        table = bs.DataTable(
            columns=COLUMNS,
            rows=ROWS,
            context_menus=value,
            allow_group=grouped,
            searchable=False,
            show_status_bar=False,
            allow_filter=False,
            page_size=10,
        )
        if grouped:
            table.group_by("team")

        counter = bs.Label(font="code", accent="primary")

        def bump(event: RowEvent) -> None:
            seen[0] += 1
            counter.text = f"events: {seen[0]}"
            last.set(
                f"{value!r} -> on_row_right_click   id={event.id!r}   "
                f"record={event.record}"
            )

        counter.text = "events: 0"
        table.on_row_right_click(bump)


with bs.App(title="#456 -- context_menus", minsize=(940, 1), padding=16, gap=12) as app:

    bs.Label("context_menus -- manual check", font="heading-md")
    bs.Label(
        "Right-click a COLUMN HEADER and a DATA ROW in each table. The caption "
        "says what must happen. A menu that appears where the caption says 'no' "
        "-- or fails to appear where it says YES -- is the failure.",
        font="caption",
    )
    bs.Divider()

    with bs.Row(gap=12, vertical_items="top"):
        _build("all", grouped=True)
        _build("headers")

    with bs.Row(gap=12, vertical_items="top"):
        _build("rows")
        _build("none")

    bs.Divider()
    bs.Label(
        "Every counter above must move on a row right-click, 'none' included. "
        "A counter that stays at 0 is the pre-fix coupling coming back.",
        font="caption",
    )
    bs.Label(textsignal=last, font="code")

app.run()