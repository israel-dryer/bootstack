"""Screenshot scenes for the Visualizing Data how-to set.

Requires the seaborn extra (``pip install bootstack[viz-seaborn]``). Each scene
builds a small, self-contained chart so no external data is needed.
"""
import math

import bootstack as bs


def plotting():
    """Hero — a themed two-series line chart (managed render)."""
    def render(ax):
        xs = [i / 10 for i in range(80)]
        ax.plot(xs, [math.sin(x) for x in xs], label="sin", linewidth=2)
        ax.plot(xs, [math.cos(x) for x in xs], label="cos", linewidth=2)
        ax.set_xlabel("x")
        ax.set_ylabel("amplitude")
        ax.grid(True, alpha=0.3)
        ax.legend(loc="upper right")

    with bs.App(title="Plotting your data", size=(560, 380), padding=16) as app:
        bs.Chart(render=render, grow=True, horizontal="stretch")
    app.run()


def live():
    """Hero — a chart and a DataTable bound to one data source."""
    from bootstack.data import MemoryDataSource

    ds = MemoryDataSource()
    ds.load([
        {"month": "Jan", "sales": 120}, {"month": "Feb", "sales": 180},
        {"month": "Mar", "sales": 150}, {"month": "Apr", "sales": 240},
        {"month": "May", "sales": 200},
    ])

    def render(ax, rows):
        ax.bar([r["month"] for r in rows], [r["sales"] for r in rows])
        ax.set_ylabel("sales")
        ax.grid(True, axis="y", alpha=0.3)

    with bs.App(title="Live charts", size=(560, 480), padding=16, gap=10) as app:
        bs.Chart(render=render, data_source=ds, grow=True, horizontal="stretch")
        bs.DataTable(data_source=ds, columns=["month", "sales"],
                     searchable=False, grow=True, horizontal="stretch")
    app.run()


def statistical():
    """Hero — a seaborn grouped bar chart seeded with the accent palette."""
    import seaborn as sns

    quarters, regions = ["Q1", "Q2", "Q3", "Q4"], ["North", "South", "East"]
    data = {"quarter": [], "region": [], "revenue": []}
    for i, q in enumerate(quarters):
        for j, r in enumerate(regions):
            data["quarter"].append(q)
            data["region"].append(r)
            data["revenue"].append(20 + 8 * i + 5 * j)

    def render(ax):
        sns.barplot(data=data, x="quarter", y="revenue", hue="region", ax=ax)
        ax.set_xlabel("")
        ax.set_ylabel("revenue ($k)")

    with bs.App(title="Statistical plots", size=(560, 380), padding=16) as app:
        bs.Chart(render=render, grow=True, horizontal="stretch")
    app.run()


# The animated-charts page uses a recorded video (chart-animation-video-*.mp4),
# not a static still — so there is no `animated` scene here.

SCENES = {
    "plotting": plotting,
    "live": live,
    "statistical": statistical,
}
