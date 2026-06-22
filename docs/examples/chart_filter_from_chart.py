"""Filter the DataTable from a chart click, and vice-versa via broadcast search.

The chart and the DataTable share ONE MemoryDataSource. Two integration points
are shown:

1. **Chart → table (click a bar)** — clicks call ``source.where(...)`` directly
   on the shared source. The source broadcasts a DataChangeEvent and both views
   update: the chart re-renders the filtered rows and the DataTable pages to
   the matching record. This is always safe and works with any number of views.

2. **Table → chart (type in the search box)** — the DataTable is created with
   ``broadcast_search=True``, which un-silences the search filter so the same
   DataChangeEvent propagates to the chart. The chart re-renders using only the
   filtered rows.

   .. WARNING::
       ``broadcast_search=True`` should be set on **at most one** DataTable per
       source. Two tables with this flag on the same source will overwrite each
       other's filter on every keystroke, causing unpredictable results.

Click the same bar again, or press **Clear filter**, to restore all rows.

Requires: ``pip install bootstack[viz]``
"""

import bootstack as bs
from bootstack.data import MemoryDataSource, col

SALES = [
    {"month": "Jan", "sales": 120},
    {"month": "Feb", "sales": 180},
    {"month": "Mar", "sales": 150},
    {"month": "Apr", "sales": 90},
    {"month": "May", "sales": 210},
    {"month": "Jun", "sales": 160},
]

active_month = bs.Signal("")  # empty = show all
_state = {"rows": []}           # rows last passed to render (for pick resolution)


with bs.App(title="Filter from chart", min_size=(720, 580), padding=16, gap=12) as app:
    sales = MemoryDataSource()
    sales.load(SALES)

    def render(ax, rows):
        _state["rows"] = rows
        months = [r["month"] for r in rows]
        values = [r["sales"] for r in rows]
        ax.bar(months, values)
        ax.set_ylabel("Sales ($)")
        month = active_month()
        ax.set_title(f"Showing: {month if month else 'all months'} — click a bar to filter")

    chart = bs.Chart(render=render, data_source=sales, grow=True, horizontal="stretch")

    # broadcast_search=True: the search box filters the SHARED source, so
    # the chart re-renders to match what you type. Safe only on ONE table
    # per source — see the module docstring warning.
    bs.DataTable(
        data_source=sales,
        columns=["month", "sales"],
        broadcast_search=True,
        grow=True,
        horizontal="stretch",
    )

    def on_click(event):
        if event.button != 1 or event.inaxes is None or event.xdata is None:
            return
        rows = _state["rows"]
        axes = chart.figure.axes
        if not axes or not rows:
            return
        # For a categorical bar chart, bar centers are at integer positions
        # 0, 1, 2, ... Use round() to find the nearest bar to the click x.
        idx = round(event.xdata)
        if 0 <= idx < len(rows):
            month = rows[idx]["month"]
            if active_month() == month:
                active_month.set("")
                sales.where(None)
            else:
                active_month.set(month)
                sales.where(col("month") == month)

    chart.figure.canvas.mpl_connect("button_press_event", on_click)

    def clear_filter():
        active_month.set("")
        sales.where(None)

    with bs.Row(gap=8):
        bs.Label("Click a bar to filter the table · click again to clear", font="caption")
        bs.Spacer()
        bs.Button("Clear filter", on_click=clear_filter)

app.run()