"""Chart bound to a data source — live, and in sync with a DataTable.

Run this directly. Requires the visualization extra: ``pip install bootstack[viz]``.
A Chart and a DataTable share ONE data source:

- **Add sale** inserts a record — both the chart and the table update.
- **High sales only** filters the *source* (`sales.where(...)`) — both views
  follow the filter, because the chart reads the source's filtered/sorted view.

Note: the DataTable's own search box filters the *table's* local view only; it
does not reshape the shared source, so it does not drive the chart. To filter
what the chart shows, filter the source (as the toggle below does).

With ``data_source=``, the chart's ``render`` receives the source's records (a
list of dicts) and re-renders whenever the source changes — including when you
filter or sort the source.
"""

import bootstack as bs
from bootstack.data import MemoryDataSource, col

MONTHS = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug"]


def render(ax, rows):
    """Bar chart of sales by month — `rows` is the source's (filtered) records."""
    ax.bar([r["month"] for r in rows], [r["sales"] for r in rows])
    ax.set_title("Sales by month")
    ax.set_ylabel("sales")


with bs.App(title="Chart + DataTable", min_size=(720, 620), padding=16, gap=12) as app:
    sales = MemoryDataSource()
    sales.load([
        {"month": "Jan", "sales": 120},
        {"month": "Feb", "sales": 180},
        {"month": "Mar", "sales": 150},
    ])

    bs.Label("One source, two views — filter or add and both follow", font="heading-md")
    bs.Chart(render=render, data_source=sales, grow=True, horizontal="stretch")
    # Search is disabled here on purpose: the table's search box filters its own
    # local view, so it would not drive the chart. We filter the SOURCE below
    # (the toggle) so both views stay in sync.
    bs.DataTable(
        data_source=sales, columns=["month", "sales"],
        enable_search=False, grow=True, horizontal="stretch",
    )

    high_only = bs.Signal(False)

    def apply_filter(checked: bool) -> None:
        # Filter the SOURCE — the chart and the table both reflect it.
        if checked:
            sales.where(col("sales") >= 150)
        else:
            sales.where(None)

    high_only.subscribe(apply_filter)

    state = {"i": 3}

    def add_sale():
        i = state["i"]
        state["i"] = i + 1
        month = MONTHS[i % len(MONTHS)]
        sales.insert({"month": f"{month}+{i}", "sales": 100 + (i * 37) % 140})

    with bs.Row(gap=8):
        bs.Switch("High sales only (>= 150)", signal=high_only)
        bs.Spacer()
        bs.Button("Add sale", accent="primary", on_click=add_sale)

app.run()