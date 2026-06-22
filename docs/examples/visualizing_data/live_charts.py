"""Live and data-driven charts — a Chart and a DataTable on one source.

Run this directly. Requires the visualization extra:
``pip install bootstack[viz]``.

The chart and the table read the **same** `DataSource`, so they stay in lockstep:
add a row or filter the source and both update. With ``data_source=``, the
chart's ``render`` receives the source's records (a list of dicts) and re-renders
whenever the source changes — including when you filter or sort it.
"""
import bootstack as bs
from bootstack.data import MemoryDataSource, col


def render(ax, rows):
    """Bar chart of sales by month — `rows` is the source's (filtered) records."""
    ax.bar([r["month"] for r in rows], [r["sales"] for r in rows])
    ax.set_ylabel("sales")
    ax.grid(True, axis="y", alpha=0.3)


with bs.App(title="Live charts", min_size=(680, 620), padding=16, gap=12) as app:
    sales = MemoryDataSource()
    sales.load([
        {"month": "Jan", "sales": 120},
        {"month": "Feb", "sales": 180},
        {"month": "Mar", "sales": 150},
        {"month": "Apr", "sales": 240},
        {"month": "May", "sales": 200},
    ])

    bs.Label("One source, two views — they stay in sync", font="heading-md")
    bs.Chart(render=render, data_source=sales, grow=True, horizontal="stretch")
    bs.DataTable(data_source=sales, columns=["month", "sales"],
                 searchable=False, grow=True, horizontal="stretch")

    high_only = bs.Signal(False)

    def apply_filter(checked):
        # Filtering the SOURCE updates both the chart and the table.
        sales.where(col("sales") >= 180 if checked else None)

    high_only.subscribe(apply_filter)

    state = {"n": 6}

    def add_month():
        n = state["n"]
        state["n"] = n + 1
        sales.insert({"month": f"M{n}", "sales": 100 + (n * 43) % 180})

    with bs.Row(gap=8, horizontal="stretch"):
        bs.Switch("High months only (>= 180)", signal=high_only)
        bs.Spacer()
        bs.Button("Add month", accent="primary", on_click=add_month)

app.run()
